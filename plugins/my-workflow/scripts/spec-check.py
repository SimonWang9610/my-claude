#!/usr/bin/env python3
"""spec-check: the deterministic gates of a my-workflow spec. Run from the project root.

  spec-check.py <ids|design|plan|coverage|all> <path/to/workflow.yaml> [--run] [--write]

ids       one definition per id, in its file; AC-<n>.<m> -> US-<n> (AC-<n> is standalone); every FN serves a
          criterion; no undefined id
design    every unit has a responsibility; the Mermaid diagrams, taken together, match the unit list; none
          shows more than 6 units; no cycle; every workaround approved; (feature) every AC delivered by a unit
plan      every AC, R and changed UNIT is served by a task (through an FN counts)
coverage  per AC: built (its tasks done, their files in the repo) and evidenced, or waived; every workaround
          approved. Evidence is a command in the project's own tooling (--run runs it; else its recorded
          mark is used) or `observed: <what was done and seen>`. --write saves coverage.md
Exit 0 = the gate passes; 1 = it fails; 2 = the spec could not be read."""
import argparse, re, subprocess, sys
from pathlib import Path

ID = r"(?:US|AC|FN|R|WA|UNIT|T)-\d+(?:\.\d+)*"
ID_RE = re.compile(rf"(?<![\w-])({ID})(?!\w)(?!\.\d)")
HOME = {"US": "spec", "AC": "spec", "FN": "spec", "R": "spec", "WA": "spec", "UNIT": "design", "T": "plan"}
REQUIRED = {  # prefix -> labels that must exist
    "US": [], "AC": ["evidence"], "R": ["checked"], "UNIT": ["responsibility"],
    "T": ["serves", "files", "status"], "WA": ["gap", "workaround", "approved", "remove"],
}
DEFAULTS = {"spec": "spec.md", "design": "design.md", "plan": "tasks.md", "coverage": "coverage.md"}
MAX_NODES = 6  # units in one dependency diagram; more is unreadable: split it


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


