# metrics — local Claude Code telemetry

Claude Code exports OpenTelemetry metrics and logs when `CLAUDE_CODE_ENABLE_TELEMETRY=1`.
This directory is a self-contained local sink for them: **OTel Collector → Prometheus + Loki
→ Grafana**, driven by one Python script. No `jq`, no `bash`, no pip installs — stdlib only,
Python 3.9+.

## Start

```bash
python3 metrics/stack.py up
```

That single command starts the containers, writes the OTEL env block into
`~/.claude/settings.json` (backing the file up first), and imports the Grafana dashboard.
**Restart Claude Code afterwards** — the exporter reads its env at startup.

```bash
python3 metrics/stack.py verify
```

`verify` is the check that says whether it worked: settings keys present, all four endpoints
answering, and `claude_code_*` series actually in Prometheus. Exit code 0 = wired.

### Why the restart, and why nothing shows up for a minute

Two separate delays, and only the first needs a restart:

- **The `env` block is startup-only.** Claude Code hot-reloads most of `settings.json`
  mid-session, but `env` is read once at session start, and the OTLP exporter is built from
  those variables when the SDK initializes. A running session has already made that decision,
  so there is no reload path — a new process is the only way, whether the vars come from
  `settings.json` or your shell. Nothing is backfilled: a session that ran without telemetry
  recorded nothing to recover.
- **Then ~75s of pipeline lag.** Metrics export every 60s by default and Prometheus scrapes
  every 15s, so `summary` stays empty for about a minute after your first prompt. Logs export
  every 5s, so `search` lights up much sooner. Set `OTEL_METRIC_EXPORT_INTERVAL` to `10000`
  under `claude.extraEnv` in `config.json` while you're testing the wiring.

`verify` reporting settings `ok`, endpoints `ok`, and metrics `none yet` means you're inside
that window — not broken.

| Service | URL |
| --- | --- |
| Grafana | <http://localhost:3000> (`admin` / `admin`) |
| Prometheus | <http://localhost:9090> |
| Loki | <http://localhost:3100> |
| OTLP | gRPC `:4317` · HTTP `:4318` |

## Configure

[`config.json`](config.json) is the only file to edit — ports, Grafana credentials,
retention (metrics `35d`, logs `840h`), dashboard id, and the Claude Code settings path.
To keep local changes out of git, put just the keys you're overriding in
`metrics/config.local.json` (gitignored); it is shallow-merged per section over `config.json`.

Two settings worth knowing:

- **`claude.endpoint`** — `null` means "the local stack". Set it to a remote collector
  (`http://collector.internal:4317`) and `configure` points Claude Code there instead; then
  run `up --no-configure` or skip the stack entirely.
- **`claude.logContent`** — `true` (the default here) adds `OTEL_LOG_USER_PROMPTS`,
  `OTEL_LOG_ASSISTANT_RESPONSES`, and `OTEL_LOG_TOOL_DETAILS`, so prompt/response/tool text
  lands in Loki and becomes greppable. It is stored unencrypted in a local Docker volume —
  set it to `false` if that isn't what you want, then `stack.py configure` again.

`configure` also sets `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE=cumulative`, because
Prometheus counters expect cumulative totals and cumulative survives a collector restart
without losing them.

## Read the metrics from the CLI

Grafana is optional — everything is queryable from the terminal.

```bash
python3 metrics/stack.py summary --since 24h
```

Sessions, cost by model, tokens by type/model, lines of code, commits, PRs, edit
accept/reject decisions, active time. Metric names are **discovered at runtime** (the OTLP →
Prometheus name mangling appends units and `_total`), so the summary never goes stale
against a Claude Code release.

```bash
python3 metrics/stack.py metrics
```

Lists the real `claude_code_*` series names — the starting point for your own PromQL:

```bash
python3 metrics/stack.py query 'sum by (model) (increase(claude_code_cost_usage_USD_total[7d]))'
```

Events (prompts, tool results, API errors, skill activations) are logs, not metrics, and live
in Loki:

```bash
python3 metrics/stack.py search '{service_name="claude-code"} |= "api_error"' --since 24h
```

```bash
python3 metrics/stack.py labels
```

`labels` prints Loki's stream labels and sample values so you can build a selector without
guessing. Use the `prompt.id` attribute to tie one prompt's user_prompt / api_request /
tool_result events together.

### Without any stack at all

For a one-off look, Claude Code can print metrics straight to your terminal — no Docker,
no Grafana:

```bash
CLAUDE_CODE_ENABLE_TELEMETRY=1 OTEL_METRICS_EXPORTER=console OTEL_METRIC_EXPORT_INTERVAL=1000 claude
```

Add `OTEL_LOGS_EXPORTER=console` for events. `claude --debug` shows export errors when
something is configured but nothing arrives.

## Commands

| Command | Does |
| --- | --- |
| `up [--no-configure] [--no-dashboard]` | start containers + configure Claude Code + import dashboard |
| `verify` | settings + endpoints + metrics-arriving check (exit 0/1) |
| `summary [--since 24h]` | canned cost/token/session tables |
| `metrics` · `query <promql>` | list series names · run a raw instant query |
| `search [logql] [--since 1h] [--limit 50]` · `labels` | query Loki · list its labels |
| `configure` · `unconfigure` | write · remove the OTEL env block in the settings file |
| `status` · `logs [service]` | container status · follow logs |
| `down` · `destroy` | stop containers · stop and delete the data volumes |
| `import-dashboard` | re-import the Grafana dashboard |

## Notes

- Ports collide with any other local telemetry stack (a work harness, for instance). Change
  them in `config.local.json`; the compose project name is `my-claude-metrics`, so the two
  stacks stay separate otherwise.
- `down` keeps your data; only `destroy` deletes the volumes.
- Cost figures are Claude Code's own accounting, not billing truth.
