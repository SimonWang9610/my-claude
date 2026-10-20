# my-spec conventions

## Flow

start → decide (optional) → build or write → critique (optional); any stage runs explore for the facts
it lacks, reading only what its caller has not already passed.

- **Fast track** — a small, clear change (a few files, no open approach, an existing pattern covers
  it): a short spec shown inline, nothing saved, no design, no plan, no gates.
- **Full track** — everything else: spec and design saved, a gate after spec, design, plan and review.
- **No spec** (explore, critique, a design part, or decide on a self-contained question, run on its
  own) — the request is its requirements, ids start at 1, it gates as on the full track and saves only
  when asked.

## Lines

- `R<n>` requirement · `D<n> <decision> — <why>` · `Q<n> <question> — default: <answer>`; a choice
  still open is a `Q`, never also a `D`. Ids are assigned once and never renumbered; a caller passes
  the next free ids to the skills and agents it runs.
- A fact carries its anchor: `<fact> — path:line | doc § | url (date)`; not read → `(inferred)`.

## Gate

After a full-track stage: the ≤3 questions whose answers would change the most, each with its default
(list the rest as defaults), then `Continue to <next>?`. Never start the next stage without a yes
unless the spec (no spec: the request) says `gates auto`, which shows the gate and continues on the
defaults. On the reply, each answered or defaulted `Q` becomes a `D` in place, keeping its id. Nested
inside another skill, or in a spawned agent: no gate; return the questions and `next` to the caller.

## Stack

Analysis and design name roles. A library or tool appears only where a step maps a role to it (`maps
to`, `enforced by`, the tree, the spec's `context`, an option or `D` line that chooses it). The stack
and its conventions come from the user, the spec or explore (manifests, the project's rules, existing
code). Where a step produces names or code, follow in order: the project's existing patterns · an
installed skill that covers this stack and step (apply its rules to that part, never its own output
files or questions) · the stack's idioms.

## Saving

The full track saves `spec.md` and `design.md` in one task folder per spec; plans and reviews stay in
chat unless asked; a written deliverable goes where the spec or user names, else inline. Folder, first
match: a path the user named (used as the task folder) · the spec's `save` line · a location the
project's context files name (CLAUDE.md, AGENTS.md, README, a docs folder) · ask once, proposing
`.docs/<task>/` (add `.docs/` to `.gitignore` unless the user wants it committed). Cannot ask → keep
it inline with `Q<n> where to save — proposed: .docs/<task>/`; only an explicit answer saves (`gates
auto` does not). Update in place.

## Agents

Dispatch a my-spec agent only where a skill step says so (`my-spec:<name>` in Claude Code, `<name>` in
Copilot). Brief: where · what · materials (absolute spec and design paths, facts already found, the
next free ids) · done when; never your reasoning. Use its report when it arrives (end the turn if it
runs in the background); never redo its work; check its files yourself. A spawned agent asks nothing
(a missing input becomes a `Q` with its default) and dispatches only if its host allows.

## Diagrams

Mermaid `flowchart`, `sequenceDiagram` or `stateDiagram-v2` only; flowchart labels in double quotes,
ids `[A-Za-z0-9_]`. Directory trees in a `text` block. A table beside each diagram carries the
meaning.
