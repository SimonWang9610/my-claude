"""score.py against the AAPL facts.json the human scorecard scored 63/100 (e2e run 2026-10-14)."""
import contextlib
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import score  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def fixture(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as fh:
        return json.load(fh)


def make_store(root, facts=None, evidence=True, holdings=None):
    d = os.path.join(root, "AAPL")
    os.makedirs(os.path.join(d, "facts"), exist_ok=True)
    os.makedirs(os.path.join(d, "research"), exist_ok=True)
    with open(os.path.join(d, "facts", "facts.json"), "w", encoding="utf-8") as fh:
        json.dump(facts or fixture("score_aapl_facts.json"), fh)
    if evidence:
        shutil.copy(os.path.join(FIX, "score_evidence.json"), os.path.join(d, "research", "evidence.json"))
    if holdings:
        with open(os.path.join(d, "facts", "holdings.json"), "w", encoding="utf-8") as fh:
            json.dump(holdings, fh)
    return d


def run(d, *args):
    with contextlib.redirect_stdout(io.StringIO()):
        score.main([d] + list(args))
    with open(os.path.join(d, "facts", "scorecard.json"), encoding="utf-8") as fh:
        return json.load(fh)


def with_momentum(facts):
    m = fixture("score_momentum.json")
    for k in ("momentum", "market", "options"):
        facts[k] = m[k]
    facts["sources"].update(m["sources"])
    return facts


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)


class ReproduceAAPL(Base):
    def test_matches_human_scorecard(self):
        sc = run(make_store(self.tmp))
        self.assertEqual(sc["score"], 63)
        self.assertEqual(sc["tier"], "research deeper")
        self.assertEqual(sc["stance"], "sell zone")
        self.assertEqual({p: x["points"] for p, x in sc["pillars"].items()},
                         {"1": 20.0, "2": 12.0, "3": 15.0, "4": 0.0, "5": 16.0})
        st = {i: x["status"] for i, x in sc["items"].items()}
        self.assertEqual(sorted(i for i, s in st.items() if s == "n/a"), ["1.2", "3.5"])
        self.assertEqual(sorted(i for i, s in st.items() if s == "no evidence"), ["3.4", "5.5"])
        zeros = sorted(i for i, x in sc["items"].items() if x["status"] == "scored" and x["score"] == 0)
        self.assertEqual(zeros, ["2.3", "2.4", "4.1", "4.2", "4.3", "4.4", "4.5"])
        self.assertTrue(all(x["result"] == "pass" for x in sc["gates"].values()))
        c = sc["confidence"]
        self.assertEqual((c["value"], c["covered"], c["applicable"], c["coverage"]), (78, 28, 30, 0.9333))
        self.assertEqual(sc["pillars"]["2"]["unverified_items"], ["2.2"])
        self.assertEqual(sc["derived_src"], "S60")
        self.assertEqual(sc["score_src"], "S61")
        self.assertEqual(sc["sources"]["S60"]["class"], "derived")
        self.assertTrue(sc["sources"]["S61"]["url"].startswith("file://"))
        self.assertEqual(sc["items"]["1.5"]["markers"], ["S100"])
        self.assertEqual({q["id"] for q in sc["open_questions"]},
                         {"G1", "G2", "2.3", "2.4", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "5.5"})
        self.assertEqual(sc["gates"]["G1"]["note"], "filings index covers 2023-11-02 to 2026-09-01; no Item 1.03 "
                         "found; coverage shorter than three years")

    def test_time_triggers(self):
        facts = with_momentum(fixture("score_aapl_facts.json"))
        trig = {t["name"]: t["date"] for t in run(make_store(self.tmp, facts))["action"]["time_triggers"]}
        self.assertEqual(trig, {"next 10-K": "2026-10-31", "next earnings": "2026-10-29"})


class ScreenMode(Base):
    def test_evidence_items_pending_and_excluded(self):
        sc = run(make_store(self.tmp, evidence=False), "--mode", "screen")
        for i in ("1.5", "5.4", "5.5"):
            self.assertEqual(sc["items"][i]["status"], "pending")
        self.assertEqual(sc["gates"]["G4"]["result"], "pending")
        self.assertEqual(sc["pillars"]["1"]["applicable"], 4)
        self.assertEqual(sc["pillars"]["5"]["applicable"], 3)
        self.assertEqual(sc["pillars"]["5"]["points"], 20.0)  # 5.1-5.3 all pass
        self.assertEqual(sc["confidence"]["applicable"], 26)

    def test_full_mode_without_evidence_is_no_evidence(self):
        sc = run(make_store(self.tmp, evidence=False))
        self.assertEqual(sc["items"]["1.5"]["status"], "no evidence")
        self.assertEqual(sc["gates"]["G4"]["result"], "no evidence")


