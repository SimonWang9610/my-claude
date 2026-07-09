# Failing reproduction test (Mode 1)

A repro test must be **named** (the AC-ID in the `describe` label so coverage is greppable),
**deterministic** (no wall-clock, random, network, or ordering dependence — MSW handles the
network), and **failing before any fix exists for the stated reason**. Author it under the
`oac-test-contract` rules; phrase the asserted behavior with the `oac-acceptance-criteria`
observable-phrasing contract.

## Skeleton

```tsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { server } from '@/test/msw/server';
import { http, HttpResponse } from 'msw';

// describe label leads with the AC-ID → `grep -r "AC-3.2" src/` finds this repro
describe('AC-3.2 cart total reflects renamed API item field', () => {
  it('shows the summed total, not $0.00, when the cart has items', async () => {
    // Arrange: reproduce the exact input that triggers the defect (typed MSW handler).
    server.use(
      http.get('/api/cart/:id', () =>
        HttpResponse.json({ items: [{ id: 'a', price: 1200 }] } satisfies CartResponse),
      ),
    );
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    render(
      <QueryClientProvider client={client}>
        <OrderTotal cartId="a" />
      </QueryClientProvider>,
    );

    // Assert the OBSERVABLE correct behavior (the AC). Pre-fix this fails: renders "$0.00".
    expect(await screen.findByText('$12.00')).toBeInTheDocument();
  });
});
```

## Gate before recording

Run the test. It MUST fail, and the failure line must be the asserted behavior (e.g.
`Unable to find text "$12.00"`), for the root cause you named — not a setup/import error.

- A **passing** repro means it doesn't capture the defect → rewrite until it fails for the right
  reason.
- A failure from a typo, missing provider, or unhandled MSW route is not a valid repro → fix the
  harness, not the assertion.

Record the repro test's file path and the observed pre-fix failure line in `analysis.md`.
