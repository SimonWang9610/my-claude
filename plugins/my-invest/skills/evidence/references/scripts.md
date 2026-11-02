# Scripts — what each does and what it reads from the question

Every call is `"${CLAUDE_PLUGIN_ROOT}/scripts/run.sh" "${CLAUDE_PLUGIN_DATA}" <script> <args> --project "${CLAUDE_PROJECT_DIR}"`.
`run.sh` picks the interpreter (config `python` → `data/.venv` → self-provisioned for prices, options,
market and facts → `python3`). Nothing in the pipeline hard-codes a horizon, lens, peer list, margin of
safety or growth rate: each comes from `request.json` (the advisor skill's `request.md`) or from a stated
default the file records.

| Script | Does | Flags from the request |
|---|---|---|
| `facts.py <T>` | SEC statements (10 years), prices, macro, market, options chain, consensus, momentum, derived metrics, valuation, outlook and the simulated record; incremental; prints `changed`, `reused`, `news_since` | `--horizons 1,3` `--g-base` `--erp` `--mos` `--horizon-days` `--refresh` |
| `filing.py <T> [--grep RE]` | splits the latest 10-K into `filings/<accn>/item-*.txt`, `auditor.txt`, `notes.txt` | `--form 10-K --accn` |
| `compare.py <T> --peers A,B [--md]` | peer table into `facts/peers.json` (growth, margin, ROIC, cash yield, debt years, 12-month return, stance) | peers from the request or `research/industry.md` |
| `holdings.py <T> --question "<holdings text>" [--md]` | positions, gains at price points, Canadian tax lines into `facts/holdings*.json` | the holdings phrases verbatim |
| `score.py <T> [--lens] [--holding] [--mode screen]` | gates, pillars, score, tier, zones, outlook verdicts, recommendation, options operations, short-term lens into `facts/scorecard.json` | lens and holding from `request.json` when flags are absent |
| `report.py <T> --question … --lens … --chat --html` | dossier, dated snapshot, HTML page, `history/log.md` line (with what was said and expected), `INDEX.md`; prints the chat answer; lints | `--narrative <path>` (default: newest file in `history/`) |
| `chart.py <T>` | the five panels as `charts/<date>.html` | — |
| `mdhtml.py <file.md> --out <file.html> --title …` | any Markdown table or brief as a page | — |
| `store.py list \| tree <T> \| path [<T>] \| next-id <T>` | the data folder | — |
| `lint.py [--part] [--facts facts/facts.json] <file>` | the citation check | — |

How scripts consume the request: `metrics.py --horizons <years>` (comma list, fractional allowed) and
`--g-base`, `--erp`, `--mos` from `what_if` and `margin_of_safety`; `score.py` reads the horizons present
in the valuation and `request.json` for lens, holdings and intent; `options.py --horizon-days` from the
longest horizon under a year or the nearest named date; `compare.py --peers` from `peers_requested`, else
the industry file's peers; `report.py` renders the horizon rows that exist and the sections in `wants`,
keeping the verdict and the proof sections whatever `wants` says.
