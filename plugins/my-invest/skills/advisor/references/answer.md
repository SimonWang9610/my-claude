# The answer — a short brief: answer, summary, why, risks, record, what to watch, not verified, sources

`report.py --chat` prints the brief from the scorecard, the facts, the research files and the narrative;
the advisor pastes it as the answer. Everything else the scripts and the analyst produced goes to
`reports/dossier.md` (and `dossier.html`), the file an agent reads for a later question; the brief never
repeats it. Rules the brief obeys:

- **Direct answer first**, then the figures it rests on, then why, then the risks. Section order never changes.
- **Every horizon is dated**: "5 years from today (to Oct 2031)", "Expected by Oct 2031", "by 2027-01-12".
  A horizon is counted from the price date printed under the headline, never from a past year.
- **Every figure ends with a marker** such as `[S3]`; the **Sources** section lists each marker with a link
  to its raw source (the SEC API call, the filing, the Yahoo page). A script's arithmetic (`S60`, `S61`)
  links to the file it was computed into and is followed by the raw sources it used. On the page the
  markers themselves are links.
- **Sections are tagged** *computed by scripts* or *the analyst's reading*.
- **Short**: under about a hundred lines for one stock; four bullets for why, three for risks, three to
  watch, three gaps plus a count; a wanted detail section is a table of at most five rows.
- Plain words; a term from the standard appears only with its gloss in **Words used here**, which lists
  only the terms used (options terms only when an options section is present).

## Shape (one stock)

```markdown
## <TICKER> — <one plain sentence: the verdict, with the dated horizon and the return the risk demands>
*As of <price date>. Every horizon below is counted from that date.*

### Answer
- **If you hold it:** <recommendation> — because <expected return over the dated horizon vs required; trend>
- **If you want to buy:** <recommendation>
- **Limit-order levels the rule points to:** $x (50-day average) · $y (10% below today) · $z (200-day average)
- If it hits $p: <where that price sits>                      ← only for a what-if in the question
(a failed deal-breaker check → "Stay away, or sell what you hold"; no scorecard or inputs → "No verdict", never a default hold)

### Summary  (computed by scripts; horizons count from today, <date>)
| Price today (<date>) | $ |
| Expected by <month year> (<h> years from today) | worst $ · likely $ · best $ — about x% a year in the likely case |
| Return the risk demands | r% a year (10-year Treasury yield plus an equity risk premium) |
| Next few months | likely $lo–$hi by <date> (one standard deviation); trend; next event |
| Analysts' average 12-month target (secondary; only about 38% of such targets are met) | $t from n analysts |
| Confidence | n/100 (band) — what lowers it |
| Your shares | worth $, gain $ (accounts)                    ← only when holdings were stated

### Why  (the analyst's reading)             ≤ 4 bullets
### Risks: the case against                  ≤ 3 bullets
### Track record                             the simulated summary line; the last earlier call, with the price and SPY since
### What to watch                            ≤ 3 observable events with a date or price
### Not verified                             ≤ 3 gaps, then "and n more, listed in the dossier"
### Your shares · News, what it means · Compared with similar companies · Options on this stock, explained · Short-term view
                                             only as the question asks (request.wants) and only when data exists
### Words used here
### Sources                                  one line per marker used above, with its link
Files: [full dossier] · [page] · [chart]
> disclaimer
```

## A fund (ETF)

`facts/fund.json` instead of a scorecard (written by `fund.py`): the same shape with **What it is**, the
fund rule for a holder and a buyer (trend, cost, concentration — labelled this standard's own reading),
a summary of price, returns against SPY over the same windows, trend, yearly cost and biggest holdings,
what to watch, not verified, sources. Leveraged, inverse and covered-call funds carry a **Watch out** line.

## Several stocks (a portfolio or holdings question)

One answer, in this order, written by the advisor from each stock's brief:

1. **The answer in one table** — one row per position: stock, accounts, worth, gain, what to do if you
   hold it, limit-order level, expected return vs required at the dated horizon, confidence, link to the
   stock's page. Funds in the same table with the fund rule's words. Then three lines: sell / hold / keep
   buying, with the names.
2. **One short block per stock** — the headline sentence, the Answer bullets and the Summary table from
   its brief (nothing else; the full brief is on the stock's page).
3. **Not verified** across the portfolio, in a few lines; Sources with links; the disclaimer.

Everything else (news, peers, industry, options, strict value lens, scorecards, evidence logs) is in each
stock's folder for the next question.

## The dossier (`reports/dossier.md`, `reports/dossier.html`)

`report.py` renders the full detail for agents and for the curious: the short answer and price map, the
price outlook and strict value lens, the track record tables, the answer, thesis, why, the case against,
news, peers, industry, strengths and weaknesses, holdings, options context, the short-term lens, business
and moat, management, market trend, industry and related stocks, facts, scorecard, risk evidence, news and
posts, what could not be verified, open questions, history, the evidence log, the disclaimer. It lints
every output and fails on a violation. `INDEX.md` carries the latest decision, the track-record line,
the folder map and the history table.
