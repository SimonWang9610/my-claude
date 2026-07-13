# Test strategy (T1–T5)

Decide **at design time** how every criterion will be verified, so test authoring becomes
mechanical — no test-shape decisions left to make while writing tests. Each rule closes a way a
green test can lie. Record the result in `design.md` ▸ **AC → Verification** — one row per
criterion: description · level · test location.

- **T1 · Traceable labels.** Every planned test embeds its AC/NFR ID verbatim at the front of its
  `describe`/`it` label, so `grep -r "AC-2.1" src/` answers "is it covered?".

  ```ts
  // ✗ identity unknown            // ✓ coverage is a grep
  it('sorts on header click')      describe('AC-14.3: clicking a header sorts the table', …)
  ```

- **T2 · Assert outcomes, not implementation.** The primary assertion is the observable signal the
  unit's contract exposes (rendered text, role/aria state, returned value) — never a spy alone.

  ```ts
  // ✗ passes even if the UI never updates
  expect(onSort).toHaveBeenCalledWith('name', 'asc')
  // ✓ the observable result is primary; the spy at most secondary
  expect(screen.getByRole('columnheader', { name: /name/i })).toHaveAttribute('aria-sort', 'ascending')
  ```

- **T3 · Production-typed fixtures.** Every fixture is `satisfies <ProdType>`; every network stub
  is typed with the production response type — adding a required field to the type must break the
  fixture at compile time, not drift silently.

  ```ts
  // ✗ drifts when Device grows a field    // ✓ compile error the moment it drifts
  const dev = { id: '1', name: 'Door' }    const dev = { id: '1', name: 'Door', … } satisfies Device
  ```

- **T4 · Real infrastructure for config NFRs.** An NFR naming a query-config value (`staleTime`,
  `retry`, `refetchOnWindowFocus`, …) is exercised inside a **real QueryClientProvider** — mocking
  the hook bypasses the very config the NFR specifies.

- **T5 · Pattern-ban NFRs become resident CI guards.** A "no occurrences of X in source" NFR gets a
  checked-in guard (a Vitest glob-scan test or an ESLint rule) that runs on every change — a
  one-shot review grep vanishes after merge.

**Mutation litmus (cross-cutting):** for every planned assertion ask — *if the production condition
were inverted, would this test fail?* If not, it's a proxy or a tautology; pick a different signal
(T2) or a different harness (T4).

## What the step decides

| Decision | Source |
|----------|--------|
| **Level** per criterion | the harness tier from the owning contract's **testability seam** — component via providers · hook via controlled inputs · service via its interface · CI guard |
| **Test location** | the planned test file, named after the owning unit |
| NFR class | standard (T1–T3) · config → real provider (T4) · pattern-ban → CI guard (T5) |
| Assertion target | the observable signal in the owning contract's **states it must expose** — lives there, not restated in the table |
