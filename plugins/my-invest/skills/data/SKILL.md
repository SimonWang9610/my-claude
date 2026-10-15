---
name: data
description: >-
  Explains how my-invest gets and keeps its numbers: the scripts and their flags, the request.json the
  question is read into, the facts.json contract, the per-stock data folder and its refresh rules.
  Use when an agent needs to fetch facts, filings, peers, holdings, options or charts, or score a stock;
  preloaded into the advisor and analyst agents, not invoked by the user.
user-invocable: false
---

# data

Scripts do every number; agents run them and read their JSON. Every call is
`"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" "${CLAUDE_PLUGIN_DATA}" <script> <args> --project "${CLAUDE_PROJECT_DIR}"`.
Settings come from `<project>/data/config.json` (`sec_user_agent` required); a missing one is an error
envelope that says how to create the file: relay it, never guess a value. A script that fails prints
`{"error": …, "script": …}` and exits 1: relay it verbatim and write `no evidence`.

## The question first: request.json

Read the question into `<DATA>/stocks/<T>/request.json` per [request.md](references/request.md) before
any script: horizons, lens, intent, holdings text, peers named, margin of safety, what-ifs, dates, wanted
sections, constraints. Nothing in the pipeline hard-codes these; a default is recorded as a default.

## Scripts

| Script | Does | Flags from the request |
|---|---|---|
| `facts.py <T>` | SEC statements (10 years), prices, macro, market, options chain, momentum, derived metrics and valuation; incremental; prints `changed`, `reused`, `news_since` | `--horizons 1,3` `--g-base` `--erp` `--mos` `--horizon-days` `--refresh` |
| `filing.py <T> [--grep RE]` | splits the latest 10-K into `filings/<accn>/item-*.txt`, `auditor.txt`, `notes.txt` | `--form 10-K --accn` |
| `compare.py <T> --peers A,B [--md]` | peer table into `facts/peers.json` (growth, margin, ROIC, cash yield, debt years, 12-month return, stance) | peers from the request or `research/industry.md` |
| `holdings.py <T> --question "<holdings text>" [--md]` | positions, gains at price points, Canadian tax lines into `facts/holdings*.json` | the holdings phrases verbatim |
| `score.py <T> [--lens] [--holding] [--mode screen]` | gates, pillars, score, tier, zones, action matrix, options operations, short-term lens into `facts/scorecard.json` | lens and holding from `request.json` when flags are absent |
| `report.py <T> --question … --lens … --chat --html` | dossier, dated snapshot, HTML page, `history/log.md`, `INDEX.md`; prints the chat answer; lints | `--narrative <path>` (default: newest file in `history/`) |
| `chart.py <T>` | the five panels as `charts/<date>.html` | — |
| `mdhtml.py <file.md> --out <file.html> --title …` | any Markdown table or brief as a page | — |
| `store.py list | tree <T> | path [<T>] | next-id <T>` | the data folder | — |
| `lint.py [--part] [--facts facts/facts.json] <file>` | the citation check | — |

## Where things live and when they refresh

[store.md](references/store.md): `<project>/data/stocks/<T>/{INDEX.md, facts/, filings/, research/, history/,
reports/, charts/}`, plus `market/`, `find/`, `digests/`. Prices daily; fundamentals only on a new 10-K or
10-Q; filings three years back; the industry file every 90 days; the rest every run.

## The facts contract

[facts-schema.md](references/facts-schema.md): every figure carries a source id `S<n>`; `null` means not
available, with a reason; `sector_class` decides which models apply.