class GatesAndStance(Base):
    def test_failed_gate_forces_pass_and_avoid(self):
        f = fixture("score_aapl_facts.json")
        f["metrics"]["gate_inputs"]["owner_earnings_negative_years_5y_full_capex"] = 3
        sc = run(make_store(self.tmp, f), "--holding")
        self.assertEqual(sc["gates"]["G5"]["result"], "fail")
        self.assertEqual((sc["tier"], sc["stance"]), ("pass", "avoid"))
        self.assertEqual(sc["action"]["cells"], {"not_holding": "avoid", "holding": "exit"})

    def test_filings_window_decides_gate_coverage(self):
        for complete, short in ((True, False), (False, True)):
            f = fixture("score_aapl_facts.json")
            f["filings_window"] = {"from": "2023-10-15", "to": "2026-10-14", "complete": complete}
            sc = run(make_store(os.path.join(self.tmp, str(complete)), f))
            self.assertEqual(sc["gates"]["G1"].get("coverage_short", short), short)
            self.assertEqual("coverage shorter than three years" in sc["gates"]["G1"]["note"], short)

    def test_holding_vs_not_holding_cells(self):
        d = make_store(self.tmp)
        self.assertEqual(run(d)["action"]["cell"], "avoid")
        self.assertEqual(run(d, "--holding")["action"]["cell"], "trim or sell")
        hold = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 10, "avg_cost": 150.0}]}
        sc = run(make_store(os.path.join(self.tmp, "h"), holdings=hold))
        self.assertTrue(sc["action"]["holding"])
        self.assertEqual(sc["action"]["holdings"][0]["gain"], round(10 * (343.8700866699219 - 150.0), 2))

    def test_bands(self):
        cases = {90.0: ("buy zone", "accumulate", "add"), 120.0: ("hold", "wait for the buy zone", "hold"),
                 160.0: ("hold", "avoid at this price", "hold, do not add")}
        for price, (stance, nh, hd) in cases.items():
            f = fixture("score_aapl_facts.json")
            f["price"]["last"] = price
            sc = run(make_store(os.path.join(self.tmp, str(price)), f))
            self.assertEqual((sc["stance"], sc["action"]["cells"]["not_holding"], sc["action"]["cells"]["holding"]),
                             (stance, nh, hd))

    def test_mos_rebases_buy_zone(self):
        sc = run(make_store(self.tmp), "--mos", "0.5")
        self.assertEqual(sc["zones"]["buy_below"], round(148.53 * 0.5, 2))
        self.assertEqual(sc["margin_of_safety"], 0.5)


class ImpliedCagr(Base):
    def test_arithmetic_and_verdict(self):
        sc = run(make_store(self.tmp))
        p = 343.8700866699219
        self.assertEqual(sc["implied_cagr"]["1"]["base"], round(155.04 / p - 1, 4))
        self.assertEqual(sc["implied_cagr"]["10"]["bull"], round((245.58 / p) ** 0.1 - 1, 4))
        self.assertEqual([r["verdict"] for r in sc["action"]["rows"]], ["unattractive"] * 4)
        f = fixture("score_aapl_facts.json")
        f["price"]["last"] = 90.0  # 10-yr base (201.27/90)^0.1 - 1 = 8.38% -> within 9.41% +/- 2 pp
        rows = run(make_store(os.path.join(self.tmp, "x"), f))["action"]["rows"]
        self.assertEqual(rows[3]["verdict"], "fair")
        self.assertEqual(rows[0]["verdict"], "attractive")


