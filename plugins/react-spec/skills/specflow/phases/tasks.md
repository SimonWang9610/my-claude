# tasks

Turn the design into trackable tasks; test authoring is never optional.

**Writes** `tasks.md` · **Reads** `requirements.md` + `design.md` (run the producing phase if missing) ·
optional caller materials (the per-unit interfaces).

**Steps**
1. **Decompose per unit** — every introduced unit covered by exactly one task; each task lists the unit
   interface(s) it covers, its AC IDs, and completion gate.
2. **Test coverage** — every AC / testable NFR assigned to test-authoring work naming the ID + its
   observable outcome (a dedicated test task or the wave's test batch); uncovered edge classes marked on
   their task (or `skipped` with a reason — never omitted silently).
3. **Waves + batches** — dependency DAG grouped into **2–4 waves** (a wave sized by one agent's context,
   not task count); each pre-split into one test batch + one impl batch (assignments decided here). Test
   authoring always precedes the implementation it covers.

**Exit** — every AC / testable NFR maps to test-authoring work naming the ID + outcome; the graph is a
valid DAG in waves with batch pairs; zero test work → `TASK-TD` with a one-sentence reason.
