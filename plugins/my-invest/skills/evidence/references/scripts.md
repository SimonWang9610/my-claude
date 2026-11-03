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
| `size.py <T> --question "<holdings text>" --total <USD> [--funds QQQ=<USD>,VGT=<USD>] [--md]` | the arithmetic behind "how many shares, at what price": outright and look-through weight, the sizing frames, the order levels, the account to sell from first, into `facts/sizing.json` | the holdings phrases verbatim; the portfolio total and fund values from the question or the broker file |
| `score.py <T> [--lens] [--holding] [--mode screen]` | gates, pillars, score, tier, zones, outlook verdicts, recommendation, options operations, short-term lens into `facts/scorecard.json` | lens and holding from `request.json` when flags are absent |
| `fund.py <T>` | a fund (ETF): what it is and holds, cost, prices and returns against SPY, trend, into `facts/fund.json`; used when `facts.py` reports the ticker is not an SEC registrant | — |
| `report.py <T> --question … --lens … --chat --html` | the brief (printed with `--chat`; the page with `--html`), `reports/dossier.md` and `dossier.html` with every detail, a dated snapshot, the `history/log.md` line (what was said and expected), `INDEX.md`; lints; renders the fund brief when `fund.json` exists and no scorecard | `--narrative <path>` (default: newest file in `history/`) |
| `chart.py <T>` | the five panels as `charts/<date>.html` | — |
| `mdhtml.py <file.md> --out <file.html> --title …` | any Markdown table or brief as a page | — |
| `store.py list \| tree <T> \| path [<T>] \| next-id <T>` | the data folder | — |
| `lint.py [--part] [--facts facts/facts.json] <file>` | the citation check | — |

How scripts consume the request: `metrics.py --horizons <years>` (comma list, fractional allowed) and
`--g-base`, `--erp`, `--mos` from `what_if` and `margin_of_safety`; `score.py` reads the horizons present
in the valuation and `request.json` for lens, holdings and intent; `options.py --horizon-days` from the
longest horizon under a year or the nearest named date; `compare.py --peers` from `peers_requested`, else
the industry file's peers; `report.py` renders the horizon rows that exist and, in the brief, only the
detail sections in `wants`; the answer, summary, why, risks, record, what to watch and not verified
always stay.

Why so many scripts: one per data source or step, so a failure in one (Yahoo breaks every few months)
stops only that step and says so, the rest stays cached, and every number can be traced to the script
and inputs that produced it. The advisor runs them; the user never has to.
