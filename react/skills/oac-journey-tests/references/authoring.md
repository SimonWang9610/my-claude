# Authoring journey tests

A journey drives the real component tree through user-visible interactions and intercepts its
writes at the network boundary with MSW.

## Page object

One page object per feature view. Expose stable locators (prefer role / label / test-id over text)
for every element the approved journeys touch, and keep selectors here — not inline in tests — so a
UI rename fixes one file. Add missing test-ids to the implementation only with explicit sign-off (a
QA stage must not silently change the code under test).

## Driving the app

Use a harness or route that renders the feature in a known state seeded by params, so a journey
starts deterministically without manual setup. If the feature is not yet reachable, test through the
nearest consumer and note the gap.

## Test harness (Vitest + RTL)

### QueryClient setup

Give every test file a fresh `QueryClient` with `retry: false` so network failures surface
immediately and don't bleed between tests.

```ts
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render } from '@testing-library/react';

function makeClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderWithProviders(ui: React.ReactElement) {
  const client = makeClient();
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}
```

### User interactions

Use `userEvent.setup()` — never bare `fireEvent` — so pointer and keyboard events fire in the
correct sequence.

```ts
import userEvent from '@testing-library/user-event';

const user = userEvent.setup();
await user.click(screen.getByRole('button', { name: /submit/i }));
await user.type(screen.getByLabelText(/email/i), 'user@example.com');
```

### Async assertions

Query by role, label, or text before falling back to `data-testid`. Use `findBy*` for async
content — avoid `waitFor(() => getBy*)`.

```ts
// preferred
const heading = await screen.findByRole('heading', { name: /success/i });

// also fine for checking non-existence after an action
await screen.findByText(/saved/i);
expect(screen.queryByRole('alert')).not.toBeInTheDocument();
```

## Happy vs error paths

- **Happy path** — the MSW handler returns success for the feature's writes; assert the
  user-visible success outcome.
- **Error path** — override the handler to fail (4xx/5xx or a network error) and assert the
  user-visible error surface. Every write must have at least one error-path journey.
- Track intercepted write requests so a silently-changed endpoint surfaces as an unmatched
  MSW request rather than a falsely-green test.

## Naming & grouping

Group tests by user story (one `describe` block per `US-*`); name each `it` by its `J-<n>` and
the ACs it covers, so a failure names both the journey and the criterion.

```ts
describe('US-1: Door management', () => {
  it('J-1 [AC-1.1, AC-1.2]: operator creates a door and sees it in the list', async () => {
    // ...
  });

  it('J-2 [AC-1.3]: server error on create shows inline error message', async () => {
    // ...
  });
});
```

## Traceability manifest

After authoring, write a manifest mapping journey → test → AC. It is an auditable coverage
deliverable, not a second approval gate.
