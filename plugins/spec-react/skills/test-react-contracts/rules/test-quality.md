# Test quality — cross-cutting rules

Each rule closes a way a green test can lie.

## Labels carry the requirement ID

Every test embeds its AC/NFR/journey ID verbatim at the front of its label —
`grep -r "AC-2.1"` answers "is it covered?".

```ts
// ✗ it('sorts on header click')
// ✓ describe('AC-14.3: clicking a header sorts the table', …)
```

## Assert outcomes, not implementation

The primary assertion is the observable signal the contract exposes (rendered text,
role/aria state, returned value) — never a spy alone, never internal state.

```ts
// ✗ passes even if the UI never updates
expect(onSort).toHaveBeenCalledWith('name', 'asc')
// ✓ the observable result; the spy at most secondary
expect(screen.getByRole('columnheader', { name: /name/i })).toHaveAttribute('aria-sort', 'ascending')
```

## Production-typed fixtures

Every fixture is `satisfies <ProdType>`; every MSW stub returns the production response
type — a required field added to the type must break the fixture at compile time, never
drift silently.

```ts
const dev = { id: '1', name: 'Door', online: true } satisfies Device
```

## Pattern-ban NFRs are resident CI guards

A "no occurrences of X in source" NFR is a checked-in glob-scan test or lint rule running
on every change — a one-shot review grep vanishes after merge.

## The mutation litmus

For every assertion ask: *if the production condition were inverted, would this test
fail?* If not, it's a proxy or a tautology — pick a different signal or harness.

## A failing test fails for the right reason

Before fixing code against a red test, read the failure: it must name the behaviour gap,
not a harness artifact (missing provider, unawaited async, wrong query). And the inverse
discipline from implementation binds here too: tests define behaviour — never weaken an
assertion or widen a query to make failing code pass.
