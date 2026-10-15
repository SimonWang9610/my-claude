import datetime as dt
import tempfile
import unittest
from unittest import mock

import common
import edgar
from tests import fx
from tests.fx import fact, facts_doc

Y = ("2024-10-01", "2025-09-30")  # a full fiscal year (start, end)
BS = [fact("2025-09-30", 100)]  # Assets anchor so the period exists


def rows_of(**concepts):
    doc = facts_doc(Assets=BS, **concepts)
    rows, cmap, missing = edgar.normalize(doc)
    return rows, cmap, missing


class RealFixtureTests(unittest.TestCase):
    def setUp(self):
        self.rows, self.cmap, self.missing = edgar.normalize(fx.load("companyfacts_aapl.json"))

    def test_three_fiscal_years_newest_first(self):
        self.assertEqual([r["fy"] for r in self.rows], [2025, 2024, 2023])
        self.assertEqual(self.rows[0]["period_end"], "2025-09-27")
        self.assertEqual(self.rows[0]["accn"], "0000320193-25-000079")
        self.assertEqual(self.rows[0]["filed"], "2025-10-31")

    def test_values_match_filing(self):
        r = self.rows[0]
        self.assertEqual((r["revenue"], r["ocf"], r["net_income"]), (416161000000, 111482000000, 112010000000))
        self.assertEqual(r["gross_profit"], r["revenue"] - r["cogs"])
        self.assertEqual(r["src"], "S1")

    def test_outflows_positive_and_debt_buckets(self):
        r = self.rows[0]
        for k in ("capex", "dividends_paid", "buybacks", "debt_repaid"):
            self.assertGreater(r[k], 0, k)
        self.assertEqual(r["st_debt"], 20329000000)  # CP + current LT debt included
        self.assertEqual(r["lt_debt"], 78328000000)

    def test_missing_lists_every_null(self):
        nulls = {(k, r["fy"]) for r in self.rows for k, v in r.items() if v is None}
        listed = {(m["field"], m["fy"]) for m in self.missing}
        self.assertEqual(nulls, listed)
        self.assertTrue(all(m["reason"] for m in self.missing))

    def test_concept_map_lists_concepts_used(self):
        self.assertEqual(self.cmap["revenue"], ["RevenueFromContractWithCustomerExcludingAssessedTax"])
        self.assertEqual(self.cmap["da"], ["DepreciationDepletionAndAmortization"])