class ShortTerm(Base):
    def st(self, facts, lens="short"):
        return run(make_store(os.path.join(self.tmp, str(id(facts))), facts), "--lens", lens)["short_term"]

    def test_trend_up(self):
        st = self.st(with_momentum(fixture("score_aapl_facts.json")))
        self.assertEqual(st["items"]["ST1"]["result"], "trend up")
        self.assertEqual(st["items"]["ST2"]["result"], "positive")
        self.assertEqual(st["items"]["ST3"]["result"], "near high")
        self.assertEqual(st["items"]["ST4"]["result"], "normal")
        self.assertEqual(st["stance"], "trend up")
        self.assertIn("A failed gate overrides this lens", st["caveat"])

    def test_trend_down_and_no_trend(self):
        f = with_momentum(fixture("score_aapl_facts.json"))
        f["momentum"].update(ma50=360.0, ma200=380.0, return_12m_skip_1m=-0.1, return_6m=-0.05)
        self.assertEqual(self.st(f)["stance"], "trend down")
        f = with_momentum(fixture("score_aapl_facts.json"))
        f["momentum"].update(ma50=342.0, ma200=340.0)  # inside the 1% band
        st = self.st(f)
        self.assertEqual((st["items"]["ST1"]["result"], st["stance"]), ("no trend", "no trend"))

    def test_null_with_reason(self):
        sc = run(make_store(self.tmp))
        self.assertIsNone(sc["short_term"])
        self.assertEqual(sc["short_term_reason"], "lens long")
        sc = run(make_store(self.tmp), "--lens", "both")
        self.assertEqual(sc["short_term_reason"], "facts.momentum absent")



def contracts(price, buy=103.97, sell=175.77):
    def c(anchor, kind, strike, mid):
        return {"anchor": anchor, "type": kind, "strike": strike, "expiry": "2026-11-20", "days": 37, "bid": mid - 0.1,
                "ask": mid + 0.1, "mid": mid, "last": mid, "oi": 1000, "iv": 0.3}
    return [c("price", "call", round(price), 9.0), c("price", "put", round(price), 8.0),
            c("buy_zone", "put", 100.0, 1.5), c("sell_zone", "call", 175.0, 4.0),
            c("down_10", "put", round(price * 0.9), 3.0), c("up_10", "call", round(price * 1.1), 2.5)]


def with_contracts(price=None, chain=True):
    f = with_momentum(fixture("score_aapl_facts.json"))
    if price is not None:
        f["price"]["last"] = price
    f["options"]["contracts"] = contracts(f["price"]["last"]) if chain else None
    return f


class OptionsOps(Base):
    """action.options per options-playbook.md: O1-O4 conditions and the not-now line."""
    HOLD = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 120.0, "avg_cost": 150.0}]}

    def ops(self, name, facts, holdings=None, *args):
        sc = run(make_store(os.path.join(self.tmp, name), facts, holdings=holdings), *args)
        return sc["action"]["options"]

    def test_o1_covered_call_and_o2_put_for_a_large_gain_above_the_sell_zone(self):
        ops = self.ops("o1", with_contracts(), self.HOLD)
        self.assertEqual([o["op"][:2] for o in ops], ["O1", "O2"])
        o1 = ops[0]
        self.assertEqual(o1["contract"]["strike"], round(343.8700866699219 * 1.1))   # sell zone below price -> up_10
        self.assertTrue(o1["pay_or_receive"].startswith("receive ≈ $2.50/sh (0.7% of the price, 7.2% a year)"))
        self.assertEqual(o1["markers"], ["S9", sc_row(self)])
        self.assertEqual(ops[1]["contract"]["type"], "put")

    def test_o2_only_when_a_gate_failed(self):
        f = with_contracts()
        f["metrics"]["gate_inputs"]["owner_earnings_negative_years_5y_full_capex"] = 3
        ops = self.ops("o2", f, self.HOLD)
        self.assertEqual([o["op"][:2] for o in ops], ["O2"])
        self.assertIn("deal-breaker check failed", ops[0]["fits_because"])

    def test_o3_cash_secured_put_waiting_for_the_buy_zone(self):
        ops = self.ops("o3", with_contracts(120.0))
        self.assertEqual([o["op"][:2] for o in ops], ["O3"])
        self.assertEqual((ops[0]["contract"]["type"], ops[0]["contract"]["strike"]), ("put", 100.0))
        self.assertLessEqual(ops[0]["contract"]["strike"], 103.97)

    def test_o4_long_call_in_the_buy_zone(self):
        ops = self.ops("o4", with_contracts(90.0))
        self.assertEqual([o["op"][:2] for o in ops], ["O4"])
        self.assertEqual((ops[0]["contract"]["type"], ops[0]["contract"]["strike"]), ("call", 90))

    def test_not_now(self):
        ops = self.ops("nn", with_contracts())
        self.assertEqual([o["op"] for o in ops], ["not now"])
        self.assertIn("you hold none", ops[0]["fits_because"])
        small = {"ticker": "AAPL", "positions": [{"account": "TFSA", "shares": 10, "avg_cost": 150.0}]}
        self.assertIn("each contract covers 100", self.ops("small", with_contracts(), small)[0]["fits_because"])
        ops = self.ops("none", with_contracts(chain=False), self.HOLD)
        self.assertEqual((ops[0]["op"], ops[0]["fits_because"]), ("not now", "no contracts available"))
        self.assertEqual(self.ops("bare", None, self.HOLD)[0]["fits_because"], "no contracts available")


