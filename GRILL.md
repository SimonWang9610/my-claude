# CLAUDE.md — specflow tooling repo

## What this repo is
This repo holds the **skills, agents, and commands** that drive the tesseract specflow.
Editing here means editing the tools themselves, not product code. Every file is a prompt
that ships into an agent's context, so **every line costs tokens and attention that could
go to the work**. The bar: a line stays only if removing it would change agent behavior.

## The specflow layers
Process knowledge lives in exactly one place per concern. Never restate it in a skill or agent.

- **`specflow-driver`** (agent) — orchestrates one spec. Holds **no** process knowledge; reads
  `workflow.yaml` and runs project `/spec-*` commands. *Graded on: stays process-free, honors
  gates, delegates with a fully-filled subagent prompt, verifies before recording.*
- **`workflow.yaml`** (generated per spec by `/spec-react-workflow`) — **law**: phase order,
  gates, inputs/outputs, exit. No tool invents, reorders, or skips it.
- **`phase-map.md`** — binds each phase → `oac-*` skills + `exitWhen`. The generator's source of
  truth and the cohesion spine. **Single owner of the phase→skill→contract table — never copy it
  into this file or a skill.**
- **`oac-*` skills** — do the per-phase work. *Graded on that phase's `exitWhen`* — that line IS
  the artifact contract.
- **project `/spec-*` commands** — own process and file formats. A skill that re-specifies a file
  format a command already owns is duplicating.

Phases (union across variants; each variant uses a subset):
`preflight → analysis → describe → requirements → clarify → design → tasks → taskstoissues → implement → spec-qa`

**Cohesion rule:** a phase's `exitWhen` is the next phase's precondition. A skill that reads or
writes outside its phase's `inputs`/`outputs` is a smell — flag it before tightening anything else.

## Tool types — the shape each must hold
- **Command** = orchestration/process entry point. Has: invocation, ordered procedure, output
  contract, file format. Teaches nothing the model already knows.
- **Skill** = reusable per-phase capability. Has: a one-line trigger boundary (when to use / when
  NOT), the phase's `exitWhen` as its done-check, and *only* non-obvious or stack-specific knowledge.
- **Agent** = a role. Has: a responsibility boundary and, when it delegates, a subagent prompt with
  every field filled (Working Directory, Skills, Rules, Responsibilities, Materials, Done When,
  Report Back). Verifies Done When before recording — never on a subagent's word.

## Token economy — cut / keep
**Cut:**
- Role-play preamble ("You are an expert…"). *The test: does deleting it change the output?*
- Anything a competent Claude already knows. *The test: would it do this unprompted?*
- The second and third example. *The test: does the next example teach a new rule?*
- Defensive coverage of cases that don't occur in this repo.
- Context repeated across files (or restated from `phase-map.md` / a `/spec-*` command). *Say it once; reference it.*

**Keep:**
- Non-obvious, stack-specific facts — the React 19 / Vite / Zustand / TanStack Query / MUI / Vitest conventions, your paths.
- The phase's `exitWhen` — the exact shape of what this tool must produce.
- The trigger boundary and the input/output contract.

*The test for the whole file: strip it to the lines that change behavior. What's left is the tool.*

## The grill loop
Work **one file at a time.** Never batch-rewrite.
On a new session, read `REFINE-LOG.md` and resume at the first un-refined file.

1. **Classify** — which phase (per `phase-map.md`), which tool type. If it serves two phases, that's the first finding.
2. **Grill** — run the questions below against it.
3. **Propose** — a tightened version as a diff, not a silent rewrite.
4. **Justify** — every cut ties to a token-economy rule or a specflow finding. Never "felt cleaner."
5. **Verify** — the phase's `exitWhen` still holds and its `inputs`/`outputs` are unchanged.
6. **Log** — append to `REFINE-LOG.md`: file, before/after token count, what was cut and why.

Stop on a file when its token count stops dropping **and** every remaining line survives the grill.
A file that's already lean gets a "confirmed tight" log entry, not manufactured cuts. Then move on.
After all files, run one **cohesion pass**.

## Grill questions (ask of every file)
- What single `exitWhen` does this serve? Is every line in service of it?
- What does this say that Claude already knows? Cut it.
- What does this restate from `phase-map.md`, `workflow.yaml`, or a `/spec-*` command? Defer to the owner; delete the copy.
- Is the trigger boundary one line and unambiguous?
- Could a skeptical reviewer say "this line never changes behavior"? Then cut it.
- Did the token count actually drop, or did you just reword? Rewording isn't simplifying.

## Cohesion pass (after all files)
- **Vocabulary** — one term per concept across every file (spec, phase, gate, exitWhen, adopted unit…).
- **No overlap** — each capability lives in one tool; others defer. Watch the known seam: the
  "single suite run, no duplicate passes" rule sits in both the driver's Hard Rules and `spec-qa`'s
  `exitWhen` — pick one owner.
- **Handoff chain** — walk `preflight → analysis → describe → requirements → clarify → design →
  tasks → taskstoissues → implement → spec-qa`; each phase's `exitWhen` satisfies the next's `inputs`. Fix any break.
- **Test traceability & authorship split** — every AC has ≥1 test task at `tasks`; at `implement`
  the test is authored by the TestAgent (from `contracts/<unit>.md`, red before green) and the impl
  by a separate WorkAgent that never edits it; the driver re-runs the named test and confirms the
  test file is unmodified. No AC without a test; no agent grading its own work.
- **Parallel units** — `tasks` marks independent units with explicit dependency edges; `implement`
  runs independent units in parallel, one Work/Test pair each, ordered within the unit (test → red → impl → green).

## Hard rules
- Never rewrite in place without a diff + justification.
- Never delete a *capability* to save tokens — only its restatement. If unsure it's redundant, flag it, don't cut it.
- Measure. A refinement with no token drop and no clarity gain isn't a refinement.
- This file obeys its own rules. If CLAUDE.md bloats, grill it too.