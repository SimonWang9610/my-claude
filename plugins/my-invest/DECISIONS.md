# Decisions — my-invest

Closed decisions are not re-litigated. A reversal is a new entry with **Supersedes** filled in.

## D-1 2026-10-14 — Ship value-investing research as a fourth marketplace plugin, `my-invest`, Claude Code only
- Non-negotiables: namespaced like the other plugins; skills carry judgment, agents carry execution; no always-on context (plugins cannot inject it)
- End state: `plugins/my-invest/` installs from this marketplace and exposes `/my-invest:<skill>` plus `my-invest:<agent>`
- Options: A new plugin / B skills inside `think` / C user-level skills only
- Chosen: A — why: the domain (finance, Python scripts, persisted watchlist) shares nothing with `think` or the stack plugins; a plugin is the unit this repo versions and installs
- Supersedes: none. Discards: none

## D-2 2026-10-14 — An explicit, cited scoring standard is written first; every skill scores against it, never against intuition
- Non-negotiables: no number from model memory; every scored item cites a fetched source with URL and as-of date, or scores "no evidence"
- End state: `scoring standard` document with five pillars, fixed published weights with rationale, red-flag gates that override the score, output 0–100 plus tier `track closely / research deeper / pass`
- Options: A quantitative screen only (Piotroski, Greenblatt, Altman) / B qualitative checklist (Buffett, Fisher, Pabrai) / C composite scorecard mixing A and B / D intrinsic-value-first (DCF)
- Chosen: C with D as the valuation pillar — why: the 5 and 10-year horizon rewards durable compounders, which A cannot see and B cannot measure; D alone is too input-sensitive to be the whole answer
- Supersedes: none. Discards: none
- Open until: scout research on canonical sources lands; weights are then fixed in the standard and tunable by the user

## D-3 2026-10-14 — Value style is quality at a fair price, with a Graham-style margin-of-safety gate
- Non-negotiables: horizon 1/2/5/10 years; no short-term trading signals; output is a research thesis, never a personalised buy or sell instruction
- End state: pillar weights favour moat, return on invested capital and reinvestment runway; the valuation pillar cannot pass without a stated margin of safety against an intrinsic-value range
- Options: A quality at fair price (Buffett, Munger, Mauboussin) / B classic deep value (Graham net-nets, low price-to-book)
- Chosen: A with B's gate — why: compounding over a decade needs businesses that reinvest at high returns; the Graham gate keeps price discipline
- Supersedes: none. Discards: none

## D-4 2026-10-14 — Data comes from Python scripts over free primary sources; web fetch is for news and posts only
- Non-negotiables: no paid API key required; optional free-tier keys allowed; every script output carries source URL and retrieval date
- End state: plugin ships scripts under its root for prices, filings-derived fundamentals and macro rates; skills call them via `${CLAUDE_PLUGIN_ROOT}`
- Options: A Python scripts over yfinance, SEC EDGAR, FRED and HKEX / B web search and page fetch only / C paid data vendor
- Chosen: A — why: exact series are needed for charts and valuation math; web-only yields ragged numbers and unreliable diagrams
- Supersedes: none. Discards: none
- Open until: data scout confirms source reliability as of 2026-10

## D-5 2026-10-14 — Markets are US and Hong Kong; state persists as a per-project `watchlist/` folder of markdown dossiers; charts are HTML artifacts
- Non-negotiables: one dossier per ticker is the long-lived record a digest and a deep dive both read and append to
- End state: `watchlist/<TICKER>/dossier.md` plus dated digest files; Notion remains an optional export, not the store
- Options: A local markdown folder / B Notion database / C both
- Chosen: A — why: a file the skills can grep and diff is the cheapest reliable memory across sessions; Notion can be layered later without changing the skills
- Supersedes: none. Discards: none

## D-6 2026-10-14 — Four capabilities in v1: track and deep-dive one stock, daily and weekly digest over the watchlist, trend charts, discovery screening of a named sector or up to 20 tickers
- Non-negotiables: digest is on demand; scheduling is documented in the README, not declared by the plugin; discovery is bounded to keep the "every number fetched" rule affordable
- End state: four user-facing skills plus the agents that execute them, all reading the scoring standard
- Options: A all four / B tracking and digest only, discovery later
- Chosen: A — why: "which stocks should I track" is the user's stated goal 3, and discovery reuses the same scorer, so its marginal cost is small
- Supersedes: none. Discards: none


