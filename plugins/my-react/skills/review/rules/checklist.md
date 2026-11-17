# React review checklist

Each check is binary; its evidence form is in brackets. A failed check is a finding only with that
evidence.

## The unit keeps its contract

- Its public surface matches the design name for name, type for type. [read]
- Every state it promises is reachable through that surface. [trace]
- Every unhappy path lands in its error, empty or boundary state; a caught error re-surfaces
  there. [trace]
- Its stated must-nots hold. [grep]

## Runtime

- Hot paths (per-frame, large list, main interaction) satisfy the optimize cards. [read, cite the
  card]
- Every subscription selects only the facts consumed; every setup pairs with its teardown. [read]
- Growth is bounded: caches evicted, effects converge, listeners removed. [read]
- Cold paths stay clear code: optimization only where measured. [read]

## Tests

- Each exposed state (loading, empty, error) has a test asserting it. [trace]
- Assertions target what the user sees through the unit's seam, not internals. [read]
- A test needs the unit's real logic to pass: fixtures and MSW stubs sit at the boundary. [read]
- The suite is deterministic: async awaited, no sleeps, no order dependence. [run]
- Setup pairs with teardown: no leaked timers, listeners or global state. [read]
- Each case proves a distinct behaviour; no snapshot dumps. [read]
