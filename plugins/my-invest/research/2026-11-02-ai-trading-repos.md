# Scout report — popular AI trading repositories on GitHub (2026-11-02)

Three sweeps on 2026-11-02 (LLM trading agents, quant and backtesting platforms, AI stock-research
assistants), star counts as GitHub rendered them that day. Input, not content: what sharpened the
plugin is recorded below as `source → decision → reason`; the rest is noted and dropped.

## What was surveyed

| Repo | Stars | What it is | What it taught us |
|---|---|---|---|
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 119.9k | LangGraph firm simulation: analysts → bull/bear debate → trader → risk team → portfolio manager | one five-tier rating on the first line; "conflict alone is not a reason to Hold"; an unparseable rating becomes `REVIEW`, never Hold; a memory log settles past calls against realised return; point-in-time SEC reads |
| [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | 75.0k | open data platform | every result carries `provider`, `warnings`, timestamp and arguments |
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | 64.4k | persona agents (Buffett, Graham…) + deterministic portfolio code | `signal + confidence 0–100 + reasoning` with prompted confidence bands; abstain on missing data instead of a fake neutral; "the LLM never touches the trade"; a ledger of paper calls as the track record |
| [freqtrade/freqtrade](https://github.com/freqtrade/freqtrade) | 56.3k | crypto bot with the clearest backtest docs | "Market change" (buy-and-hold) beside every result; lookahead analysis as a tool; dry-run first; hyperopt warned as overfitting |
| [microsoft/qlib](https://github.com/microsoft/qlib) | 49.9k | ML quant platform | excess return vs benchmark with and without cost; point-in-time database because figures get restated |
| [HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading) | 37.5k | trading workbench | grounding gate: figures in an answer are checked against tool evidence and cut when unsupported |
| [hsliuping/TradingAgents-CN](https://github.com/hsliuping/TradingAgents-CN) | 32.8k | A-share fork | states no target prices, no stop levels, no timing: an advisor, not a trader |
| [QuantConnect/Lean](https://github.com/QuantConnect/Lean) | 22.4k | production engine | research guide: state the hypothesis before testing; in-sample winners "almost always underperform" |
| [stefan-jansen/machine-learning-for-trading](https://github.com/stefan-jansen/machine-learning-for-trading) | 21.7k | book code | walk-forward; backtest as falsification; point-in-time EDGAR; breakeven costs |
| [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 8.4k | equity-research agents | "models reason, software computes, agents orchestrate, systems verify"; DCF tables labelled code-computed; Bull, Bear, Judge; data caveats in the report |
| [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | 3.6k | ~40 Claude skills for investors | fixed report sections incl. bull and bear cases; "include data sources and dates"; beginner on-ramp guides |
| [mshumer/gpt-investor](https://github.com/mshumer/gpt-investor) | 2.3k | one-notebook ranker | negative example: price targets with no citations |
| [stefanoamorelli/sec-edgar-mcp](https://github.com/stefanoamorelli/sec-edgar-mcp) | 384 | SEC MCP server | every response carries the filing URL |
| [xvary-research/claude-code-stock-analysis-skill](https://github.com/xvary-research/claude-code-stock-analysis-skill) | 19 | Claude Code plugin | fixed order: Verdict → Rationale → Scores → Pillars → Risks → **Kill criteria** → Snapshot → Next checks; "cite filing form/date whenever stating a hard figure" |
| [AdvancingTitans/stock-analysis](https://github.com/AdvancingTitans/stock-analysis) | 34 | Claude Code / Codex research system | every claim typed **fact / derived fact (formula shown) / analysis**; "missing values are not treated as zero"; "community opinion cannot alone support a financial fact" |
| [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading) | 969 | memory-layered LLM trader | a decision cites the memory ids that informed it |
| also read | | FinGPT 21.5k, RD-Agent 15.2k, FinRL 17.0k, vectorbt 9.6k, backtrader 23.6k (dormant), zipline 20.2k (dormant), yfinance 25.8k, gs-quant 13.9k, financial-datasets/mcp-server 2.3k, daymade/claude-code-skills 1.5k, maverick-mcp 717, Stock-Prediction-Models 9.5k (archived; undefined "accuracy", no costs) | |

## Adopted (source → decision → reason)

- TradingAgents, xvary, AdvancingTitans, FinRobot → **one fixed answer order: verdict, then proof, then detail**, the same every run → a beginner can compare two answers only when the sections never move; the verdict line comes first so the proof is read as proof.
- FinRobot, ai-hedge-fund, daymade, Vibe-Trading → **scripts compute, the agent narrates; a figure not in a script's output is cut, not explained** → already the plugin's rule; the grounding-gate wording makes the lint's purpose plain.
- AdvancingTitans, FinRobot → **claim typing in the answer: sections tagged "computed by scripts" or "the analyst's reading"** → the reader sees which lines are arithmetic and which are judgment; the lint already separates `derived` from `primary`.
- TradingAgents, FinRobot, tradermonty → **one "case against" section written by the same analyst, weighed on merit** → the cheapest honest device against a one-sided story; a multi-agent debate buys cost and run-to-run variance, not accuracy.
- TradingAgents → **"conflict alone is not Hold"; a verdict is committed when the evidence leans and "balanced" only when it is** → a rookie reads Hold as safety; it must be earned.
- TradingAgents `REVIEW`, ai-hedge-fund abstention, FinMem → **`no verdict` when the scorecard is missing or stale or a required script failed; never a default hold** → a fake neutral is the lie a beginner cannot detect.
- xvary kill criteria, AdvancingTitans next signals → **"what could change the answer" is mandatory and each line is an observable with a date or price, tied to the item it would flip** → teaches that a thesis is conditional and makes the next check concrete.
- daymade, OpenCandle, AdvancingTitans, OpenBB warnings → **"what could not be verified" is a mandatory section listing every null, pending item, stale figure and refused page** → gaps shown beside the conclusion are what let the reader size their trust.
- TradingAgents memory log, ai-hedge-fund ledger, FinMem → **a real track record: every call is logged with price and recommendation, and the next answer settles the earlier calls against the price and SPY since** → calls made before the outcome was known are the only honest evidence that the advisor is not fitting the story to the chart.
- Qlib, Lean, freqtrade "Market change", ml4t → **a simulated record: the same method applied at past fiscal years, forecast vs realised vs SPY over the same window, labelled simulated and in-sample** → one point five years back was anecdote; a grid is evidence, and the label keeps it honest.
- all quant repos → **every return beside its benchmark over the same window** → +12% means nothing without the market's +20%.
- ai-hedge-fund bands → **confidence shown as a number with a band word (thin / mixed / solid / strong) and what lowers it** → a bare percentage reads as a probability to a beginner; the formula stays printed.
- TradingAgents-CN, surveys' consensus → **no single-number price target; scenarios with stated inputs, consensus as a secondary row with its base rate** → already D-32; the survey confirms targets are the practice to avoid.
- AdvancingTitans → **a post or forum view never supports a figure** → sentiment feeds are the input most likely to mislead a rookie; posts stay attributed opinion.
- Lean research guide → **the rule is stated before it is scored; thresholds are never chosen on the dates they are then evaluated on** → the simulated record must say its thresholds are in-sample.
- tradermonty, Vibe-Trading wiki → **beginner on-ramp stays in the README and the glossary; no celebrity personas** → the checklist, not the name, carries the judgment.

## Rejected (source → decision → reason)

- TradingAgents 7+ roles, FinRobot 9 agents → no multi-agent debate → cost and non-determinism; the repos' own READMEs admit two runs can differ.
- nofx, ValueCell, Vibe-Trading live, AI-Trader → no broker surface, no "execute" vocabulary → a years-long holder gains nothing and inherits the failure modes.
- freqtrade, backtrader, vectorbt → no stop-loss, trailing stop or ROI exits → they turn volatility into realised losses and taxable events; review dates replace them.
- freqtrade hyperopt, vectorbt sweeps, Qlib training → no tuning of the standard's thresholds → with ~15 annual observations per company any search overfits.
- Lean, backtrader, freqtrade → no Sharpe headline → conventions differ and a rookie cannot read it; return vs benchmark and max drawdown instead.
- ai-hedge-fund, FinRobot personas → no Buffett-voice agents → stylised approximations add nothing the pillar checklist does not.
- TradingAgents StockTwits/Reddit, FinGPT forecaster → no sentiment or next-week direction inputs → short-horizon noise contradicts the horizon and the evidence rule.
- ai-hedge-fund hash-chained ledger → a dated log in the project folder, under git, is the ledger → crypto-style chaining solves a problem the owner's own repository does not have.
- freqtrade lookahead-analysis as a script → deferred → worth a lint once the simulated record uses point-in-time filings; today the record is labelled instead.
- xvary vendor footer, hidden thresholds → every threshold stays printed in `skills/standard/rules/` → a beginner must be able to see how a score is computed.
