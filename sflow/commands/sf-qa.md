---
description: Audit the implemented branch and produce a sign-off-ready QA report.
---
# sf:qa

Audit the branch for mergeability and surface evidence for human disposition — QA never
approves or blocks. **Precondition:** the post-implement human code check passed AND
`/sf-validate` returned PASS. Reads the spec artifacts (missing required one → STOP and
report); writes `qa-report.md` under `.specflow/specs/<name>/`; audits code + tests in the
target repo; steering supplies the build/test commands.

**Steps.**

1. **Scoped-work pre-check** — every test-authoring work item in `tasks.md` complete and
   every plan journey has its test; one missing → STOP back to implement (an unfinished
   scoped test is incomplete implementation, never a QA finding).
2. **Build gate** — ONE full-suite run (journey tests included; they went green at
   implement) + the project build; red → STOP (audit nothing on a broken branch).
   Classify any failure **test-bug** (harness/timing) or **real-defect** (impl ≠ spec) as
   a finding — report, never fix.
3. **Audit families** — evidence per hit:
   - **spec authenticity** — the specs honestly describe the work (baseline, phase/task
     honesty, spec↔code value drift);
   - **scope creep** — changes outside the feature (governance files, identity, unrelated
     deps/routes/CI);
   - **coverage forensics** — a coverage matrix `AC/journey | test | strength | status`
     (covered · covered-but-hollow · gap); hollow = a stub would pass it; a never-scoped
     gap is a finding, never authored here;
   - **silent failures** — swallowed errors, stubs returning fake success, ephemeral state
     shown as persisted;
   - **consumers** — each direct consumer still integrates; the tests named in
     `design.md` § Blast Radius pass, and the radius still matches the shipped diff.
4. **`qa-report.md`** — coverage matrix, per-family results, `F-<n>` findings table
   (suggested severity + disposition checkboxes), reviewer checklist; present for human
   disposition. Rewrite no existing test without sign-off.

**Exit.** Build + suite green; every family ran with hits logged; every AC-mapped test
survives the mutation mindset; findings dispositioned by the reviewer
(Approved / Changes requested / Blocked).
