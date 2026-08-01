# Behavior — does the code do what the contracts say, and fail loudly?

## Contract conformance

Per changed unit: the public API matches what the spec's design artifacts declare (no
undeclared props, no widened optionals); every promised state reachable and observable;
the ACs the unit claims demonstrably satisfied; the design's stated constraints hold.

## Silent failure patterns (flag on sight)

- a **write** operation wrapped in a fallback that fakes success — writes never fall back
- `.catch(() => {})` or console-only handling with no user-facing error surface
- stub functions returning fake success ("TODO: wire real API")
- in-memory state (refs/maps) presented as persisted — it dies on reload
- client-generated IDs (`Date.now()`) where the server assigns the key

## N+1 and request waterfalls

- `useQuery` (or effect-fetch) inside a list renderer — N requests, no batching → the fix
  is `useQueries` or a batch endpoint
- `await` inside any `for`/`while`/`forEach` — serialized requests → `Promise.all`
- a `queryFn` that loops awaits — N requests hidden inside one query object

Severity: unbounded (no pagination guard) → HIGH; bounded/paginated → WARNING.

## Test honesty (false-positive signals)

- asserts on static fallback data that happens to contain the expected value
- mocks the unit under test — the test covers only plumbing
- events fired at the wrong target (a text node instead of the dialog/backdrop)
- lower-bound count assertions (`>= 5`) that survive a regression
- logic duplicated inside the test instead of imported from the real module

**Mutation test:** disable the branch a test claims to cover; still green = false
positive — flag the test, not just the gap.

## Races & lifecycle (spot-check any async/subscription diff)

- async results applied with no staleness guard (late response overwrites fresh state)
- subscriptions/timers on the changed paths without a matching teardown
