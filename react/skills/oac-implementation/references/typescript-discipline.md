---
title: Type the Unit Strictly
impact: HIGH
impactDescription: any and boolean-soup state let malformed data and impossible states compile
tags: typescript, any, unknown, discriminated-union, satisfies, props
---

## Type the Unit Strictly

Types are the cheapest correctness check the contract gives you. Keep them honest.

**No `any`.** It disables checking and silently propagates. At untyped boundaries (JSON,
`localStorage`, third-party `any`) accept `unknown` and narrow before use.

```tsx
const raw: unknown = JSON.parse(text)
if (isCameraConfig(raw)) applyConfig(raw)      // user-defined type guard narrows unknown
```

**Model variant/async state as a discriminated union — never a bag of booleans.** Booleans
admit impossible states (`isLoading && isError`); a tagged union makes them unrepresentable and
forces an exhaustive `switch`.

```tsx
// ✗ four booleans encode 16 states, most impossible
type State = { isLoading: boolean; isError: boolean; data?: Camera[]; error?: Error }

// ✓ exactly the reachable states, exhaustively handled
type State =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; cameras: Camera[] }

function render(s: State) {
  switch (s.status) {
    case 'loading': return <Spinner />
    case 'error':   return <ErrorPanel error={s.error} />
    case 'ready':   return <Grid cameras={s.cameras} />
    // no default: a new variant becomes a compile error, not a silent blank
  }
}
```

**`satisfies` keeps literal types while checking shape** — use it for fixtures, config maps, and
query-option objects instead of a widening annotation:

```tsx
const keys = { list: ['cameras'], detail: (id: string) => ['cameras', id] } satisfies QueryKeys
```

**Type the platform surface, don't paper over it.** Typed refs (`useRef<HTMLDivElement>(null)`,
not `useRef(null)`); typed events (`React.PointerEvent<HTMLDivElement>`); exact prop types via a
plain typed function — not `React.FC`, which implicitly adds `children` and obscures the props.

```tsx
// ✗                                              // ✓
const Tile: React.FC<TileProps> = ({ c }) => …    function Tile({ c }: TileProps) { … }
```

**Don't launder types with `!` or `as`.** A non-null assertion on contract/query data (`data!.id`)
or a cast to silence an error hides the very case the contract told you to handle — narrow it
(`if (!data) return <Empty/>`) instead.
