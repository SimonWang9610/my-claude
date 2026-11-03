"""size.py: sizing frames, look-through weight, order levels and the sell-from order, from the stated positions."""
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import lint  # noqa: E402
import score  # noqa: E402
import size  # noqa: E402

FIX = os.path.join(HERE, "fixtures")
HOLD = "RRSP: 37.0661 shares of AAPL at USD 203.07; TFSA: 13.0304 shares of AAPL at USD 213.28"


def quiet(fn, argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(argv)
    return buf.getvalue()


class Size(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.d = os.path.join(self.tmp, "stocks", "AAPL")
        for sub in ("facts", "research"):
            os.makedirs(os.path.join(self.d, sub))
        shutil.copy(os.path.join(FIX, "score_aapl_facts.json"), os.path.join(self.d, "facts", "facts.json"))
        shutil.copy(os.path.join(FIX, "score_evidence.json"), os.path.join(self.d, "research", "evidence.json"))
        quiet(score.main, [self.d])
        q = os.path.join(self.tmp, "stocks", "QQQ", "facts")
        os.makedirs(q)
        shutil.copy(os.path.join(FIX, "fund_qqq.json"), os.path.join(q, "fund.json"))
        self.price = json.load(open(os.path.join(self.d, "facts", "facts.json")))["price"]["last"]

    def run_size(self, *extra):
        return quiet(size.run, [self.d, "--question", HOLD] + list(extra))

    def test_frames_weights_levels_and_json(self):
        out = json.loads(self.run_size("--total", "95070", "--funds", "QQQ=8198,VGT=3648"))
        t = json.load(open(out["out"]))
        p = t["position"]
        self.assertAlmostEqual(p["shares"], 50.0965, places=3)
        self.assertAlmostEqual(p["cost_total"], 37.0661 * 203.07 + 13.0304 * 213.28, places=1)
        self.assertAlmostEqual(p["value"], 50.0965 * self.price, places=1)
        self.assertAlmostEqual(p["weight"], p["value"] / 95070, places=4)
        names = [f["frame"] for f in t["frames"]]
        self.assertEqual(names, ["cap at 15.0% of the portfolio", "cap at 12.5% of the portfolio",
                                 "cap at 10.0% of the portfolio", "sell the gain, keep your cost invested",
                                 "recover your cost, keep the gain as house money"])
        cap15 = t["frames"][0]
        self.assertEqual(cap15["sell_shares"], int((p["value"] - 0.15 * 95070) // self.price))
        self.assertLessEqual(cap15["weight_after"], 0.15 + self.price / 95070)      # whole shares: just above the cap
        gain = t["frames"][3]
        self.assertEqual(gain["sell_shares"], int(p["gain"] // self.price))
        self.assertAlmostEqual(gain["keep_value"], (p["shares"] - gain["sell_shares"]) * self.price, places=1)
        cost = t["frames"][4]
        self.assertGreaterEqual(cost["proceeds"], p["cost_total"])                     # rounded up: the cost comes back
        lt = t["look_through"]
        self.assertEqual([r["fund"] for r in lt["rows"]], ["QQQ"])
        self.assertAlmostEqual(lt["rows"][0]["value_through_fund"], 8198 * 0.074, places=1)
        self.assertAlmostEqual(lt["true_weight"], (p["value"] + 8198 * 0.074) / 95070, places=4)
        self.assertEqual(lt["missing"][0]["fund"], "VGT")
        self.assertIn("fund.json missing", lt["missing"][0]["reason"])
        lv = t["levels"]
        self.assertEqual(lv["price"], self.price)
        self.assertIsNotNone(lv["high_52w"])
        self.assertEqual(t["sell_from"]["order"], ["RRSP", "TFSA"])
        self.assertEqual([x["tax_rule"] for x in t["positions"]], ["T-RRSP", "T-TFSA"])
        self.assertEqual(set(t["sources"]), {"S98", "S99"})
        self.assertIn("size.py", t["sources"]["S98"]["what"])

    def test_md_lints_as_a_part_and_names_the_rules(self):
        md = self.run_size("--total", "95070", "--funds", "QQQ=8198", "--md")
        self.assertTrue(md.startswith("## AAPL — sizing a trim at $%s" % format(round(self.price, 2), ",.2f")))
        self.assertIn("| cap at 12.5% of the portfolio |", md)
        self.assertIn("| Also held through funds | QQQ 7.4% of the fund = $607 — true weight", md)
        self.assertIn("Sell from: RRSP then TFSA — taxable accounts last; RRSP before TFSA", md)
        self.assertIn("| 50-day average |", md)
        self.assertIn("| 52-week high / low |", md)
        self.assertIn("| The rule's cell for a holder |", md)
        path = os.path.join(self.tmp, "sizing.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(md)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = lint.main(["--part", "--facts", os.path.join(self.d, "facts", "facts.json"), path])
        self.assertEqual(rc, 0)

    def test_without_total_and_with_custom_caps_and_loss(self):
        t = json.load(open(json.loads(self.run_size("--caps", "20"))["out"]))
        self.assertIsNone(t["position"]["weight"])
        self.assertEqual(t["frames"][0]["sell_shares"], None)
        self.assertIn("--total missing", t["frames"][0]["reason"])
        self.assertEqual(t["caps"], [0.2])
        loss = quiet(size.run, [self.d, "--question", "TFSA: 10 shares of AAPL at USD 900", "--total", "50000"])
        t = json.load(open(json.loads(loss)["out"]))
        self.assertEqual(t["frames"][-1]["sell_shares"], None)
        self.assertIn("shows a loss", t["frames"][-1]["reason"])
        self.assertEqual(t["frames"][0]["sell_shares"], 0)                                 # 10 shares: under every cap
        self.assertEqual(t["frames"][0]["note"], "already under 15.0%")

    def test_errors_are_envelopes(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit):
            size.run_main("size.py", size.run, [self.d, "--question", "no position here", "--total", "1"])
        self.assertEqual(json.loads(buf.getvalue())["script"], "size.py")


if __name__ == "__main__":
    unittest.main()
