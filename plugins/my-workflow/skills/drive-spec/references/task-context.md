# Task context

How drive-spec runs a task: the folder, the artifacts, role, tracks and gates. No other skill or agent
knows this; each only returns its result, and drive-spec passes what a step needs in its brief.

## Folder

Once the track settles to full, confirm the folder with the user: `specs/<task>/`, where `<task>` is a
short kebab-case name and `specs/` sits under a location the user named, else one the project's
context files name (CLAUDE.md, AGENTS.md, README), else the project root. A `specs/` in the project is
added to `.gitignore` unless the user wants it committed. Cannot ask → keep everything inline. Fast
track: no folder; the role and decisions are stated in the conversation.

## Artifacts

Only drive-spec saves them, assembling each returned result to its template, and updates them in
place as later results arrive (answered questions, revisions, check commands):

- `spec.md` — `templates/spec.md` with the task header; build's plan goes in its Tasks section and
  every reported check command in Done when.
- `design.md` — only when a design ran, from decide or spec-architect.
- `review.md` — only when a review's verdict is rework; otherwise the report stays in the session.

Every brief names `spec.md` (and `design.md`); its header gives teammates the ids, sources and atlas.

## Role

The user's instructions set the workflow first: a stated decision is a `D` (its options skipped, its
claims still checked) · a named path or symbol is read, not searched for · "quick" or "deep" sets the
track and the grounding · "just do it" sets gates to auto. Only what they leave open is grounded, at
the role's depth:

| | senior (includes staff) | junior |
|---|---|---|
| Grounding | the touched area's mechanism and its callers | map, then mechanism, then callers |
| Questions | default and why | plus a one-line consequence per option |
| Review | on for the full track | on for the full track, offered for the fast track |
| Fast track | as sized | only when audit-truth found an existing example to copy |

Role, first match: stated ("as junior") · a `my-workflow role:` line in CLAUDE.md or AGENTS.md ·
inferred (paths, symbols, decisions or a named area → senior; only an outcome, or "how does X work" →
junior; unclear → senior). Show it as stated or inferred, so one word corrects it.
## Tracks and gates

- **Fast track** — a small, clear change (a few files, no open approach, an existing pattern covers
  it): the spec shown inline with its defaults as `D`s, nothing saved, no design, plan, gate or
  teammate. A question with no safe default makes it full.
- **Full track** — everything else, and at most two gates: one on the spec and design together, and
  one before teammates start building (none when you build it yourself).
- **Gate** — the batched questions with their defaults, then `Continue?`; no yes, no next step. Gates
  auto: show the gate and continue on the defaults. A second review verdict other than accept stops
  even on auto.
