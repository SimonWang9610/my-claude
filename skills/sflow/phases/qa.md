# qa

Audit the branch for mergeability and surface evidence for human disposition — QA never approves or
blocks. **Precondition:** the post-implement human code check passed AND `/sflow validate` returned PASS.

**Writes** `qa-report.md` · **Reads** the spec artifacts (missing required → STOP); audits code + tests
in the target repo (steering supplies build/test commands).

**Steps**
1. **Scoped-work pre-check** — every test-authoring item in `tasks.md` complete + every plan journey has
   its test; one missing → STOP back to implement (not a QA finding).
2. **Build gate** — ONE full-suite run (journeys included) + the project build; red → STOP (audit nothing
   on a broken branch). Classify a failure **test-bug** or **real-defect** as a finding.
3. **Audit families** (evidence per hit) — **spec authenticity** (specs honestly describe the work) ·
   **scope creep** (changes outside the feature) · **coverage forensics** (matrix
   `AC/journey | test | strength | status`; hollow = a stub would pass) · **silent failures** (swallowed
   errors, fake success, ephemeral-as-persisted) · **consumers** (each still integrates; `design.md` §
   Blast Radius tests pass, radius matches the diff).
4. **Report** — `qa-report.md`: coverage matrix, per-family results, `F-<n>` findings table (severity +
   disposition checkboxes), reviewer checklist. Rewrite no test without sign-off.

**Exit** — build + suite green; every family ran with hits logged; every AC-mapped test survives the
mutation mindset; findings dispositioned (Approved / Changes requested / Blocked).
