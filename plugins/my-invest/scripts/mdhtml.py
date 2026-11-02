#!/usr/bin/env python3
"""mdhtml.py <file.md> --out <file.html> --title "Two To Four Words"

Stdlib Markdown -> self-contained HTML page for the subset my-invest files use: ATX headings, paragraphs,
bullet and numbered lists (indent nests), tables with a header row, **bold**, `inline code`, [links](url),
> blockquotes, fenced code. [S<n>] markers become superscript links to the Evidence log row anchors
(#ev-S<n>, set on every row of a table whose first header is "S"); a marker whose row is not on the page
stays plain text. No scripts, no external assets; colors are tokens with a guarded dark mode.
Named mdhtml, not html: a scripts/html.py would shadow the stdlib html package that macro.py and filing.py use.
Importable: render(md_text, title, extra_sections=None, css="") and to_html(md_text, shift=0).
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import EnvelopeParser, fail  # noqa: E402

SCRIPT = "mdhtml.py"
LIGHT = ("--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;"
         "--axis:#c3c2b7;--border:rgba(11,11,11,.10);--s1:#2a78d6;--s2:#eb6834;--s3:#1baf7a;--s4:#eda100;--s5:#e87ba4;"
         "--good:#0ca30c;--crit:#d03b3b;--link:#256abf;--code:#f0efec;color-scheme:light")
DARK = ("--page:#0d0d0d;--surface:#1a1a19;--ink:#ffffff;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;"
        "--axis:#383835;--border:rgba(255,255,255,.10);--s1:#3987e5;--s2:#d95926;--s3:#199e70;--s4:#c98500;--s5:#d55181;"
        "--good:#0ca30c;--crit:#d03b3b;--link:#86b6ef;--code:#2c2c2a;color-scheme:dark")
TOKENS = """:root{%s}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){%s}}
:root[data-theme="dark"]{%s}
""" % (LIGHT, DARK, DARK)
PROSE = """*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:760px;margin:0 auto;padding:16px}
h1{font-size:22px;margin:8px 0 8px}h2{font-size:19px;margin:28px 0 8px}h3{font-size:16px;margin:20px 0 6px}
h4,h5,h6{font-size:15px;margin:16px 0 4px}
p,li{overflow-wrap:anywhere}ul,ol{padding-left:22px}
a{color:var(--link)}code{background:var(--code);border-radius:4px;padding:0 4px;font-size:.92em}
pre{background:var(--code);border-radius:6px;padding:10px;overflow-x:auto}pre code{padding:0}
blockquote{margin:16px 0;padding:4px 12px;border-left:3px solid var(--axis);color:var(--ink2)}
.tw{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;font-variant-numeric:tabular-nums;font-size:14px}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink2);font-weight:600}tr:target{background:var(--code)}
hr{border:0;border-top:1px solid var(--grid);margin:24px 0}
details.sec{font-size:15px;margin:8px 0;border:1px solid var(--border);border-radius:6px;padding:6px 12px;background:var(--surface)}
details.sec>summary{cursor:pointer;font-weight:600;color:var(--ink)}
sup.mk{font-size:.7em;line-height:0;color:var(--ink2)}sup.mk a{text-decoration:none}
"""

_esc = {"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}
MARKER = re.compile(r"\[(S\d+(?:\s*[,;]?\s*S\d+)*)\]")
LINK = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
SAFE_URL = re.compile(r"^(https?:|file:|mailto:|#|\./|\.\./|[\w\-./]+$)", re.I)


def esc(s):
    return "".join(_esc.get(c, c) for c in str(s))


def _marker(m):
    ids = re.findall(r"S\d+", m.group(1))
    return '<sup class="mk">[%s]</sup>' % ", ".join('<a class="mk" href="#ev-%s">%s</a>' % (i, i) for i in ids)


def _link(m):
    text, url = m.group(1), m.group(2)
    if not SAFE_URL.match(url):
        return text
    return '<a href="%s">%s</a>' % (url, text)


def inline(s):
    """Code spans first (verbatim), then links, bold, markers on escaped text."""
    out = []
    for k, part in enumerate(re.split(r"(`[^`]*`)", s)):
        if k % 2:
            out.append("<code>%s</code>" % esc(part[1:-1]))
            continue
        t = esc(part)
        t = LINK.sub(_link, t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
        t = MARKER.sub(_marker, t)
        out.append(t)
    return "".join(out)


def _cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def _table(rows):
    head, body = _cells(rows[0]), [_cells(r) for r in rows[2:]]
    log = head and head[0].strip() == "S"
    out = ['<div class="tw"><table><thead><tr>%s</tr></thead><tbody>' % "".join("<th>%s</th>" % inline(c) for c in head)]
    for r in body:
        rid = ' id="ev-%s"' % r[0] if log and r and re.fullmatch(r"S\d+", r[0]) else ""
        out.append("<tr%s>%s</tr>" % (rid, "".join("<td>%s</td>" % inline(c) for c in r)))
    out.append("</tbody></table></div>")
    return "".join(out)


LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def _list(items):
    """items: [(indent, ordered, text)] -> nested <ul>/<ol>."""
    out, stack = [], []                               # stack of (indent, tag)
    for indent, ordered, text in items:
        tag = "ol" if ordered else "ul"
        while stack and indent < stack[-1][0]:
            out.append("</li></%s>" % stack.pop()[1])
        if not stack or indent > stack[-1][0]:
            out.append("<%s>" % tag)
            stack.append((indent, tag))
        else:
            out.append("</li>")
        out.append("<li>%s" % inline(text))
    while stack:
        out.append("</li></%s>" % stack.pop()[1])
    return "".join(out)


DETAILS = re.compile(r"^(#{1,6})\s+Details\s*(?:\(.*\))?\s*$", re.M)
HEAD = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$", re.M)


def collapse(md, shift, ids):
    """Each top-level section of `md` becomes a closed <details> block titled by its heading."""
    heads = list(HEAD.finditer(md))
    if not heads:
        return _blocks(md, shift, ids)
    top = min(len(h.group(1)) for h in heads)
    cut = [h for h in heads if len(h.group(1)) == top]
    out = [_blocks(md[:cut[0].start()], shift, ids)]
    for k, h in enumerate(cut):
        body = md[h.end():cut[k + 1].start() if k + 1 < len(cut) else len(md)]
        out.append('<details class="sec"><summary>%s</summary>\n%s\n</details>' % (inline(h.group(2)),
                                                                                  _blocks(body, shift, ids)))
    return "\n".join(x for x in out if x)


def to_html(md, shift=0, ids=None):
    """Markdown fragment -> HTML fragment; headings demoted by `shift` (capped at h6). Everything after a
    `Details` heading renders as closed <details> blocks, one per section."""
    ids = {} if ids is None else ids
    md = md.replace("\r\n", "\n")
    m = DETAILS.search(md)
    if not m:
        return _blocks(md, shift, ids)
    return "\n".join(x for x in (_blocks(md[:m.end()], shift, ids), collapse(md[m.end():], shift, ids)) if x)


def _blocks(md, shift=0, ids=None):
    ids = {} if ids is None else ids
    lines = md.split("\n")
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", s):
            out.append("<hr>")
            i += 1
            continue
        if s.startswith("```"):
            j = i + 1
            while j < n and not lines[j].strip().startswith("```"):
                j += 1
            out.append("<pre><code>%s</code></pre>" % esc("\n".join(lines[i + 1:j])))
            i = j + 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*?)\s*#*\s*$", s)
        if m:
            lvl = min(6, len(m.group(1)) + shift)
            slug = re.sub(r"[^a-z0-9]+", "-", m.group(2).lower()).strip("-") or "s"
            ids[slug] = ids.get(slug, 0) + 1
            hid = slug if ids[slug] == 1 else "%s-%d" % (slug, ids[slug])
            out.append('<h%d id="%s">%s</h%d>' % (lvl, hid, inline(m.group(2)), lvl))
            i += 1
            continue
        if s.startswith("|") and i + 1 < n and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            out.append(_table(lines[i:j]))
            i = j
            continue
        if s.startswith(">"):
            j, quote = i, []
            while j < n and lines[j].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[j]))
                j += 1
            out.append("<blockquote>%s</blockquote>" % _blocks("\n".join(quote), shift, ids))
            i = j
            continue
        if LIST_ITEM.match(line):
            items, j = [], i
            while j < n and lines[j].strip():
                lm = LIST_ITEM.match(lines[j])
                if lm:
                    items.append((len(lm.group(1).expandtabs(4)), lm.group(2)[0].isdigit(), lm.group(3)))
                elif items:                           # lazy continuation line
                    ind, o, t = items[-1]
                    items[-1] = (ind, o, t + " " + lines[j].strip())
                j += 1
            out.append(_list(items))
            i = j
            continue
        j, para = i + 1, [s]
        while j < n and lines[j].strip() and not re.match(r"^\s*(#{1,6}\s|```|>|\|)", lines[j]) \
                and not LIST_ITEM.match(lines[j]):
            para.append(lines[j].strip())
            j += 1
        out.append("<p>%s</p>" % inline(" ".join(para)))
        i = j
    return "\n".join(out)


def link_markers(body):
    """Keep marker links whose Evidence log row is on the page; the rest become plain text."""
    present = set(re.findall(r'id="ev-(S\d+)"', body))
    return re.sub(r'<a class="mk" href="#ev-(S\d+)">S\d+</a>',
                  lambda m: m.group(0) if m.group(1) in present else m.group(1), body)


def render(md_text, title, extra_sections=None, css=""):
    """Full page: md_text converted, then each extra section (an HTML fragment) appended in order."""
    body = to_html(md_text) + "".join("\n" + x for x in (extra_sections or []))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title>'
            '<style>%s%s%s</style></head><body><main>\n%s\n</main></body></html>\n'
            % (esc(title), TOKENS, PROSE, css, link_markers(body)))


def main(argv=None):
    ap = EnvelopeParser(prog=SCRIPT, description="Markdown file -> self-contained HTML page")
    ap.add_argument("md")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", required=True, help="page title, two to four words")
    a = ap.parse_args(argv)
    if not os.path.exists(a.md):
        fail(SCRIPT, "%s not found" % a.md)
    with open(a.md, encoding="utf-8") as f:
        page = render(f.read(), a.title)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as f:
        f.write(page)
    print(json.dumps({"path": os.path.abspath(a.out), "bytes": len(page.encode())}))


if __name__ == "__main__":
    main()
