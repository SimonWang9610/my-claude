# Root-cause trace (Mode 1)

Goal: name the exact unit + line that is *wrong*, not the place the symptom surfaces. The two
are usually different files.

## Procedure

1. **Reproduce first.** Establish the failing observable behavior — the wrong text, wrong
   navigation, thrown error, stale value — from the defect report. If you can't reproduce it,
   you can't root-cause it; ask the caller for exact steps/state.
2. **Trace the path backward from the symptom.** Start where the wrong thing is observed (a
   component's rendered output, a store selector, a query result) and walk upstream: which value
   feeds it, which unit produced that value, which input produced *that*. Follow the data, not
   the call stack alone.
3. **Stop at the first unit whose logic is incorrect.** That is the root. Everything downstream is
   faithfully propagating a bad value — those are symptoms, not causes. Fixing a symptom site
   leaves the defect live for the next consumer.
4. **Confirm by inversion.** Ask: if this unit's logic were correct, would the symptom vanish
   with no other change? If not, you haven't reached the root yet — keep tracing.

## Symptom vs. cause — worked distinction

- Symptom: `<OrderTotal>` renders `$0.00`. Cause candidate: the component? No — it renders the
  prop it's given.
- Trace up: prop comes from `useCartTotal()`; that hook sums `items`; `items` came back empty
  from the `['cart', id]` query because the selector mapped `data.lineItems` but the API field
  renamed to `data.items`.
- **Root = the query's `select` mapper (file + line)**, not `<OrderTotal>`. The AC and repro test
  target the wrong-empty cart value, so a fix at the component (defaulting the label) would be a
  symptom patch and the repro test would still fail.
