# Principle examples — P1–P7 right/wrong sketches

Right/wrong code sketches for the seven target-architecture principles enforced by this gate.
General best practices for a React 19 + Vite + TypeScript + Zustand + TanStack Query + MUI +
Vitest project; examples use a neutral "list + detail" feature (`useDevices`, `DeviceListPage`)
so they transfer to any domain. For violation signals and trigger crosswalk, see
[`principle-checks.md`](principle-checks.md).

| ID | Rule | Trigger | Problem class it prevents |
|----|------|---------|---------------------------|
| P1 | Server state in TanStack Query, never copied to Zustand/localStorage | new server data | dual-source-of-truth |
| P2 | Components render; logic in named single-responsibility hooks; soft LOC ceiling | new component/hook | God-component / God-hook |
| P3 | One owner per fact; derive client selection, never mirror with effects | selection alongside server data | prop→state sync |
| P4 | Writes via `useMutation`; errors via `onError`/`isError` | new write path | un-awaited / silent-error writes |
| P5 | Every unit renderable/invocable in isolation (testability seam) | any AC behavior | proxy tests + uncovered behavior |
| P6 | Token-layer selection rule for every color value | new color/theming | theme/dark-mode regressions |
| P7 | No module-scope mutable domain state; else `_resetForTest()` | new module-level var | untestable singleton / flaky tests |

---

## P1 — Server state lives in TanStack Query, never copied into Zustand or localStorage

**Rule.** Data that originates from a server API call is owned by `useQuery`/`useInfiniteQuery`.
Never copied into a Zustand slice, a `useState` local copy, or `localStorage`. Zustand owns
client UI state only (open modals, selected tab, sidebar collapse, theme preference).

**Rationale.** Copying server data into a second store creates two owners; the copy goes stale,
opts out of background refetching, and lets an assertion be true in one owner and false in the other.

```typescript
// RIGHT
const useDevices = () => useQuery({ queryKey: ['devices'], queryFn: fetchDevices });
const useDeviceStore = create<{ selectedId: string | null; select: (id: string) => void }>(
  (set) => ({ selectedId: null, select: (id) => set({ selectedId: id }) }),
);
function DevicePanel() {
  const { data: devices } = useDevices();
  const selectedId = useDeviceStore((s) => s.selectedId);
  const device = devices?.find((d) => d.id === selectedId) ?? null; // derived at read time
}

// WRONG
const useDeviceStore = create((set) => ({ devices: [], setDevices: (d) => set({ devices: d }) }));
function DevicePanel() {
  const { data } = useDevices();
  useEffect(() => { setDevices(data ?? []); }, [data]); // stale copy; opts out of background refetch
}
```

**Crosswalk:** `rules-architecture/state-no-server-data-in-stores.md`,
`rules-architecture/state-single-source-of-truth.md`,
`rules-architecture/state-ownership-decision.md`.

**Sources:** https://tanstack.com/query/v4/docs/framework/react/guides/does-this-replace-client-state · https://tkdodo.eu/blog/practical-react-query

---

## P2 — Components render; logic in named single-responsibility hooks; soft ceiling

**Rule.** A component file is a renderer: it composes JSX and calls hooks. Stateful logic,
effects, data fetching, and derived computation live in named hooks describing a concrete use
case (`useDeviceFilters`, `useDeviceSelection`). Soft ceiling: ~400 LOC for a component, ~300
LOC for a hook. Past the ceiling, split or carry an `// ARCH-EXCEPTION: <reason>` comment
approved at design exit.

**Rationale.** A God-component has no isolation seam — the only test path is to mock the whole
host, which assures nothing about the behavior inside. P2 is what makes P5 physically possible.

```typescript
// RIGHT: component renders; each hook is independently testable
function DeviceListPage() {
  const filters = useDeviceFilters();
  const { devices, isLoading } = useFilteredDevices(filters);
  const selection = useDeviceSelection(devices);
  return <DeviceListView filters={filters} devices={devices} selection={selection} />;
}

// WRONG: logic, effects, and JSX interleaved — no seam
function DeviceListPage() {
  const [devices, setDevices] = useState([]);
  const [filters, setFilters] = useState({ status: 'all' });
  useEffect(() => { fetchDevices().then(setDevices); }, []);
  useEffect(() => { /* clear selection when devices change */ }, [devices]);
  // 300+ more lines of interleaved logic and JSX
}
```

