# my-invest

Ask about US stocks in plain words. Get a verdict a beginner can check: where the price is likely to go,
whether to buy or sell, when and at what price, how confident — followed by the proof (the scenarios and
their inputs, the case against, the model's track record on that stock, what could change the answer,
what could not be verified) and then the detail (news, peers, industry, your shares and Canadian tax,
options on real contracts, charts). Every figure carries a source URL and date. Each stock's file grows
with every question you ask.

## How you use it

You talk to the **advisor**. Ask in plain words, in the project folder where your data lives:

- "how about Apple?" · "should I sell AAPL? I have 120 shares at $150 in my TFSA and 80 at $210 non-registered, marginal rate 43%" · "is it a good time to sell GOOGL" · "what did the 10-K say about China" · "what if AAPL hits 400" · "AI is hot, which stocks are popular and rising in it or its supply chain?" · "which stocks should I buy for the next 3 years" · "daily digest"
- or type `/my-invest:advisor <question>`.

The advisor reads your question (stocks, horizon, holdings, what you want to know), decides whether the
saved analysis is fresh enough or asks the **analyst** to do the deep work first, and answers in the same
order every time:

1. **The verdict** — a table: where is the price likely to go at your horizon, the next few months, should I
   sell, should I buy (with entry levels), how confident (a number, its band, and what lowers it); then a
   one-line price map.
2. **The proof** — *computed by scripts*: the bear, base and bull scenarios with the growth, multiple and
   cash-return assumptions behind them, and analyst consensus as a secondary row · *the analyst's reading*:
   the case against the verdict · *computed by scripts*: the track record — the same method applied at each
   past fiscal year (forecast vs what happened vs SPY, labelled simulated) and what this advisor said about
   the stock before, with the price and SPY since · what could change the answer (observable events with a
   date or price) · what could not be verified (every missing input, stale figure and refused page).
3. **The detail** you asked for — what the news says and what it means, compared with similar companies,
   how the industry chain is doing, your shares (worth, gain, tax if sold now, per account), options
   explained on this stock's own contracts, a short-term view for questions about weeks or months, and the
   words used.
4. An HTML page with the same first and the full dossier collapsed below.

Nothing is fixed in advance: horizons ("next 3 years", "by 2030", "this quarter"), the lens, the peers,
a margin of safety or a growth what-if are read from your question, and any assumption is stated. Your
positions are read from the question for that answer only and never stored. When the data cannot support a
verdict, the answer says `no verdict` and why; it never defaults to "hold".

## Agents and skills

- **advisor** (a skill, the one you talk to): understands the question, delegates, answers.
- **analyst** (an agent the advisor spawns): the professional. Fetches ten years of SEC facts, prices,
  options and market data; reads the 10-K from local extracts; researches news, posts and the industry
  chain with citations; judges the evidence items; compares peers; scores at your horizons; argues the case
  against its own verdict; lists what it could not verify; writes the analyst's note, the dossier and the
  page. Also screens an industry's chain or a ticker list, and runs the daily or weekly digest.
- Two knowledge skills the analyst preloads and the advisor reads, never invoked by you: `evidence` (how
  every number and claim is obtained and cited: scripts, data folder, research procedure, the lint) and
  `standard` (how a verdict is formed and what proof it must carry).

Everything numeric is done by scripts, not by any agent. The design draws on a survey of the most-starred
AI trading repositories (`research/2026-11-02-ai-trading-repos.md`): what was adopted (a fixed answer
order, scripts compute and the model narrates, the case against, abstaining instead of a fake hold, a
settled record of past calls, every return beside its benchmark) and what was deliberately not (live
trading, multi-agent debates, stop-losses, tuned thresholds, celebrity personas, sentiment feeds).

## The standard, briefly