class RuleTests(unittest.TestCase):
    def test_dedupe_by_period_keeps_latest_filed(self):
        rows, _, _ = rows_of(Revenues=[
            fact("2025-09-30", 900, start=Y[0], filed="2025-11-01", accn="a"),
            fact("2025-09-30", 950, start=Y[0], filed="2026-11-01", accn="b"),  # restated later
            fact("2025-09-30", 800, start=Y[0], filed="2024-01-01", accn="c")])
        self.assertEqual(rows[0]["revenue"], 950)

    def test_share_counts_as_originally_reported(self):
        rows, _, _ = rows_of(
            Revenues=[fact("2025-09-30", 900, start=Y[0], filed="2025-11-01", accn="a"),
                      fact("2025-09-30", 950, start=Y[0], filed="2026-11-01", accn="b")],
            WeightedAverageNumberOfDilutedSharesOutstanding=("shares", [
                fact("2025-09-30", 100, start=Y[0], filed="2025-11-01", accn="a"),
                fact("2025-09-30", 400, start=Y[0], filed="2026-11-01", accn="b")]),  # restated for a 4:1 split
            EarningsPerShareDiluted=("USD/shares", [
                fact("2025-09-30", 8.0, start=Y[0], filed="2025-11-01", accn="a"),
                fact("2025-09-30", 2.0, start=Y[0], filed="2026-11-01", accn="b")]))
        r = rows[0]
        self.assertEqual((r["shares_diluted"], r["eps_diluted"], r["revenue"]), (100, 8.0, 950))

    def test_full_year_duration_only(self):
        rows, _, missing = rows_of(Revenues=[
            fact("2025-09-30", 250, start="2025-07-01"),   # Q4 stub tagged fp=FY in a 10-K
            fact("2025-09-30", 700, start="2024-10-01")])
        self.assertEqual(rows[0]["revenue"], 700)
        rows, _, missing = rows_of(Revenues=[fact("2025-09-30", 250, start="2025-07-01")])
        self.assertIsNone(rows[0]["revenue"])
        self.assertIn("full-year", [m for m in missing if m["field"] == "revenue"][0]["reason"])

    def test_52_53_week_year_accepted(self):
        rows, _, _ = rows_of(Revenues=[fact("2025-09-30", 5, start="2024-10-02")])  # 363 days
        self.assertEqual(rows[0]["revenue"], 5)

    def test_only_10k_fy_facts(self):
        rows, _, _ = rows_of(Revenues=[
            fact("2025-09-30", 1, start=Y[0], form="10-Q", fp="Q3"),
            fact("2025-09-30", 2, start=Y[0], fp="Q4"),
            fact("2025-09-30", 3, start=Y[0], form="10-K/A"),
            fact("2025-09-30", 4, start=Y[0])])
        self.assertEqual(rows[0]["revenue"], 4)

    def test_outflows_stored_positive(self):
        rows, _, _ = rows_of(
            PaymentsToAcquirePropertyPlantAndEquipment=[fact("2025-09-30", -50, start=Y[0])],
            PaymentsOfDividends=[fact("2025-09-30", 20, start=Y[0])],
            PaymentsForRepurchaseOfCommonStock=[fact("2025-09-30", -30, start=Y[0])],
            RepaymentsOfLongTermDebt=[fact("2025-09-30", -10, start=Y[0])])
        r = rows[0]
        self.assertEqual((r["capex"], r["dividends_paid"], r["buybacks"], r["debt_repaid"]), (50, 20, 30, 10))

    def test_concept_fallback_per_period(self):
        old = [fact("2024-09-30", 10, start="2023-10-01", fy=2024, accn="o")]
        new = [fact("2025-09-30", 20, start=Y[0])]
        doc = facts_doc(Assets=[fact("2025-09-30", 1), fact("2024-09-30", 1, fy=2024, accn="o")],
                        SalesRevenueNet=old, RevenueFromContractWithCustomerExcludingAssessedTax=new)
        rows, cmap, _ = edgar.normalize(doc)
        self.assertEqual([r["revenue"] for r in rows], [20, 10])
        self.assertEqual(cmap["revenue"], ["RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"])

    def test_first_listed_concept_wins(self):
        rows, _, _ = rows_of(Revenues=[fact("2025-09-30", 1, start=Y[0])],
                             SalesRevenueNet=[fact("2025-09-30", 2, start=Y[0])])
        self.assertEqual(rows[0]["revenue"], 1)

    def test_gross_profit_fallback_and_da_fallback(self):
        rows, _, _ = rows_of(Revenues=[fact("2025-09-30", 100, start=Y[0])],
                             CostOfRevenue=[fact("2025-09-30", 60, start=Y[0])],
                             DepreciationAndAmortization=[fact("2025-09-30", 7, start=Y[0])])
        self.assertEqual((rows[0]["gross_profit"], rows[0]["da"]), (40, 7))
        rows, _, _ = rows_of(GrossProfit=[fact("2025-09-30", 33, start=Y[0])],
                             Revenues=[fact("2025-09-30", 100, start=Y[0])],
                             CostOfRevenue=[fact("2025-09-30", 60, start=Y[0])])
        self.assertEqual(rows[0]["gross_profit"], 33)

    def test_composite_sga_only_when_aggregate_absent(self):
        parts = dict(SellingAndMarketingExpense=[fact("2025-09-30", 26, start=Y[0])],
                     GeneralAndAdministrativeExpense=[fact("2025-09-30", 8, start=Y[0])])
        rows, cmap, _ = rows_of(**parts)
        self.assertEqual(rows[0]["sga"], 34)
        self.assertEqual(cmap["sga"], ["sum: SellingAndMarketingExpense + GeneralAndAdministrativeExpense"])
        rows, cmap, _ = rows_of(SellingGeneralAndAdministrativeExpense=[fact("2025-09-30", 50, start=Y[0])], **parts)
        self.assertEqual(rows[0]["sga"], 50)
        self.assertEqual(cmap["sga"], ["SellingGeneralAndAdministrativeExpense"])
        rows, _, missing = rows_of(SellingAndMarketingExpense=parts["SellingAndMarketingExpense"])  # one half is not enough
        self.assertIsNone(rows[0]["sga"])
        self.assertIn("sga", [m["field"] for m in missing])

    def test_da_candidate_order_ends_with_plain_depreciation(self):
        rows, cmap, _ = rows_of(Depreciation=[fact("2025-09-30", 34, start=Y[0])])
        self.assertEqual((rows[0]["da"], cmap["da"]), (34, ["Depreciation"]))
        rows, _, _ = rows_of(Depreciation=[fact("2025-09-30", 34, start=Y[0])],
                             DepreciationAmortizationAndOther=[fact("2025-09-30", 40, start=Y[0])])
        self.assertEqual(rows[0]["da"], 40)

    def test_st_debt_includes_current_long_term_debt(self):
        rows, _, _ = rows_of(CommercialPaper=[fact("2025-09-30", 5)], LongTermDebtCurrent=[fact("2025-09-30", 7)])
        self.assertEqual(rows[0]["st_debt"], 12)

    def test_instant_facts_reject_durations(self):
        rows, _, _ = rows_of(AssetsCurrent=[fact("2025-09-30", 9, start=Y[0])])
        self.assertIsNone(rows[0]["current_assets"])

    def test_total_liabilities_derived_when_untagged(self):
        rows, _, _ = rows_of(LiabilitiesAndStockholdersEquity=[fact("2025-09-30", 100)],
                             StockholdersEquity=[fact("2025-09-30", 40)])
        self.assertEqual(rows[0]["total_liabilities"], 60)

    def test_missing_entries_and_reasons(self):
        rows, _, missing = rows_of(Revenues=[fact("2025-09-30", 1, start=Y[0])])
        m = {(x["field"], x["fy"]): x["reason"] for x in missing}
        self.assertEqual(m[("buybacks", 2025)], "no us-gaap concept matched")
        self.assertNotIn(("revenue", 2025), m)
        self.assertIsNone(rows[0]["buybacks"])
        self.assertEqual(set(missing[0]), {"field", "fy", "reason"})

    def test_max_ten_rows_newest_first(self):
        assets, ni = [], []
        for i in range(12):
            y = 2014 + i
            assets.append(fact("%d-09-30" % y, 1, fy=y, accn="a%d" % i))
        rows, _, _ = edgar.normalize(facts_doc(Assets=assets))
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0]["fy"], 2025)

    def test_no_10k_data_raises(self):
        with self.assertRaises(common.FetchError):
            edgar.normalize(facts_doc(Assets=[fact("2025-09-30", 1, form="10-Q", fp="Q3")]))