## D-7 2026-10-14 — Watchlist lives in the plugin data directory with a userConfig override; supersedes D-5's per-project folder
- Non-negotiables: state must survive plugin updates; one dossier per ticker remains the long-lived record
- End state: `${CLAUDE_PLUGIN_DATA}/watchlist/` by default; `watchlist_dir` (directory) in plugin.json userConfig redirects it to any folder, including a committed project folder
- Options: A plugin data dir / B per-project folder / C both via override
- Chosen: C — why: `${CLAUDE_PLUGIN_ROOT}` moves on update and a per-project folder ties a personal watchlist to one repo; the override keeps the team/git case open
- Supersedes: D-5 (storage location only; dossier shape and HTML charts stand). Discards: none

## D-8 2026-10-14 — Gates first, five equal-weight pillars, published tier cutoffs
- Non-negotiables: every threshold pinned to a primary text or dropped; evidence-required items score zero without a cited passage; no number from model memory
- End state: any failed gate forces tier `pass`; pillars 20 points each, mean of binary items; tiers: ≥70 `track closely`, 45–69 `research deeper`, <45 `pass`; cutoffs stated as opinion in the standard, revisited after ten dossiers
- Options: A weighted composite with tuned weights / B equal weights plus hard gates / C gates only, no score
- Chosen: B — why: no published source validates stock-level weights for a value investor (research/2026-10-14-scoring-frameworks.md); equal weights keep the opinion visible, gates carry the published evidence
- Supersedes: none; closes D-2's open item. Discards: none
- Open until: ten dossiers exist; then tune cutoffs

## D-9 2026-10-14 — Three agents with a fenced scorer; fresh-eyes check is a lint script, not an agent
- Non-negotiables: nobody grades their own work; the citation check is mechanical
- End state: `quant` (Bash + scripts, sonnet), `researcher` (web search and fetch, sonnet), `scorer` (Read and Grep only, opus); `scripts/lint.py` fails any dossier or digest with an uncited number
- Options: A one agent does everything / B three fenced agents plus lint / C four agents including an auditor
- Chosen: B — why: the scorer's tool fence enforces separation of duties better than instructions; a lint script is cheaper and stricter than an auditor agent
- Supersedes: none. Discards: brief's done-when item 7 is satisfied by lint.py instead of an agent

## D-10 2026-10-14 — Hong Kong fundamentals are flag-only in v1; posts come through web search, not scripts
- Non-negotiables: a secondary-source figure is marked as such in the dossier; "no evidence" beats an estimate
- End state: HK dossiers use yfinance statements flagged secondary plus the HKEXnews annual-report link; mechanical items without inputs read "no evidence"; posts (Reddit, X, Xueqiu, Substack) are found by the researcher's web search and cited by URL
- Options: A parse annual-report PDFs in v1 / B flag-only in v1, PDF parsing as follow-up / C drop HK
- Chosen: B — why: no free structured HK API exists and Reddit, Seeking Alpha and Google News are dead or blocked for scripts (research/2026-10-14-data-sources.md); flagging keeps the accuracy rule intact at v1 cost
- Supersedes: none. Discards: none
- Open until: HK names dominate the watchlist; then build the PDF parser

## D-11 2026-10-14 — US-listed stocks only; supersedes the Hong Kong scope in D-5 and D-10
- Non-negotiables: every fundamental figure comes from an SEC filing via the XBRL APIs; prices remain secondary-source and marked so
- End state: tickers resolve through the SEC ticker-to-CIK file; no HK code paths, no HKD or FX handling
- Options: A US only / B US and HK with HK flag-only (D-10)
- Chosen: A — why: the user narrowed the market; dropping HK removes the one data gap that forced "no evidence" rows and the FX problem
- Supersedes: D-5 (markets), D-10 (entirely). Discards: the HK annual-report PDF follow-up

## D-12 2026-10-14 — Each evaluation states fair value per horizon, buy and sell zones, a stance, and a mechanical confidence
- Non-negotiables: no bare point forecast without a stated model; every input cited; the stance is derived from price versus zones, never asserted; the disclaimer line stays
- End state: scorecard carries base, bear and bull fair value at 1, 2, 5 and 10 years from the owner-earnings model; buy zone = base value today × (1 − margin of safety), sell zone = bull value today; stance ∈ {buy zone, hold, sell zone}; confidence 0–100 from a published formula over evidence coverage, scenario spread and data freshness
- Options: A research tiers only, no price view (brief v1) / B fair-value range plus zones plus confidence / C point price forecast plus buy or sell call
- Chosen: B — why: the user asked for a price view and buy/sell confidence; B gives both as model outputs with cited inputs, which C cannot (no source backs a point forecast and it breaks the accuracy rule); one pushback given, user's call stands if C is still wanted
- Supersedes: brief v1 "never buy or sell" wording (now "never without the model and zones behind it"). Discards: none
- Open until: margin-of-safety default (30%) and confidence weights are tuned after ten dossiers

