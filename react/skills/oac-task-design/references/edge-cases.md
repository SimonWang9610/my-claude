# Edge-case enumeration

For each unit, walk the four classes below and emit one edge-case test task for every class that
applies — unless an AC task already asserts that exact outcome (then skip; don't duplicate).
Assert the **user-visible** result, not that a mock was called.

## Which classes apply per unit kind
| Unit kind            | error | empty | loading | boundary |
|----------------------|:-----:|:-----:|:-------:|:--------:|
| Component (renders query data) | ✔ | ✔ | ✔ | ✔ (prop/input at documented limit) |
| Hook wrapping a query          | ✔ | ✔ | ✔ | — |
| Zustand store                  | — | — | — | ✔ (clamp / invalid input / reset) |
| Service / API module           | ✔ (maps failure to typed error) | — | — | ✔ (pagination last page, max page size) |

## Trigger → assertion by class

### Error
- **Trigger:** TanStack Query `isError` (MSW handler returns 500), or a mutation `onError`.
- **Assert:** `screen.findByRole('alert')` / the contract's error copy is rendered. Retry control
  enabled if the contract promises one.

### Empty
- **Trigger:** query resolves to `[]` / `null` data.
- **Assert:** the empty-state message renders (`getByText(/no .* match/i)`) and **zero** result rows
  (`queryAllByRole('row')` length 0) — not a bare blank region.

### Loading
- **Trigger:** query `isPending` (MSW handler delayed).
- **Assert:** skeleton or `getByRole('progressbar')` is shown, and there is **no flash** of the empty
  or error state before data arrives.

### Boundary
- **Trigger:** input/prop at its documented limit — max text length, submit disabled while invalid,
  pagination on the last page, a store value clamped to its range.
- **Assert:** the control's observable state at the limit — `toBeDisabled()` / `toBeEnabled()`, the
  rendered clamped value, "Next" absent on the last page.

## Anti-patterns (do not emit these as edge tasks)
- Asserting `expect(mockFetch).toHaveBeenCalled()` instead of what the user sees.
- An edge task with no `Traces to:` contract unit — that is an orphan.
- Re-covering an outcome an AC test already asserts.