class SectorTests(unittest.TestCase):
    def test_mapping(self):
        cases = {"3571": "manufacturer", "2000": "manufacturer", "3999": "manufacturer", "7372": "non-manufacturer",
                 "6021": "financial", "6000": "financial", "6799": "financial", "6798": "reit",
                 "4911": "utility", "4900": "utility", "4999": "utility", "1000": "non-manufacturer",
                 "4000": "non-manufacturer", "": "non-manufacturer", None: "non-manufacturer"}
        for sic, want in cases.items():
            self.assertEqual(edgar.sector_class(sic), want, sic)


class ResolveTests(unittest.TestCase):
    def test_resolve_cik_and_share_class_ticker(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c")
        with mock.patch.object(ctx, "get_json", return_value=(fx.load("company_tickers_subset.json"), "t")):
            self.assertEqual(edgar.resolve_cik(ctx, "aapl")[0], 320193)
            self.assertEqual(edgar.resolve_cik(ctx, "BRK.B")[1].upper()[:6], "BERKSH")
            with self.assertRaises(common.FetchError):
                edgar.resolve_cik(ctx, "NOPE")

    def test_build_end_to_end_with_mocked_http(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c", now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))
        docs = {"company_tickers.json": fx.load("company_tickers_subset.json"),
                "submissions": fx.load("submissions_aapl.json"), "companyfacts": fx.load("companyfacts_aapl.json")}

        def get_json(url, source, **kw):
            key = "company_tickers.json" if url.endswith("company_tickers.json") else \
                ("submissions" if "submissions" in url else "companyfacts")
            return docs[key], "2026-10-14T00:00:00Z"

        with mock.patch.object(ctx, "get_json", side_effect=get_json):
            out = edgar.build(ctx, "AAPL")
        self.assertEqual((out["cik"], out["sector_class"], out["sic"]), ("0000320193", "manufacturer", "3571"))
        self.assertEqual(set(out["sources"]), {"S1", "S2"})
        self.assertEqual(out["sources"]["S1"]["as_of"], "FY2025")
        self.assertEqual(out["shares_history"][0], {"fy": 2025, "period_end": "2025-09-27",
                                                    "shares_diluted": 15004697000, "src": "S1"})
        self.assertEqual(out["fundamentals"]["annual"][0]["src"], "S1")


class IncrementalTests(unittest.TestCase):
    SUB = fx.load("submissions_aapl.json")

    def built(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c", now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))
        docs = {"company_tickers.json": fx.load("company_tickers_subset.json"),
                "submissions": self.SUB, "companyfacts": fx.load("companyfacts_aapl.json")}

        def get_json(url, source, **kw):
            key = "company_tickers.json" if url.endswith("company_tickers.json") else \
                ("submissions" if "submissions" in url else "companyfacts")
            return docs[key], "2026-10-14T00:00:00Z"

        with mock.patch.object(ctx, "get_json", side_effect=get_json):
            return ctx, edgar.build(ctx, "AAPL")

    def test_latest_periodic_ignores_other_forms(self):
        self.assertEqual(edgar.latest_periodic(self.SUB), "2026-07-31")      # newest filing is a Form 4 on 2026-10-08
        self.assertEqual(edgar.latest_periodic({}), "")

    def test_needs_fundamentals(self):
        self.assertTrue(edgar.needs_fundamentals(self.SUB, "2025-10-31"))
        self.assertFalse(edgar.needs_fundamentals(self.SUB, "2025-10-31", seen="2026-07-31"))
        self.assertFalse(edgar.needs_fundamentals(self.SUB, "2026-08-01"))

    def test_reuse_matches_build_without_companyfacts(self):
        ctx, built = self.built()
        prev = {k: built[k] for k in ("ticker", "cik", "name", "sic", "sector_class", "sources")}
        prev["fundamentals"] = dict(built["fundamentals"], shares_history=built["shares_history"])
        self.assertTrue(edgar.reusable(prev))
        out = edgar.reuse(ctx, prev, self.SUB, "2026-10-14T05:00:00Z")
        for k in ("ticker", "cik", "name", "sic", "sector_class", "fundamentals", "shares_history"):
            self.assertEqual(out[k], built[k], k)
        self.assertEqual(out["sources"]["S1"], built["sources"]["S1"])           # companyfacts row kept as fetched
        self.assertEqual(out["sources"]["S2"]["retrieved"], "2026-10-14")
        self.assertNotIn("shares_history", out["fundamentals"])

    def test_build_accepts_a_shared_submissions_fetch(self):
        ctx = common.Ctx(tempfile.mkdtemp(), "ua a@b.c")
        urls = []

        def get_json(url, source, **kw):
            urls.append(url)
            return (fx.load("company_tickers_subset.json") if url.endswith("company_tickers.json")
                    else fx.load("companyfacts_aapl.json")), "t"

        with mock.patch.object(ctx, "get_json", side_effect=get_json):
            edgar.build(ctx, "AAPL", sub=(self.SUB, "t"))
        self.assertFalse([u for u in urls if "submissions" in u])

    def test_reusable_rejects_unusable_previous_facts(self):
        for prev in ({}, {"cik": "1", "fundamentals": {"annual": []}},
                     {"cik": "1", "fundamentals": {"annual": [{}]}, "sources": {"S1": {"what": "prices"}}}):
            self.assertFalse(edgar.reusable(prev))


if __name__ == "__main__":
    unittest.main()
