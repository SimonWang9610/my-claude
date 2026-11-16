#!/usr/bin/env python3
"""spec-check: the deterministic gates of a my-workflow spec. Run from the project root.

  spec-check.py <ids|design|plan|coverage|all> <path/to/workflow.yaml> [--run] [--write]

ids       templates valid; one definition per id, in its file; AC-<n>.<m> -> US-<n> and FN -> AC links
          (AC-<n> and an FN serving nothing are standalone); no undefined id
design    units state responsibility, input, output, boundary; Mermaid diagram matches the unit list; no
          cycle; every workaround approved; (feature) every FN, or AC when there is no FN, delivered by a unit
plan      every AC, FN, R and changed UNIT is served by a task
coverage  per AC and FN: planned, implemented (files tracked), tested (a test file names the id), passing,
          or waived; every workaround approved. --run runs each criterion's Check command (else the
          recorded status is used); --write saves coverage.md beside workflow.yaml
Exit 0 = the gate passes; 1 = it fails; 2 = the spec could not be read."""
import argparse, re, subprocess, sys
from pathlib import Path

ID = r"(?:US|AC|FN|R|WA|UNIT|T)-\d+(?:\.\d+)*"
ID_RE = re.compile(rf"(?<![\w-])({ID})(?!\w)(?!\.\d)")
HOME = {"US": "spec", "AC": "spec", "FN": "spec", "R": "spec", "WA": "spec", "UNIT": "design", "T": "plan"}
REQUIRED = {  # prefix -> header substrings that must exist and be filled
    "US": ["as a", "i want", "so that"], "AC": ["given", "when", "then", "check"], "FN": ["serves"],
    "R": ["checked"], "UNIT": ["responsibility", "input", "output", "boundary"],
    "T": ["serves", "files", "check", "status"], "WA": ["gap", "workaround", "approved", "remove"],
}
DEFAULTS = {"spec": "spec.md", "design": "design.md", "plan": "tasks.md", "coverage": "coverage.md"}
TESTLIKE = re.compile(r"test|spec|check|e2e", re.I)


def prefix(i):
    return i.split("-")[0]


def ids_in(text):
    return ID_RE.findall(text or "")


def cells(line):
    """Split a table row on unescaped pipes outside backticks."""
    out, cur, code, i = [], "", False, 0
    line = line.strip()
    line = line[1:] if line.startswith("|") else line
    line = line[:-1] if line.endswith("|") and not line.endswith("\\|") else line
    while i < len(line):
        ch = line[i]
        if ch == "\\" and i + 1 < len(line):
            cur += line[i:i + 2]; i += 2; continue
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
        i += 1
    out.append(cur.strip())
    return out


