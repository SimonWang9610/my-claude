# Report — the chat answer, the dossier and the narrative slots

## Chat answer — written for a beginner (produced by `report.py --chat`, pasted by the skill)

Plain words first, numbers in tables, technical detail below a divider. No term from the standard
appears above the divider without its gloss. Section order is fixed; sections the question did not ask
for are dropped from the chat, never from the page.

```markdown
## <TICKER> — <one plain sentence that answers the question: e.g. "expensive on fundamentals, strong trend; expect roughly 3% to 7% a year over five years, below the 9% the risk demands">

### The short answer
| Question | Answer |
|---|---|
| Where is the price likely to go? | <the user's horizon, or 5 years when none was stated>: $<bear> to $<bull> (base $<base>), about <x>% a year expected vs <r>% required — <attractive / fair / expensive> |
| Next few months? | likely range $<lo>–$<hi> by <date> (one standard deviation); trend <up/down/none>; next event <date> |
| Should I sell? | <recommendation cell for a holder, with its reason in one clause> |
| Should I buy? | <recommendation cell for a non-holder, with the entry levels> |
| How confident is the analyst? | <n>/100 — <what lowers it> |

### Price map
`strict value $<v> ◄── pullback $<p50> ── today $<price> ── consensus target $<t> ──► bull <h>-yr $<bull>`
<one line: "A strict value investor would pay $<v>; the model's record on this stock: <calibration line>">

### What the analyst expects, and why
| Horizon | Bear | Base | Bull | Expected yearly return (base) | Verdict |
|---|---|---|---|---|---|
| <h1> | $ | $ | $ | x% | fair |
| <h2> | $ | $ | $ | x% | expensive |
| Analyst consensus (n analysts, secondary) | $<low> | $<mean> | $<high> | — | — |
- Growth assumed: base <g>% a year (half the company's 5-year record of <x>%, half analysts' <y>%) [S]
- Multiple assumed: today's <P/E> drifting to the 10-year median <m> (range <lo>–<hi>) [S]
- Cash returned: <y>% a year in dividends and buybacks [S]
- The market's own assumption: today's price implies <g>% growth for ten years [S]

### Why, in plain words
- <≤ 5 bullets; each a plain sentence with its marker; jargon glossed inline, e.g. "the business earns far more than its capital costs (quality 20/20)">

### What the news says
| Date | What happened | What it means for this stock |
|---|---|---|
| <date> | <one plain sentence, cited> | <good / bad / neutral — one plain clause> |
<≤ 5 rows, newest first, from research.md News and posts; the meaning column is the narrative's judgment>

### Compared with similar companies
| | <TICKER> | <peer 1> | <peer 2> | <peer 3> |
|---|---|---|---|---|
| Sales growth (5 yr/yr) | | | | |
| Profit kept per $1 of sales (operating margin) | | | | |
| Return on the money invested (ROIC) | | | | |
| Cash the business makes, as % of price | | | | |
| Debt vs that cash (years to repay) | | | | |
| Price change, 12 months | | | | |
| Model stance | | | | |
<from compare.py over the peers named in research/industry.md; one line under the table saying what stands out, in plain words>

### How the industry is doing
- <≤ 4 bullets from research/industry.md: where this company sits in the chain, the sector ETF's 12-month return vs the market, the one or two drivers and risks that matter now, with markers>

### Your shares  (only when holdings were stated)
| Account | Shares | You paid | Worth now | Gain | Tax if sold now | You keep |
|---|---|---|---|---|---|---|
| TFSA | 120 | $150.00 | $41,155 | +$23,155 | $0 | $41,155 |
| Non-registered | 80 | $210.00 | $27,437 | +$10,637 | ≈ CAD 3,262 at 43% | ≈ CAD 35,871 |
<one line: "at $400: TFSA +$30,000; non-registered +$15,200, tax ≈ CAD 4,661">

### What could change the answer
- <≤ 3 bullets, each an observable event with a date or price, in plain words: an estimate revision, the next earnings, a multiple moving outside its range, a gate>

### Options, explained with your numbers
| Operation | When it fits | Contract | You pay / receive | Best case | Worst case |
|---|---|---|---|---|---|
| Covered call — get paid to agree to sell at $x | you hold shares and the model says trim or sell | sell 1 call per 100 sh, strike $x, expires <date> | receive ≈ $x/sh (x% of the price, x% a year) | shares sold at $x plus the premium | you miss gains above $x; a fall still hurts, minus the premium |
| <one row per operation whose condition holds, from options-playbook.md; otherwise one "Not now: …" line> |
- Options can lose the whole premium; selling a call caps your gain; shares can be called away early. This shows how the pieces work on this stock, not a recommendation.

### Short-term view  (only when the question is about weeks or months, or is unclear)
- <trend: up / down / none, in one plain sentence> · <implied move to <expiry>: ± $x> · <next event and date>
- Caution: short-term signals describe the recent past; they do not override the answer above.

### Words used here
- **fair value** — what the model thinks one share is worth today, from the cash the business makes
- **buy zone / sell zone** — cheap enough to buy / expensive enough to sell, by the model's own rule
- <one line for every other glossed term that appeared above, including the options terms>

Files: [page](reports/<date>.html) · [dossier](reports/dossier.md) · [chart](charts/<date>.html)
> disclaimer (verbatim)

---
## Details  (the page shows these as collapsed sections)
1. Strict value lens — owner-earnings fair value by horizon, buy and sell zones, implied growth, calibration
2. Action matrix — cells for holding and not holding, price and time triggers
3. Strengths / weaknesses — items with values and markers
4. Industry and peers — chain position and related tickers
5. Options context — implied volatility, implied move, put/call ratio, max pain, next earnings, the contracts considered
6. Short-term lens — the full table with base rates
7. Open questions — the three that matter most
```

