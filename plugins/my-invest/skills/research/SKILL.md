---
name: research
description: >-
  Explains how my-invest gathers evidence for a stock: filings from local extracts (never a truncating
  web fetch), the four evidence-required verdicts, market trend, news, posts, the industry chain and
  related stocks, industry mode for a theme, incremental rules and the cumulative research file. Use when
  an agent must add cited evidence for a stock or map an industry; preloaded into the advisor and analyst
  agents, not invoked by the user.
user-invocable: false
---

# research

You turn fetched text into cited evidence, incrementally. A search result is a lead; only a page or a
local filing extract you read can be cited. Figures come from the filing extract or not at all. What
the store already holds is not re-researched: you add, date, and mark superseded.

## Operating procedure

1. **Scope** — the prompt gives: the stock folder `<project>/data/stocks/<TICKER>` (files under `facts/`,
   `filings/`, `research/` per the layout), the since-date, the `changed`
   list, the first free source id (`S<n>`, ≥ 100), whether `evidence.json` must be judged, the lens
   (`long`, `short`, `both`), whether `research/industry.md` is due, and an optional specific question.
   Read `research/research.md`, `research/evidence.json` and the last `history/log.md` line first.
2. **Filings** — when `evidence.json` is missing or `changed` includes `fundamentals` or `filings`: run
   (a no-op when the extracts already exist)
   `"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" "${CLAUDE_PLUGIN_DATA}" filing.py <TICKER> --project "<project>"` (never fetch a
   10-K over the web; the fetch truncates before Item 9A), then read and grep `filings/<accn>/item-1.txt`,
   `item-1a.txt`, `item-7.txt`, `item-9a.txt`, `auditor.txt`, `notes.txt`. Judge the four evidence items and
   write `evidence.json` per the scorecard schema: G4 going-concern language (present/absent, quote),
   1.5 moat sources the text supports (name only those), 5.4 Item 9A material weakness, 5.5 customer
   concentration (the disclosure, the statement that none, or the stated grep over the extract finding
   none; `quote` may be empty when the verdict rests on a grep that found nothing, with `method` saying
   so). One Evidence log row per filing is enough; the four verdicts may share its marker. Quotes ≤ 15
   words, verbatim from the extract, each with its marker. Also refresh the
   **Business and moat**, **Management** (capital-allocation statements, acquisitions and divestitures,
   CEO changes) and **Risk evidence** (≤ 5 named risk factors) sections with dated entries when the 10-K
   is new; mark replaced entries `(superseded <date>)`.
3. **Market trend** — one dated entry: index and sector context in words from `facts.json.market`
   (cite its `S7` row), rates from `macro` (`S4`), and one or two fetched macro or sector news items
   since the since-date (cited). Facts ids `S1`–`S99` are cited directly, never copied into your log;
   the lint resolves them with `--facts`.
4. **News** — items since the since-date, up to 10 (digest: ≤ 3), from company IR, SEC press releases
   and major outlets: date, outlet, one line of fact, URL. A summarising fetch yields a paraphrase,
   written without quotation marks. Short lens: include the next earnings date and any scheduled event.
5. **Posts** — up to 5 since the since-date, searched one domain per call (reddit.com, x.com,
   substack.com, xueqiu.com, seekingalpha.com; a domain the search tool rejects is skipped, not
   retried), fetched, cited with handle and date, the view attributed. Refused fetches or a refused
   search domain → "posts: none fetchable this run (site)".
6. **Specific question** — answer it in a dated **Questions** entry with markers, from the extracts
   first, the web second.
6a. **Industry and related stocks** (when due) — write `research/industry.md`: the stock's industry in one
   line (SIC description from the submissions data, sector ETF from `facts.json`); its position in the
   chain (upstream suppliers → core → downstream customers and enablers), one line per link; a table of
   related US-listed stocks, ≤ 10 rows: ticker, link (supplier / peer / customer / enabler), one cited
   reason (a 10-K passage naming the relationship, an ETF holdings page, an index list); the two or three
   chain-level drivers and risks that bear on this stock; and a dated `## Industry development` entry
   (≤ 3 cited items since the since-date on how the chain is doing: demand, pricing, regulation, big
   moves by the key players), appended on every run while the rest of the file refreshes on its 90-day
   cadence. Every line with a marker; ids continue the research log (the file has its own `## Evidence
   log`, or cites rows already in `research.md`).
6b. **Industry mode** (for `find`; no ticker folder) — the prompt gives an industry, theme or index, a
   limit N and an output path. The purpose is the stocks, reached through the chain: write the **Industry
   chain map** at the output path — the links from upstream to downstream (suppliers, equipment and
   inputs; the core producers; distribution, platforms and downstream users; enablers such as power or
   logistics when they matter), each link with its role in one line, its demand driver, its main risk,
   and the US-listed companies at that link: ticker, one cited reason it belongs (an ETF holdings page,
   an index constituent list, a 10-K Item 1 segment description or the company's own description, with
   URL and date). Size or growth figures only as a fetched page states them, marked secondary when from
   market research. Then the **Universe** line: up to N tickers spread across the links (at least one per
   link, the rest by market cap or ETF weight; state the rule) — this list is what `find` screens. News
   since the since-date (≤ 6 items, dated, cited) only where it changes a link's driver or risk. Every
   figure line carries a marker; the file ends with `## Evidence log` (ids from S1) and lints with
   `--part`. Return the universe (ticker, link) with the file path.
7. **Write** — append dated bullets (`- <YYYY-MM-DD> — …`) under the existing `##` sections of
   `research/research.md` (create missing ones in this order: Business and moat, Management, Market trend,
   Risk evidence, News and posts, Questions, Open questions, Evidence log); new Evidence log rows continue from the first free id, class
   `primary`, `secondary` or `social`; never renumber or delete a row. Prose counts and codes are figures
   to the lint: spell small numbers out, keep status codes for the return report.
8. **Lint** — `"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" "${CLAUDE_PLUGIN_DATA}" lint.py --part --facts <facts/facts.json> <research/research.md> [<research/industry.md>]`;
   fix marker gaps by adding the marker, never by deleting the figure.

## What a research pass records (in the agent's own notes)

Entries added per section (counts) · evidence verdicts with markers, or "unchanged" · the highest id
used · pages or domains refused (URL, status) · lint result · the answer to the specific question in
≤ 3 lines when one was asked · related tickers written to `industry.md` (ticker: link) · in industry mode:
the universe with the source URL and the chain map's path.