def prose(text):
    """The text without HTML comments."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def tables(text):
    """(header, rows) per Markdown table outside comments and code fences; rows are header-keyed dicts."""
    text = re.sub(r"```.*?```", "", prose(text), flags=re.S)
    block = []
    for line in text.splitlines() + [""]:
        if line.strip().startswith("|"):
            block.append(line); continue
        if len(block) >= 2 and re.match(r"^\s*\|[\s:|-]+\|?\s*$", block[1]):
            head = [h.lower() for h in cells(block[0])]
            yield head, [dict(zip(head, cells(r))) | {"_cells": cells(r)} for r in block[2:]]
        block = []


def col(row, name):
    """The first cell whose header contains `name`."""
    return next((v for k, v in row.items() if k != "_cells" and name in k), "")


def filled(v):
    """A cell with content that is not a status mark or a template placeholder."""
    return bool(v.strip()) and v.strip() not in ("—", "-", "⏳", "⬜", "none") and not re.search(r"<[a-z][^>]*>", re.sub(r"`[^`]*`", "", v))


class Spec:
    def __init__(self, wf):
        text = wf.read_text()
        self.dir = wf.parent
        kind = re.search(r"^kind:\s*(\w+)", text, re.M)
        self.kind = kind.group(1) if kind else "feature"
        self.not_a_bug = bool(re.search(r"^\s*verdict:\s*not a bug", text, re.M))
        arts = dict(re.findall(r"^\s+(spec|design|plan|coverage):\s*([^\s#]+)", text, re.M))
        self.path = {k: self.dir / arts.get(k, v) for k, v in DEFAULTS.items()}
        self.text = {k: self.path[k].read_text() if self.path[k].is_file() else "" for k in ("spec", "design", "plan")}
        self.root = self._root()
        self.defs, self.waived, self.errors = {}, {}, []
        seen = set()
        for key in ("spec", "design", "plan"):
            if self.path[key] in seen:
                continue
            seen.add(self.path[key])
            for head, rows in tables(self.text[key]):
                if not head or head[0] != "id":
                    continue
                waiver = any("waived" in h for h in head)
                for row in rows:
                    first = row["_cells"][0].strip("`* ")
                    if not ID_RE.fullmatch(first) or (len(row["_cells"]) > 1 and re.fullmatch(r"<[^>]*>", row["_cells"][1])):
                        continue  # not an id row, or an unfilled template row
                    if waiver:
                        if filled(col(row, "approved")):
                            self.waived[first] = col(row, "approved")
                        else:
                            self.errors.append(f"{first}: waiver has no approval")
                        continue
                    if first in self.defs:
                        self.errors.append(f"{first}: defined twice"); continue
                    home = HOME[prefix(first)]
                    if self.path[home] != self.path[key]:
                        self.errors.append(f"{first}: defined in {self.path[key].name}, belongs in {self.path[home].name}")
                    row["_dropped"] = len(row["_cells"]) > 1 and row["_cells"][1].lower().startswith("dropped")
                    self.defs[first] = row

    def _root(self):
        try:
            out = subprocess.run(["git", "-C", str(self.dir), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
            if out.returncode == 0:
                return Path(out.stdout.strip())
        except OSError:
            pass
        return Path.cwd()

    def live(self, *prefixes):
        return [i for i, r in self.defs.items() if prefix(i) in prefixes and not r["_dropped"]]

    def template(self, *prefixes):
        errs = []
        for i in self.live(*prefixes):
            for need in REQUIRED[prefix(i)]:
                if not any(need in k for k in self.defs[i] if k != "_cells" and not k.startswith("_")):
                    errs.append(f"{i}: its table has no '{need}' column")
                elif not filled(col(self.defs[i], need)) and need not in ("approved", "status", "check") and (i[:2], need) != ("FN", "serves"):
                    errs.append(f"{i}: '{need}' is empty")
        return errs

    def unapproved(self):
        return [f"{i}: workaround not approved by the user" for i in self.live("WA") if not filled(col(self.defs[i], "approved"))]

    # ---- ids
    def check_ids(self):
        errs = list(self.errors)
        if not self.text["spec"]:
            return [f"{self.path['spec']}: missing or empty"]
        errs += self.template("US", "AC", "FN", "R", "WA")
        us, ac, fn = self.live("US"), self.live("AC"), self.live("FN")
        if not ac and not self.not_a_bug:
            errs.append("no acceptance criterion (AC) is defined")
        if self.kind == "feature" and not us:
            errs.append("a feature needs at least one user story (US)")
        for a in ac:
            parent = "US-" + a.split("-")[1].split(".")[0]
            if "." in a and parent not in self.defs:  # AC-<n> with no dot is standalone
                errs.append(f"{a}: no parent story ({parent})")
        for u in us:
            if not any(a.startswith("AC-" + u.split("-")[1] + ".") for a in ac):
                errs.append(f"{u}: no acceptance criterion")
        served = set()
        for f in fn:
            refs = [i for i in ids_in(col(self.defs[f], "serves")) if prefix(i) == "AC"]
            served |= set(refs)  # none: a standalone functionality, proved by its tasks' checks
        if fn and self.kind == "feature":
            errs += [f"{a}: no functionality (FN) serves it" for a in ac if a not in served]
        for key in ("spec", "design", "plan"):
            for i in sorted(set(ids_in(prose(self.text[key])))):
                if i not in self.defs:
                    errs.append(f"{i}: referenced in {self.path[key].name} but never defined")
        return sorted(set(errs))

    # ---- design
    def flowcharts(self):
        for block in re.findall(r"```mermaid\s*\n(.*?)```", prose(self.text["design"]), flags=re.S):
            if not re.match(r"\s*(flowchart|graph)\b", block):
                continue
            nodes, edges = {}, set()

            def decl(m):
                nodes[m.group(1)] = m.group(2) if m.group(2) is not None else m.group(3); return m.group(1)
            for line in block.splitlines()[1:]:
                line = line.strip().rstrip(";")
                if not line or re.match(r"(%%|classDef|class |style |subgraph|end$|direction|linkStyle|click )", line):
                    continue
                line = re.sub(r'(\w+)\s*(?:\[\[|\[\(|\(\(|\[|\(|\{)\s*(?:"([^"]*)"|([^"\]\)\}]*))\s*(?:\]\]|\)\]|\)\)|\]|\)|\})', decl, line)
                line = re.sub(r":::\w+", "", line)
                line = re.sub(r"\|[^|]*\|", " ", line)                      # -->|label|
                line = re.sub(r"--\s*\"?[^->\"|]+\"?\s*-->", "-->", line)   # -- label -->
                hops = [[n.strip() for n in part.split("&") if n.strip()] for part in re.split(r"<?-\.->|<?==>|<?-->|---|-\.-|===", line)]
                for a, b in zip(hops, hops[1:]):
                    edges |= {(x, y) for x in a for y in b}
                for hop in hops:
                    for n in hop:
                        nodes.setdefault(n, n)

            def unit(n):
                found = [i for i in ids_in(nodes.get(n, "")) if prefix(i) == "UNIT"]
                if found:
                    return found[0]
                m = re.fullmatch(r"UNIT_(\d+(?:_\d+)*)", n)
                return "UNIT-" + m.group(1).replace("_", ".") if m else None
            units = {n: unit(n) for n in nodes}
            if any(units.values()):
                yield {u for u in units.values() if u}, {(units[a], units[b]) for a, b in edges if units.get(a) and units.get(b)}

    def check_design(self):
        errs = [e for e in self.errors if e.split(":")[0].startswith(("UNIT", "WA"))]
        units = self.live("UNIT")
        if not units:
            return errs + [f"{self.path['design'].name}: no unit (UNIT) is defined"] + self.unapproved()
        errs += self.template("UNIT")
        drawn, edges = set(), set()
        for n, e in self.flowcharts():
            drawn |= n; edges |= e
        if len(units) >= 2 and not drawn:
            errs.append("no Mermaid flowchart shows the units' dependencies")
        if drawn:
            errs += [f"{u}: missing from the dependency diagram" for u in units if u not in drawn]
            errs += [f"{u}: in the diagram but not in the unit list" for u in sorted(drawn) if u not in units]
            for u in units:
                for cell in ("input", "output"):
                    for other in ids_in(col(self.defs[u], cell)):
                        if prefix(other) == "UNIT" and other != u and (u, other) not in edges and (other, u) not in edges:
                            errs.append(f"{u}: its {cell} names {other} but the diagram has no edge between them")
            cycle = find_cycle(edges)
            if cycle:
                errs.append("dependency cycle: " + " → ".join(cycle))
        if self.kind == "feature":
            delivered = {i for u in units for i in ids_in(col(self.defs[u], "delivers"))}
            need = self.live("FN") or self.live("AC")
            errs += [f"{i}: no unit delivers it" for i in need if i not in delivered]
        return sorted(set(errs)) + self.unapproved()

    # ---- plan
    def serving(self):
        """id -> the live tasks that serve it."""
        out = {}
        for t in self.live("T"):
            for i in ids_in(col(self.defs[t], "serves")):
                out.setdefault(i, []).append(t)
        return out

    def check_plan(self):
        errs = [e for e in self.errors if e.startswith("T-")]
        tasks = self.live("T")
        if not tasks:
            return errs + [f"{self.path['plan'].name}: no task (T) is defined"]
        errs += self.template("T")
        serving = self.serving()
        errs += [f"{t}: serves no id" for t in tasks if not ids_in(col(self.defs[t], "serves"))]
        errs += [f"{i}: served by {', '.join(ts)} but never defined" for i, ts in serving.items() if i not in self.defs]
        changed = [u for u in self.live("UNIT") if not col(self.defs[u], "change").lower().startswith("reuse")]
        errs += [f"{i}: no task serves it" for i in self.live("AC", "FN", "R") + changed if i not in serving]
        return sorted(set(errs))

    # ---- coverage
    def files_of(self, task):
        found = []
        for tok in re.split(r"[\s,·;]+|<br\s*/?>", col(self.defs[task], "files")):
            tok = tok.strip("`*()[]")
            if not tok or tok in ("—", "-") or tok.startswith("<"):
                continue
            hits = sorted(self.root.glob(tok)) if any(c in tok for c in "*?[") else [self.root / tok]
            for p in hits:
                if p.is_dir():
                    found += [f for f in sorted(p.rglob("*")) if f.is_file()]
                elif p.is_file():
                    found.append(p)
        return found

    def check_coverage(self, run):
        serving = self.serving()
        files = {t: self.files_of(t) for t in self.live("T")}
        tests = {}
        for fs in files.values():
            for f in fs:
                if f not in tests and TESTLIKE.search(str(f.relative_to(self.root))):
                    try:
                        tests[f] = set(ids_in(f.read_text(errors="ignore")))
                    except OSError:
                        tests[f] = set()
        rows, errs, result = [], [], {}

        def passing(row, recorded):
            """A row's Check command exits 0 (--run), else its recorded status."""
            check = col(self.defs[row], "check")
            cmd = re.search(r"`([^`]+)`", check)
            if run:
                if not cmd or cmd.group(1).startswith("<"):
                    return False
                try:
                    return subprocess.run(cmd.group(1), shell=True, cwd=self.root, capture_output=True, timeout=900).returncode == 0
                except subprocess.TimeoutExpired:
                    return False
            status = col(self.defs[row], recorded)
            return "✅" in status or status.lower().startswith("done")

        def fn_passing(fn, ts):
            refs = [a for a in ids_in(col(self.defs[fn], "serves")) if a in ac_pass]
            if refs:
                return all(ac_pass[a] for a in refs)
            return bool(ts) and all(passing(t, "status") for t in ts)  # standalone: its tasks' checks

        ac_pass = {a: passing(a, "check") for a in self.live("AC")}
        for i in self.live("AC", "FN"):
            ts = serving.get(i, [])
            own = sorted({f for t in ts for f in files[t]})
            done = bool(ts) and all("✅" in col(self.defs[t], "status") or "done" in col(self.defs[t], "status").lower() for t in ts)
            state = {
                "planned": bool(ts),
                "implemented": done and all(files[t] for t in ts),
                "tested": any(i in found for found in tests.values()),
                "passing": ac_pass[i] if prefix(i) == "AC" else fn_passing(i, ts),
            }
            missing = [k for k, ok in state.items() if not ok]
            if not missing:
                result[i] = "ok"
            elif i in self.waived:
                result[i] = f"waived ({self.waived[i]})"
            else:
                result[i] = "FAIL: " + ", ".join("not " + m for m in missing)
                errs.append(f"{i}: " + ", ".join("not " + m for m in missing))
            rows.append((i, state, own, result[i]))
        table = ["| Id | Planned | Implemented | Tested | Passing | Files | Result |", "|---|---|---|---|---|---|---|"]
        mark = lambda ok: "✅" if ok else "⛔"
        for u in self.live("US"):
            mine = [r for r in rows if r[0].startswith("AC-" + u.split("-")[1] + ".")]
            own = sorted({f for r in mine for f in r[2]})
            ok = bool(mine) and all(not r[3].startswith("FAIL") for r in mine)
            table.append(f"| {u} | | | | | {self.show(own)} | {'ok' if ok else 'FAIL: see its criteria'} |")
        for i, state, own, res in rows:
            table.append(f"| {i} | " + " | ".join(mark(state[k]) for k in ("planned", "implemented", "tested", "passing")) + f" | {self.show(own)} | {res} |")
        was = [f"- {i} — approved: {col(self.defs[i], 'approved') if filled(col(self.defs[i], 'approved')) else '⛔ not approved'}" for i in self.live("WA")]
        errs += self.unapproved() + [e for e in self.errors if "waiver" in e]
        how = "run by this script" if run else "recorded in the spec's Check cells by an agent, not run here (judged)"
        report = "\n".join([
            f"# Coverage — {self.dir.name}", "",
            f"**Result:** {'pass' if not errs else f'fail — {len(errs)} to fix'}",
            f"Checked by script: planned, implemented, tested. Passing: {how}.", "", *table, "",
            "## Workarounds", "", *(was or ["- none"]), ""])
        return errs, report

    def show(self, files):
        return " · ".join(f"`{f.relative_to(self.root)}`" for f in files) or "—"


