---
title: React 19 Idioms over Legacy Ceremony
impact: LOW
impactDescription: forwardRef wrappers and hand-rolled pending flags are ceremony that drifts and hides bugs the built-ins handle
tags: react19, ref-as-prop, useActionState
---

**Rule:** `ref` is a prop (no `forwardRef`); `use(Context)` where conditional reading helps;
form/mutation pending state from `useActionState`/`useOptimistic`.

- CORRECT Example:

```tsx
function Input({ ref, ...props }: InputProps & { ref?: Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props}/>
}

const [state, submit, isPending] = useActionState(async (_prev, form) => save(form), initial)
```

- BAD Example:

```tsx
const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => <input ref={ref} {...props}/>)

const [isPending, setIsPending] = useState(false)
const onSubmit = async () => { setIsPending(true); try { await save(form) } finally { setIsPending(false) } }
```