## D-13 2026-10-14 — Settings resolve flag → env → `<data>/config.json` → default; `userConfig` stays in the manifest
- Non-negotiables: the SEC user agent must never reach the API as a literal placeholder; the plugin must load on CLIs that predate `userConfig`
- End state: `${user_config.*}` is used in skill bodies; `common.py` treats a value containing `${` as absent and falls through to `MY_INVEST_*` env vars, then `config.json` written by `scripts/config.py set`, then defaults; a missing SEC user agent is an error envelope with the fix
- Options: A `userConfig` only / B config.json only / C both with ordered fallback
- Chosen: C — why: `claude plugin validate` on the local CLI 2.1.58 rejects `userConfig` while the current docs define it; C works on both without two code paths in the skills
- Supersedes: none. Discards: none

## D-14 2026-10-14 — Filings are read from local extracts written by `filing.py`, never from a web fetch
- Non-negotiables: Item 9A, the auditor's report and the notes must be reachable; quotes must be verbatim
- End state: `filing.py` downloads the primary document with the SEC user agent, splits it by Item headings (skipping the table of contents) into `filings/<accn>/item-*.txt`, `auditor.txt`, `notes.txt`; the researcher reads and greps those files and quotes only from them; summarising fetches yield paraphrases, never quotes
- Options: A web-fetch the 10-K / B local extraction script / C EDGAR R-file pages
- Chosen: B — why: the end-to-end run showed a web fetch truncates a 10-K at roughly 177k characters, before Item 9A, and returns a paraphrase rather than text; B is primary, deterministic and cacheable
- Supersedes: the researcher's original "fetch the 10-K" step. Discards: none

## D-15 2026-10-14 — Three question-shaped skills (`analyze`, `find`, `digest`) and one agent; mechanical scoring and report assembly move into scripts
- Non-negotiables: the user asks questions, not pipeline steps; every figure stays cited; the standard and the lint are unchanged
- End state: `analyze <question with tickers, optional holdings>` answers scenarios about one or more stocks (price outlook, action matrix, reasons, strengths and weaknesses, options context, holdings and tax, short-term lens when asked); `find <question>` proposes stocks for a horizon and lens; `digest daily|weekly` runs over the stocks in the history store. `score.py` computes gates and every mechanical item; `report.py` renders the dossier, the history entry and the chat tables; the `researcher` agent returns cited evidence plus verdicts for the four evidence-required items
- Options: A keep five skills and three agents / B three skills, one agent, scripts for arithmetic / C one skill for everything
- Chosen: B — why: the user found the pipeline surface too complicated; the quant agent only transcribed JSON and the scorer's items are 80% arithmetic, which code does without error; separation of duties is now enforced by code rather than by an agent fence
- Supersedes: D-9 (agents), D-6 (capability list). Discards: skills track, dive, chart, discover; agents quant, scorer; the parts and assembly steps

## D-16 2026-10-14 — No watchlist; a per-ticker history store grows incrementally from the questions asked
- Non-negotiables: every stock comes from an inline question; a later question about the same stock reuses saved evidence, refreshes only what is stale, and appends what it learned
- End state: `${CLAUDE_PLUGIN_DATA}/stocks/<TICKER>/` holds facts.json, series.json, filings/, research.md (cumulative cited evidence), evidence.json (verdicts), scorecard.json, narrative.md, holdings.json, dossier.md, dossiers/<date>.md, history.md (one line per analysis), charts/. Prices refresh daily, filings and news since the last run, fundamentals only when a newer 10-K or 10-Q exists; the researcher receives the known evidence and a since-date
- Options: A watchlist folder (D-5, D-7) / B history store keyed by ticker, populated by questions
- Chosen: B — why: the user asked for it; a question-driven store removes the add/remove ceremony and makes "what did we know last time" the default input
- Supersedes: D-5, D-7 (storage), D-13 (the `watchlist_dir` setting is removed; `sec_user_agent` and `margin_of_safety` stay). Discards: watchlist.py