class Horizons(Base):
    """Horizons come from metrics.valuation.by_horizon; request.json sets lens and holding."""

    def facts_with(self, keys):
        f = fixture("score_aapl_facts.json")
        bh = f["metrics"]["valuation"]["by_horizon"]
        f["metrics"]["valuation"]["by_horizon"] = {k: bh["5"] for k in keys}
        return f

    def test_three_year_only(self):
        sc = run(make_store(self.tmp, self.facts_with(["3"])))
        self.assertEqual([(r["horizon"], r["label"]) for r in sc["action"]["rows"]], [(3, "3 years")])
        self.assertEqual(list(sc["implied_cagr"]), ["3"])
        v = sc["fair_value"]["3"]["base"]
        self.assertAlmostEqual(sc["implied_cagr"]["3"]["base"], round((v / 343.8700866699219) ** (1 / 3) - 1, 4))

    def test_fractional_horizon(self):
        sc = run(make_store(self.tmp, self.facts_with(["0.25", "1"])))
        self.assertEqual([(r["horizon"], r["label"]) for r in sc["action"]["rows"]], [(0.25, "3 months"), (1, "1 year")])
        v = sc["fair_value"]["0.25"]["base"]
        self.assertAlmostEqual(sc["implied_cagr"]["0.25"]["base"], round((v / 343.8700866699219) ** 4 - 1, 4))
        self.assertEqual(score.horizon_label(2.5), "2.5 years")

    def test_request_sets_lens_and_holding(self):
        d = make_store(self.tmp, with_momentum(fixture("score_aapl_facts.json")))
        with open(os.path.join(d, "request.json"), "w", encoding="utf-8") as fh:
            json.dump({"lens": "short", "holdings_text": "120 shares at $150 in my TFSA"}, fh)
        sc = run(d)
        self.assertEqual((sc["lens"], sc["action"]["holding"], sc["action"]["cell"]), ("short", True, "trim or sell"))
        self.assertIsNotNone(sc["short_term"])
        self.assertEqual(run(d, "--lens", "long")["lens"], "long")              # the flag wins


def with_outlook(base_cagr=0.036, trend="up", consensus=True, facts=None):
    """score_aapl_facts + momentum + the outlook block; trend set through the 50/200-day averages."""
    f = facts or with_momentum(fixture("score_aapl_facts.json"))
    blk = fixture("outlook_block.json")
    f["metrics"].update(blk["metrics"])
    if consensus:
        f["consensus"] = blk["consensus"]
    f["metrics"]["outlook"]["horizons"]["5"]["base"]["cagr"] = base_cagr
    f["metrics"]["outlook"]["horizons"]["5"].pop("verdict", None)
    f["momentum"]["ma50"], f["momentum"]["ma200"] = {"up": (330.0, 300.0), "down": (380.0, 400.0),
                                                      "none": (340.0, 343.0)}[trend]
    return f


