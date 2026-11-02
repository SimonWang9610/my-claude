"""Shared plumbing for my-invest scripts: HTTP, throttle, file cache, provenance, CLI, error envelope.

Python 3.9, stdlib only. Every script prints one JSON object; on any failure it prints
{"error": "...", "script": "..."} and exits 1 (see `run_main`).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

# --- cache TTLs (seconds) per source; "prices" is handled by trading-day rule -------------------
TTL = {"edgar": 86400, "prices": 86400, "macro": 86400, "news": 6 * 3600,
       "filings": 90 * 86400}  # filing documents are immutable once filed
DEFAULT_UA = "my-invest/0.1"
MAX_ATTEMPTS = 4
BACKOFF_BASE = 1.0  # seconds; doubles per attempt


class FetchError(Exception):
    """Any failure to obtain or interpret a source. Message is shown verbatim to the user."""


def utcnow():
    return dt.datetime.now(dt.timezone.utc)


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)


# --- throttle --------------------------------------------------------------------------------
class TokenBucket:
    """Token bucket: `rate` tokens/second, burst `capacity`. `clock`/`sleep` are injectable."""

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


# --- cache -----------------------------------------------------------------------------------
def last_trading_date(t):
    """Calendar date of the most recent weekday on or before t (holidays ignored)."""
    d = t.date()
    while d.weekday() >= 5:
        d -= dt.timedelta(days=1)
    return d


def is_fresh(source, retrieved, now, ttl=None):
    age = (now - retrieved).total_seconds()
    if age < 0:
        return False
    ttl = TTL[source] if ttl is None else ttl
    if age < ttl:
        return True
    if source == "prices":  # 1 trading day: weekends and holidays-free approximation
        return age < 3 * 86400 and last_trading_date(now) == last_trading_date(retrieved)
    return False


class Cache:
    """<store>/.cache/<source>/<sha256(key)>.body + .meta.json {key, retrieved}."""

    def __init__(self, root, source, now=utcnow):
        self.root, self.dir = root, os.path.join(root, ".cache", source)
        self.source, self.now = source, now

    def _paths(self, key):
        h = hashlib.sha256(key.encode("utf-8")).hexdigest()
        return os.path.join(self.dir, h + ".body"), os.path.join(self.dir, h + ".meta.json")

    def get(self, key, refresh=False, ttl=None):
        """Return (body_bytes, retrieved_iso) when a fresh entry exists, else None."""
        if refresh:
            return None
        body_p, meta_p = self._paths(key)
        try:
            with open(meta_p, "r", encoding="utf-8") as f:
                meta = json.load(f)
            retrieved = parse_iso(meta["retrieved"])
            if not is_fresh(self.source, retrieved, self.now(), ttl):
                return None
            with open(body_p, "rb") as f:
                return f.read(), meta["retrieved"]
        except (OSError, ValueError, KeyError):
            return None

    def put(self, key, body):
        ensure_store(self.root)
        os.makedirs(self.dir, exist_ok=True)
        body_p, meta_p = self._paths(key)
        retrieved = iso(self.now())
        with open(body_p, "wb") as f:
            f.write(body)
        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump({"key": key, "retrieved": retrieved}, f)
        return retrieved


# --- HTTP ------------------------------------------------------------------------------------
def http_get(url, ua=None, accept=None, timeout=30):
    """GET with throttle (sec.gov), declared User-Agent, retry+backoff on 429/5xx. Returns bytes."""
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
            last = "HTTP %s from %s" % (e.code, _redact(url))
            if e.code != 429 and e.code < 500:
                raise FetchError(last)
            ra = e.headers.get("Retry-After") if e.headers else None
            if ra and ra.isdigit():
                wait = max(wait, float(ra))
        except (urllib.error.URLError, OSError) as e:
            last = "network error for %s: %s" % (_redact(url), getattr(e, "reason", e))
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(wait)
    raise FetchError("%s (after %d attempts)" % (last, MAX_ATTEMPTS))


def _redact(url):
    p = urllib.parse.urlparse(url)
    q = [(k, "REDACTED" if k == "api_key" else v) for k, v in urllib.parse.parse_qsl(p.query)]
    return urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(q)))


class Ctx:
    """Per-run context: store root (holds .cache/), UA, refresh flag. `get` is cached HTTP; returns (bytes, retrieved_iso)."""

    def __init__(self, root, ua=None, refresh=False, now=utcnow, data="", project="", env=None):
        self.root, self.ua, self.refresh, self.now = root, ua, refresh, now
        self.data, self.project, self.env = data, project, env

    def with_refresh(self, refresh=True):
        return Ctx(self.root, self.ua, refresh, self.now, self.data, self.project, self.env)

    def setting(self, key):
        """A setting (e.g. fred_api_key) through the same precedence as the CLI settings; "" when unset."""
        v = resolve_setting(key, "", self.data, self.env, self.project)
        return "" if v is None else str(v)

    def cache(self, source):
        return Cache(self.root, source, self.now)

    def get(self, url, source, ttl=None, key=None, accept=None):
        c = self.cache(source)
        key = key or url
        hit = c.get(key, self.refresh, ttl)
        if hit:
            return hit
        body = http_get(url, self.ua, accept)
        return body, c.put(key, body)

    def get_json(self, url, source, ttl=None, key=None):
        body, retrieved = self.get(url, source, ttl, key, accept="application/json")
        try:
            return json.loads(body.decode("utf-8")), retrieved
        except ValueError as e:
            raise FetchError("invalid JSON from %s: %s" % (_redact(url), e))


# --- provenance ------------------------------------------------------------------------------
class Provenance:
    """`sources` map with stable ids S1..Sn: same (class, what, url) always returns the same id."""

    def __init__(self):
        self.sources = {}

    def add(self, klass, what, url, as_of, retrieved, sid=None):
        """Return the id of the (class, what, url) row, adding it first when new. `sid` pins the id
        (facts.py keeps S1..S10 stable); otherwise the next number above the highest in use."""
        for k, s in self.sources.items():
            if (s["class"], s["what"], s["url"]) == (klass, what, url):
                return k
        sid = sid or "S%d" % (max([int(k[1:]) for k in self.sources] or [0]) + 1)
        self.sources[sid] = {"class": klass, "what": what, "url": url,
                             "as_of": as_of, "retrieved": (retrieved or "")[:10]}
        return sid

    def merge(self, other_sources, ids=None):
        """Add another script's sources in S-number order; return {their_id: our_id}.
        `ids` ({their_id: our_id}) pins the ids this run assigns; unlisted rows take the next free number."""
        idmap = {}
        for sid in sorted(other_sources, key=lambda s: int(s[1:])):
            s = other_sources[sid]
            idmap[sid] = self.add(s["class"], s["what"], s["url"], s["as_of"], s["retrieved"], (ids or {}).get(sid))
        return idmap

    def ordered(self):
        return {k: self.sources[k] for k in sorted(self.sources, key=lambda k: int(k[1:]))}


def remap_src(obj, idmap):
    """Rewrite every `src` / `erp_src` value (string id) in a nested structure, in place."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("src", "erp_src") and isinstance(v, str):
                obj[k] = idmap.get(v, v)
            else:
                remap_src(v, idmap)
    elif isinstance(obj, list):
        for v in obj:
            remap_src(v, idmap)
    return obj