def find_cycle(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
    state = {}

    def visit(n, path):
        state[n] = 1
        for m in graph.get(n, []):
            if state.get(m) == 1:
                return path[path.index(m):] + [m] if m in path else [n, m]
            if m not in state:
                found = visit(m, path + [m])
                if found:
                    return found
        state[n] = 2
        return None
    for n in sorted(graph):
        if n not in state:
            found = visit(n, [n])
            if found:
                return found
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("check", choices=["ids", "design", "plan", "coverage", "all"])
    ap.add_argument("workflow", type=Path)
    ap.add_argument("--run", action="store_true", help="coverage: run each criterion's Check command")
    ap.add_argument("--write", action="store_true", help="coverage: save coverage.md beside workflow.yaml")
    args = ap.parse_args()
    if not args.workflow.is_file():
        print(f"spec-check: {args.workflow} not found"); return 2
    spec = Spec(args.workflow.resolve())
    wanted = ["ids", "design", "plan", "coverage"] if args.check == "all" else [args.check]
    if args.check == "all":
        wanted = [w for w in wanted if w in ("ids", "coverage") or (w == "design" and spec.live("UNIT")) or (w == "plan" and spec.live("T"))]
    failed = False
    for name in wanted:
        if name == "coverage":
            errs, report = spec.check_coverage(args.run)
            print(report)
            if args.write:
                spec.path["coverage"].write_text(report); print(f"saved {spec.path['coverage']}")
        else:
            errs = getattr(spec, "check_" + name)()
        for e in errs:
            print(f"FAIL {name}: {e}")
        print(f"{'FAIL' if errs else 'PASS'} {name}" + (f" — {len(errs)} to fix" if errs else ""))
        failed |= bool(errs)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