class Recommendation(Base):
    """action.recommendation per outlook.md §5, one assertion per table row."""
    ROWS = [  # (holding, base cagr, trend, cell); r_base 9.41%: above >= 11.41%, below < 7.41%
        (True, 0.14, "down", "hold; add on pullbacks to the 50-day average"),
        (True, 0.09, "up", "hold; re-check at the next event"),
        (True, 0.09, "none", "hold; re-check at the next event"),
        (True, 0.09, "down", "hold, consider trimming to target weight"),
        (True, 0.03, "up", "trim into strength; trailing trigger at the 50-day average"),
        (True, 0.03, "down", "trim or sell"),
        (True, 0.03, "none", "trim or sell"),
        (False, 0.14, "up", "accumulate (staged entries)"),
        (False, 0.14, "none", "accumulate (staged entries)"),
        (False, 0.14, "down", "wait for the trend to turn; first entry at the 200-day average"),
        (False, 0.09, "down", "buy only on pullbacks: 50-day average, or 10% below today"),
        (False, 0.03, "up", "wait; the strict value and the pullback levels are the entry map"),
    ]

    def test_each_table_row(self):
        for k, (held, cagr, trend, cell) in enumerate(self.ROWS):
            sc = run(make_store(os.path.join(self.tmp, str(k)), with_outlook(cagr, trend)), *(["--holding"] if held else []))
            rec = sc["action"]["recommendation"]
            self.assertEqual((rec["cell"], rec["trend"], rec["basis"]), (cell, trend, "outlook"), (held, cagr, trend))
            self.assertEqual(rec["horizon"], "5")

    def test_gate_failed_and_levels(self):
        f = with_outlook(0.14, "up")
        f["metrics"]["gate_inputs"]["owner_earnings_negative_years_5y_full_capex"] = 3
        rec = run(make_store(self.tmp, f), "--holding")["action"]["recommendation"]
        self.assertEqual((rec["holding"], rec["not_holding"], rec["cell"]), ("exit", "avoid", "exit"))
        rec = run(make_store(os.path.join(self.tmp, "l"), with_outlook()))["action"]["recommendation"]
        self.assertEqual(rec["levels"], {"ma50": 330.0, "ma200": 300.0, "pullback_10pct": round(343.8700866699219 * 0.9, 2),
                                         "strict_value": 148.53, "consensus_mean": 352.4})

    def test_outlook_copied_with_verdicts_and_confidence_spread(self):
        sc = run(make_store(self.tmp, with_outlook(0.036)))
        o = sc["outlook"]
        self.assertEqual((o["longest"], o["horizons"]["5"]["verdict"], o["horizons"]["5"]["label"]),
                         ("5", "expensive", "5 years"))
        self.assertEqual(o["spread"], round(0.0907 - (-0.0196), 4))
        c = sc["confidence"]
        term = max(0.0, min(1.0, 1 - o["spread"] / 0.20))
        self.assertEqual(c["value"], score.round_half_up(100 * (0.4 * c["coverage"] + 0.2 * c["agreement"] + 0.2 * term
                                                                + 0.2 * c["freshness"])))
        self.assertEqual(c["weights"]["outlook_spread"], 0.2)

    def test_reference_horizon(self):
        f = with_outlook(0.036)
        f["metrics"]["outlook"]["horizons"]["10"] = {"bear": {"price": 240.0, "cagr": -0.035},
                                                     "base": {"price": 600.0, "cagr": 0.14},
                                                     "bull": {"price": 900.0, "cagr": 0.101}}
        sc = run(make_store(os.path.join(self.tmp, "d"), copy.deepcopy(f)))
        self.assertEqual((sc["outlook"]["longest"], sc["outlook"]["reference"]), ("10", "5"))   # no request: 5 years
        self.assertEqual(sc["action"]["recommendation"]["horizon"], "5")
        d = make_store(os.path.join(self.tmp, "q"), copy.deepcopy(f))
        with open(os.path.join(d, "request.json"), "w", encoding="utf-8") as fh:
            json.dump({"horizon_source": "question", "horizons_years": [10]}, fh)
        rec = run(d)["action"]["recommendation"]
        self.assertEqual((rec["horizon"], rec["band"], rec["cell"]), ("10", "above", "accumulate (staged entries)"))

    def test_fallback_without_outlook(self):
        sc = run(make_store(self.tmp), "--holding")
        rec = sc["action"]["recommendation"]
        self.assertEqual((rec["basis"], rec["cell"]), ("strict value", "trim or sell"))
        self.assertIn("metrics.outlook absent", rec["note"])
        self.assertIsNone(sc["outlook"])
        self.assertEqual(sc["confidence"]["weights"], {"coverage": 0.5, "agreement": 0.3, "freshness": 0.2})


def sc_row(test):
    with open(os.path.join(test.tmp, "o1", "AAPL", "facts", "scorecard.json"), encoding="utf-8") as fh:
        return json.load(fh)["score_src"]

if __name__ == "__main__":
    unittest.main()
