---
description: Detect shared-unit drift and unspecced behavior after merge.
---
# sf:drift

Detect code↔spec drift and behavioral drift (code the spec no longer covers).

---

**Purpose.** Catch divergence in both directions. Classic drift checks code against the spec; the more dangerous direction is usually unchecked — code the spec does *not* cover (improvised branches, superseded NFRs, an adopted shared unit modified after merge). This stage adds a behavioral lens: not just does code match the spec, but does the spec still cover what the code does.

## Spec Artifacts

Read the spec's artifacts under `.specflow/specs/<name>/`; compare against the target repo and report a drift report to the caller.
- **Required:** the spec artifacts the workflow declares — `design.md` + `tasks.md` on feature/brownfield, `analysis.md` + `tasks.md` on bugfix.
- **Optional:** prior-phase `references/`.
- **Additional:** steering `.specflow/steering/*`; the target repo (code under comparison).

## Gate / exit

Clean only when implemented code matches the design/tasks/contracts; no ADOPTED shared unit was modified (a `SHARED-UNIT-DRIFT` is blocking); and every behavior the code exhibits still maps to a governing AC. Blocking violations are reported with file references.

## Steps

1. **Read design + tasks** — the spec the code is checked against.
2. **Code-vs-spec** — check implemented code against the spec descriptions and the `contracts/` interfaces; flag divergence with file references.
3. **Shared-unit drift** — an ADOPTED unit modified vs the base branch → `SHARED-UNIT-DRIFT` (blocking).
4. **Behavioral drift** — at each delta, confirm every behavior still maps to an AC; flag any unspecced behavior.
5. **Test-codifies-bug** — flag any test that shields drifted code by codifying the divergent behavior.
