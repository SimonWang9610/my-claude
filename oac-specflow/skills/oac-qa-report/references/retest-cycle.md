# Retest cycle (re-runs)

A re-run is a **comparison against the prior report**, not a fresh audit from zero.

1. **Read the prior `qa-report.md`.** Parse its findings and their dispositions (confirmed defect /
   accepted / dismissed).
2. **See what changed.** Diff the branch since the prior run; note whether it was force-pushed (prior
   findings may no longer apply).
3. **Re-gate.** Re-run the build and existing suite (`audit-catalogue.md` §0).
4. **Re-run the audits and existing tests.** Do **not** modify tests except to fix a genuine test bug —
   and never loosen an assertion, delete a test, or weaken coverage to make a finding "pass." Tampering
   to clear a finding is itself a Critical finding.
5. **Classify each item into five buckets:**
   - **Fixed** — a prior confirmed defect now passes.
   - **Still failing** — a prior defect persists.
   - **New** — a finding not in the prior report.
   - **Regression** — something that passed before now fails.
   - **Stable pass** — unchanged and green.
6. **Write a "Changes since last run" delta** at the top of the updated report, then the full report.
7. **Re-disposition.** The prior sign-off is **void**; the reviewer dispositions again.

**Cycle limit.** If the same finding fails three consecutive re-runs, flag it for escalation rather
than looping — the fix approach or the requirement needs a human decision.
