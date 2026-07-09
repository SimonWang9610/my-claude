---
title: Split Contexts by Change-Rate; Separate State from Dispatch
impact: MEDIUM-HIGH
impactDescription: one fat context re-renders all consumers on any change
tags: rerender, context, provider
---

## Split Contexts by Change-Rate; Separate State from Dispatch

Every consumer of a context re-renders when the context value changes — there is no selector. Two standard defects:

1. **Fat context**: rarely-changing config bundled with rapidly-changing state; the config consumers re-render at the fast field's rate.
2. **Unstable value**: `<Ctx value={{ user, setUser }}>` creates a fresh object per provider render, re-rendering every consumer even when nothing changed.

**Correct:**

```tsx
// Split by change-rate, and state from actions:
const SessionContext = createContext<Session | null>(null)        // changes rarely
const PlaybackStateContext = createContext<PlaybackState | null>(null) // changes often
const PlaybackActionsContext = createContext<PlaybackActions | null>(null) // never changes

function PlaybackProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initial)
  const actions = useMemo(() => bindActions(dispatch), [])         // stable forever
  return (
    <PlaybackActionsContext value={actions}>
      <PlaybackStateContext value={state}>{children}</PlaybackStateContext>
    </PlaybackActionsContext>
  )
}
```

Buttons that only dispatch consume the actions context and never re-render with state. If a context needs per-field subscription granularity, that's the signal it should be a Zustand store instead — recommend the migration rather than fighting context.
