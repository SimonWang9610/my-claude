# Scout report — value-investing scoring frameworks (2026-10-14)

Legend: [U] = primary text not fetched; claim rests on secondary summaries and must be verified before scoring against it.

## 1. Business quality and moat
- Morningstar moat sources (intangible assets, switching costs, network effect, cost advantage, efficient scale). No formula; rating requires evidence of at least one source plus returns above WACC; narrow = excess returns likely for 10+ years. Inputs: 10-K business section, ROIC history. Fit: adapt as a cited-evidence checklist. Sources: https://www.morningstar.com/business/insights/blog/equity-economic-moat-ratings ; methodology PDF (Mar 2017) https://s21.q4cdn.com/198919461/files/doc_downloads/governance_documents/MorningstarEquityResearch_Methodology-%282%29.pdf
- ROIC minus WACC spread. NOPAT / operating invested capital; spread > 0. Inputs: EBIT, tax rate, debt, leases, equity, cash, WACC inputs. Fit: use. Source: Mauboussin and Callahan, "Measuring the Moat," Credit Suisse 2013, https://www.safalniveshak.com/wp-content/uploads/2014/03/Measuring-The-Moat-2013.pdf
- ROIIC (return on incremental invested capital) = change in NOPAT / change in invested capital over the same window; ROIIC > WACC (derived). Closest published concept to "reinvestment runway" (that phrase was not found). Fit: use. Source: Mauboussin and Callahan, "Competitive Advantage Period," Consilient Observer [U], https://www.morganstanley.com/im/it-it/institutional-investor/insights/series/consilient-observer.html
- Gross profitability = (Revenue minus COGS) / total assets; ranking only. Fit: use as ranked factor. Source: Novy-Marx, JFE 108(1) 2013, DOI 10.1016/j.jfineco.2013.01.003; NBER WP 15940 https://www.nber.org/system/files/working_papers/w15940/w15940.pdf
- Fisher's 15 points. No formula; scuttlebutt inputs. Fit: avoid as scored items; usable only when each point has a cited document [U]. Summary https://foragerfunds.com/?p=83471

## 2. Financial strength
- Piotroski F-score: 1 point each for ROA>0; CFO>0; change in ROA>0; CFO>NI; change in LTD/assets<0; change in current ratio>0; no equity issuance; change in gross margin>0; change in asset turnover>0. 8 to 9 high, 0 to 1 low. Inputs: two years of statements plus share count. Fit: use. Source: Piotroski, JAR 38 Supplement, 2000 [U]
- Altman Z (public manufacturers): 1.2 WC/TA + 1.4 RE/TA + 3.3 EBIT/TA + 0.6 MVE/TL + 1.0 Sales/TA; >2.99 safe, <1.81 distress. Fit: manufacturers only. Source: Altman, Journal of Finance 1968 [U]; zones via https://arxiv.org/pdf/1109.1087
- Altman Z'' (non-manufacturers): 6.56 X1 + 3.26 X2 + 6.72 X3 + 1.05 X4 (X1 WC/TA, X2 RE/TA, X3 EBIT/TA, X4 book equity/total liabilities); 2.60 safe, 1.10 distress (secondary; some sources add 3.25 constant). Fit: use with primary check [U]. https://en.wikipedia.org/wiki/Altman_Z-score
- Graham defensive tests: current ratio >= 2; LTD <= net current assets; no loss in last 10 years; EPS growth >= 33% over 10 years (secondary). Fit: floor for defensive mode. Source: Graham, The Intelligent Investor ch. 14 [U]; secondary https://blog.validea.com/the-graham-strategy-value-and-safety-make-for-big-returns/
- Mohanram G-score: eight binary tests for growth firms; 6 to 8 long. Fit: adapt only for low book-to-market growth names. Source: Mohanram, RAS 10(2) 2005, https://ideas.repec.org/a/spr/reaccs/v10y2005i2d10.1007_s11142-005-1526-4.html