Plain-word glosses the renderer uses (one line each, only when the term appears): fair value · buy zone /
sell zone · confidence · deal-breaker check (gate) · cash the business really makes (owner earnings) ·
yearly return the price implies (implied CAGR) · quality / strength / capital use / price / risk (the five
pillars) · trend (short-term lens).

## The narrative file — `history/<date>-<HHMM>.md`, written by the analyze skill before `report.py`; every figure carries a marker

```markdown
## Question
`<the user's question, verbatim, in inline code so its figures need no marker>` · lens: long | short | both

## Outlook
- <the longest-horizon expectation in one sentence, with the two or three inputs that drive it and their markers>
- <the months-ahead range and trend in one sentence>
- <the strict value line and the calibration line>

## Why (≤ 5 plain-word bullets: pillar results glossed, market trend, dated news)
- …

## News, what it means
- <date> — <what happened> [S] — <good / bad / neutral: one plain clause>

## Compared with peers
<one or two plain sentences on what stands out in compare.py's table, with markers>

## Industry
- <≤ 4 plain bullets from research/industry.md with markers>

## Strengths
- …

## Weaknesses
- …

## Thesis
- **1 year** — …
- **2 years** — …
- **5 years** — …
- **10 years** — …
- **What would break it** — ≤3 observable events tied to gate or item ids

## Answer
<the five rows of "The short answer" (where is the price going? next months? sell? buy? confidence?) as
plain sentences, each with its marker, plus the one-sentence headline; with holdings, the "at $x" line.
Scenario outputs named as such. No term without its gloss.>
```

Markers for scorecard figures: zones, fair value by horizon and valuation parameters cite the metrics
derived row; implied CAGR, action cells, score, tier, confidence cite the score derived row; the price
cites `price_src`; holdings figures cite the S9x rows. The lint resolves all of them with `--facts`, so
`narrative.md` carries no Evidence log of its own.

## dossier.md (rendered by `report.py`; parts inserted verbatim)

```markdown
# <Company name> (<TICKER>) — dossier
Updated <date> · CIK <n> · <sector class> · last price $<x> on <date> [S<n>]

## The short answer  ← the five-row table and price map; then "Model cells and triggers" (verdict line, zones, action cells, triggers)
## Price outlook     ← the horizon table and implied CAGR
## Answer            ← narrative.md Answer and Question
## Thesis            ← narrative.md Thesis
## Why               ← narrative Why
## What the news says ← narrative News, what it means
## Compared with similar companies ← facts/peers.json + narrative Compared with peers
## How the industry is doing ← narrative Industry
## Strengths and weaknesses
## Holdings          ← holdings.py tables (only when holdings.json exists)
## Options context   ← options block
## Short-term lens   ← only when computed
## Business and moat ← research.md section
## Management        ← research.md section
## Market trend      ← research.md section + market block
## Industry and related stocks ← research/industry.md (chain position, related tickers, drivers and risks)
## Facts             ← ten-year table, derived metrics, valuation block, gate inputs (from facts.json)
## Scorecard         ← scorecard-template.md shape from scorecard.json
## Risk evidence     ← research.md section
## News and posts    ← research.md section
## Open questions    ← merged: scorecard, facts nulls, research
## History           ← history.md lines, newest first
## Evidence log      ← S1–S99 from facts.json and scorecard.json, S100+ from research.md
> disclaimer (verbatim, last line)
```

`report.py` runs `lint.py` on the dossier and exits non-zero on a violation, printing the lines.

## INDEX.md (regenerated by `report.py` at the stock root)

Title line (name, ticker, CIK, sector class, sector ETF) · Industry line (chain position, related tickers)
· latest Decision block · folder map with links to every file in store.md · History table from
`history/log.md`, newest first · open-questions count · "Updated <datetime>".
