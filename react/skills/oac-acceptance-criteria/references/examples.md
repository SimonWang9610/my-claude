# AC anti-patterns — before/after with test-name skeletons

Four recurring anti-patterns, each shown as the ill-formed criterion, the corrected
observable form, and the test-name skeleton it produces.

## Contents

- [1. The cache-invalidation no-op (spy-on-the-call AC)](#1-the-cache-invalidation-no-op-spy-on-the-call-ac)
- [2. The mock-call assertion (callback fired, nothing happened)](#2-the-mock-call-assertion-callback-fired-nothing-happened)
- [3. The render-it-back tautology](#3-the-render-it-back-tautology)
- [4. The one-shot ban that decays](#4-the-one-shot-ban-that-decays)

---

## 1. The cache-invalidation no-op (spy-on-the-call AC)

A feature toggles a query-cache invalidation; the AC is written as "shall call
`invalidate(...)`". A spy fires even when the key set is empty, so the test stays green
while nothing refetches. `invalidateQueries` only refetches queries that match the key
([tanstack.com](https://tanstack.com/query/latest/docs/framework/react/guides/query-invalidation)).

**Reject:**
```
AC-9: When the user toggles "Include sub-scopes", the system shall call
      invalidate(queryClient).
      // "invalidate(queryClient)" is not a real API; the real call is
      // queryClient.invalidateQueries({ queryKey: [...] }) — but even with
      // the correct call, asserting that the call was made is the wrong AC shape.
```

**Require:**
```
AC-9.1: Given the device list has loaded for the parent scope, when the user toggles
        "Include sub-scopes" on, then the device list refetches and sub-scope device
        rows appear in the table.

AC-9.2: Given sub-scope rows are shown, when the user toggles "Include sub-scopes" off,
        then those rows disappear and only parent-scope devices remain.
```

**Test-name skeleton:**
```ts
describe('AC-9.1: toggling "include sub-scopes" on shows sub-scope devices', () => {
  it('refetches and renders sub-scope rows after the toggle', async () => {
    // assert (observable): a sub-scope device row is now in the document
  })
})
```

---

## 2. The mock-call assertion (callback fired, nothing happened)

An interactive control is specced as "the `onSort` callback shall be called with the
column id". The test asserts a spy fired but never checks that rows reordered. The durable
assertion is on the rendered output the user sees, not an internal callback
([kentcdodds.com](https://kentcdodds.com/blog/testing-implementation-details)).

**Reject:**
```
AC-14: The onSort callback shall be called with the column id and direction when a header is clicked.
```

**Require:**
```
AC-14.3: Given the table is rendered with unsorted rows, when the user clicks a column
         header, then the rows reorder by that column and the header shows the sort
         direction (aria-sort).
```

**Test-name skeleton:**
```ts
describe('AC-14.3: clicking a column header sorts rows by that column', () => {
  it('reorders rows ascending and sets aria-sort=ascending on first click', () => {
    // assert (observable): first row text is lowest value; header aria-sort=ascending
    // optional secondary: onSort mock was called — but row order is the primary signal
  })
})
```

---

## 3. The render-it-back tautology

A display component is specced as "the message shall be displayed". A test renders with a
`message` prop then asserts `screen.getByText(message)` using the same variable — a
mathematical identity that cannot fail. The criterion is too loose, inviting a
self-confirming assertion
([testing-library.com](https://testing-library.com/docs/guiding-principles/)).

**Reject:**
```
AC-1: The notification message shall be displayed.
```

**Require:**
```
AC-1.1: Given an unread notification of type "alarm", when the card renders, then the
        alarm icon is shown and the card has the unread visual treatment (accessible
        "unread" state), alongside the notification's title text.

AC-1.2: Given a read notification, when the card renders, then the card does NOT show
        the unread state and the mark-as-read control is absent.
```

**Test-name skeleton:**
```ts
describe('AC-1.1: unread alarm notification shows alarm icon and unread state', () => {
  it('renders the alarm icon and exposes an unread accessible state', () => {
    // assert (observable): alarm icon by role/label; container has unread marking
  })
})
describe('AC-1.2: read notification omits unread state and mark-as-read control', () => {
  it('does not render the mark-as-read control once read', () => {
    // assert (observable): queryByRole('button', { name: /mark as read/i }) is null
  })
})
```

---

## 4. The one-shot ban that decays

A pattern ban (no hardcoded hex colours) is "enforced" by a one-shot grep at review.
Once merged, nothing re-runs it. A check that runs only once decays to zero enforcement
— the durable form is a resident CI guard that runs on every change
([eslint.org](https://eslint.org/docs/latest/use/core-concepts/)).

**Avoid:**
```
NFR-1: grep -r '#[0-9a-fA-F]{6}' src/components returns zero matches.
```

**Require:**
```
NFR-1: Given the app is viewed with system dark-mode active, when any surface in this
       feature renders, then every colour resolves through the design-token CSS-variable
       chain — no hardcoded hex literal appears in component source. (Enforce as an
       enduring CI guard, not a one-shot grep.)
```

**Test/guard skeleton:**
```ts
describe('NFR-1: no hardcoded hex literals in component source', () => {
  // resident source-scan guard — see the test-contract skill for implementation
})
```

---

See `ac-format.md` for the ID and phrasing rules. See `traceability.md` for how these
IDs flow into `describe`/`it` names and `--tags-filter` queries.
