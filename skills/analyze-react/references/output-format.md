# Output layout

Write to the `analysis.md` path the caller supplies. Include only the section for the chosen mode.

## 1. Defect / root-cause mode

```md
# Analysis — <short defect title>

## Symptom
<observable wrong behavior: exact text / navigation / error / stale value, and where seen>

## Root cause
- **Unit:** `src/…/<file>.ts` line <n>
- **Why the root (not the symptom site):** <one sentence — this unit produces the bad value;
  downstream units faithfully propagate it>

## Acceptance criterion
- **AC-<story>.<n>** — Given <context>, When <action>, Then <observable outcome>.

## Reproduction test
- **File:** `src/…/<file>.test.tsx`
- **Label:** `AC-<story>.<n> …`
- **Pre-fix result:** FAILS — `<observed failure line, e.g. Unable to find text "$12.00">`
```

## 2. In-place change / impact-first mode

```md
# Analysis — <short change title>

## Change surface
<the units/components/hooks/stores/query-keys this change edits, each with its path>

## Impact table
| Unit | Touched as | External importers | Read-only? | Action |
|------|-----------|--------------------|-----------|--------|
| `useCartTotal` | signature change | `<Cart>`, `<Checkout>` | ADOPTED | copy → feature-local variant |
| `orderStore` | new selector | `<Header>` | UNADOPTED | edit in place |

- **Read-only? = ADOPTED** → copy, never modify in place without caller approval.
- **Read-only? = UNADOPTED** → only this feature imports it; safe to edit.

## Notes
<any shared-unit edit that looks unavoidable — surfaced for the caller's decision, not taken>
```
