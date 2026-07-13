# Change surface & blast radius (Mode 2)

## 1. Reverse-import blast radius

For each unit the change edits, the blast radius is its **external importers** — every other
module that imports it. Changing the unit's behavior or signature can break each of them.

```bash
# consumers of a hook/component/store/util (adjust the specifier to how it's exported)
grep -rln "from '[^']*useCartTotal'" src/
grep -rln "useCartTotal" src/            # widen if re-exported through a barrel
```

- Walk barrels (`index.ts`) — a unit re-exported through one has importers that reference the
  barrel path, not the file.
- For a Zustand store, the importers are the components/hooks calling its selectors; a changed
  selector shape ripples to all of them.
- For a TanStack Query key or `select` shape, the importers are every `useQuery`/`useMutation`
  site keyed on it — a key or shape change invalidates their cached reads.

## 2. Read-only adopted / shared components

Among the touched units and their importers, flag every **adopted shared component** — a unit
owned/consumed by code outside this change's feature. An adopted shared unit is **read-only**:

- **Copy it, never modify it in place**, unless the caller explicitly approves editing the shared
  unit. In-place edits to a shared unit change behavior for every external importer — that is the
  blast radius realized as a regression.
- If the change genuinely needs different behavior, record the copy (a feature-local variant) as
  the action; do not silently fork or silently edit.
- If in-place modification looks unavoidable, stop and surface it to the caller with the importer
  list — the decision to touch a shared unit is theirs, not yours.

Distinguish ADOPTED (has external importers → read-only) from UNADOPTED (only this feature uses
it → safe to edit) exactly as the impact table's Read-only? column records.
