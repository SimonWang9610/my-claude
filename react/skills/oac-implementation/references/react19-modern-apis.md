---
title: Reach for React 19 Idioms
impact: MEDIUM
impactDescription: the modern APIs cut hand-rolled ceremony that drifts and hides bugs
tags: react19, ref-as-prop, use, actions, useActionState, useOptimistic, compiler
---

## Reach for React 19 Idioms

On React 19 write the modern form directly; the legacy shape below is ceremony that adds noise
and, for hand-rolled pending state, a class of bugs.

**`ref` is an ordinary prop — no `forwardRef`:**

```tsx
// Legacy                                             // React 19
const Tile = forwardRef<HTMLDivElement, TileProps>(   function Tile(
  (props, ref) => <div ref={ref} {...props} />)         { ref, ...props }: TileProps & { ref?: Ref<HTMLDivElement> }
                                                       ) { return <div ref={ref} {...props} /> }
```

**`use(Context)` over `useContext(Context)`**, and `<Ctx value={…}>` over `<Ctx.Provider value={…}>`.
`use` may be called conditionally (after an early return, inside a branch), which `useContext`
could not. `use(promise)` also unwraps a promise with Suspense — but for server data prefer a
TanStack Query hook over hand-thrown promises.

**Actions for form submit and mutations — not hand-rolled `isPending`/`error`.** If a component
wires its own `useState(false)` pending flag and `useState<string|null>` error around an async
call, replace it with `useActionState` (submit + pending + returned state) or wrap the optimistic
UI in `useOptimistic`.

```tsx
// Hand-rolled — the pattern to replace
const [isPending, setIsPending] = useState(false)
const [error, setError] = useState<string | null>(null)
async function onSubmit(e: FormEvent) {
  setIsPending(true)
  try { await api.save(data) } catch (err) { setError(String(err)) } finally { setIsPending(false) }
}

// React 19 — useActionState drives pending + result; wire it to <form action={submit}>
const [state, submit, isPending] = useActionState(
  async (_prev: ActionState, form: FormData): Promise<ActionState> => {
    try { await api.save(Object.fromEntries(form)); return { ok: true, error: null } }
    catch (e: unknown) { return { ok: false, error: String(e) } }
  },
  { ok: false, error: null },
)
```

`useOptimistic` shows the intended result instantly and reconciles when the mutation settles —
reach for it when the contract promises immediate feedback (a toggle, a rename) on a write.

**Compiler-aware memoization — decide this once per project, up front.** Check
`vite.config`/`babel` for `babel-plugin-react-compiler`:

- **Enabled:** the compiler inserts memoization for you. Do *not* hand-write `useMemo`/
  `useCallback`/`memo` for referential stability — it is redundant. Keep only `useMemo` that
  guards a genuinely expensive computation, and memoization whose stable identity is a semantic
  contract (an effect dependency, a value passed to a non-reactive subscriber). Remove leftover
  "for performance" wrapping.
- **Not enabled:** memoization is manual — apply the boundary rules in the performance corpus
  (`rerender-memo-boundaries`, `rerender-functional-updates`, `render-hoist-static-jsx`).

Report which case applies before making any memoization change, since it inverts the advice.
