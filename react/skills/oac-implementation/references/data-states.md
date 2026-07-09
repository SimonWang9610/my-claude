---
title: Render Every State the Contract Promises
impact: HIGH
impactDescription: rendering only the success path ships blank screens and crashes on loading/error/empty
tags: async, loading, error, empty, tanstack-query, mutations, error-boundary
---

## Render Every State the Contract Promises

A contract that says "shows the camera list" implies four states, not one. Handle each
explicitly; do not collapse them into a single happy path that blanks or throws on the rest.

| State | TanStack Query v5 signal | What to render |
|-------|--------------------------|----------------|
| Loading | `isPending` | Skeleton/spinner sized to the content, not a layout-shifting flash |
| Error | `isError` (+ `error`) | An error message the user can act on + a retry (`refetch`), never a blank screen |
| Empty | `data` present, but zero-length / no records | An empty-state distinct from loading ("No cameras yet"), not a bare `[]` |
| Success | `data` present, non-empty | The content |

```tsx
// ✗ renders success only — blank on pending, crash on error, ambiguous on empty
function CameraList() {
  const { data } = useQuery(cameraKeys.list())
  return <>{data.map((c) => <CameraRow key={c.id} camera={c} />)}</>
}

// ✓ every promised state, in order
function CameraList() {
  const { data, isPending, isError, error, refetch } = useQuery(cameraKeys.list())
  if (isPending) return <ListSkeleton rows={6} />
  if (isError)   return <ErrorPanel error={error} onRetry={refetch} />
  if (data.length === 0) return <EmptyState title="No cameras yet" />
  return <>{data.map((c) => <CameraRow key={c.id} camera={c} />)}</>
}
```

**Mutations expose their own states** — a write is not fire-and-forget. `isPending` disables the
trigger and shows progress; `isError` surfaces a recoverable message; success confirms
(toast/close/navigate). Hand-rolled `useState` pending/error flags around a mutation are the
signal to reach for the React 19 form/action idioms — see `react19-modern-apis`.

```tsx
const { mutate, isPending, isError } = useMutation({ mutationFn: api.rename })
<Button onClick={() => mutate(next)} disabled={isPending}>
  {isPending ? 'Saving…' : 'Save'}
</Button>
{isError && <FormError>Couldn't save — try again.</FormError>}
```

**Boundaries vs inline state.** Async failures (a rejected query) render as inline error state
as above. Unexpected render-time throws are caught by an error boundary around the unit — inline
`try/catch` cannot catch a child's render error. A silently swallowed `catch {}` that returns
nothing is worse than a throw: it produces a blank UI with no signal. Surface, don't swallow.