## D-17 2026-10-14 — Short-horizon questions get a separate, cited short-term lens; the skill classifies the horizon from the question
- Non-negotiables: the lens is labelled as such, its base rates are stated, and it never overrides a failed gate
- End state: `momentum.py` computes trend state (50- and 200-day averages), 1/3/6/12-month returns, distance from the 52-week high, realized volatility, relative strength versus SPY and the sector ETF, the options-implied move and the event calendar; `lens-short-term.md` gives each item its test, source and caveat; the skill answers short-horizon questions (weeks to months) with this lens, long-horizon questions (years) with the standard, and ambiguous ones ("good time to sell?") with both
- Options: A exclude (D-3) / B labelled lens with cited methodology / C unlabelled mixing
- Chosen: B — why: the user asked for short-term support after one pushback; a labelled lens with stated base rates keeps the accuracy rule intact
- Supersedes: D-3's exclusion of short-term signals (the value style for long horizons stands). Discards: none
- Open until: the momentum sources are pinned to primary texts

## D-18 2026-10-14 — Holdings and Canadian tax treatment: inline input, published CRA rules with citations, user-supplied marginal rate
- Non-negotiables: no account data is asked for beyond what the question contains; tax lines are general rules with sources, never a filing position; after-tax figures are estimates labelled as such
- End state: `holdings.py` parses shares, average cost and account type (RRSP, TFSA, non-registered) from the question, writes holdings.json, and renders gain or loss at the current price, each zone and any named price, per account; tax treatment per account from `tax-ca.md` (inclusion rate, RRSP deferral, TFSA exemption, US dividend withholding by account, foreign-currency adjusted cost base, superficial loss) with Canada Revenue Agency citations; after-tax estimates at the marginal rate the user names
- Options: A Canada only / B Canada and US
- Chosen: A — why: the user's accounts are Canadian
- Supersedes: none. Discards: none

## D-19 2026-10-14 — Run artifacts live inside the working project, never inside the plugin or its data folder
- Non-negotiables: a dossier is the user's research and travels with their project; the plugin folder holds code only
- End state: `<project>/my-invest/` (`stocks/<TICKER>/`, `_market/`, `_find/`, `_digests/`, git-ignored `.cache/`), with `<project>` = `${CLAUDE_PROJECT_DIR}` passed as `--project`; overrides `MY_INVEST_STORE` or `config.py set store_dir`; only the virtualenv and `config.json` stay under `${CLAUDE_PLUGIN_DATA}`
- Options: A plugin data folder (D-16) / B project folder with ignored cache / C project folder, cache in plugin data
- Chosen: B — why: the user asked for all intermediate artifacts inside the project; an ignored cache keeps git clean without splitting locations
- Supersedes: D-16 (location only). Discards: the `store_dir` userConfig option

## D-20 2026-10-14 — An industry question is an industry-chain question; `find` maps the chain to reach the stocks
- Non-negotiables: the output is a list of relevant listed stocks with cited reasons, not an industry essay; every link and company placement cites a page
- End state: the researcher's industry mode writes a chain map (upstream, core, downstream, enablers) with the US-listed companies at each link and a universe of up to 20 tickers spread across links; `find` screens that universe and reports chain position next to each stock; lenses: growth, value, dividend, trending (momentum plus attention, with the value stance shown beside it), short-term
- Options: A screen a sector ETF's holdings only / B map the chain, then screen across links
- Chosen: B — why: the user's purpose is to find stocks upstream and downstream of a hot industry (semiconductors for AI), which a single sector list misses
- Supersedes: none. Discards: the "industry brief" essay form

## D-21 2026-10-14 — Configuration comes from the project (`my-invest/config.json` or `.env`), never from plugin settings
- Non-negotiables: the SEC user agent must still be declared; secrets stay out of git; a missing setting is an error that says where to put it
- End state: resolution flag → env → `<project>/my-invest/config.json` → `<project>/my-invest/.env` → `<project>/.env` → legacy `<data>/config.json` → default; keys sec_user_agent, margin_of_safety, store_dir, fred_api_key, finnhub_api_key, python; `setup.sh --project .` creates `<project>/my-invest/.venv`; `run.sh` picks `MY_INVEST_PYTHON` → project `.venv` → legacy venv → `python3`; the manifest has no `userConfig`; skills carry no `${user_config.*}`
- Options: A plugin userConfig (D-13) / B project config.json or .env / C both
- Chosen: B — why: the user asked for it; it removes the `userConfig` validation error on older CLIs and keeps every per-project choice with the project
- Supersedes: D-13. Discards: the `userConfig` block and the `${user_config.*}` substitutions

