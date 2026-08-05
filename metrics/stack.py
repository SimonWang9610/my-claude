#!/usr/bin/env python3
"""stack.py — run and query the local Claude Code telemetry stack
(OTel Collector -> Prometheus + Loki -> Grafana).

  python3 metrics/stack.py up            # start containers, point Claude Code at them, import dashboard
  python3 metrics/stack.py summary       # cost / tokens / sessions in the terminal
  python3 metrics/stack.py down          # stop containers (data volumes survive)

Configuration lives in metrics/config.json; override any section from a
gitignored metrics/config.local.json. Stdlib only — no jq, no pip installs.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
COMPOSE_FILE = HERE / "docker-compose.yml"
CONFIG = HERE / "config.json"
CONFIG_LOCAL = HERE / "config.local.json"

# Env keys this script owns in the Claude Code settings file — written by
# `configure`, removed by `unconfigure`. Nothing else in the file is touched.
OWNED_ENV_KEYS = [
    "CLAUDE_CODE_ENABLE_TELEMETRY",
    "OTEL_METRICS_EXPORTER",
    "OTEL_LOGS_EXPORTER",
    "OTEL_EXPORTER_OTLP_PROTOCOL",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE",
    "OTEL_LOG_USER_PROMPTS",
    "OTEL_LOG_ASSISTANT_RESPONSES",
    "OTEL_LOG_TOOL_DETAILS",
]

# label -> (metric-name prefix, aggregation applied to the resolved series)
CANNED_SUMMARY = [
    ("Sessions", "claude_code_session_count", "sum({m})"),
    ("Cost USD", "claude_code_cost_usage", "sum({m})"),
    ("Cost USD by model", "claude_code_cost_usage", "sum by (model) ({m})"),
    ("Tokens by type", "claude_code_token_usage", "sum by (type) ({m})"),
    ("Tokens by model", "claude_code_token_usage", "sum by (model) ({m})"),
    ("Lines of code", "claude_code_lines_of_code_count", "sum by (type) ({m})"),
    ("Commits", "claude_code_commit_count", "sum({m})"),
    ("Pull requests", "claude_code_pull_request_count", "sum({m})"),
    ("Edit decisions", "claude_code_code_edit_tool_decision", "sum by (decision) ({m})"),
    ("Active time", "claude_code_active_time", "sum({m})"),
]

UNITS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}


# --------------------------------------------------------------------------- config


def load_config() -> dict:
    cfg = json.loads(CONFIG.read_text())
    if CONFIG_LOCAL.exists():
        for section, value in json.loads(CONFIG_LOCAL.read_text()).items():
            if isinstance(value, dict) and isinstance(cfg.get(section), dict):
                cfg[section].update(value)
            else:
                cfg[section] = value
    return cfg


def grafana_url(cfg: dict) -> str:
    return "http://localhost:%s" % cfg["grafana"]["port"]


def prometheus_url(cfg: dict) -> str:
    return "http://localhost:%s" % cfg["prometheus"]["port"]


def loki_url(cfg: dict) -> str:
    return "http://localhost:%s" % cfg["loki"]["port"]


def otlp_endpoint(cfg: dict) -> str:
    configured = cfg["claude"].get("endpoint")
    if configured:
        return configured
    port = cfg["otlp"]["httpPort"] if cfg["claude"]["protocol"] != "grpc" else cfg["otlp"]["grpcPort"]
    return "http://localhost:%s" % port


def settings_path(cfg: dict) -> Path:
    return Path(os.path.expanduser(cfg["claude"]["settingsPath"]))


def otel_env(cfg: dict) -> dict:
    env = {
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_LOGS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_PROTOCOL": cfg["claude"]["protocol"],
        "OTEL_EXPORTER_OTLP_ENDPOINT": otlp_endpoint(cfg),
        # Claude Code defaults to delta temporality; cumulative is what Prometheus
        # counters expect, and it survives a collector restart without losing totals.
        "OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE": "cumulative",
    }
    if cfg["claude"].get("logContent"):
        env["OTEL_LOG_USER_PROMPTS"] = "1"
        env["OTEL_LOG_ASSISTANT_RESPONSES"] = "1"
        env["OTEL_LOG_TOOL_DETAILS"] = "1"
    env.update(cfg["claude"].get("extraEnv") or {})
    return env


# --------------------------------------------------------------------------- shell


def die(message: str) -> "NoReturn":  # noqa: F821
    sys.exit("ERROR: %s" % message)


def compose(cfg: dict, *args: str, check: bool = True) -> int:
    if shutil.which("docker") is None:
        die("docker not found on PATH — install Docker Desktop or the docker CLI.")
    env = dict(os.environ)
    env.update(
        {
            "METRICS_PROJECT": cfg["project"],
            "GRAFANA_PORT": str(cfg["grafana"]["port"]),
            "GRAFANA_USER": cfg["grafana"]["user"],
            "GRAFANA_PASSWORD": cfg["grafana"]["password"],
            "PROMETHEUS_PORT": str(cfg["prometheus"]["port"]),
            "PROMETHEUS_RETENTION": cfg["prometheus"]["retention"],
            "LOKI_PORT": str(cfg["loki"]["port"]),
            "LOKI_RETENTION": cfg["loki"]["retention"],
            "OTLP_GRPC_PORT": str(cfg["otlp"]["grpcPort"]),
            "OTLP_HTTP_PORT": str(cfg["otlp"]["httpPort"]),
        }
    )
    base = ["docker", "compose", "-f", str(COMPOSE_FILE)]
    result = subprocess.run(base + list(args), env=env)
    if check and result.returncode != 0:
        sys.exit(result.returncode)
    return result.returncode


# --------------------------------------------------------------------------- http


def http_json(url: str, payload: object = None, auth: "tuple | None" = None, timeout: int = 15) -> object:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    if auth:
        token = base64.b64encode(("%s:%s" % auth).encode()).decode()
        request.add_header("Authorization", "Basic %s" % token)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def reachable(url: str, timeout: int = 3) -> bool:
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except urllib.error.HTTPError:
        return True  # any HTTP response proves the port is serving
    except Exception:
        return False


def tcp_open(host: str, port: int, timeout: int = 3) -> bool:
    try:
        socket.create_connection((host, port), timeout=timeout).close()
        return True
    except OSError:
        return False


def parse_since(value: str) -> int:
    """'24h' -> 86400 seconds."""
    if not value or value[-1] not in UNITS or not value[:-1].isdigit():
        die("--since must look like 30m, 24h, 7d (got %r)" % value)
    return int(value[:-1]) * UNITS[value[-1]]


# --------------------------------------------------------------------------- claude settings


def configure_claude(cfg: dict) -> None:
    path, wanted = settings_path(cfg), otel_env(cfg)
    settings = {}
    if path.exists():
        try:
            settings = json.loads(path.read_text())
        except json.JSONDecodeError:
            die("%s is not valid JSON — refusing to edit it." % path)
        if all(settings.get("env", {}).get(k) == v for k, v in wanted.items()):
            print("Claude Code already points at this stack: %s" % path)
            return
        backup = path.with_suffix(".json.bak.%s" % time.strftime("%Y%m%d-%H%M%S"))
        backup.write_text(path.read_text())
        print("Backed up %s -> %s" % (path, backup.name))

    settings.setdefault("env", {}).update(wanted)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    print("Wrote OTEL env into %s" % path)
    for key, value in wanted.items():
        print("  %s=%s" % (key, value))
    print("Restart Claude Code for telemetry changes to take effect.")


def unconfigure_claude(cfg: dict) -> None:
    path = settings_path(cfg)
    if not path.exists():
        print("No settings file at %s — nothing to remove." % path)
        return
    settings = json.loads(path.read_text())
    removed = [k for k in OWNED_ENV_KEYS if k in settings.get("env", {})]
    for key in removed:
        del settings["env"][key]
    if not settings.get("env"):
        settings.pop("env", None)
    path.write_text(json.dumps(settings, indent=2) + "\n")
    print("Removed %d OTEL key(s) from %s" % (len(removed), path))


# --------------------------------------------------------------------------- commands


def cmd_up(cfg: dict, args: argparse.Namespace) -> None:
    compose(cfg, "up", "-d")
    if not args.no_configure:
        configure_claude(cfg)
    if not args.no_dashboard:
        wait_for_grafana(cfg)
        import_dashboard(cfg)
    print("\nStack up:")
    print("  Grafana     %s/dashboards  (%s / %s)" % (grafana_url(cfg), cfg["grafana"]["user"], cfg["grafana"]["password"]))
    print("  Prometheus  %s" % prometheus_url(cfg))
    print("  Loki        %s" % loki_url(cfg))
    print("  OTLP        grpc :%s · http :%s" % (cfg["otlp"]["grpcPort"], cfg["otlp"]["httpPort"]))
    print("  Retention   metrics %s · logs %s" % (cfg["prometheus"]["retention"], cfg["loki"]["retention"]))
    print("\nNext: restart Claude Code, run a session, then `python3 %s summary`" % _rel(__file__))


def wait_for_grafana(cfg: dict, attempts: int = 60) -> None:
    url = "%s/api/health" % grafana_url(cfg)
    for _ in range(attempts):
        if reachable(url, timeout=2):
            return
        time.sleep(2)
    die("Grafana did not become ready at %s" % grafana_url(cfg))


def import_dashboard(cfg: dict) -> None:
    dashboard_id = cfg["grafana"]["dashboardId"]
    remote = http_json("https://grafana.com/api/dashboards/%s" % dashboard_id)
    dashboard = remote["json"]
    inputs = [
        {
            "name": item.get("name"),
            "type": item.get("type"),
            "pluginId": item.get("pluginId"),
            "value": "Loki" if "loki" in (item.get("pluginId", "") + item.get("name", "")).lower() else "Prometheus",
        }
        for item in dashboard.get("__inputs", [])
    ]
    http_json(
        "%s/api/dashboards/import" % grafana_url(cfg),
        payload={"dashboard": dashboard, "overwrite": True, "inputs": inputs},
        auth=(cfg["grafana"]["user"], cfg["grafana"]["password"]),
    )
    print("Imported Grafana dashboard %s." % dashboard_id)


def claude_metric_names(cfg: dict) -> "list[str]":
    body = http_json("%s/api/v1/label/__name__/values" % prometheus_url(cfg))
    return sorted(n for n in body.get("data", []) if n.startswith("claude_code"))


def promql_query(cfg: dict, expr: str) -> "list[tuple[str, str]]":
    url = "%s/api/v1/query?%s" % (prometheus_url(cfg), urllib.parse.urlencode({"query": expr}))
    body = http_json(url)
    if body.get("status") != "success":
        die("Prometheus rejected the query: %s" % body.get("error", body))
    rows = []
    for series in body["data"]["result"]:
        labels = {k: v for k, v in series["metric"].items() if k != "__name__"}
        label = ", ".join("%s=%s" % kv for kv in sorted(labels.items())) or series["metric"].get("__name__", "")
        rows.append((label, series["value"][1]))
    return rows


def print_rows(rows: "list[tuple[str, str]]", indent: str = "  ") -> None:
    if not rows:
        print("%s(no data)" % indent)
        return
    width = max(len(label) for label, _ in rows)
    for label, value in rows:
        try:
            shown = "%.4g" % float(value)
        except ValueError:
            shown = value
        print("%s%-*s  %s" % (indent, width, label, shown))


def cmd_summary(cfg: dict, args: argparse.Namespace) -> None:
    available = claude_metric_names(cfg)
    if not available:
        die(
            "No claude_code_* metrics in Prometheus yet. Check `stack.py verify`, "
            "and remember Claude Code must be restarted after `configure`."
        )
    window = " over last %s" % args.since if args.since else " (all time)"
    print("Claude Code telemetry%s\n" % window)
    for label, prefix, template in CANNED_SUMMARY:
        series = next((n for n in available if n.startswith(prefix)), None)
        if series is None:
            continue
        selector = "increase(%s[%s])" % (series, args.since) if args.since else series
        print("%s  [%s]" % (label, series))
        print_rows(promql_query(cfg, template.format(m=selector)))
        print()


def cmd_metrics(cfg: dict, args: argparse.Namespace) -> None:
    names = claude_metric_names(cfg)
    print("\n".join(names) if names else "(no claude_code_* metrics yet)")


def cmd_query(cfg: dict, args: argparse.Namespace) -> None:
    print_rows(promql_query(cfg, args.expr), indent="")


def cmd_search(cfg: dict, args: argparse.Namespace) -> None:
    end = time.time()
    start = end - parse_since(args.since)
    url = "%s/loki/api/v1/query_range?%s" % (
        loki_url(cfg),
        urllib.parse.urlencode(
            {
                "query": args.expr,
                "start": str(int(start * 1e9)),
                "end": str(int(end * 1e9)),
                "limit": str(args.limit),
                "direction": "backward",
            }
        ),
    )
    body = http_json(url)
    entries = []
    for stream in body.get("data", {}).get("result", []):
        entries.extend((int(ts), line) for ts, line in stream.get("values", []))
    if not entries:
        print("(no log entries matched %s in the last %s)" % (args.expr, args.since))
        return
    for ts, line in sorted(entries):
        when = datetime.fromtimestamp(ts / 1e9, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        print("%s  %s" % (when, line))


def cmd_labels(cfg: dict, args: argparse.Namespace) -> None:
    body = http_json("%s/loki/api/v1/labels" % loki_url(cfg))
    for name in body.get("data", []):
        values = http_json("%s/loki/api/v1/label/%s/values" % (loki_url(cfg), name)).get("data", [])
        print("%s: %s" % (name, ", ".join(values[:10]) + (" …" if len(values) > 10 else "")))


def cmd_verify(cfg: dict, args: argparse.Namespace) -> None:
    ok = True
    path, wanted = settings_path(cfg), otel_env(cfg)
    env = json.loads(path.read_text()).get("env", {}) if path.exists() else {}
    for key, value in wanted.items():
        actual = env.get(key)
        state = "ok" if actual == value else ("MISSING" if actual is None else "differs (%s)" % actual)
        ok = ok and actual == value
        print("  [%s] %s" % (state, key))

    endpoint = urllib.parse.urlparse(otlp_endpoint(cfg))
    checks = [
        ("OTLP collector", tcp_open(endpoint.hostname or "localhost", endpoint.port or 4317)),
        ("Prometheus", reachable("%s/-/ready" % prometheus_url(cfg))),
        ("Loki", reachable("%s/ready" % loki_url(cfg))),
        ("Grafana", reachable("%s/api/health" % grafana_url(cfg))),
    ]
    for name, up in checks:
        ok = ok and up
        print("  [%s] %s" % ("ok" if up else "DOWN", name))

    try:
        found = claude_metric_names(cfg)
        print("  [%s] claude_code_* metrics ingested (%d series names)" % ("ok" if found else "none yet", len(found)))
        ok = ok and bool(found)
    except Exception as exc:
        ok = False
        print("  [DOWN] could not read metric names: %s" % exc)

    print("\n%s" % ("All checks passed." if ok else "Some checks failed — see above. `stack.py up` fixes most of them."))
    sys.exit(0 if ok else 1)


def _rel(path: str) -> str:
    try:
        return str(Path(path).resolve().relative_to(Path.cwd()))
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------- cli


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command")

    up = sub.add_parser("up", help="start the stack, point Claude Code at it, import the dashboard")
    up.add_argument("--no-configure", action="store_true", help="do not touch the Claude Code settings file")
    up.add_argument("--no-dashboard", action="store_true", help="skip the Grafana dashboard import")
    up.set_defaults(fn=cmd_up)

    sub.add_parser("down", help="stop containers (volumes survive)").set_defaults(
        fn=lambda cfg, a: compose(cfg, "down")
    )
    sub.add_parser("destroy", help="stop containers AND delete the data volumes").set_defaults(
        fn=lambda cfg, a: compose(cfg, "down", "-v")
    )
    sub.add_parser("status", help="container status").set_defaults(fn=lambda cfg, a: compose(cfg, "ps"))

    logs = sub.add_parser("logs", help="follow container logs")
    logs.add_argument("service", nargs="*", help="limit to these services")
    logs.set_defaults(fn=lambda cfg, a: compose(cfg, "logs", "-f", *a.service, check=False))

    sub.add_parser("configure", help="write the OTEL env block into the Claude Code settings file").set_defaults(
        fn=lambda cfg, a: configure_claude(cfg)
    )
    sub.add_parser("unconfigure", help="remove that OTEL env block again").set_defaults(
        fn=lambda cfg, a: unconfigure_claude(cfg)
    )
    sub.add_parser("import-dashboard", help="(re)import the Grafana dashboard").set_defaults(
        fn=lambda cfg, a: (wait_for_grafana(cfg), import_dashboard(cfg))
    )
    sub.add_parser("verify", help="check settings, endpoints, and that metrics are arriving").set_defaults(fn=cmd_verify)

    summary = sub.add_parser("summary", help="cost / tokens / sessions table in the terminal")
    summary.add_argument("--since", help="window such as 24h or 7d (default: all time)")
    summary.set_defaults(fn=cmd_summary)

    sub.add_parser("metrics", help="list the claude_code_* metric names Prometheus has").set_defaults(fn=cmd_metrics)

    query = sub.add_parser("query", help="run a raw PromQL instant query")
    query.add_argument("expr")
    query.set_defaults(fn=cmd_query)

    search = sub.add_parser("search", help="run a LogQL query against Loki")
    search.add_argument("expr", nargs="?", default='{service_name="claude-code"}')
    search.add_argument("--since", default="1h", help="lookback window (default 1h)")
    search.add_argument("--limit", type=int, default=50)
    search.set_defaults(fn=cmd_search)

    sub.add_parser("labels", help="list Loki stream labels and their values").set_defaults(fn=cmd_labels)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return
    args.fn(load_config(), args)


if __name__ == "__main__":
    main()
