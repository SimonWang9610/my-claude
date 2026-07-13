# Phrasing contract — observable Given/When/Then

Given `AC-<story#>.<n>` or `NFR-<n>` ID, phrase the criterion in observable Given/When/Then form, following [AC pattern](#ac-pattern) or [NFR pattern](#nfr-pattern) below.

## AC pattern
```
AC-1.1: Given [precondition], when [action or trigger], then [observable result].
```
The Then clause must be assertable **without reaching into the implementation's internals** — a
value a caller receives, a visible output, a persisted record, a status or state an observer can
read.

For behavior that varies only by data, express it as a single **Examples-table AC** rather than
many near-duplicate criteria, see [AC-table example](#ac-table-example).

### Observable examples:

- `AC-2.1: Given the device list has loaded, when the user clicks "Add Device", then the add-device drawer opens and the form fields are empty.`
- `AC-3.2: Given the user submits an invalid email, when the form is submitted, then an inline error "Enter a valid email address" appears below the email field.`
- `AC-4.1: Given a network error occurs during save, when the user clicks "Save", then an error toast "Failed to save — please try again" appears and the form remains open with input preserved.`

### Reject examples:

- `shall call updateThing()` — internal call.
- `shall set isPending to false` — internal state.
- `shall invoke the API with payload X` — mechanism, not outcome.
- `shall dispatch an action to the store` — internal plumbing.
- `the onSort callback is called with the column id` — mock-call assertion; passes even if rows never reorder.

**Litmus test:** if the only way to verify it is to spy on a function or read internal state,
it is an implementation step — rephrase it to the observable effect the user or a consumer sees.

### AC-table example:

When one rule has many examples that differ only by data, write **one** parameterized AC plus a
table instead of many near-duplicate ACs. Each row still expands to its own named test.

```
AC-5.1: Given a cart holding <items>, when checkout runs, then the order total shows <total>.

| items      | total  |
|------------|--------|
| (empty)    | $0.00  |
| 1 × $5.00  | $5.00  |
| 2 × $5.00  | $10.00 |
```

## NFR pattern

```
NFR-1: Given [condition], when [trigger], then [measurable or verifiable system behaviour].
```

### Examples

- `NFR-1: Given a dataset of 10,000 records, when the user requests a sorted view, then the reordered results are returned within 200ms.`
- `NFR-2: Given any module in this feature, when the source is scanned, then no secret literal appears in code — every credential resolves through the configured secret store.`

When an NFR is a pattern ban (like NFR-2 above), it must become an **enduring** check that runs on
every change, not a one-shot check that stops enforcing once merged.