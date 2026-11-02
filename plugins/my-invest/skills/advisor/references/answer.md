# The answer — verdict, proof, detail, in that order every time

Rendered by `report.py --chat` from the scorecard, the facts, the research files and the narrative;
pasted by the advisor above the `Details` divider. The order never changes, so the reader learns where
to look: the verdict first, then the proof that it is not made up, then the detail the question asked
for. Each section opens with a tag — *computed by scripts* or *the analyst's reading* — so the reader
knows which lines are arithmetic and which are judgment. No term from the standard appears above the
divider without its one-line gloss; every figure keeps the marker of its source file.

## Shape of the chat answer

```markdown
## <TICKER> — <one plain sentence: the verdict, e.g. "expensive on fundamentals, rising trend; expect roughly 3% to 7% a year over five years, below the 9% the risk demands">

### The short answer                      ← the verdict
| Question | Answer |
| Where is the price likely to go? | <horizon>: $<bear> to $<bull> (base $<base>), <x>% a year expected vs <r>% required — attractive / fair / expensive |
| Next few months? | likely range $<lo>–$<hi> by <date> (one standard deviation); trend <up/down/none>; next event <date> |
| Should I sell? | <recommendation for a holder, reason in one clause> |
| Should I buy? | <recommendation for a non-holder, entry levels> |
| How confident is the analyst? | <n>/100 (<thin / mixed / solid / strong evidence>) — <what lowers it> |

### Price map
`strict value $v ◄── pullback $p ── today $price ── consensus $t ──► bull <h>-yr $bull`

### What the analyst expects, and why     ← proof 1: the scenarios and their inputs (computed by scripts)
| Horizon | Bear | Base | Bull | Expected yearly return (base) | Verdict |
| Analyst consensus (n, secondary) | low | mean | high | — | — |
- growth assumed · multiple assumed · cash returned · the growth today's price implies, each with its marker

### The case against                      ← proof 2 (the analyst's reading)
- ≤ 4 bullets: the strongest reasons the verdict could be wrong, each tied to a figure or a cited passage

### Why, in plain words                   ← the analyst's reading
- ≤ 5 bullets, jargon glossed inline

### Track record                          ← proof 3 (computed by scripts; simulated rows labelled so)
| Years ago | FY | Price then | Strict value then | Base case said | What happened | SPY same window |
<one line: mean error, how often the stock beat SPY, "simulated with today's method on then-available data">
What this advisor said before about <TICKER>: | Date | Said | Price then | Price now (change) | SPY same window |

### What the news says · Compared with similar companies · How the industry is doing · Your shares
<as the question asks; each table with its tag; "Your shares" only when holdings were stated>

### What could change the answer          ← proof 4
- ≤ 3 observable events with a date or price, each naming the item or gate it would flip

### What could not be verified            ← proof 5 (computed by scripts)
- every `no evidence` or pending item, null metric with its reason, stale figure, refused page

### Options, explained with your numbers · Short-term view
<as the question asks>

### Words used here
- one line per glossed term that appeared above

Files: [page] · [dossier] · [chart]
> disclaimer (verbatim)
---
## Details  (collapsed on the page: strict value lens · action matrix · strengths and weaknesses · industry and peers · options context · short-term lens · open questions)
```

## Rules the advisor applies when pasting

- `request.wants` decides which detail sections stay in the chat; the verdict, the price map and the five
  proof sections (expectations, case against, track record, what could change, could not be verified)
  always stay. The page keeps everything.
- A sell question leads with the short answer and the shares; a news question with the news table; a
  compare question with the peers table — the order above still holds, the lead section is just quoted
  first in one sentence.
- A wanted section with no data is one line saying so, never omitted silently.
- Assumptions forced by the question (`request.constraints`) are said where they matter ("I assumed five
  years because you said long term").
- Several stocks: one block each, then one comparison table from the scorecards.
- The last line is the disclaimer from the evidence skill; the page is published with the Artifact tool
  when available, else sent as a file.

## The dossier and INDEX.md

`report.py` renders `reports/dossier.md` (header · the short answer · price outlook · track record · answer
· thesis · why · the case against · news · peers · industry · strengths and weaknesses · holdings · options
· short-term lens · business and moat · management · market trend · industry and related stocks · facts ·
scorecard · risk evidence · news and posts · what could not be verified · open questions · history ·
evidence log · disclaimer), a dated snapshot, the HTML page (answer, charts, full dossier) and `INDEX.md`
(title line, industry line, the latest decision block with the track-record line, folder map, history
table). It lints every output and fails on a violation.
