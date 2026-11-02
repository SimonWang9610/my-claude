import datetime as dt
import os
import tempfile
import unittest
from unittest import mock

import common
import macro
from tests import fx


class ParseTests(unittest.TestCase):
    def test_treasury_latest_10yr(self):
        self.assertEqual(macro.parse_treasury(fx.text("treasury_snippet.html")), (5.21, "2026-10-13"))

    def test_treasury_skips_na_rows_and_missing_column(self):
        page = ('<table><thead><tr><th>Date</th><th>10 Yr</th></tr></thead><tbody>'
                '<tr><td><time datetime="2026-10-12T12:00:00Z">10/12/2026</time></td><td>4.10</td></tr>'
                '<tr><td><time datetime="2026-10-13T12:00:00Z">10/13/2026</time></td><td>N/A</td></tr>'
                '</tbody></table>')
        self.assertEqual(macro.parse_treasury(page), (4.10, "2026-10-12"))
        with self.assertRaises(common.FetchError):
            macro.parse_treasury("<table><tr><th>Date</th><th>2 Yr</th></tr></table>")

    def test_fred_latest_non_missing(self):
        obj = {"observations": [{"date": "2026-10-10", "value": "4.21"}, {"date": "2026-10-13", "value": "."}]}
        self.assertEqual(macro.parse_fred(obj), (4.21, "2026-10-10"))
        with self.assertRaises(common.FetchError):
            macro.parse_fred({"observations": [{"date": "2026-10-13", "value": "."}]})


class BuildTests(unittest.TestCase):
    def ctx(self):
        return common.Ctx(tempfile.mkdtemp(), None, now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc))

    def test_treasury_fallback_without_key(self):
        ctx = self.ctx()
        with mock.patch.object(ctx, "get", return_value=(fx.text("treasury_snippet.html").encode(), "2026-10-14T00:00:00Z")):
            out = macro.build(ctx, env={})
        m = out["macro"]
        self.assertEqual((m["dgs10"], m["dgs10_date"], m["src"]), (5.21, "2026-10-13", "S1"))
        self.assertEqual((m["erp"], m["erp_date"], m["erp_src"]), (4.20, "2026-10-01", "S2"))
        self.assertEqual(out["sources"]["S1"]["class"], "primary")
        self.assertIn("adamodar", out["sources"]["S2"]["url"])

    def test_fred_used_when_key_set_and_key_not_leaked(self):
        ctx = self.ctx()
        obj = {"observations": [{"date": "2026-10-13", "value": "4.30"}]}
        with mock.patch.object(ctx, "get_json", return_value=(obj, "2026-10-14T00:00:00Z")) as g:
            out = macro.build(ctx, erp=4.5, erp_date="2026-10-14", env={"FRED_API_KEY": "SECRETKEY"})
        self.assertEqual(out["macro"]["dgs10"], 4.30)
        self.assertEqual(out["macro"]["erp"], 4.5)
        self.assertNotIn("SECRETKEY", str(out))
        self.assertNotIn("SECRETKEY", g.call_args[1]["key"])
        self.assertEqual(out["sources"]["S1"]["url"], "https://fred.stlouisfed.org/series/DGS10")

    def test_fred_key_comes_from_project_settings_not_os_environ(self):
        proj = tempfile.mkdtemp()
        os.makedirs(os.path.join(proj, "data"))
        with open(os.path.join(proj, "data", "config.json"), "w") as f:
            f.write('{"fred_api_key": "ENVFILEKEY"}')
        ctx = common.Ctx(tempfile.mkdtemp(), None, now=lambda: dt.datetime(2026, 10, 14, tzinfo=dt.timezone.utc),
                         project=proj, env={})
        obj = {"observations": [{"date": "2026-10-13", "value": "4.30"}]}
        with mock.patch.object(ctx, "get_json", return_value=(obj, "2026-10-14T00:00:00Z")) as g:
            out = macro.build(ctx)
        self.assertEqual(out["macro"]["dgs10"], 4.30)
        self.assertIn("ENVFILEKEY", g.call_args[0][0])        # used in the request ...
        self.assertNotIn("ENVFILEKEY", g.call_args[1]["key"])  # ... but never in the cache key
        self.assertNotIn("ENVFILEKEY", str(out))


if __name__ == "__main__":
    unittest.main()
