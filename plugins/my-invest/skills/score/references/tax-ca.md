# Canadian tax rules for holdings — federal, general information

Read by `holdings.py` (rows by `id`; the `rule` cell is the treatment line, the `url` its citation) and by the
analyze skill for the Holdings section. Federal rules only; every row was fetched on the date shown. A row
that could not be confirmed on a primary page says `UNVERIFIED`.

**Disclaimer (carried into every Holdings section).** General information, not tax advice: provinces add
their own rates and credits, the user's marginal rate is an input the user states, and after-tax figures
are estimates.

**Capital-gains inclusion status (as of 2026-10-14).** One-half. The 2024 proposal (two-thirds above
$250,000 for individuals, deferred to 2026-01-01) was cancelled on 2025-03-21 (`T-CANCEL`), and the 2026
federal tax-expenditure report states that Budget 2025 confirmed the government would not proceed
(`T-CANCEL2`). Section 38(a) of the Act, current to 2026-09-21, still reads one-half (`T-INCL`).

## Rules

| id | rule | url | retrieved | quote (≤15 words, verbatim) |
|---|---|---|---|---|
| T-INCL | Taxable capital gain is one-half of the capital gain (inclusion rate 50%) for individuals. | https://laws-lois.justice.gc.ca/eng/acts/I-3.3/section-38.html | 2026-10-14 | "½ of the taxpayer's capital gain for the year" |
| T-CANCEL | The 2024 two-thirds inclusion-rate increase was cancelled before taking effect. | https://www.pm.gc.ca/en/news/news-releases/2025/03/21/prime-minister-mark-carney-cancels-proposed-capital-gains-tax-increase | 2026-10-14 | "the Government of Canada will cancel the proposed hike in the capital gains inclusion rate" |
| T-CANCEL2 | Finance confirms Budget 2025 did not proceed with the inclusion-rate changes. | https://www.canada.ca/en/department-finance/services/publications/federal-tax-expenditures/2026/part-2.html | 2026-10-14 | "The government confirmed in Budget 2025 that it would not proceed with these changes." |
| T-GAIN | Non-registered: capital gain = proceeds of disposition − adjusted cost base − outlays and expenses of selling; 50% of it is taxable at the marginal rate. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12700-capital-gains/calculating-reporting-your-capital-gains-losses.html | 2026-10-14 | "To calculate your capital gain or loss, subtract the total of your property's ACB" |
| T-SUPER | Superficial loss: a loss is denied when you or an affiliated person buy identical property 30 days before or after the sale and still hold it 30 days after; it is added to the new ACB. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12700-capital-gains/capital-losses-deductions.html | 2026-10-14 | "during the period starting 30 calendar days before the sale" |
| T-FDIV | Non-registered: US dividends are foreign income, reported gross in CAD with no dividend tax credit; the US tax withheld is claimed as a foreign tax credit. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12100-interest-other-investment-income.html | 2026-10-14 | "Foreign dividends do not qualify for the dividend tax credit." |
| T-FTC | The federal foreign tax credit covers foreign tax paid on income reported on the Canadian return. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/deductions-credits-expenses/line-40500-federal-foreign-tax-credit.html | 2026-10-14 | "You were a resident of Canada at any time in the year" |
| T-TREATY | US withholding on portfolio dividends to a Canadian resident is capped at 15% (treaty Art. X(2)(b)). | https://www.canada.ca/en/department-finance/programs/tax-policy/tax-treaties/country/united-states-america-convention-consolidated-1980-1983-1984-1995-1997-2007.html | 2026-10-14 | "15 per cent of the gross amount of the dividends in all other cases" |
| T-TFSA | TFSA: interest, dividends and capital gains are tax-free, including on withdrawal; a sale inside the account has no Canadian tax. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/what.html | 2026-10-14 | "any income you earn through interest, dividends or capital gains are generally tax-free" |
| T-TFSA-WHT | TFSA: the 15% US dividend withholding is a cost; foreign tax on TFSA investments is excluded from the foreign tax credit (Folio S5-F2-C1 ¶1.69). | https://www.canada.ca/en/revenue-agency/services/tax/technical-information/income-tax/income-tax-folios-index/series-5-international-residency/folio-2-foreign-tax-credits-deductions/income-tax-folio-s5-f2-c1-foreign-tax-credit.html | 2026-10-14 | "any foreign taxes paid on foreign income earned on qualifying investments" |
| T-TFSA-ROOM | TFSA room: 2026 dollar limit $7,000, unused room carries forward, withdrawals restore room next 1 January; excess taxed 1% per month. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/contributing/overcontribute.html | 2026-10-14 | "taxable at 1% per month for as long as it remains in your account" |
| T-RRSP | RRSP (also RRIF, LIRA): no tax on gains or income inside the plan; a withdrawal is taxed as ordinary income at the marginal rate. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans/making-withdrawals.html | 2026-10-14 | "Any income you earn in the RRSP is usually exempt from tax." |
| T-RRSP-WHT | RRSP lump-sum withdrawal withholding outside Quebec: 10% up to $5,000, 20% to $15,000, 30% above; the final tax is set on the return. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/rrsps-related-plans/making-withdrawals/tax-rates-on-withdrawals.html | 2026-10-14 | "include the withdrawal on your income tax and benefit return for that year" |
| T-RRSP-US | RRSP: US dividends are exempt from US withholding under treaty Art. XXI(2) (IRS letter ruling PLR-142074-07, 2008; the broker needs the account documented as an RRSP). | https://www.irs.gov/pub/irs-wd/0810013.pdf | 2026-10-14 | "dividends and interest derived by an RRSP will be exempt from U.S. income tax" |
| T-FX | Foreign currency: ACB converts at the rate on the purchase date and proceeds at the rate on the sale date, so USD/CAD moves create gains or losses (ITA s.261(2)(b), Bank of Canada rate). | https://www.canada.ca/en/revenue-agency/services/forms-publications/publications/t4037/capital-gains.html | 2026-10-14 | "the exchange rate in effect at the time the property was acquired" |
| T-FX-LAW | The Act converts each amount at the Bank of Canada rate for the day it arose (relevant spot rate). | https://laws-lois.justice.gc.ca/eng/acts/I-3.3/section-261.html | 2026-10-14 | "the particular amount is to be converted to an amount expressed in Canadian currency" |
| T-FX-AVG | Income (dividends, interest) may use an average rate over the period in some cases; capital transactions use the day's rate. | https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/about-your-tax-return/tax-return/completing-a-tax-return/personal-income/line-12100-interest-other-investment-income.html | 2026-10-14 | "an average of exchange rates over the relevant period of time may be used" |
| T-BOC | Daily USD/CAD rate: Bank of Canada Valet series FXUSDCAD (Canadian dollars per US dollar). | https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json | 2026-10-14 | "Daily average exchange rate of the US dollar in Canadian dollars." |

## Limits of what was verified

- FHSA is treated as TFSA (holdings.md); FHSA withdrawals that are not qualifying are taxable — not modelled.
- TFSA US withholding: the CRA folio confirms no Canadian credit; that the US does not exempt a TFSA under
  Art. XXI is UNVERIFIED on an IRS page (no ruling found), stated here as the general practice.
- RRSP treaty exemption rests on an IRS private letter ruling, which binds only its requester; the treaty
  text (T-TREATY url, Art. XXI(2)) states the pension-trust exemption, and its application to RRSPs per the
  ruling is consistent but is not a published IRS position for all plans.
- LIRA and RRIF are treated as RRSP; RRIF minimum-withdrawal rules and LIRA unlocking are not modelled.
- Province rates, the Quebec withholding table, and the alternative minimum tax are out of scope.
