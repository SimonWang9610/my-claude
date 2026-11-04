# Decisions (rebuild of 2026-11-03; the earlier D-1..D-36 belong to the discarded plugin and live in git history)

Format: what was decided, the options weighed, why. Source → decision → reason for adoptions from outside.

## D-1 2026-11-03 — Rebuild from scratch; discard the scorecard, options and the tax module
- Options: A refactor the three-skill plugin / B rebuild with readable standards and nameable scripts
- Chosen: B — why: the user could not read the scorecard's standard, name each of 23 scripts' purpose, or
  explain the six per-stock folders; keep only US-only, every-figure-cited, no default hold, the proof idea
- Dropped: five equal-weight pillars, options operations, after-tax estimates (one account-order rule kept)

## D-2 — Six dimensions ending in a view; the verdict composed in the open
- fundamentals, dcf, statistics, macro and politics, industry, sentiment; each a row in `views` with stance,
  strength 1-3, horizon, sentence, evidence ids — why: no hidden weights; coverage is measurable
- Per intent only the dimensions the question needs (stock 6, holdings 4, sector 3, macro 2, digest 3)

## D-3 — Three options defined by risk taken, in separate tables with question-shaped columns
- Conservative acts at the DCF low value and on primary evidence; aggressive accepts sentiment and trend up
  to the high value; on a sell question conservative protects capital first — why: "conservative" must
  always mean less risk, not less action
- Default all three, each its own table; one when the user names a level; columns from the question's own
  words — why (user): a fixed-column table with the tiers as rows cannot carry enough per option

## D-4 — Confidence out of 100 from three auditable parts
- evidence 35 (coverage × source grade), agreement 35 (|weighted stance| × DCF-spread factor), record 30
  (30 × (right + 2.5)/(n + 5) over settled calls of the same side); bands 80/65/45 — why: the user asked
  for a score they can trust, so each part prints its reason and `record.py` computes it from the tables

## D-5 — Calls scored against SPY when due
- buy-side right if the stock beat SPY over the horizon, sell-side if it lagged; no editing after the fact
  — why: a method that sounds good and keeps being wrong must show up in the record part

## D-6 — One SQLite database for fetched series and analysis history; holdings never stored
- `data/invest.db`, 15 tables, every numeric row with a `source_id`; schema generated from `db.py` so the
  reference cannot drift; created and migrated by the first script that runs
- Holdings come from the user's CSV (or `holdings/` folder) each run — why (user): a database of their
  positions is not wanted; the DB earns its place with price history (incremental fetch), fundamentals and
  the track record

## D-7 — Scripts only for deterministic work: fetch, format, arithmetic; agents judge
- nine scripts, one purpose each; DCF assumptions, news leans, stances and the answer are the agents' —
  why (user): a script per purpose they can name; arithmetic stays in scripts because a model doing sums
  in prose is where numbers go wrong

## D-8 — Horizons at most five years, dated from the price date
- data defaults follow: five years of prices and fundamentals, statistics windows 1y/3y/5y, DCF forecast 5 years

## D-9 — Chat answer in Markdown; the saved report an HTML page
- `record.py report` lints the markers, links them, appends Sources and a price chart (SVG from the prices
  table), writes `data/reports/<date>-<slug>.html` — why (user): better visualisation for what is kept

## D-10 — A fourth skill, `digest`, for the daily read of the holdings
- reuses the scripts, tables, markers and page; reads `<project>/holdings/*.csv`; leads with what needs
  attention; makes no calls — why (user): useful information before diving in, mainly on their holdings.
  Relaxes the three-skill cap of the old D-33 to four, each with a distinct trigger.

## Adoptions from the 2026-11-02 survey of AI-trading repos (research/)
- TradingAgents (debate between bull and bear) → the case against is mandatory → a verdict must survive its
  strongest counter-argument
- ai-hedge-fund (named analyst personas with confidence) → one confidence per conclusion, but computed from
  the tables rather than stated → auditable
- OpenBB (one data layer, many views) → one database, scripts per source → a wrong number is traced to one table
- Rejected: trained price models (qlib, FinRL) → not explainable to a beginner and no reliable edge

## D-11 2026-11-03 — The valuation dimension pairs the DCF with what the market pays
- `dcf` dimension renamed `valuation`; `dcf.py` adds a sensitivity grid (growth ±5 points × discount ±1.5
  points), the reverse DCF (the growth today's price assumes, solved by bisection), and the trailing P/E
  against the stock's own five-year range and the stored peers' median, plus P/FCF and EV/EBIT; implied
  values stored as `reverse_dcf`, `pe_range`, `pe_peers` rows with a `method` column
- Why (user): different parameters give different DCF results; the inputs are now derived from named
  origins, printed with the result, and the price is read back into an implied growth and a multiple so
  the DCF cannot be the only voice. Not applicable (with the reason) for loss-makers and funds.
