#!/usr/bin/env python3
"""news.py {fetch|lean} - news items per subject (secondary, Google News RSS) and the analyst's lean on each.

Usage: python3 news.py fetch SUBJECT [--query "..."] [--days 30] [--md] --project P
       python3 news.py lean ID VALUE --by "analyst run N" [--note "..."] --project P
SUBJECT is a ticker, sector:<name> or market. fetch stores the items (newest first, capped at config depth.news)
into `news` by url, lean left NULL; lean records the analyst's reading (-1 against .. +1 for) on one item.
"""
import argparse
import datetime as dt
import email.utils
import html
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402
import db  # noqa: E402

SCRIPT = "news.py"
RSS_URL = "https://news.google.com/rss/search?%s"


# --- query --------------------------------------------------------------------------------------
def normalise_subject(subject):
    if subject.lower() == "market":
        return "market"
    if subject.lower().startswith("sector:"):
        return "sector:" + subject[7:].strip()
    return subject.upper()


def default_query(conn, subject):
    if subject == "market":
        return "stock market"
    if subject.startswith("sector:"):
        return "%s industry" % subject[7:]
    row = db.one(conn, "SELECT name FROM securities WHERE ticker = ?", (subject,))
    if row and row["name"]:
        return '"%s" OR %s stock' % (row["name"], subject)
    return "%s stock" % subject


def rss_url(query):
    return RSS_URL % urllib.parse.urlencode({"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"})


# --- parsing ------------------------------------------------------------------------------------
def strip_html(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def iso_utc(pubdate):
    """RFC 2822 pubDate -> ISO UTC, or None when it cannot be read."""
    if not pubdate:
        return None
    try:
        t = email.utils.parsedate_to_datetime(pubdate)
    except (TypeError, ValueError):
        return None
    if t.tzinfo is None:
        t = t.replace(tzinfo=dt.timezone.utc)
    return common.iso(t.astimezone(dt.timezone.utc))


def parse_rss(text):
    """RSS body -> [{published, source, url, title, summary}] in feed order."""
    root = ET.fromstring(text)
    items = []
    for it in root.iter("item"):
        url = (it.findtext("link") or "").strip()
        title = strip_html(it.findtext("title") or "")
        if not url or not title:
            continue
        src = it.find("source")
        items.append({"published": iso_utc(it.findtext("pubDate")), "source": (src.text or "").strip() if src is not None else None,
                      "url": url, "title": title, "summary": strip_html(it.findtext("description")) or None})
    return items


def select_items(items, days, cap, now=None):
    """Items published within `days` of now (undated items dropped), newest first, at most `cap`."""
    now = now or common.utcnow()
    since = common.iso(now - dt.timedelta(days=days))
    kept = [i for i in items if i["published"] and i["published"] >= since]
    kept.sort(key=lambda i: i["published"], reverse=True)
    return kept[:cap]


# --- commands -----------------------------------------------------------------------------------
def fetch(conn, subject, query, days, cap, text=None):
    """Fetch (or parse `text`) and store; returns (stored rows with ids, url)."""
    url = rss_url(query)
    text = text if text is not None else common.get_text(url)
    items = select_items(parse_rss(text), days, cap)
    now = common.iso()
    sid = db.source(conn, url, "secondary", "Google News: %s" % query)
    for i in items:
        i.update({"subject": subject, "fetched_at": now, "source_id": sid})
    db.upsert(conn, "news", items, keys=["url"])
    urls = [i["url"] for i in items]
    stored = []
    if urls:
        stored = db.rows(conn, "SELECT id, subject, published, source, title, url, summary, lean FROM news WHERE url IN (%s) "
                         "ORDER BY published DESC" % ",".join("?" * len(urls)), urls)
    return stored, url


def set_lean(conn, item_id, value, by, note):
    if not -1 <= value <= 1:
        raise ValueError("lean must be between -1 and 1, got %s" % value)
    if not db.one(conn, "SELECT id FROM news WHERE id = ?", (item_id,)):
        raise ValueError("no news item with id %s" % item_id)
    conn.execute("UPDATE news SET lean = ?, lean_by = ?, lean_note = ? WHERE id = ?", (value, by, note, item_id))


def run(argv=None):
    p = common.parser(SCRIPT, "news items per subject and the analyst's lean")
    sub = p.add_subparsers(dest="command")
    sub.required = True
    f = sub.add_parser("fetch", help="fetch news for a ticker, sector:<name> or market")
    f.add_argument("subject")
    f.add_argument("--query", default="", help="search query (default built from the subject)")
    f.add_argument("--days", type=int, default=30, help="keep items published within N days (default 30)")
    l = sub.add_parser("lean", help="record the analyst's lean on one item")
    l.add_argument("id", type=int)
    l.add_argument("value", type=float, help="-1 against .. +1 for the subject")
    l.add_argument("--by", required=True, help="who set it, e.g. 'analyst run 12'")
    l.add_argument("--note", default=None, help="why, in a few words")
    for sp in (f, l):  # accepted after the subcommand too; SUPPRESS keeps the main parser's value otherwise
        sp.add_argument("--project", default=argparse.SUPPRESS)
        sp.add_argument("--md", action="store_true", default=argparse.SUPPRESS)
    a = p.parse_args(argv)
    project = common.resolve_project(a.project)
    cfg = common.load_config(project)
    conn = db.connect(project)

    if a.command == "lean":
        try:
            set_lean(conn, a.id, a.value, a.by, a.note)
        except ValueError as e:
            return common.fail(SCRIPT, e)
        return common.emit({"ok": True, "script": SCRIPT, "id": a.id, "lean": a.value, "lean_by": a.by, "lean_note": a.note})

    subject = normalise_subject(a.subject)
    query = a.query or default_query(conn, subject)
    stored, url = fetch(conn, subject, query, a.days, common.depth(cfg, "news"))
    sid = db.source(conn, url, "secondary", "Google News: %s" % query)
    out = {"ok": True, "script": SCRIPT, "subject": subject, "query": query, "days": a.days, "n": len(stored),
           "source_id": sid, "items": stored}
    md = db.md_table(stored, ["id", "published", "source", "title"]) if a.md else None
    return common.emit(out, md)


if __name__ == "__main__":
    sys.exit(common.run_main(SCRIPT, run))