- Gates first: bankruptcy or restatement 8-K items, Altman distress, going-concern paragraph, negative owner earnings in three of five years, serial dilution. Any failure → tier `pass`, stance `avoid`.
- Five equal-weight pillars of yes/no items, 20 points each: quality and moat · financial strength · capital allocation · valuation and margin of safety · risks.
- Outlook: expected yearly return per horizon from earnings growth, the multiple's path back toward its own ten-year range, and cash returned, in bear, base and bull cases, against the return the risk demands (Treasury yield plus an equity risk premium). The recommendation follows from that return, your position and the trend.
- A strict owner-earnings fair value with buy and sell zones is shown as one labelled lens, never as the headline.
- Confidence = evidence coverage, scenario agreement, data freshness, outlook spread; the formula is printed with the number and its band.
- Thresholds that could not be verified against the primary text are marked UNVERIFIED in every output and are never gates.
- Details: `skills/standard/rules/` (one card per gate set, pillar, the outlook, the short-term lens and the options playbook), `skills/standard/references/` (valuation, action matrix, Canadian tax rules, the note slots), `DECISIONS.md` (why each choice was made), `research/` (the pinned sources and the repo survey).

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
- First question: `/my-invest:advisor how about Apple?`

## What is saved, and where

Everything is written under `<project>/data/` in the folder you run Claude Code in. The plugin folder holds code only.

```
<project>/data/
  config.json           the one file you write (SEC user agent, margin of safety, optional keys); git-ignored
  .cache/  .venv/       raw downloads and the yfinance environment the plugin creates; git-ignored
  market/               SPY and sector ETF price series shared by all stocks (the benchmark in every track record)
  find/                 industry chain maps and ranked screens (.md and .html)
  digests/              daily and weekly digests (.md and .html)
  stocks/<TICKER>/
    INDEX.md            start here: latest decision, track-record line, industry line, folder map, history table
    facts/              facts.json (statements, prices, macro, market, options, consensus, momentum, metrics incl. the simulated record), series.json, scorecard.json, peers.json
    filings/<accn>/     the 10-K split into items, auditor's report, notes
    research/           research.md (cumulative, cited, dated), evidence.json (the four verdicts), industry.md (chain position and related stocks)
    history/            log.md (one line per question: what was said, at what price, what was expected), the analyst's note and the advisor's narrative for each question
    reports/            dossier.md (latest), dated snapshots, and the HTML answer pages
    charts/             the five-panel chart per run
```

- Refresh rules: prices daily; fundamentals only when a new 10-K or 10-Q is filed; filings three years back; the industry file every 90 days or when you ask about peers; everything else every run.
- Override the location with `"store_dir"` in `data/config.json`.

## Sources

- Primary: SEC XBRL APIs and the filings themselves; FRED or the Treasury par-yield table; Bank of Canada USD/CAD; Canada Revenue Agency and Department of Justice pages for tax rules.
- Secondary, marked so in every output: Yahoo prices, options chains, analyst consensus and ETF series; news outlets; Damodaran's implied equity risk premium (a dated constant, refreshed by hand).
- Social: posts found by search and fetched, cited by handle and date, shown as attributed opinion that never supports a figure. Reddit and X usually refuse automated access; the output then says so.

## Limitations

- US-listed stocks only. Financials, REITs and utilities get `n/a` on the industrial models, so their scores rest on fewer items.
- The outlook is a model output, not a forecast: stated growth and multiple paths, a discount rate from the Treasury yield plus an equity risk premium. Parameters are printed and are the standard's opinion. No single-number price target is ever given.
- The simulated track record uses the figures the SEC API reports today, not as first filed, and the standard's thresholds were not chosen out of sample; it is labelled simulated for that reason. Only the logged past calls are a true record, and they accumulate as you ask.
- Short-term signals describe the recent past. The verified sources report modest average edges with large drawdowns after market declines; the output says so each time.
- Tax lines are general federal rules with citations. Provincial rates differ, the adjusted cost base uses today's exchange rate as an approximation, and the result is not a filing position.
- Yahoo data breaks every few months. Scripts cache, back off and report the failure; they never fill a gap with an estimate.
- Several thresholds (Beneish coefficients and cutoff, Graham's wording, the Altman safe-zone bounds) rest on secondary sources and are labelled UNVERIFIED.
- Nothing here is investment or tax advice. Every dossier ends with that line.
