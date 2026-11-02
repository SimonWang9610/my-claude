"""run.sh: project resolution, interpreter order and .venv self-provisioning (fake pythons, stub pip; no network)."""
import os
import stat
import subprocess
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = os.path.join(HERE, "run.sh")
SYSTEM_PATH = "/usr/bin:/bin"

# Acts as python3.12: version check passes, `-m venv DIR` copies itself to DIR/bin/python, `-m pip` logs to $PIPLOG.
FAKE = """#!/bin/sh
case "$1" in
  -c) exit 0;;
  --version) echo "Python 3.12.1"; exit 0;;
  -m) if [ "$2" = venv ]; then mkdir -p "$3/bin"; cp "$0" "$3/bin/python"; exit 0; fi
      if [ "$2" = pip ]; then echo "$@" >> "$PIPLOG"; exit 0; fi;;
esac
echo "TAG $@"
"""


def fake(path, body=None, tag="FAKE"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write((body or FAKE).replace("TAG", tag))
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR)
    return path


class RunShTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.proj = os.path.join(self.tmp, "p")
        self.mine = os.path.join(self.proj, "data")
        self.bin = os.path.join(self.tmp, "bin")
        os.makedirs(self.proj)
        self.piplog = os.path.join(self.tmp, "pip.log")
        self.env = {"PATH": SYSTEM_PATH, "HOME": self.tmp, "PIPLOG": self.piplog}

    def run_sh(self, script, *args, path=None, env=None, cwd=None):
        e = dict(self.env, PATH=path or SYSTEM_PATH, **(env or {}))
        r = subprocess.run(["bash", RUN, self.tmp, script, *args], capture_output=True, text=True, env=e,
                           cwd=cwd or self.tmp)
        return r.stdout.strip(), r.stderr.strip()

    def config(self, text):
        os.makedirs(self.mine, exist_ok=True)
        with open(os.path.join(self.mine, "config.json"), "w") as f:
            f.write(text)

    def test_config_python_wins_over_venv(self):
        fake(os.path.join(self.mine, ".venv", "bin", "python"), tag="VENV")
        cfg = fake(os.path.join(self.tmp, "cfgpy"), tag="CFG")
        self.config('{"sec_user_agent": "A a@b.c", "python": "%s"}' % cfg)
        out, _ = self.run_sh("edgar.py", "--project", self.proj)
        self.assertEqual(out, "CFG %s/edgar.py --project %s --data %s" % (HERE, self.proj, self.tmp))

    def test_existing_venv_used_for_any_script(self):
        fake(os.path.join(self.mine, ".venv", "bin", "python"), tag="VENV")
        for script in ("edgar.py", "facts.py"):
            out, err = self.run_sh(script, "--project=%s" % self.proj)
            self.assertTrue(out.startswith("VENV " + os.path.join(HERE, script)), out)
            self.assertEqual(err, "")

    def test_project_from_env_then_cwd(self):
        fake(os.path.join(self.mine, ".venv", "bin", "python"), tag="VENV")
        self.assertTrue(self.run_sh("edgar.py", env={"MY_INVEST_PROJECT": self.proj})[0].startswith("VENV"))
        self.assertTrue(self.run_sh("edgar.py", cwd=self.proj)[0].startswith("VENV"))
        self.assertTrue(self.run_sh("edgar.py", "--project", self.proj, env={"MY_INVEST_PROJECT": "/nowhere"})[0]
                        .startswith("VENV"))

    def test_missing_configured_interpreter_is_an_error_envelope(self):
        self.config('{"python": "/no/such/python"}')
        out, _ = self.run_sh("edgar.py", "--project", self.proj)
        self.assertIn('"error"', out)
        self.assertIn("/no/such/python", out)

    def test_placeholder_python_is_ignored(self):
        fake(os.path.join(self.mine, ".venv", "bin", "python"), tag="VENV")
        self.config('{"python": "${user_config.python}"}')
        self.assertTrue(self.run_sh("edgar.py", "--project", self.proj)[0].startswith("VENV"))

    def test_yfinance_script_provisions_venv_with_stub_pip(self):
        fake(os.path.join(self.bin, "python3.12"))
        out, err = self.run_sh("prices.py", "--project", self.proj, path=self.bin + ":" + SYSTEM_PATH)
        self.assertEqual(err, "my-invest: created data/.venv (python 3.12) and installed yfinance")
        self.assertTrue(out.startswith("FAKE %s/prices.py" % HERE), out)      # ran under the new .venv python
        self.assertTrue(os.path.exists(os.path.join(self.mine, ".venv", "bin", "python")))
        with open(self.piplog) as f:
            self.assertIn("-r %s/requirements.txt" % HERE, f.read())
        with open(os.path.join(self.mine, ".gitignore")) as f:
            self.assertEqual(f.read(), ".cache/\n.venv/\nconfig.json\n")

    def test_provisioning_happens_once(self):
        fake(os.path.join(self.bin, "python3.12"))
        p = self.bin + ":" + SYSTEM_PATH
        self.run_sh("facts.py", "--project", self.proj, path=p)
        _, err = self.run_sh("facts.py", "--project", self.proj, path=p)
        self.assertEqual(err, "")
        with open(self.piplog) as f:
            self.assertEqual(len(f.read().splitlines()), 1)

    def test_every_yfinance_script_triggers_it(self):
        fake(os.path.join(self.bin, "python3.12"))
        for script in ("options.py", "market.py"):
            proj = os.path.join(self.tmp, script)
            os.makedirs(proj)
            _, err = self.run_sh(script, "--project", proj, path=self.bin + ":" + SYSTEM_PATH)
            self.assertIn("created data/.venv", err, script)

    def test_other_scripts_never_provision(self):
        fake(os.path.join(self.bin, "python3.12"))
        for script in ("edgar.py", "news.py", "macro.py", "filing.py", "metrics.py", "momentum.py", "chart.py",
                       "store.py", "score.py", "report.py", "lint.py", "holdings.py"):
            self.run_sh(script, "--project", self.proj, path=self.bin + ":" + SYSTEM_PATH)
        self.assertFalse(os.path.exists(os.path.join(self.mine, ".venv")))
        self.assertFalse(os.path.exists(self.piplog))

    def test_no_python_310_continues_with_python3(self):
        # PATH has only the system python3 (3.9 on this machine, or any <3.10): no venv, script still runs
        probe = subprocess.run(["/usr/bin/python3", "-c", "import sys; print(sys.version_info >= (3, 10))"],
                               capture_output=True, text=True).stdout.strip()
        if probe != "False":
            self.skipTest("system python3 is 3.10+")
        out, err = self.run_sh("prices.py", "AAPL", "--project", self.proj)
        self.assertFalse(os.path.exists(os.path.join(self.mine, ".venv")))
        self.assertIn("Python 3.10+", out)          # prices.py's own error envelope
        self.assertEqual(err, "")


if __name__ == "__main__":
    unittest.main()
