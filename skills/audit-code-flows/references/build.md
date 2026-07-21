# build — procedure and artifact formats

Inputs: **entry points** · **purpose** (the caller's questions — gates every read) ·
**source kind** per entry: **existing** (live code — the note adds Dependents + a
REUSE/MODIFY/REPLACE proposal) · **legacy** (read-only reference — the note is a
behavioral spec: preserve vs drop). Optional: an **external atlas** (read-only, caller-supplied
— a curated atlas for shared/stable code) → a **map you distill** to audit faster (Locate §
Distill), never finished notes to copy; you still Walk source for the details your purpose
needs. Every note you **write** goes in the local `atlas/`; the external is never written.

Explore the way you would by hand — **Locate → Walk → Organize** — bounding depth *during* the
walk (jump only where a purpose question is still open), so the off-purpose graph is never
built and the read can't run away.

## 1. Locate — narrow by keyword

Start where a human starts: **grep the purpose's keywords** (symbol names, routes, store /
field names) + project structure to find the candidate entry file(s) / symbols, and list the
entry modules' exported surface. Text search is the right tool here — fast, no pattern to
author. Cheap and wide — the starting point, not a full-graph sweep.

**Distill an external atlas** (if one guides this build) — audit the external itself: read its
index and **cherry-pick the flows relevant to your purpose into `atlas/references/`** (one note
per flow, headed `— external, from <path>`, trimmed to what helps). Those references are your
Locate result — their entry anchors, coupling map, and boundary surfaces tell you where to look
— but they were framed for another purpose, so you **still Walk the source and write your own
top-level notes**, citing the reference. A cherry-picked flow you don't audit yourself stays a
reference only and answers queries tagged `(external <path>)`.

**Warm start** — if you carry the project's conventions (where kinds of unit live, standard
boundaries, naming), check the conventional location first: a hint that biases order, never a
prune — the grep still runs and confirms.

Check once whether the structural tool is available for the walk: `ast-grep --version` (or
`npx --yes @ast-grep/cli --version`); absent → the walk runs on grep alone (§ 2). ast-grep
commands: [ast-grep-usage.md](./ast-grep-usage.md).

## 2. Walk — go-to-definition, on-purpose, one hop at a time

From each located entry, follow the definition graph outward like go-to-definition — **only
where a purpose question is still open.** Per hop, both directions: what it calls / who calls
it (the next unit), and the fact touch points it reads or writes (a store / key / field the
purpose names — the couplings surface here).

Pick the tool by precision — grep and ast-grep are complementary, not interchangeable:

- **grep** finds candidate references fast — enough when the symbol is uncommon or unique.
- **ast-grep** resolves them structurally when text would be ambiguous: a common identifier
  buried in string / comment hits, a call to match by shape, or a structural predicate grep
  can't express. Reach for it *when necessary*, not for plain keyword-finding.
- ast-grep absent → grep alone; its edges are `(grep)` candidates (§ 3) until a read confirms.

Stop a branch when it's understood, off-purpose (record the name), already walked, or a
boundary / cap is hit. A branch cut while still on-purpose becomes a **Self-audit pointer**.
Read budget ~15 files/flow; spent → stop and report notes + gaps. A gap list is a valid
result; an overrun is not.

## 3. Organize — the walked hops into flows

Turn the walked hops into each flow's note fields + the couplings index.

- **Audit flows, not files** — follow each flow end-to-end (entry → handler → state →
  boundary); per hop: WHAT data · WHERE from · WHERE to · HOW (mechanism).
- **Record boundaries, not implementations** — name the exact surface (method + path +
  params + body/response shape · DB table · topic · storage key) and stop; never descend
  into the client/SDK/framework plumbing behind it.
- **Indirection: annotate the hops the purpose needs; box the rest.** Name the chain —
  config origin → interpreter → collector (+ data model) → submission. An opened hop is
  traced and anchored; a boxed hop records in/out shapes + a Self-audit pointer. The chain
  stays continuous — never collapsed to the mechanism's name.
- **Couplings live in `index.md`** — the walk's fact-touch-points already found the sites;
  write each into `index.md`'s Couples-with cell (direction + shared fact) and map the
  moment the second flow hits it. Never in flow notes, never a second scan.
- **Tag what you didn't read directly** — untagged = read from source · `(inferred)` =
  deduced · `(uncertain)` = must carry a Self-audit pointer · `(grep)` = a walked edge
  found without ast-grep, a candidate until a read confirms it · `(external <path>)` = carried
  from an external atlas as context, not read from source this run — a candidate until a read
  confirms it.
- **Scan wide; note narrow** — facts, anchors, surfaces, shapes; no narration, nothing
  that doesn't affect a downstream decision.

## Artifact — `atlas/` in the caller-designated directory

The walk fills the mechanical cells (index's Units touched + Entry anchor, the call edges,
the inline `path:symbol` anchors); organizing fills Problem + GIVEN/WHEN/THEN/HOW — judgment
authors, search verifies.

`index.md` — the always-loaded tier:

````markdown
# Atlas — <scope> · <purpose, one line>

Guided by: `<path/to/external/atlas>` <!-- external atlas distilled to speed this audit; omit if none -->

| Flow | Kind | Entry anchor | Units touched | Couples with |
|------|------|--------------|---------------|--------------|
| F1 <name> | existing | `path:symbol` | <units> | → F3 (invalidates <fact>) |

## Interaction map
<mermaid: nodes = flows, labeled edges = coupling + direction; hub units several flows
couple through flagged — widest change radius. Omit under 2 interacting flows.>

## Gaps
<what wasn't audited, and why>
````

`<flow-id>.md` — one per flow; each field a `##` subheading in this order, omit the
inapplicable; bodies are facts in the fewest lines that carry them:

````markdown
# F<n> <flow> — existing | legacy

## Abstract
what it solves + solution shape, 1–2 sentences

## GIVEN
per fact: origin (surface + shape) · preconditions (auth · flag · prior flow) · initial state

## WHEN
trigger (user action · timer · external event · state change) + guards

## THEN
per case (happy · error · empty · race · permission): outcome · state changed + where ·
propagation

## HOW
transforms per hop · side effects (exact surface: method+path+body · storage key · event) ·
mechanism per hop; for indirection, name the full chain (config origin → interpreter →
collector → submission), each hop anchored, opened or boxed

## Dependents / Verdict       <!-- existing only -->
external importers · REUSE | MODIFY | REPLACE — one-line reason (a proposal; the caller
confirms)

## Preserve / drop            <!-- legacy only -->
behaviors kept vs deliberately dropped

## Self-audit pointers
`path:symbol` — what deeper detail lives there + which decision needs it
````

`references/<flow>.md` — optional; a flow cherry-picked from an external atlas while distilling
it (Locate § Distill). Same note shape, headed `# <flow> — external, from <path>`, trimmed to
what guided this audit. Reference material, not your source-read notes — a finding taken from it
is tagged `(external <path>)`, a candidate until a read confirms it.
