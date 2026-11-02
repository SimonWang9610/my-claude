# Pillar 3 — Management and capital allocation (20 points, 5 items; 3.5 is n/a until insiders are collected)

**3.1 Retained earnings create value.** Test: (market cap today − market cap five years ago) ÷
Σ(net income − dividends paid) over the same five years ≥ 1.0. Inputs
`metrics.retained_earnings_test`. Source: Buffett, 1984 letter, "Dividend Policy" (VERIFIED): "for every
dollar retained … at least one dollar of market value"; "a five-year rolling average". Why: management
that retains cash must show the owner got at least a dollar back per dollar kept. Not this: a company
that retained nothing (denominator ≤ 0 → `n/a`); a five-year window ending in a market-wide drawdown
(score as computed, note it).

**3.2 No dilution.** Test: split-adjusted diluted shares today ≤ diluted shares five years ago.
Inputs `metrics.dilution_5y`. Source: arithmetic; Piotroski (2000) EQ_OFFER for the single-year form.
Why: each new share is a claim on the same owner earnings. Not this: a stock split (adjusted); shares
issued for an acquisition that raised owner earnings per share (still 0 on the test; note it).

**3.3 Cash returned to owners.** Test: shareholder yield = (dividends + buybacks + net debt
repayment) ÷ market cap > 0. Inputs `metrics.shareholder_yield`. Source: Faber, Shareholder Yield
(2013) (UNVERIFIED book); AAII summary URL in research notes. Why: cash that reached the owner is the
one earnings figure accounting cannot restate. Not this: buybacks funded by net new debt (the debt term
nets them out — report the components).

**3.4 No admitted overpayment.** Test: no goodwill impairment charge in the last five fiscal years.
Inputs `metrics.goodwill_impairment_5y`. Source: arithmetic on the XBRL `GoodwillImpairmentLoss`
concept. Why: an impairment is management's own statement that an acquisition cost more than it was
worth. Not this: an impairment taken by a new CEO on a predecessor's deal — still 0, name the CEO
change in the note.

**3.5 Insider buying.** Test: at least one open-market purchase (Form 4 transaction code P) by an
officer or director in the last twelve months. Inputs `insiders`. Source: Lakonishok and Lee (2001),
RFS 14(1): purchases are informative, "insider selling appears to have no predictive ability"
(abstract VERIFIED). `n/a` while `insiders` is null by design. Why: a purchase with the insider's own
money is a signal; sales are noise and never score. Not this: option exercises, 10b5-1 sales, grants.
