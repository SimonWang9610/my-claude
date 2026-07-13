---
name: plan-react-tasks
description: >
  Turns an approved design.md + contracts/ into an ordered tasks and development plan.
---

# plan-react-tasks

Break an approved design into a dependency-ordered, fully traceable task list.

- **Given:** `design.md` + `contracts/` or an equivalent approved design package.
- **Produce:** `tasks.md` — Implementation · Test · Edge-case sections + a Parallel plan.

Each task is formatted as a table row with the following fields:

| Field          | Answers                              | Comes from                                    |
| -------------- | ------------------------------------ | --------------------------------------------- |
| **Inputs**     | what it consumes to start            | the contract / the AC → Verification row      |
| **Depends on** | which tasks must land first          | the unit index's `Depends on` column          |
| **Traces to**  | which criteria/contract it satisfies | the contract's `Traces to` / the criterion ID |
| **Gate**       | how "done" is mechanically verified  | the contract's states + must-nots / CI green  |

## Instructions

1. **Verify the inputs** — `design.md`'s completeness check holds: gate passed, every MODIFY/NEW
   unit links a non-empty contract, every criterion has an AC → Verification row. Any failure →
   back to the design skill before writing tasks.
2. **One implementation task per MODIFY/NEW unit** — walk the unit index; EXISTING units get no
   task. Fill the Impl shape from [tasks-doc.md](./tasks-doc.md): inputs and gate come from the
   contract; `Depends on` is copied from the index (EXISTING dependencies don't count as _new_).
   Never merge two units into one task or split one across two.
3. **One test task per AC → Verification row** — fill the Test shape from
   [tasks-doc.md](./tasks-doc.md): the row fixes level and location; the owning contract fixes the
   assertion target. Authored first (failing), green in its unit's wave.
4. **Edge-case tasks** — per unit, walk the [enumeration below](#edge-case-enumeration) and emit
   one Edge task per class that applies and no AC row already asserts.
5. **Derive the parallel waves** — from the `Depends on` edges: Wave 1 = tasks with no new
   dependencies; Wave _n_ = tasks whose dependencies all complete earlier. Drop each unit to the
   earliest wave its dependencies allow — units in a wave build concurrently, each with its test
   and edge tasks alongside.
6. **Assemble and count-check** — write `tasks.md` from [tasks-doc.md](./tasks-doc.md), then verify:
   `total = MODIFY/NEW units + AC → Verification rows + edge cases`. A task missing **Traces to**
   is an orphan — assign or delete; a task missing a **Gate** is unverifiable — fix it. A count
   mismatch means something was dropped or duplicated — reconcile before hand-off.

## Edge-case enumeration

Per unit, walk the four classes; emit one task per class that applies — unless an AC → Verification
row already asserts that exact outcome (skip; don't duplicate). Always assert the **user-visible**
result — the contract's "states it must expose" names the signal.

| Unit kind                      |               error               | empty | loading |                boundary                |
| ------------------------------ | :-------------------------------: | :---: | :-----: | :------------------------------------: |
| Component rendering query data |                 ✔                 |   ✔   |    ✔    | ✔ (prop/input at its documented limit) |
| Hook wrapping a query/mutation |                 ✔                 |   ✔   |    ✔    |                   —                    |
| Client store                   |                 —                 |   —   |    —    |   ✔ (clamp · invalid input · reset)    |
| Service / API module           | ✔ (failure maps to a typed error) |   —   |    —    |        ✔ (last page · max size)        |

- **Error** — trigger: the query/mutation errors (stub returns 500). Assert: the alert role / the
  contract's error copy renders; the retry control enabled if the contract promises one.
- **Empty** — trigger: the query resolves to `[]`/`null`. Assert: the empty-state message renders
  **and** zero result rows — not a bare blank region.
- **Loading** — trigger: the query is pending (delayed stub). Assert: skeleton/progressbar shown,
  with **no flash** of the empty or error state before data arrives.
- **Boundary** — trigger: an input/prop at its documented limit (max length, last page, clamped
  store value). Assert: the control's observable state at the limit — disabled/enabled, the
  rendered clamped value, "Next" absent on the last page.

**Anti-pattern:** an edge task asserting `expect(mockFetch).toHaveBeenCalled()` instead of what the
user sees — that's a proxy, not an edge case (mutation litmus: invert the production condition; the
test must fail).
