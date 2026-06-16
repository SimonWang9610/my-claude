---
title: Use React 19 Idioms
impact: LOW-MEDIUM
impactDescription: legacy ceremony adds noise and will be deprecated
tags: react19, forwardRef, use, context, compiler
---

## Use React 19 Idioms

On React 19, flag these legacy patterns in reviewed code:

**`forwardRef` → ref as a prop:**

```tsx
// Legacy
const Tile = forwardRef<HTMLDivElement, TileProps>((props, ref) => <div ref={ref} {...props} />)
// React 19
function Tile({ ref, ...props }: TileProps & { ref?: Ref<HTMLDivElement> }) {
  return <div ref={ref} {...props} />
}
```

**`useContext(Ctx)` → `use(Ctx)`**, and `<Ctx.Provider value=...>` → `<Ctx value=...>`. `use` may also be called conditionally, which `useContext` could not.

**Manual memoization ceremony**: if the project has the React Compiler enabled, blanket `useMemo`/`useCallback`/`memo` wrapping is noise — recommend removing ceremony that exists only "for performance" (keep `useMemo` that guards genuinely expensive computation, and any memoization whose referential stability is a semantic contract, e.g., effect deps). If the Compiler is *not* enabled, do not flag memoization — defer judgment to `react-performance-review`.

Check `vite.config`/`babel` for `babel-plugin-react-compiler` before making compiler-dependent recommendations; report which case applies.
