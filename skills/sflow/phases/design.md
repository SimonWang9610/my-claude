# design

Decide the structure before any code — one interface per unit — and design the verification with the
feature: test strategy, journey plan, and blast radius are authored here, not deferred to QA.

**Writes** `design.md` (+ `qa-journey-plan.md` for user-facing journeys) · **Reads** `requirements.md`
(`/sflow requirements` if missing) · optional caller materials (`clarify.md`, `preflight.md`, prior
audits, a design decomposition).

**Steps**
1. **Architecture** — decompose into units (clear responsibilities, interactions, data models, error
   handling); every AC lands on a unit + a flow.
2. **Reconcile** — a reuse verdict per touched existing unit; a Shared Unit Plan (Reuse or Copy, never
   modify an adopted unit); reconcile with a design decomposition when provided.
3. **Per-unit interfaces** — every introduced unit gets an interface spec: its API, the AC-IDs it
   traces, its testability seam; `design.md` indexes them, never restates.
4. **Test strategy** — per AC/NFR a level (unit / journey / manual) in a `design.md` table; name each
   behaviour positive + negative + boundary; **ask the user what failure modes are missing**.
5. **Journey plan** — no journey-level AC → skip (one-line note). Else `qa-journey-plan.md`: per journey
   a happy path + every error/boundary step, `J-<n>` (precondition · steps · covers ACs), each **NEW** or
   **MODIFY <test path>**; plus a "NOT automated" table with reasons.
6. **Journey approval** — present at design review (`approve` · `revise:` · `skip J-<n>` · `add:`);
   re-present until approved; on approval add an "E2E Surface" note to `design.md`.
7. **Blast radius** — `design.md` section: reverse-import closure of changed files → their tests (may be
   empty — say so); a test that must *change* is flagged.
8. **Architecture gate** — ONE pass: every AC covered, no God-unit, no dual source of truth, no missing
   seam; PASS or justify each in `design.md`.

**Exit** — every AC / testable NFR covered by ≥1 unit interface + one strategy row; a per-unit interface
spec (AC trace + testability seam) for every introduced unit; `qa-journey-plan.md` approved (or skip
noted); architecture gate PASS or justified.
