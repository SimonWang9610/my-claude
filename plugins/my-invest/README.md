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

The advisor reads your question (tickers, horizon, holdings, what you want to know), decides whether the
saved analysis is fresh enough or asks the **analyst** to do the deep work first, and answers with a
short brief, the same shape every time:

- **Answer** — if you hold it: hold, trim or sell, and why in one clause; if you want to buy: buy in
  stages, wait, or stay away, with the limit-order levels the rule points to. A failed deal-breaker
  check says "stay away"; missing data says "no verdict", never a default hold.
- **Summary** — the figures the answer rests on: price today, the expected range by a named month ("by
  Oct 2031, 5 years from today": worst, likely, best, and the yearly return that implies), the return
  the risk demands, the next few months, analysts' average target with its base rate, confidence with
  its band, your shares. Every horizon counts from the price date printed under the headline.
- **Why** (four bullets), **Risks: the case against** (three), **Track record** (how the same method did
  in past years against what happened and against SPY, and what this advisor said last time), **What to
  watch**, **Not verified**.
- The detail you asked for, and only that: the news and what it means, similar companies, your shares
  with Canadian tax, options explained on this stock's contracts, a short-term view.
- **Words used here** and **Sources**: every figure carries a marker such as `[S3]`, and Sources lists
  each marker with a link to the raw source — the SEC filing or API call, the Yahoo page — or, for a
  script's arithmetic, the file it was computed into and the raw sources it used. On the page the
  markers are links.
- A page with the brief and the charts, and one link to the **full dossier** (every table, the
  scorecard, the strict value lens, the evidence log), which stays in the stock's folder for the next
  question rather than in the answer.

A follow-up such as "which price should I sell, and how many shares?" is answered in the conversation:
the sizing frames (cap the weight at 15%, 12.5% or 10% of your accounts, sell the gain, recover the
cost) with the advisor's pick, the look-through weight once your funds are counted, which account to
sell from first, the plan in halves at named levels (52-week high, 50-day average, the options-implied
range, the next earnings date), and what it changes in the earlier answers.

A portfolio question gets one table (one row per position: worth, gain, what to do, limit level,
expected vs required return, confidence, link) and one short block per ticker; funds (ETFs) are
answered too, by the fund rule (trend, cost, concentration, labelled as this standard's own reading),
with a warning for leveraged, inverse and covered-call funds.

Nothing is fixed in advance: horizons ("next 3 years", "by 2030", "this quarter"), the lens, the peers,
a margin of safety or a growth what-if are read from your question, and any assumption is stated. Your
positions are read from the question (or the broker file it names) for that answer only and never stored.

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

Everything numeric is done by scripts, not by any agent: one script per data source or step (SEC facts,
filings, prices, options, consensus, momentum, news, a fund, metrics, score, compare, holdings, chart,
report, lint), so a failure in one stops only that step and every number traces to the script and inputs
that produced it. The advisor runs them; you never do. The design draws on a survey of the most-starred
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
    facts/              facts.json (statements, prices, macro, market, options, consensus, momentum, metrics incl. the simulated record), series.json, scorecard.json, peers.json — or fund.json for an ETF
    filings/<accn>/     the 10-K split into items, auditor's report, notes
    research/           research.md (cumulative, cited, dated), evidence.json (the four verdicts), industry.md (chain position and related stocks)
    history/            log.md (one line per question: what was said, at what price, what was expected), the analyst's note and the advisor's narrative for each question
    reports/            dossier.md and dossier.html (every detail, for later questions), dated snapshots of the brief, the answer pages
    charts/             the five-panel chart per run
```

- Refresh rules: prices daily; fundamentals only when a new 10-K or 10-Q is filed; filings three years back; the industry file every 90 days or when you ask about peers; everything else every run.
- Override the location with `"store_dir"` in `data/config.json`.

## Sources

- Primary: SEC XBRL APIs and the filings themselves; FRED or the Treasury par-yield table; Bank of Canada USD/CAD; Canada Revenue Agency and Department of Justice pages for tax rules.
- Secondary, marked so in every output: Yahoo prices, options chains, analyst consensus and ETF series; news outlets; Damodaran's implied equity risk premium (a dated constant, refreshed by hand).
- Social: posts found by search and fetched, cited by handle and date, shown as attributed opinion that never supports a figure. Reddit and X usually refuse automated access; the output then says so.

## Limitations

- US-listed stocks and ETFs only. Financials, REITs and utilities get `n/a` on the industrial models, so their scores rest on fewer items; a fund has no scorecard and is answered by the fund rule from Yahoo data.
- The outlook is a model output, not a forecast: stated growth and multiple paths, a discount rate from the Treasury yield plus an equity risk premium. Parameters are printed and are the standard's opinion. No single-number price target is ever given.
- The simulated track record uses the figures the SEC API reports today, not as first filed, and the standard's thresholds were not chosen out of sample; it is labelled simulated for that reason. Only the logged past calls are a true record, and they accumulate as you ask.
- Short-term signals describe the recent past. The verified sources report modest average edges with large drawdowns after market declines; the output says so each time.
- Tax lines are general federal rules with citations. Provincial rates differ, the adjusted cost base uses today's exchange rate as an approximation, and the result is not a filing position.
- Yahoo data breaks every few months. Scripts cache, back off and report the failure; they never fill a gap with an estimate.
- Several thresholds (Beneish coefficients and cutoff, Graham's wording, the Altman safe-zone bounds) rest on secondary sources and are labelled UNVERIFIED.
- Nothing here is investment or tax advice. Every dossier ends with that line.
