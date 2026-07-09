---
title: Get the Hooks Right
impact: HIGH
impactDescription: conditional hooks, lying deps, and state-mirroring effects cause stale UI and crashes
tags: hooks, rules-of-hooks, dependencies, derive-dont-store, effects
---

## Get the Hooks Right

**Rules of Hooks — non-negotiable.** Call hooks at the top level of a component or custom hook,
unconditionally, in the same order every render. No hooks inside conditions, loops, early
returns, or event handlers. Do the early return *after* the hooks, or lift the condition to a
parent that mounts different components.

```tsx
// ✗ hook after a conditional return — order changes between renders
function Panel({ id }: Props) {
  if (!id) return null
  const q = useQuery(cameraKeys.detail(id))    // sometimes called, sometimes not
}
// ✓ hooks first, branch on the result
function Panel({ id }: Props) {
  const q = useQuery({ ...cameraKeys.detail(id), enabled: !!id })
  if (!id) return null
  …
}
```

**Derive, don't store.** Anything computable from props, state, or a query result is computed
during render — never mirrored into `useState` + a syncing `useEffect`. The mirror guarantees a
stale frame and a double render.

```tsx
// ✗ derived state via effect — renders stale for one frame, then again
const [fullName, setFullName] = useState('')
useEffect(() => setFullName(`${first} ${last}`), [first, last])

// ✓ derive in render (wrap in useMemo only if the compute is genuinely expensive)
const fullName = `${first} ${last}`
```

**Effects are for external synchronization only** — subscribing to a store/socket, driving a
non-React widget (a video player, a map), reading/writing outside React. They are *not* for
transforming props into state and *not* for responding to a user event (do that in the handler).
If an effect has no external system on either side, it probably shouldn't exist.

**Dependency arrays must tell the truth.** List every reactive value the effect/callback reads.
Don't silence the linter by omitting a dep — stabilize the value instead (functional `setState`,
`useCallback`, a ref for values needed but not depended-on). Every subscription an effect opens
gets a matching teardown — see `hf-effect-cleanup`.

**Never `setState` during render** (outside the one documented derived-from-prev-props pattern) —
it loops. Compute the value inline; if it must reset on a prop change, prefer a `key` on the
child to remount it over an effect that resets state.