## D-22 2026-10-14 — One settings file, `<project>/my-invest/config.json`, and no setup step
- Non-negotiables: the user writes one JSON file and runs nothing; the SEC user agent stays mandatory
- End state: resolution flag → `config.json` → default; keys sec_user_agent, margin_of_safety, store_dir, fred_api_key, finnhub_api_key, python; `.env` parsing, `config.py` and `setup.sh` removed; `run.sh` creates `my-invest/.venv` with yfinance on the first run that needs prices (Python ≥ 3.10) or uses the configured `python`; `config.json` is git-ignored by the generated `.gitignore`
- Options: A config.json plus .env (D-21) / B config.json only, self-provisioning interpreter
- Chosen: B — why: the user asked for one file and no scripts to run
- Supersedes: D-21. Discards: `.env` support, config.py, setup.sh

## D-23 2026-10-14 — Every skill answer is also an HTML page
- Non-negotiables: self-contained HTML (no external scripts), dark mode, phone width; the Markdown stays the lint-checked source
- End state: `mdhtml.py` converts the Markdown subset the plugin writes; `report.py --html` writes `reports/<date>.html` with the chat sections, the chart panels inlined and the full dossier; `find` and `digest` convert their saved Markdown the same way; skills publish the page with the Artifact tool when available, otherwise send the file
- Options: A Markdown in chat only / B HTML page per answer
- Chosen: B — why: the user asked for better visualisation of each answer
- Supersedes: none. Discards: none

## D-24 2026-10-14 — Data root is `<project>/data/`; each stock has `INDEX.md` and the subfolders facts/, filings/, research/, history/, reports/, charts/
- Non-negotiables: a reader opens `INDEX.md` and finds everything; generated files never mix with the user's config
- End state: layout per skills/analyze/references/store.md; `report.py` regenerates `INDEX.md` and appends `history/log.md` every run; the narrative for each question is kept under `history/`; snapshots and HTML pages under `reports/`
- Options: A flat stock folder (D-16) / B subfolders by kind with an index
- Chosen: B — why: the user asked for grouped artifacts and a plain `data/` root
- Supersedes: D-16 and D-19 (layout only). Discards: `my-invest/` as the root, `dossiers/`, `history.md` at the root

## D-25 2026-10-14 — Every stock carries its industry chain position and related stocks
- Non-negotiables: each related ticker has a cited reason for its link; the file refreshes on a 90-day cadence or on demand
- End state: `research/industry.md` written by the researcher (industry line, chain position, ≤ 10 related tickers with link and citation, chain drivers and risks); rendered in the dossier and in the chat answer; `INDEX.md` shows the industry line
- Options: A only in `find` / B per stock in `analyze` too
- Chosen: B — why: the user wants the relevant industry and stocks visible for every stock asked about
- Supersedes: none. Discards: none

## D-26 2026-10-14 — Answers are written for a beginner: the five questions first, tables and a price map, jargon glossed, detail below a divider
- Non-negotiables: no figure without a marker; the standard's words stay in the detail, not in the headline
- End state: the chat answer = headline, "The short answer" table (sell? when? price? buy? confidence?), price map, ≤ 5 plain reasons, your shares, what could change it, short-term view when relevant, words used here, links, disclaimer; the HTML page shows the same first and the technical sections collapsed under Details; `report.py --chat` renders this shape and glosses terms
- Options: A analyst-style sections (first version) / B beginner-first with details below
- Chosen: B — why: the user found the output verbose and the terms unfriendly; the questions they listed are exactly the five rows
- Supersedes: the chat-answer order in report-template.md (first version). Discards: none

## D-27 2026-10-14 — Options are shown as explained operations on the stock's own contracts, selected by the model's stance
- Non-negotiables: contracts come from the live chain and are marked secondary; every rendering states the premium loss, capped upside and early-assignment risks once; nothing is phrased as a recommendation
- End state: `options.py` lists contracts at five anchors (price, buy zone, sell zone, ±10%) for the first monthly expiry ≥ 30 days; `score.py` picks the operations whose conditions hold per rules/options-playbook.md (covered call, protective put, cash-secured put, long call, or "not now"); the chat answer shows one table row per operation with when, contract, pay or receive, best and worst case, plus glosses
- Options: A options context only (implied move, ratios) / B explained operations tied to stance and holdings
- Chosen: B — why: the user has never used options and asked for suggestions that teach how they work
- Supersedes: none. Discards: none