## 3. Management and capital allocation
- Buffett retained-earnings test: each retained dollar should create at least one dollar of market value; secondary adaptation = change in market value / sum of (EPS minus DPS) over 5 to 10 years, threshold >= 1.0. Use the 2010 five-year revision if scored [U]. 1986 letter (fetched) has the argument, not the test: https://www.berkshirehathaway.com/letters/1986.html
- Thorndike, The Outsiders (2012): five uses of cash judged per share; compare per-share growth to total growth over CEO tenure. Fit: adapt as per-share growth check [U]
- Shareholder yield = dividend yield + net buyback yield + net debt paydown yield (Faber 2013 [U]); AAII uses dividend plus buyback. Fit: use, ranked. https://www.aaii.com/journal/article/12915-shareholder-yield-works-on-wall-street-as-a-value-measure
- Dilution test: change in diluted shares over 3 to 5 years <= 0 (Piotroski's no-issuance signal). Fit: use.
- Insider open-market purchases (Form 4 code P): buying is informative, selling is not. Fit: score purchases only, never sales. Source: Lakonishok and Lee, RFS 14(1) 2001, https://ideas.repec.org/a/oup/rfinst/v14y2001i1p79-111.html

## 4. Valuation and margin of safety
- Graham margin of safety: price <= intrinsic value times (1 minus MoS); investor-set buffer. Fit: the gate. Source: Graham, Security Analysis (1934), The Intelligent Investor [U]
- Graham number = sqrt(22.5 x EPS x BVPS); with P/E <= 15 and P/B <= 1.5 (secondary). Fit: sanity cap only; breaks for asset-light or loss-making firms [U]
- Owner earnings = reported earnings + D&A + other non-cash charges minus average maintenance capex minus working capital needed for unit volume; yield on market cap or EV. Maintenance/growth capex split is an estimate. Fit: use only when the filing discloses the split, else flag as estimated. Source: Buffett, Berkshire 1986 letter (fetched), https://www.berkshirehathaway.com/letters/1986.html
- Greenblatt Magic Formula: EY = EBIT/EV; ROC = EBIT/(net fixed assets + NWC); sum of ranks; excludes financials and utilities. Fit: relative rank within a universe only. Source: Greenblatt 2005 [U]
- Reverse DCF: solve for the growth (or discount rate) the price implies; compare implied g to sustainable growth = reinvestment rate x ROIC (derived). Fit: use. Source: Damodaran, Stern valuation session 5 slides, 2015, https://pages.stern.nyu.edu/~adamodar/podcasts/valfall15/valsession5.pdf

## 5. Risks and red flags
- Beneish M-score = -4.84 + 0.920 DSRI + 0.528 GMI + 0.404 AQI + 0.892 SGI + 0.115 DEPI - 0.172 SGAI + 4.679 TATA - 0.327 LVGI; flag if M > -1.78 (secondary; one source uses -2.22; TATA coefficient also reported as 4.697). Exclude financials. Fit: gate. Source: Beneish, FAJ 1999 [U]; https://en.wikipedia.org/wiki/Beneish_M-score
- Sloan accrual ratio = (NI minus CFO) / average total assets; top-decile flag (convention). Fit: flag. Source: Sloan, TAR 71(3) 1996 [U]
- Sharpe ratio. Fit: avoid; volatility is not permanent loss. Sharpe, JPM 1994 [U]
- Pabrai, The Dhandho Investor (2007): bear-case value floor framing, not a score [U]. https://valuevultures.substack.com/p/the-dhandho-investor-the-low-risk
- Not verified or searched: Spier checklist (2014), Gray and Carlisle Quantitative Value (2012), Montier C-score, Dechow et al. misstatement F-score (2011). Include only after fetching primary text.

## Prior art on weighting
- Piotroski 2000 and Mohanram 2005: equal-weight sums of binary tests.
- Greenblatt 2005: equal-weight sum of two ranks.
- Novy-Marx 2013: single factor, no weights.
- AQR Quality minus Junk (Asness, Frazzini, Pedersen, RAS 2019; SSRN 2312432, 2013): profitability, growth, safety as z-scores combined; exact sub-weights [U]. https://papers.ssrn.com/abstract=2312432
- Morningstar Quantitative Equity Ratings (Dec 2024): valuation, uncertainty-based margin of safety, momentum, market cap; no weights disclosed. https://s21.q4cdn.com/198919461/files/doc_downloads/2024/11/Quantative-Equity-Research-Effective-2-Dec-2024.pdf
- Implication: no source publishes validated stock-level weights for a value investor; equal-weight binary tests and hard gates are the most-cited default. Prefer gates to weights.

## Red-flag gates that override any score
- Altman distress zone: Z < 1.81 (manufacturers) or Z'' < 1.10 (non-manufacturers) [U]
- Beneish M > -1.78 (threshold conflict noted) [U]
- Net share issuance year over year (Piotroski signal) [U]
- Negative owner earnings for multiple years (Buffett 1986; year count derived)
- ROIC below WACC across the full history (Mauboussin 2013; threshold derived)
- Any loss in the last 10 years for a defensive profile (Graham) [U]
- Accrual ratio in top decile (Sloan 1996) [U]
- Insider selling is NOT a gate (Lakonishok and Lee 2001)

## Pitfalls
- Piotroski, Altman, Beneish, Sloan, Graham and Mohanram were not fetched in primary form; pin every [U] threshold before scoring.
- Beneish cutoff (-1.78 vs -2.22) and TATA coefficient (4.679 vs 4.697) conflict across sources; resolve from the FAJ article.
- Altman, Beneish and Piotroski were calibrated on US samples from the 1960s to 1990s; exclude financials, REITs and utilities or use separate models.
- Owner-earnings maintenance capex is management's estimate; without a disclosed split an LLM will invent one.
- "Reinvestment runway" is not a published term; use ROIIC / competitive advantage period and say so.

## Recommendation
Pillars 2 and 5 from mechanical filing-based tests (Piotroski 9, Altman Z and Z'', Beneish M, accruals) with primary-verified thresholds; pillar 4 from Graham number, owner-earnings yield and reverse DCF; moat sources, Fisher, Thorndike and Pabrai as evidence-required items scored "unverifiable" without a cited passage. Changes if full 10-K and 10-Q statements cannot be fetched, which would leave Piotroski and Beneish without inputs.
