# Authoring journey tests

A journey drives the **real component tree** through user-visible interactions and intercepts its
writes at the network boundary with MSW. Stack: Vitest + React Testing Library + MSW +
`userEvent` — match the project's existing test setup; this file carries the discipline, not the
tooling.

## Page object

One page object per feature view. Keep every selector here — not inline in tests — so a UI rename
fixes one file. Prefer role / label over test-id, test-id over text. Adding a missing test-id to
the implementation requires explicit sign-off — a QA stage must not silently change the code
under test.

## Harness

- A route or harness renders the feature in a known state seeded by params, so every journey
  starts deterministically. Feature not reachable yet → test through the nearest consumer and
  note the gap.
- Fresh `QueryClient` per test file with `retry: false`, so failures surface immediately and
  nothing bleeds between tests.

```tsx
function renderWithProviders(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>)
}
```

## Driving and asserting

- Interactions via `userEvent.setup()` — never bare `fireEvent` — so pointer/keyboard events fire
  in the correct sequence.
- Async content via `findBy*` (not `waitFor(() => getBy*)`); query by role/label first.

```ts
const user = userEvent.setup()
await user.type(screen.getByLabelText(/name/i), 'Door A')
await user.click(screen.getByRole('button', { name: /save/i }))
expect(await screen.findByRole('heading', { name: /saved/i })).toBeInTheDocument()
expect(screen.queryByRole('alert')).not.toBeInTheDocument()
```

## Happy vs error paths

- **Happy path** — MSW handlers return success for the journey's writes; assert the user-visible
  success outcome.
- **Error path** — override the handler to fail (4xx/5xx/network error); assert the user-visible
  error surface. Every write journey has one, per the approved plan.
- Track intercepted write requests, so a silently-changed endpoint surfaces as an unmatched MSW
  request instead of a falsely-green test.

## Naming & grouping

One `describe` per user story; each `it` named by its `J-<n>` and the ACs it covers — a failure
then names both the journey and the criterion, and coverage stays a grep.

```ts
describe('US-1: Door management', () => {
  it('J-1 [AC-1.1, AC-1.2]: operator creates a door and sees it in the list', async () => { /* … */ })
  it('J-2 [AC-1.3]: server error on create shows inline error, form stays open', async () => { /* … */ })
})
```

## Manifest

After authoring, write the journey → test file → AC-IDs manifest next to the plan. Every approved
journey appears exactly once; a journey with no test line means authoring isn't done.
