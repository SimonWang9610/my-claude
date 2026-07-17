# Specflow integrity — is the spec honest, and does the code match it?

## Drift patterns

- **Retroactive spec fiction** — one commit carrying spec + code + every task
  `completed`. Detect: `git log <base>..<head> --oneline -- <spec-dir>` shows a single
  commit. Worst variants invent a fictional pre-existing state (a "Root Cause" for a bug
  that never existed).
- **Phantom baseline** — the spec describes pre-existing files/components absent from the
  base branch. Verify with `git show <base>:<path>` before trusting any Root Cause.
- **Internal contradiction** — tasks.md describes behavior opposite to requirements.md's
  ACs. Compare spec docs against each other, not only spec-vs-code.
- **Spec ↔ code value drift** — design/contracts prescribe values, types, or field names
  the implementation doesn't contain. Grep for values the spec claims removed; check
  every variant surface (e.g. both theme blocks) when the change is themed.
- **`.meta.yaml` dishonesty** — `completed`/`validated` states on work that observably
  isn't (a deletion task whose files still exist). Spot-check task claims against the
  tree.

## Gates (mandatory — can force the verdict)

- **Spec QA gate** — a spec-driven PR (it has a spec dir) needs QA evidence before any
  approve: `qa-report.md` exists, or `.meta.yaml` reached its validated/complete phase.
  Neither → **block**, citing the missing evidence. No spec at all → the review states
  why none was warranted, or blocks.
- **AC gate** — for the requirements the change claims to deliver (requirements.md or the
  linked story): classify **every AC** against the diff — met · unmet · not-attempted —
  cross-verifying "met" against actual files, never the PR description's self-assessment.
  Any unmet or not-attempted AC → no clean approve: **request changes**, or
  **approve-with-note** naming the unmet AC IDs and stating the story must not close on
  merge. Enumerate them on the PR; never spin them silently into a follow-up.
- **Artifact conformance** — the change respects the spec's design artifacts: public API
  name-for-name, stated constraints hold (grep), listed importers of modified units
  unbroken. A deliberate deviation must be recorded in the spec artifacts with its
  reason; an undocumented divergence is a finding.
