# The note — slots the analyst and the advisor write, read by `report.py`

Two files share this shape: the analyst's note, `history/<date>-<HHMM>-analyst.md`, written for a
professional (the standard's terms allowed, every judgment tied to an item id or a cited passage), and
the advisor's narrative, `history/<date>-<HHMM>.md`, the same slots in plain words for a beginner. Every
figure carries the marker it has in its source file; `report.py --narrative <file>` renders the chat
answer and the dossier from the newest narrative and lints it with `--facts`, so the file carries no
Evidence log of its own. Slot names are `##` headings and must match exactly.

```markdown
## Question
`<the question, verbatim, in inline code so its figures need no marker>` · lens: long | short | both

## Outlook
- <the longest-horizon expectation in one sentence, with the two or three inputs that drive it and their markers>
- <the months-ahead range and trend in one sentence>
- <the strict value line and the calibration line>

## Why
- ≤ 5 bullets: pillar results, market trend, dated news — the evidence for the verdict

## Case against
- ≤ 4 bullets: the strongest reasons the verdict could be wrong — a pillar or item that scored 0, a
  multiple outside its range, a risk factor, a bear scenario input, a peer doing better — each with its
  marker or item id; weighed on merit, not softened

## News, what it means
- <date> — <what happened> [S] — <good / bad / neutral: one plain clause>

## Compared with peers
<one or two sentences on what stands out in compare.py's table, with markers>

## Industry
- ≤ 4 bullets from research/industry.md with markers

## Strengths
- …

## Weaknesses
- …

## Thesis
- **<horizon 1>** — …
- **<horizon n>** — …
- **What would break it** — ≤ 3 observable events with a date or price, each naming the gate or item it would flip

## Not verified
- one line per gap the scripts cannot see: a page or domain refused (URL, status), a filing section
  missing from the extracts, a figure two sources disagree on (both cited, which one was used), a
  judgment made on thin text — each with its marker where a figure is involved

## Answer
<the five rows of "The short answer" as plain sentences, each with its marker, plus the one-sentence
headline; with holdings, the "at $x" line. Scenario outputs named as such. In the analyst's note, a
closing "Confidence and gaps" paragraph: the confidence figure, what lowers it, what was not verified.>
```

Markers for scorecard figures: zones, fair value by horizon, valuation parameters and the simulated
record cite the metrics derived row (`S60`); implied CAGR, action cells, recommendation, score, tier and
confidence cite the score derived row (`S61`); past calls cite the history row (`S62`); the price cites
`price_src`; holdings figures cite the `S9x` rows; research facts cite their `S100+` rows.