STORE_NAME = "data"  # <project>/data/ holds config.json, .cache, .venv, market/, find/, digests/, stocks/

# --- settings: flag > <project>/data/config.json > default. One file, no .env, no env vars except the project
#     fallback MY_INVEST_PROJECT and the hidden override MY_INVEST_STORE; empty values and "${...}" count as absent ---
SETTINGS = {  # key -> (env override or None, default)
    "sec_user_agent": (None, None),
    "margin_of_safety": (None, 0.30),
    "store_dir": ("MY_INVEST_STORE", None),
    "fred_api_key": (None, None),
    "finnhub_api_key": (None, None),
    "python": (None, None),
}
NO_UA_MSG = ('no SEC User-Agent configured: create <project>/data/config.json with '
             '{"sec_user_agent": "AppName you@example.com"}')


def usable(v):
    """A setting value counts only when non-empty and free of an unsubstituted "${" placeholder."""
    return v is not None and str(v).strip() != "" and "${" not in str(v)


def load_project_config(project):
    """<project>/data/config.json as a dict ({} when absent). Malformed JSON is an error naming file and line;
    unknown keys are kept here and ignored by `resolve_setting`."""
    path = os.path.join(project, STORE_NAME, "config.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return {}
    try:
        obj = json.loads(text)
    except ValueError as e:
        raise FetchError("malformed JSON in %s, line %s: %s" % (path, getattr(e, "lineno", "?"),
                                                              getattr(e, "msg", e)))
    if not isinstance(obj, dict):
        raise FetchError("%s must hold a JSON object, line 1" % path)
    return obj


def resolve_setting(key, flag, data=None, env=None, project=""):
    """flag > (MY_INVEST_STORE for store_dir) > <project>/data/config.json > default. `data` is accepted for
    older callers and ignored."""
    env = os.environ if env is None else env
    if usable(flag):
        return flag
    name = SETTINGS[key][0]
    if name and usable(env.get(name)):
        return env.get(name)
    v = load_project_config(resolve_project(project, env)).get(key)
    return v if usable(v) else SETTINGS[key][1]


def resolve_mos(data, flag=None, env=None, project=""):
    v = resolve_setting("margin_of_safety", flag, data, env, project)
    try:
        v = float(v)
    except (TypeError, ValueError):
        raise FetchError("margin_of_safety must be a number between 0 and 1, got %r" % (v,))
    if not 0 <= v < 1:
        raise FetchError("margin_of_safety must be in [0, 1), got %s" % v)
    return v


# --- CLI / output ----------------------------------------------------------------------------
class EnvelopeParser(argparse.ArgumentParser):
    """argparse that reports usage errors through the JSON error envelope (exit 1)."""

    def error(self, message):
        fail(os.path.basename(self.prog.split()[0]) if self.prog else "script", "usage: " + message)


def base_parser(description):
    p = EnvelopeParser(description=description)
    add_common_args(p)
    return p


def add_common_args(p):
    p.add_argument("--data", default=os.environ.get("MY_INVEST_DATA", os.path.expanduser("~/.my-invest")),
                   help="unused; accepted for run.sh compatibility")
    add_store_arg(p)
    p.add_argument("--ua", default="",
                   help='declared User-Agent for SEC "AppName you@example.com" '
                        "(else sec_user_agent in <project>/data/config.json)")
    p.add_argument("--out", default="", help="write JSON here instead of stdout")
    p.add_argument("--refresh", action="store_true", help="ignore cache")


def store_from(args):
    return resolve_store(args.data, getattr(args, "store", ""), project=getattr(args, "project", ""))


def ctx_from(args):
    project = getattr(args, "project", "")
    ua = resolve_setting("sec_user_agent", args.ua, args.data, project=project)
    return Ctx(store_from(args), ua, args.refresh, data=args.data, project=project)


def emit(obj, out=""):
    text = json.dumps(obj, indent=2, ensure_ascii=False)
    if out:
        d = os.path.dirname(os.path.abspath(out))
        os.makedirs(d, exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print("wrote %s" % out, file=sys.stderr)
    else:
        print(text)


def fail(script, msg):
    print(json.dumps({"error": str(msg), "script": script}))
    sys.exit(1)


def run_main(script, fn, argv=None):
    """Run fn(argv) converting any exception into the error envelope + exit 1."""
    try:
        fn(argv)
    except SystemExit:
        raise
    except FetchError as e:
        fail(script, e)
    except Exception as e:  # noqa: BLE001 - envelope contract: any failure -> JSON error, exit 1
        fail(script, "%s: %s" % (type(e).__name__, e))


def resolve_project(flag="", env=None):
    """Project dir: --project, env MY_INVEST_PROJECT, else the working directory."""
    env = os.environ if env is None else env
    v = flag if usable(flag) else env.get("MY_INVEST_PROJECT")
    return os.path.abspath(os.path.expanduser(v)) if usable(v) else os.getcwd()


def resolve_store(data, flag="", env=None, project=""):
    """Store root: --store, env MY_INVEST_STORE, config.json store_dir, else <project>/data.
    Tickers live in <store>/stocks/<TICKER>/; <store>/market, find, digests, .cache and .venv sit beside it."""
    v = resolve_setting("store_dir", flag, data, env, project)
    return os.path.expanduser(str(v)) if v else os.path.join(resolve_project(project, env), STORE_NAME)


def ticker_dir(store, ticker):
    return os.path.join(store, "stocks", ticker)


class Stock:
    """Paths inside one stock folder <store>/stocks/<TICKER>/ (layout: skills/evidence/references/store.md)."""

    def __init__(self, folder):
        j = os.path.join
        self.root = folder = os.path.abspath(folder).rstrip(os.sep)
        self.ticker = os.path.basename(folder).upper()
        self.market_dir = j(os.path.dirname(os.path.dirname(folder)), "market")
        self.facts_dir = j(folder, "facts")
        (self.facts, self.series, self.scorecard, self.holdings, self.holdings_tables,
         self.last_run) = (j(self.facts_dir, n) for n in (
             "facts.json", "series.json", "scorecard.json", "holdings.json", "holdings_tables.json", "last_run.json"))
        self.filings = j(folder, "filings")
        self.research_dir = j(folder, "research")
        self.research, self.evidence, self.industry = (j(self.research_dir, n) for n in (
            "research.md", "evidence.json", "industry.md"))
        self.history_dir = j(folder, "history")
        self.log = j(self.history_dir, "log.md")
        self.reports_dir = j(folder, "reports")
        self.dossier = j(self.reports_dir, "dossier.md")
        self.charts_dir = j(folder, "charts")
        self.index = j(folder, "INDEX.md")

    def newest_narrative(self):
        """Newest history/<date>-<HHMM>.md other than log.md, or None."""
        try:
            names = sorted(n for n in os.listdir(self.history_dir) if n.endswith(".md") and n != "log.md")
        except OSError:
            return None
        return os.path.join(self.history_dir, names[-1]) if names else None


def locate(target, args=None):
    """A bare ticker (resolved in the store of `args`) or a stock folder path -> Stock."""
    t = str(target)
    if os.sep in t or t.startswith((".", "~")) or os.path.isdir(os.path.join(t, "facts")):
        return Stock(os.path.expanduser(t))
    return Stock(ticker_dir(store_from(args), safe_ticker(t)))


GITIGNORE = ".cache/\n.venv/\nconfig.json\n"


def ensure_store(store):
    """Create the store; write its .gitignore (.cache/ .venv/ config.json) whenever the file is missing."""
    os.makedirs(store, exist_ok=True)
    gi = os.path.join(store, ".gitignore")
    if not os.path.exists(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write(GITIGNORE)


def safe_ticker(t):
    """Upper-case ticker usable as a folder name; refuses path separators and other surprises."""
    t = str(t).strip().upper()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,9}", t):
        raise FetchError("bad ticker %r" % t)
    return t


def add_store_arg(p):
    p.add_argument("--store", default="", help="store root (else env MY_INVEST_STORE, config store_dir, "
                                               "default <project>/data)")
    p.add_argument("--project", default="", help="project dir holding data/ (else env MY_INVEST_PROJECT, "
                                                 "else the working directory)")


def stamp(now=None):
    """<date>-<HHMM> (UTC), the name of a run's history, report and html files."""
    return (now or utcnow()).strftime("%Y-%m-%d-%H%M")


def today():
    return utcnow().strftime("%Y-%m-%d")