## D-28 2026-10-14 — The answer covers news, peers and the industry, not only price: an advisor's brief for a beginner
- Non-negotiables: every peer figure comes from that peer's own facts file; news judgments are words beside cited items; nothing is computed by the model
- End state: the researcher's `industry.md` names peers and carries dated industry-development entries; `analyze` fetches up to four peers and `compare.py` writes `facts/peers.json` and the comparison table; the chat answer adds "What the news says", "Compared with similar companies" and "How the industry is doing" between Why and Your shares; the narrative gains the matching slots
- Options: A price-centred answer / B advisor brief with news, peers, industry
- Chosen: B — why: the user wants an AI financial advisor for beginners, not a valuation printout
- Supersedes: none. Discards: none

## D-29 2026-10-14 — Three role agents (analyst, researcher, advisor); skills orchestrate; nothing from the question is hard-coded
- Non-negotiables: numbers only from scripts; evidence only from fetched text; judgment only in words; every horizon, lens, peer list, margin and what-if comes from `request.json`, which records its inferences
- End state: `analyze`, `find` and `digest` write a request file, spawn the analyst and the researcher in parallel, then the advisor, and paste its answer; `metrics.py --horizons` and `--g-base`, `score.py` and `report.py` read horizons from the valuation and the request; agents: `analyst` (Bash + scripts, sonnet), `researcher` (web + extracts, sonnet), `advisor` (narrative + report, opus)
- Options: A skill orchestrates scripts itself and writes the narrative (previous version) / B role agents behind thin skills
- Chosen: B — why: the user asked for advisor and analyst agents handling different tasks, and for the plugin to infer constraints from the question instead of fixed horizons
- Supersedes: D-15 (agent count), the fixed 1/2/5/10 horizon set in D-12 (now the default when the question names none). Discards: none

## D-30 2026-10-14 — The advisor is the persona the user talks to (a skill in the main session) and delegates deep work to the analyst agent; knowledge lives in skills both use
- Non-negotiables: only the main session can spawn agents in Claude Code; numbers from scripts; the advisor answers from saved work when it is fresh and delegates when it is not or when the question needs depth
- End state: skills `advisor` (user-facing), `data`, `research`, `score`, `answer`, `evidence` (knowledge); one agent `analyst` (modes analyze, screen, digest) preloading the knowledge skills; the researcher agent folds into the `research` skill; the advisor writes the beginner narrative and runs `report.py`; delegation rules written in the advisor skill
- Options: A skills orchestrate agents (D-29) / B advisor persona delegating to a self-sufficient analyst
- Chosen: B — why: the user wants to talk to an advisor that has the latest and the history and delegates deep analysis to a more professional analyst; subagents cannot spawn subagents, so the advisor must be the main session
- Supersedes: D-29 (agent set), D-15 (skill set). Discards: skills analyze, find, digest, ask; agents researcher, advisor (as an agent)

## D-31 2026-10-14 — Holdings are read from the question and never stored
- Non-negotiables: no position file survives the answer; the question's own answer may keep the figures it asked about
- End state: `holdings.py` writes `facts/holdings*.json` for the run; the advisor deletes them after the answer; the dated report snapshot remains
- Options: A optional stored portfolio / B question-only
- Chosen: B — why: the user's holdings change often and they asked not to save them
- Supersedes: D-18 (storage of holdings.json). Discards: none

## D-32 2026-10-14 — The headline is a forward outlook (expected-return scenarios by horizon, months-ahead range, consensus, calibration); the strict owner-earnings value is one lens
- Non-negotiables: every scenario input is stated and cited; consensus is secondary; the model's own past error on the stock is shown; recommendations fit the reader's situation (holding or not) and the trend; no point forecast for months
- End state: `metrics.outlook` (EPS × growth × multiple path + shareholder yield per horizon and scenario, verdict vs required return), `metrics.multiples` (10-year P/E, P/FCF, EV/EBIT history), `facts.consensus` (Yahoo analyst data), `metrics.calibration` (strict value and base forecast five years ago vs realised); `score.py action.recommendation` per outlook.md §5; the answer leads with "where is the price likely to go" and "next few months"
- Options: A strict value headline (D-12) / B outlook headline with the strict value as a labelled lens
- Chosen: B — why: the user found "wait for $104 at $343" useless; a professional states where the price is likely to go, on what evidence, and what to do from the reader's position
- Supersedes: D-12 (headline), D-26 (short-answer rows). Discards: none
