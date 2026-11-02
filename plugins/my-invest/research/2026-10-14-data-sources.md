# Scout report — free data sources for US and HK (2026-10-14)

V = fetched directly on 2026-10-14. S = secondary source only.

## 1. Daily prices and dividends (10+ years, US and HK)
- yfinance 1.7.0 (PyPI 2026-08-26, V). `yf.Ticker("0700.HK").history(start=...)`. No key; unofficial Yahoo endpoints. Verdict: flaky but works today. Rate-limit and 401 "Invalid Crumb" issues recur (#2533 closed 2025-07-24; #2568, #2614 closed 2025-10-26). https://pypi.org/project/yfinance/ · https://github.com/ranaroussi/yfinance/issues
- Stooq CSV: keyless path dead since ~March 2026 (pandas-datareader #1012, S). Verdict: dead without key.
- Alpha Vantage: free key, 25 requests/day (V); US realtime premium-only. Verdict: fallback only. https://www.alphavantage.co/support/#api-key
- Tiingo: free token, 500 symbols/month, 50 req/hour, 1,000/day (V); HK coverage not stated. Verdict: adapt after an HK test. https://www.tiingo.com/about/pricing
- EODHD free: 20 calls/day, 1 year history (V). Verdict: avoid for 10 years. https://eodhd.com/pricing
- HKEX: no free historical price API; old page 404 (V); Data Marketplace is paid. Verdict: avoid.

## 2. Fundamentals
- SEC companyfacts `https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json`; frames `https://data.sec.gov/api/xbrl/frames/us-gaap/{Concept}/USD/CY2025.json`; companyconcept; submissions `https://data.sec.gov/submissions/CIK##########.json`. Keyless; max 10 req/s; declared User-Agent required (V). Verdict: works. https://www.sec.gov/os/accessing-edgar-data · https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Ticker to CIK: `https://www.sec.gov/files/company_tickers.json` (V).
- Concept map (memory, validate on a sample): revenue `Revenues` or `RevenueFromContractWithCustomerExcludingAssessedTax`; OCF `NetCashProvidedByUsedInOperatingActivities`; capex `PaymentsToAcquirePropertyPlantAndEquipment`; shares `dei:EntityCommonStockSharesOutstanding`; debt `LongTermDebtNoncurrent` + `LongTermDebtCurrent`; cash `CashAndCashEquivalentsAtCarryingValue`.
- HK filings: HKEXnews https://www.hkexnews.hk/ has title and content search only; no API, RSS or structured data (V-absence). No free structured HK financials API found. Verdict: link-out; annual report PDFs are the primary source.

## 3. Macro and rates
- FRED DGS10 `https://api.stlouisfed.org/fred/series/observations?series_id=DGS10&api_key=KEY&file_type=json`; free key; no rate limit stated (V). Verdict: works. https://fred.stlouisfed.org/docs/api/fred/series_observations.html
- Treasury daily par yield curve (keyless) https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026 ; 10 Yr column present (V); CSV export unverified. Verdict: fallback.

## 4. News with stable URLs and dates
- EDGAR 8-K current Atom `https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&type=8-K&dateb=&owner=include&count=40&output=atom` (V, entries dated 2026-10-14). Per-company `action=getcompany&CIK=...&type=8-K&output=atom` unverified. Verdict: works.
- EDGAR full-text search `https://efts.sec.gov/LATEST/search-index?q="phrase"&forms=8-K` returns JSON with file_date, capped at 10,000 (V). Verdict: works.
- Google News RSS `https://news.google.com/rss/search?q=...&hl=en-US&gl=US&ceid=US:en`: undocumented, 503s reported (S). Verdict: flaky extra; poll no more than every 15 to 30 minutes.
- Reddit `.json`: 403 without OAuth since late May 2026 (S; direct fetch failed, V). RSS ends 2026-11-13 (S). Verdict: dead for scripts.
- Seeking Alpha: Cloudflare blocks feed readers (S). Verdict: avoid for scripts.
- Substack `https://<pub>.substack.com/feed`: works per named newsletter; paid posts truncated (S). Verdict: adapt.

## 5. Analyst consensus
- Yahoo analysis via yfinance quoteSummary: needs cookie and crumb; flaky. 
- Finnhub recommendation trends: free key; free-plan access unconfirmed (S). Verdict: optional after endpoint test. https://finnhub.io/pricing
- Zacks: no free scriptable source. Verdict: avoid.

## Pitfalls
- yfinance is unofficial scraping: cache raw responses, back off, pin the version, never the sole source for consensus.
- SEC: throttle to about 5 req/s and send `AppName you@example.com` as User-Agent or get an "Undeclared Automated Tool" error. https://www.sec.gov/os/webmaster-faq
- HK tickers are 4-digit zero-padded `NNNN.HK`, priced in HKD; cross-market comparisons need FX, and no free FX source was verified.
- Store unadjusted closes and corporate actions separately; check yfinance auto_adjust default. companyfacts repeats facts once per filing: dedupe by period, keep latest `filed`.
- Reddit and Google News RSS are not build-on-able; posts need the host's web search, not scripts.

## Recommendation
Prices: yfinance behind a cache with backoff; Tiingo cross-check only after an HK test. Fundamentals: SEC companyfacts, frames, submissions with declared UA at ~5 req/s. Macro: FRED DGS10 (optional key) with Treasury table fallback. News: EDGAR 8-K Atom and full-text search; Google News RSS as flaky extra. Consensus: yfinance quoteSummary, Finnhub optional. Avoid Reddit, Seeking Alpha, Zacks, keyless Stooq. Changes if Yahoo's limits worsen (EODHD paid), if keyed Stooq is acceptable, or if Tiingo confirms HK and dividends free.