**Crosswalk:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/layer-feature-folders.md`,
`rules-architecture/query-no-effect-fetching.md`.

**Sources:** https://react.dev/learn/reusing-logic-with-custom-hooks · https://felixgerschau.com/react-hooks-separation-of-concerns/ · https://feature-sliced.design/

---

## P3 — One authoritative owner per fact; derive client selection, never mirror with effects

**Rule.** Every fact has exactly one owner. Keep the raw key in client state (Zustand or
`useState`) and derive the resolved entity at read time. Never use `useEffect` to keep a local
copy in sync with server data or a prop.

**Rationale.** A sync effect fires after render (stale frame visible) and races when two sources
update in different render cycles. Deriving at read time has no stale window and no race.

```typescript
// RIGHT
const selectedId = useDeviceStore((s) => s.selectedId);
const { data: devices } = useDevices();
const selectedDevice = devices?.find((d) => d.id === selectedId) ?? null;

// WRONG
const [selected, setSelected] = useState<Device | null>(null);
useEffect(() => {
  if (selected && !devices?.find((d) => d.id === selected.id)) setSelected(null);
}, [devices, selected]); // fires after render; stale frame visible
```

**Crosswalk:** `rules-architecture/state-derive-dont-store.md`,
`rules-architecture/state-no-prop-to-state-copy.md`,
`rules-architecture/query-select-transform.md`.

**Source:** https://tkdodo.eu/blog/deriving-client-state-from-server-state

---

## P4 — Writes via `useMutation`; errors via `onError`/`isError`

**Rule.** All writes (POST/PUT/PATCH/DELETE) use `useMutation`. Cache invalidation in `onSuccess`;
cleanup in `onSettled`; user-visible error state from `mutation.isError`/`mutation.error`. Prefer
`mutate` + `onError` for single writes; `mutateAsync` + `try/catch` only when chaining dependent
writes. Never fire a write as an un-awaited call in a handler; never swallow with `console.error`.

**Rationale.** An imperative write in a handler leaves no `isError` state for the UI, often
forgets cache invalidation, and un-awaited failures are never exercised by `mockResolvedValue` tests.

```typescript
// RIGHT
const saveMutation = useMutation({
  mutationFn: (payload: UpdateDevicePayload) => api.updateDevice(payload),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['devices'] }),
  onSettled: () => closeDialog(),
});
// {saveMutation.isError && <Alert>...</Alert>}
// <Button onClick={() => saveMutation.mutate(formValues)} disabled={saveMutation.isPending}>Save</Button>

// WRONG
async function handleSave() {
  try { await api.updateDevice(formValues); }
  catch (e) { console.error(e); } // no UI error, no cache invalidation
}
```

**Crosswalk:** `rules-architecture/query-mutation-invalidation.md`,
`rules-architecture/query-no-effect-fetching.md`,
`rules-architecture/query-key-factory.md`.

**Sources:** https://tanstack.com/query/v4/docs/framework/react/guides/mutations · https://blog.logrocket.com/deep-dive-mutations-tanstack-query/

---

## P5 — Every unit must be renderable/invocable in isolation (testability seam)

**Rule.** Before a spec exits design, every behavior named in an AC must have a testability seam:
a component renderable with a providers wrapper, or a hook callable with `renderHook`, in a test
that controls all its inputs. A unit testable only by mocking its parent's entire hook is not
independently verifiable and must be decomposed.

**Rationale.** When the only way to reach a behavior is `vi.mock` of the host, the behavior under
test sits inside the mock and is never exercised — a proxy test.

```typescript
// RIGHT: hook is independently invocable; AC maps to a real assertion
function useDeviceFilters(initialStatus = 'all') {
  const [status, setStatus] = useState(initialStatus);
  const [search, setSearch] = useState('');
  return { status, setStatus, search, setSearch };
}
it('AC-4.2: resetting filters sets status to "all" and clears search', () => {
  const { result } = renderHook(() => useDeviceFilters('offline'));
  act(() => { result.current.setSearch('cam'); result.current.setStatus('all'); });
  expect(result.current.status).toBe('all');
  expect(result.current.search).toBe('');
});

