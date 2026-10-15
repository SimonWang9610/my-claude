# my-invest

Ask about US stocks in plain words. Get a cited answer: price outlook, buy and sell prices with timing,
reasons, strengths and weaknesses, options context, your holdings and Canadian tax treatment, charts.
Every figure carries a source URL and date. Each stock's file grows with every question you ask.

## How you use it

You talk to the **advisor**. Ask in plain words, in the project folder where your data lives:

- "how about Apple?" · "should I sell AAPL? I have 120 shares at $150 in my TFSA and 80 at $210 non-registered, marginal rate 43%" · "is it a good time to sell GOOGL" · "what did the 10-K say about China" · "what if AAPL hits 400" · "AI is hot, which stocks are popular and rising in it or its supply chain?" · "which stocks should I buy for the next 3 years" · "daily digest"
- or type `/my-invest:advisor <question>`.

The advisor reads your question (stocks, horizon, holdings, what you want to know), decides whether the
saved analysis is fresh enough or asks the **analyst** to do the deep work first, and answers for a
beginner:

- **The short answer** table: Should I sell? When? At what price? Should I buy? How confident is the model?
- a one-line **price map**: buy zone, fair value, sell zone, and where today's price sits
- **why**, in plain sentences, each tied to a source
- **what the news says** and what each item means for this stock
- **compared with similar companies** and **how the industry is doing** (its place in the industry chain)
- **your shares**, when you state them: worth now, gain, tax if sold now, what you keep, per account
- **options, explained with your numbers**: which operation fits and how it would work on real contracts
- a **short-term view** when you ask about weeks or months, **what could change the answer**, and the
  **words used**
- an HTML page with the same first and the technical detail collapsed below

Nothing is fixed in advance: horizons ("next 3 years", "by 2030", "this quarter"), the lens, the peers,
a margin of safety or a growth what-if are read from your question, and any assumption is stated. Your
positions are read from the question for that answer only and never stored.

## Agents and skills

- **advisor** (a skill, the one you talk to): understands the question, delegates, answers.
- **analyst** (an agent the advisor spawns): the professional. Fetches ten years of SEC facts, prices,
  options and market data; reads the 10-K from local extracts; researches news, posts and the industry
  chain with citations; judges the evidence items; compares peers; scores at your horizons; writes the
  analyst's note, the dossier and the page. Also screens an industry's chain or a ticker list, and runs
  the daily or weekly digest.
- Knowledge skills both use, never invoked by you: `data` (scripts, request, data folder), `research`
  (how evidence is gathered), `score` (the standard), `answer` (how a beginner is answered), `evidence`
  (every figure cited, the lint).

Everything numeric is done by scripts, not by any agent.

## The standard, briefly

- Gates first: bankruptcy or restatement 8-K items, Altman distress, going-concern paragraph, negative owner earnings in three of five years, serial dilution. Any failure → tier `pass`, stance `avoid`.
- Five equal-weight pillars of yes/no items, 20 points each: quality and moat · financial strength · capital allocation · valuation and margin of safety · risks.
- Fair value from a ten-year owner-earnings model (bear, base, bull), rolled forward to each horizon. Buy zone = base value minus the margin of safety (default 30%). Sell zone = bull value.
- Confidence = evidence coverage, scenario agreement, data freshness; the formula is printed with the number.
- Thresholds that could not be verified against the primary text are marked UNVERIFIED in every output and are never gates.
- Details: `skills/score/rules/` (one card per gate set, pillar and the short-term lens), `skills/score/references/` (valuation, action matrix, Canadian tax rules), `DECISIONS.md` (why each choice was made), `research/` (the pinned sources).

## Installation

```
claude plugin marketplace add SimonWang9610/my-claude
claude plugin install my-invest@my-claude
```

Then, in the project folder where you will ask questions, create **one file**, `data/config.json`:

```json
{
  "sec_user_agent": "AppName you@example.com",
  "margin_of_safety": 0.30
}
```

- `sec_user_agent` is required: the SEC rejects requests without a declared user agent. Without it the
  scripts stop and tell you to create this file.
- Optional keys: `"store_dir"` (another folder for the saved files), `"fred_api_key"` (10-year Treasury
  yield; the Treasury table is the fallback), `"finnhub_api_key"`, `"python"` (an interpreter that already
  has `yfinance`, if you prefer your own environment).
- Nothing else to run. On the first question that needs prices, the plugin creates `data/.venv` with
  `yfinance` by itself (needs Python 3.10 or newer on your PATH) and tells you it did.
- First question: `/my-invest:analyze how about Apple?`

## What is saved, and where

Everything is written under `<project>/data/` in the folder you run Claude Code in. The plugin folder holds code only.

```
<project>/data/
  config.json           the one file you write (SEC user agent, margin of safety, optional keys); git-ignored
  .cache/  .venv/       raw downloads and the yfinance environment the plugin creates; git-ignored
  market/               SPY and sector ETF price series shared by all stocks
  find/                 industry chain maps and ranked screens (.md and .html)
  digests/              daily and weekly digests (.md and .html)
  stocks/<TICKER>/
    INDEX.md            start here: latest decision, industry line, folder map, history table
    facts/              facts.json (statements, prices, macro, market, options, momentum, metrics), series.json, scorecard.json, peers.json
    filings/<accn>/     the 10-K split into items, auditor's report, notes
    research/           research.md (cumulative, cited, dated), evidence.json (the four verdicts), industry.md (chain position and related stocks)
    history/            log.md (one line per question), the analyst's note and the advisor's narrative for each question
    reports/            dossier.md (latest), dated snapshots, and the HTML answer pages
    charts/             the five-panel chart per run
```

- Refresh rules: prices daily; fundamentals only when a new 10-K or 10-Q is filed; filings three years back; the industry file every 90 days or when you ask about peers; everything else every run.
- Override the location with `"store_dir"` in `data/config.json`.

## Sources

- Primary: SEC XBRL APIs and the filings themselves; FRED or the Treasury par-yield table; Bank of Canada USD/CAD; Canada Revenue Agency and Department of Justice pages for tax rules.
- Secondary, marked so in every output: Yahoo prices, options chains and ETF series; news outlets; Damodaran's implied equity risk premium (a dated constant, refreshed by hand).
- Social: posts found by search and fetched, cited by handle and date. Reddit and X usually refuse automated access; the output then says so.

## Limitations

- US-listed stocks only. Financials, REITs and utilities get `n/a` on the industrial models, so their scores rest on fewer items.
- The price outlook is a model output, not a forecast: owner earnings, a discount rate from the Treasury yield plus an equity risk premium, growth capped by the company's own record. Parameters are printed and are the standard's opinion.
- Short-term signals describe the recent past. The verified sources report modest average edges with large drawdowns after market declines; the output says so each time.
- Tax lines are general federal rules with citations. Provincial rates differ, the adjusted cost base uses today's exchange rate as an approximation, and the result is not a filing position.
- Yahoo data breaks every few months. Scripts cache, back off and report the failure; they never fill a gap with an estimate.
- Several thresholds (Beneish coefficients and cutoff, Graham's wording, the Altman safe-zone bounds) rest on secondary sources and are labelled UNVERIFIED.
- Nothing here is investment or tax advice. Every dossier ends with that line.
