---
title: Use React 19 Idioms
impact: LOW-MEDIUM
impactDescription: legacy ceremony adds noise and will be deprecated
tags: react19, forwardRef, use, context, compiler, useActionState, useOptimistic
---

## Use React 19 Idioms

<!-- TOC -->
- [ref as a prop (no forwardRef)](#ref-as-a-prop)
- [Plain typed functions (no React.FC)](#plain-typed-functions)
- [use(Context) over useContext](#usecontext--useCtx)
- [useActionState and useOptimistic](#useactionstate-and-useoptimistic)
- [Memoization ceremony](#memoization-ceremony)
<!-- /TOC -->

On React 19, flag these legacy patterns in reviewed code:

### ref as a prop (no forwardRef)

```tsx
// Legacy
const Tile = forwardRef<HTMLDivElement, TileProps>((props, ref) => <div ref={ref} {...props} />)

// React 19 — ref is a normal prop; merge it into the props type
function Tile({ ref, ...props }: TileProps & { ref?: React.Ref<HTMLDivElement> }) {
  return <div ref={ref} {...props} />
}
```

### Plain typed functions (no React.FC)

`React.FC` and `React.FunctionComponent` implicitly type `children` and carry historical baggage. Use a plain typed function instead:

```tsx
// Incorrect
const CameraTile: React.FC<CameraTileProps> = ({ camera }) => { ... }

// Correct
function CameraTile({ camera }: CameraTileProps) { ... }
```

### use(Context) over useContext

**`useContext(Ctx)` → `use(Ctx)`**, and `<Ctx.Provider value=...>` → `<Ctx value=...>`. `use` may also be called conditionally, which `useContext` could not.

### useActionState and useOptimistic

When code hand-rolls async form/action state (loading flag + error state + data), prefer `useActionState`. When code implements manual optimistic UI with a separate `useState` that mirrors a pending mutation, prefer `useOptimistic`. Flag these opportunities but do not force-replace working code; flag and recommend.

```tsx
// Hand-rolled pattern to flag
const [isPending, setIsPending] = useState(false)
const [error, setError] = useState<string | null>(null)
async function handleSubmit(e: FormEvent) {
  setIsPending(true)
  try { await api.save(data) } catch (err: any) { setError(String(err)) }
  finally { setIsPending(false) }
}

// React 19 — useActionState
const [state, submitAction, isPending] = useActionState(
  async (_prev: ActionState, formData: FormData) => {
    try { await api.save(Object.fromEntries(formData)); return { ok: true } }
    catch (e: unknown) { return { ok: false, error: String(e) } }
  },
  { ok: false, error: null },
)
```

### Memoization ceremony

If the project has the React Compiler enabled, blanket `useMemo`/`useCallback`/`memo` wrapping is noise — recommend removing ceremony that exists only "for performance" (keep `useMemo` that guards genuinely expensive computation, and any memoization whose referential stability is a semantic contract, e.g., effect deps). If the Compiler is *not* enabled, do not flag memoization — defer judgment to `react-performance-review`.

Check `vite.config`/`babel` for `babel-plugin-react-compiler` before making compiler-dependent recommendations; report which case applies.
