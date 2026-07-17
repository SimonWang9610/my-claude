# Build components — contract surface and render discipline

## Implement exactly the contract's surface

Props name-for-name, type-for-type; no undeclared props, no widened optionals; every state
in "States exposed" rendered with its observable signal. A case the contract missed is a
**design gap** (raise it), not a new prop.

```tsx
// contract: DeviceTile({ device }) · states: unknown | online | offline
// ✗ undeclared `showLabel`; promised 'unknown' state never rendered
function DeviceTile({ device, showLabel = true }) { return <Tile>{device.name}</Tile> }
// ✓
function DeviceTile({ device }: DeviceTileProps) {
  if (device.status === 'unknown') return <UnavailableTile />
  return <Tile status={device.status}>{device.name}</Tile>
}
```

## Render every data state

A data-backed component renders all four — loading · error · empty · success. Blank on
pending, crash on error, and indistinguishable empty are the three default bugs.

```tsx
if (isPending) return <Skeleton />
if (isError) return <ErrorPanel error={error} />
if (!data.length) return <Empty />
return <>{data.map(renderRow)}</>
```

## Honest types

No `any`, no `as`/`!` laundering. Variant and async state is a discriminated union, not a
bag of booleans — impossible states (`isLoading && isError`) must not compile.

```ts
// ✗ type State = { isLoading: boolean; isError: boolean; data?: Device[] }
// ✓
type State =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'ready'; devices: Device[] }
```

## Never define a component inside a component

An inline definition is a new type every render — the subtree unmounts and remounts,
losing state (a playing video restarts, form input vanishes). Hoist to module scope.

```tsx
// ✗ function Panel() { function Badge() {…} return <Badge /> }
// ✓ module-scope Badge, composed by Panel
```

## Semantic elements — the contract's signals must be queryable

Interactive elements are real `<button>`/`<input>`/`<a>`, never clickable divs; each
exposed state renders a role/label/aria signal; dialogs move focus on open. The contract's
"observable signal" is only real if a test can find it by role — an unsemantic
implementation breaks the Test seam.

```tsx
// ✗ <div onClick={save}>Save</div>                      // no role, no keyboard, unqueryable
// ✓ <button onClick={save} disabled={isPending}>Save</button>
// ✓ error state: <p role="alert">{error.message}</p>
```

## Stable keys

Keys are stable identities — never array indexes on lists that can reorder, filter, or
insert; index keys re-associate item state with the wrong row.

```tsx
// ✗ {devices.map((d, i) => <DeviceRow key={i} device={d} />)}
// ✓ {devices.map(d => <DeviceRow key={d.id} device={d} />)}
```

## Composition details

- Logic lives in the hooks the contract names; the component composes them and renders —
  it adds no second responsibility.
- Ternary over `&&` when the condition can be a number/NaN/string — `{count && <X/>}`
  renders a literal `0`.

```tsx
{offlineCount > 0 ? <OfflineBanner count={offlineCount} /> : null}
```