def sections(text):
    """Rows defined as sub-sections: a heading (level 2+) that starts with an id, then `**Label:** value` lines."""
    text = re.sub(r"```.*?```", "", prose(text), flags=re.S)
    parts = re.split(rf"^#{{2,6}}\s+`?({ID})`?(?!\w)(?!\.\d)[ \t]*([^\n]*)\n", text, flags=re.M)
    for i in range(1, len(parts), 3):
        body = re.split(r"^#{1,6}\s", parts[i + 2], maxsplit=1, flags=re.M)[0]
        row = {m.group(1).strip().lower(): m.group(2).strip()
               for m in re.finditer(r"^\s*(?:[-*]\s*)?\*\*([^*:]+):?\*\*:?[ \t]*(.*)$", body, flags=re.M)}
        yield row | {"_cells": [parts[i], parts[i + 1].strip(" ·—-")]}


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
        folder = self.path["design"].parent / "design"  # group and part files beside design.md
        self.design_files = sorted(folder.glob("*.md")) if folder.is_dir() else []
        self.unit_text = {f: f.read_text() for f in self.design_files}
        self.design_all = "\n".join([self.text["design"], *self.unit_text.values()])
        seen = set()
        sources = [(k, self.path[k], self.text[k]) for k in ("spec", "design", "plan")]
        sources += [("design", f, t) for f, t in self.unit_text.items()]
        for key, path, body in sources:
            if path in seen:
                continue
            seen.add(path)
            heads = list(sections(body))
            if path in self.unit_text:  # there a `## UNIT-n` heading is the unit's detail, not a definition
                heads = [r for r in heads if prefix(r["_cells"][0]) != "UNIT"]
            for head, rows in [*tables(body), (["id"], heads)]:
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
                    if self.path[home] != path and not (home == "design" and path in self.unit_text):
                        self.errors.append(f"{first}: defined in {path.name}, belongs in {self.path[home].name}")
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
                    errs.append(f"{i}: no '{need}' column or line")
                elif not filled(col(self.defs[i], need)) and need not in ("approved", "status", "evidence"):
                    errs.append(f"{i}: '{need}' is empty")
        return errs

    def acs_of(self, i):
        """The criteria a functionality serves."""
        if prefix(i) != "FN" or i not in self.defs:
            return []
        return [a for a in ids_in(col(self.defs[i], "serves")) if prefix(a) == "AC"]

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
        for a in ac:
            parent = "US-" + a.split("-")[1].split(".")[0]
            if "." in a and parent not in self.defs:  # AC-<n> with no dot is standalone
                errs.append(f"{a}: no parent story ({parent})")
        for u in us:
            if not any(a.startswith("AC-" + u.split("-")[1] + ".") for a in ac):
                errs.append(f"{u}: no acceptance criterion")
        errs += [f"{f}: serves no criterion (state how it is observed as an AC)" for f in fn if not self.acs_of(f)]
        for name, body in [(self.path[k].name, self.text[k]) for k in ("spec", "design", "plan")] + [(f.name, t) for f, t in self.unit_text.items()]:
            for i in sorted(set(ids_in(prose(body)))):
                if i not in self.defs:
                    errs.append(f"{i}: referenced in {name} but never defined")
        return sorted(set(errs))

    # ---- design
    def flowcharts(self):
        for block in re.findall(r"```mermaid\s*\n(.*?)```", prose(self.design_all), flags=re.S):
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
        top = [u for u in units if "." not in u]
        drawn, edges = set(), set()
        for n, e in self.flowcharts():
            drawn |= n; edges |= e
            if len(n) > MAX_NODES:
                errs.append(f"a diagram shows {len(n)} units ({', '.join(sorted(n)[:3])}, …): split it, at most {MAX_NODES} each")
        if len(top) >= 2 and not drawn:
            errs.append("no Mermaid flowchart shows the units' dependencies")
        if drawn:
            errs += [f"{u}: missing from every dependency diagram" for u in top if u not in drawn]
            errs += [f"{u}: in a diagram but not in the unit list" for u in sorted(drawn) if u not in units]
            cycle = find_cycle(edges)
            if cycle:
                errs.append("dependency cycle: " + " → ".join(cycle))
        if self.kind == "feature":
            delivered = {a for u in units for i in ids_in(col(self.defs[u], "delivers")) for a in [i, *self.acs_of(i)]}
            errs += [f"{i}: no unit delivers it" for i in self.live("AC") if i not in delivered]
        return sorted(set(errs)) + self.unapproved()

    # ---- plan
    def serving(self):
        """id -> the live tasks that serve it; serving an FN serves its criteria."""
        out = {}
        for t in self.live("T"):
            for i in ids_in(col(self.defs[t], "serves")):
                for j in [i, *self.acs_of(i)]:
                    if t not in out.setdefault(j, []):
                        out[j].append(t)
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
        changed = [u for u in self.live("UNIT") if "." not in u and not col(self.defs[u], "change").lower().startswith("reuse")]
        errs += [f"{i}: no task serves it" for i in self.live("AC", "R") + changed if i not in serving]
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

    def evidence(self, ac, run):
        """(kind, ok) of a criterion's Evidence line: a command exits 0 (--run; else its recorded mark), or an observation."""
        v = col(self.defs[ac], "evidence")
        if re.match(r"[^\w`]*observed\b", v, re.I):
            return "observed", filled(re.sub(r"^[^\w`]*observed\W*", "", v, flags=re.I))
        cmd = re.search(r"`([^`]+)`", v)
        if not cmd or cmd.group(1).startswith("<"):
            return "none", False
        if not run:
            return "recorded", "✅" in v
        try:
            return "run", subprocess.run(cmd.group(1), shell=True, cwd=self.root, capture_output=True, timeout=900).returncode == 0
        except subprocess.TimeoutExpired:
            return "run", False

    def check_coverage(self, run):
        serving = self.serving()
        files = {t: self.files_of(t) for t in self.live("T")}
        done = lambda t: "✅" in col(self.defs[t], "status") or "done" in col(self.defs[t], "status").lower()
        bad = {"none": "no evidence", "observed": "the observation is empty", "recorded": "evidence not recorded as passing", "run": "evidence fails"}
        mark = lambda ok: "✅" if ok else "⛔"
        rows, errs, result = [], [], {}
        for a in self.live("AC"):
            ts = serving.get(a, [])
            built = bool(ts) and all(done(t) and files[t] for t in ts)
            kind, ok = self.evidence(a, run)
            why = ([] if built else ["not built"]) + ([] if ok else [bad[kind]])
            if not why:
                result[a] = "ok — observed: yours to judge" if kind == "observed" else "ok"
            elif a in self.waived:
                result[a] = f"waived ({self.waived[a]})"
            else:
                result[a] = "FAIL: " + ", ".join(why)
                errs.append(f"{a}: " + ", ".join(why))
            rows.append(f"| {a} | {mark(built)} | {mark(ok)} {kind} | {self.show(sorted({f for t in ts for f in files[t]}))} | {result[a]} |")
        table = ["| Id | Built | Evidence | Files | Result |", "|---|---|---|---|---|"]
        groups = [(u, [a for a in result if a.startswith("AC-" + u.split("-")[1] + ".")]) for u in self.live("US")]
        groups += [(f, [a for a in self.acs_of(f) if a in result]) for f in self.live("FN")]
        for i, mine in groups:
            ok = bool(mine) and not any(result[a].startswith("FAIL") for a in mine)
            table.append(f"| {i} | | | | {'ok' if ok else 'FAIL'}: {' · '.join(mine) or 'no criterion'} |")
        was = [f"- {i} — approved: {col(self.defs[i], 'approved') if filled(col(self.defs[i], 'approved')) else '⛔ not approved'}" for i in self.live("WA")]
        errs += self.unapproved() + [e for e in self.errors if "waiver" in e]
        how = "each command run by this script" if run else "the mark an agent recorded, not run here (judged)"
        report = "\n".join([
            f"# Coverage — {self.dir.name}", "",
            f"**Result:** {'pass' if not errs else f'fail — {len(errs)} to fix'}",
            f"Built: the serving tasks are done and their files are in the repo. Evidence: {how}.", "", *table, *rows, "",
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
    ap.add_argument("--run", action="store_true", help="coverage: run each criterion's Evidence command")
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