// WRONG: behavior buried in a God-hook
vi.mock('../hooks/useDeviceData', () => ({ useDeviceData: vi.fn(() => mockData) }));
// → filter/tab logic inside useDeviceData is invisible to the test
```

**Crosswalk:** `rules-architecture/compose-extract-hooks.md`,
`rules-architecture/compose-children-over-render-props.md`,
`rules-architecture/layer-service-isolation.md`.

**Source:** https://testing-library.com/docs/guiding-principles/

---

## P6 — Token-layer selection rule for every color value

**Rule.** Select the correct token layer for every color value per this table. (Token names below
are placeholders — substitute the project's own design-token API; the layering discipline is what generalizes.)

| Context | Correct | Wrong |
|---------|---------|-------|
| MUI `createTheme`/`ThemeProvider` | CSS custom property `var(--app-surface)` | hard-coded hex `#1A1A1A` |
| Component `sx` / `styled()` | semantic-color object backed by CSS vars | static hex scale or raw Tailwind class |
| Tailwind utility in JSX | semantic token class (`bg-app-surface`) | raw scale class (`bg-gray-900`) |
| SVG `fill`/`stroke` | static hex token — SVG cannot resolve CSS vars | CSS-var-backed token or Tailwind class |

**Rationale.** Theming (dark mode) only works if color flows through the token layer the theme
switch controls. A hard-coded hex bypasses the switch; a JSDOM test asserting class presence
can't resolve a CSS variable — so the regression is invisible until production.

```tsx
// RIGHT
<Box sx={{ backgroundColor: semanticColors.surfacePrimary }} />
<div className="bg-app-surface text-app-onSurface" />
<path fill={colors.iconDefault} d="..." />

// WRONG
<Box sx={{ backgroundColor: '#1A1A1A' }} />
<div className="bg-gray-900" />
```

**Crosswalk:** no bundled architecture rule file maps directly — confirm against the project's
design-token documentation and pair with a CI guard banning raw hex and scale classes.

**Sources:** https://mui.com/material-ui/customization/dark-mode/ · https://www.w3.org/TR/css-variables-1/

---

## P7 — No module-scope mutable domain state; if unavoidable, export `_resetForTest()`

**Rule.** Module-level mutable variables (`let`, mutable `Map`, class instances) that accumulate
domain state across renders or test runs are prohibited. Use React context, Zustand, or `useRef`.
If a module-scope Map is genuinely needed for performance, the module must export
`_resetForTest()` and every test file must call it in `beforeEach`.

**Rationale.** Module-scope mutable state persists across test cases — flaky, order-dependent CI.
A lazily-wired module-scope registry is also often empty at test time, turning an AC into a
silent no-op.

```typescript
// RIGHT: singleton scoped to context; resets naturally on unmount
const SearchContext = createContext<MiniSearch | null>(null);
export function SearchProvider({ children }: { children: ReactNode }) {
  const [index] = useState(() => new MiniSearch({ fields: ['title', 'body'] }));
  return <SearchContext.Provider value={index}>{children}</SearchContext.Provider>;
}

// ALSO ACCEPTABLE: escape-hatch export for a performance-sensitive registry
const _runningRequests = new Map<string, AbortController>();
export const _resetForTest = () => _runningRequests.clear();

// WRONG: accumulates across tests, no reset
let searchIndex: MiniSearch | null = null;
export function getIndex() {
  if (!searchIndex) searchIndex = new MiniSearch({ fields: ['title'] });
  return searchIndex;
}
```

**Crosswalk:** `rules-architecture/zustand-slice-organization.md`,
`rules-architecture/state-ownership-decision.md`.

**Sources:** https://testing-library.com/docs/guiding-principles/ · https://vitest.dev/api/#beforeeach
