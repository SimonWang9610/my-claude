#!/usr/bin/env python3
"""common.py - what every my-invest script shares: the project folder, the one config file, HTTP fetching
with the SEC throttle, and the JSON envelope every script prints.

Project: --project FLAG > $MY_INVEST_PROJECT > the working directory. Everything the plugin writes lives in
<project>/data/: config.json (yours; created with defaults when absent), invest.db (the database), reports/.
"""
import argparse
import datetime as dt
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

DATA_DIR = "data"
CONFIG_NAME = "config.json"
DEFAULT_CONFIG = {
    "sec_user_agent": "",          # SEC asks for "AppName you@example.com"; sec.py refuses to run without it
    "fred_api_key": "",            # optional; without it fred.py reads the public CSV endpoint
    "python": "",                  # optional interpreter for run.sh; else data/.venv is created when needed
    "equity_risk_premium": 4.2,    # percent, Damodaran's implied ERP; edit when he updates it
    "max_horizon_years": 5,      # every outlook, statistic window and DCF forecast stays within this
    "depth": {"news": 10, "peers": 5, "macro_series": 8, "price_years": 5, "fundamental_years": 5},
}
DEFAULT_UA = "my-invest/1.0 (+https://github.com/SimonWang9610/my-claude)"
MAX_ATTEMPTS = 4
BACKOFF_BASE = 1.0
NO_UA_MSG = ('no SEC User-Agent configured: set "sec_user_agent" to "AppName you@example.com" in '
             '<project>/data/config.json (the SEC requires it)')


class FetchError(Exception):
    """A source could not be obtained or read. The message is shown to the user verbatim."""


# --- time ---------------------------------------------------------------------------------------
def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def iso(t=None):
    return (t or utcnow()).strftime("%Y-%m-%dT%H:%M:%SZ")


def today():
    return dt.date.today().isoformat()


# --- project and config -------------------------------------------------------------------------
def resolve_project(flag=""):
    p = flag or os.environ.get("MY_INVEST_PROJECT") or os.getcwd()
    return os.path.abspath(os.path.expanduser(p))


def data_dir(project):
    """<project>/data, created on first use with a .gitignore for the files that never belong in git."""
    d = os.path.join(project, DATA_DIR)
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    gi = os.path.join(d, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w") as f:
            f.write(".venv/\ninvest.db\ninvest.db-*\nconfig.json\n")
    return d


def load_config(project):
    """<project>/data/config.json merged over DEFAULT_CONFIG; written with the defaults when absent."""
    path = os.path.join(data_dir(project), CONFIG_NAME)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
            f.write("\n")
    with open(path) as f:
        user = json.load(f)
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    for k, v in user.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    return cfg


def depth(cfg, key):
    return int(cfg.get("depth", {}).get(key, DEFAULT_CONFIG["depth"][key]))


# --- HTTP ---------------------------------------------------------------------------------------
class TokenBucket:
    """`rate` tokens per second, burst `capacity`; the SEC allows 10 requests/second, we use half."""

    def __init__(self, rate, capacity, clock=time.monotonic, sleep=time.sleep):
        self.rate, self.capacity = float(rate), float(capacity)
        self.tokens, self.clock, self.sleep = float(capacity), clock, sleep
        self.last = clock()
        self.lock = threading.Lock()

    def acquire(self):
        with self.lock:
            while True:
                now = self.clock()
                self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
                self.last = now
                if self.tokens >= 1:
                    self.tokens -= 1
                    return
                self.sleep((1 - self.tokens) / self.rate)


SEC_BUCKET = TokenBucket(rate=5, capacity=2)


def is_sec(url):
    host = urllib.parse.urlparse(url).hostname or ""
    return host == "sec.gov" or host.endswith(".sec.gov")


def redact(url):
    """Drop query parameters that look like keys before a URL is shown or stored."""
    u = urllib.parse.urlsplit(url)
    q = [(k, "REDACTED" if "key" in k.lower() or "token" in k.lower() else v)
         for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True)]
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(q), ""))


def http_get(url, ua=None, accept=None, timeout=30):
    """GET -> bytes. SEC hosts need a declared User-Agent and are throttled; 429 and 5xx are retried."""
    sec = is_sec(url)
    if sec and not ua:
        raise FetchError(NO_UA_MSG)
    headers = {"User-Agent": ua or DEFAULT_UA, "Accept-Encoding": "identity"}
    if accept:
        headers["Accept"] = accept
    last = None
    for attempt in range(MAX_ATTEMPTS):
        if sec:
            SEC_BUCKET.acquire()
        req = urllib.request.Request(url, headers=headers)
        wait = BACKOFF_BASE * (2 ** attempt)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            last = "HTTP %s from %s" % (e.code, redact(url))
            if e.code != 429 and e.code < 500:
                raise FetchError(last)
            ra = e.headers.get("Retry-After") if e.headers else None
            if ra and ra.isdigit():
                wait = max(wait, float(ra))
        except (urllib.error.URLError, OSError) as e:
            last = "network error for %s: %s" % (redact(url), getattr(e, "reason", e))
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(wait)
    raise FetchError("%s (after %d attempts)" % (last, MAX_ATTEMPTS))


def get_json(url, ua=None, timeout=30):
    try:
        return json.loads(http_get(url, ua, "application/json", timeout).decode("utf-8"))
    except ValueError as e:
        raise FetchError("not JSON from %s: %s" % (redact(url), e))


def get_text(url, ua=None, timeout=30):
    return http_get(url, ua, None, timeout).decode("utf-8", "replace")


# --- CLI envelope -------------------------------------------------------------------------------
class Parser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps({"ok": False, "script": self.prog, "error": message}))
        sys.exit(2)


def parser(script, description):
    p = Parser(prog=script, description=description)
    p.add_argument("--project", default="", help="project folder (default: $MY_INVEST_PROJECT or the cwd)")
    p.add_argument("--md", action="store_true", help="print a Markdown table instead of JSON where one exists")
    return p


def emit(obj, md=None):
    """Print the JSON envelope (or the Markdown given) and return 0."""
    if md is not None:
        print(md)
    else:
        print(json.dumps(obj, indent=2, default=str))
    return 0


def fail(script, msg, **extra):
    out = {"ok": False, "script": script, "error": str(msg)}
    out.update(extra)
    print(json.dumps(out, indent=2, default=str))
    return 1


def run_main(script, fn, argv=None):
    """Run fn(argv) -> exit code, turning FetchError into the JSON error envelope."""
    try:
        return fn(argv)
    except FetchError as e:
        return fail(script, e)
    except KeyboardInterrupt:
        return fail(script, "interrupted")
