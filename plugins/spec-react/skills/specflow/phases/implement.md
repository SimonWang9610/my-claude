# implement

Execute `tasks.md` wave by wave under an evidence contract that makes "completed" structural: an
AC-named, outcome-asserting test passes, authored independently of the implementation.

**Writes** `tasks.md` status (code → target repo) · **Reads** `tasks.md` + `design.md` · optional
`qa-journey-plan.md` (drives step 4) + caller materials (the per-unit interfaces).

**Steps**
1. **Author tests per batch** — a test agent writes each task's AC-named outcome tests from the unit
   interfaces (test files only; from the interfaces, never from the code under test); run them **red per
   task**, failing on behaviour, not setup — record the ref.
2. **Implement per batch** — a separate agent (never the test author) builds to the interfaces (source
   only); a wrong-looking test is raised, never edited; copy an adopted shared unit.
3. **Verify per task** — tests **green** AND test paths byte-unchanged since red; modified → redo with a
   fresh test/impl pair. Chunked pairs run concurrently.
4. **Journeys** — `qa-journey-plan.md` → **NEW**: author the E2E test (`J-<n>` + AC IDs in the name);
   **MODIFY**: update the named existing test (material change surfaced); run green.

**Exit** — every task's AC-traceable test green + byte-unchanged since authoring; journey tests green (or
skip note stands); shared-unit immutability held; `tasks.md` records the test satisfying each AC.
