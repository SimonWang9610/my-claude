---
description: Author user stories and acceptance criteria with stable IDs and observable Given/When/Then phrasing.
---
# spec:requirements

Author requirements in EARS notation; every acceptance criterion gets a stable ID and observable Given/When/Then phrasing.

---

**Purpose.** Produce the source of truth for all downstream phases: bind intent to a testable, named unit *at authoring time*. Stable AC IDs are the spine the whole chain anchors to — without them, tasks can emit zero test tasks and behavior ships unverified.

## Spec Artifacts

Write `requirements.md` under `.specflow/specs/<name>/`.
- **Required:** `.meta.yaml` — run `/spec-init` if missing.
- **Optional:** `preflight.md` (reuse + shared-unit context); prior-phase `references/`; the design unit map (`references/design-units.md`) if preflight produced one.
- **Additional:** steering `.specflow/steering/*`.

## Gate / exit

Exits only when every story has ≥1 AC; every AC/NFR carries a unique stable ID (`AC-<story#>.<n>` / `NFR-<n>`) phrased as an observable Given/When/Then outcome; and EARS notation is valid. IDs never renumber.

## Steps

1. **Write user stories** — each with its acceptance criteria — when `references/design-units.md` is present, ground UI stories and their ACs in the actual screen units it lists.
2. **Define functional requirements** — EARS notation (Ubiquitous / Event / State / Optional / Unwanted).
3. **List NFRs** — as `NFR-<n>`; include stack-relevant NFRs (per steering).
4. **Apply the AC contract** — every AC/NFR gets a stable ID and observable Given/When/Then phrasing; reject implementation-step phrasing.
