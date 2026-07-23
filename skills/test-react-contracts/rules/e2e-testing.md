# E2E testing — one journey, one test

A journey is a user flow walked end-to-end through the real UI — from the approved
`qa-journey-plan.md`, or design.md's flows when no plan exists. One test per journey;
every **write** journey (create/update/delete) also gets a forced-error path — the failure
MSW will force, with its observable result.

## Harness — the whole app slice, UI-only driving

Mount the feature with its real providers (router, query client, stores); MSW serves the
network. Drive **only** through the UI with `user-event` — no store poking, no direct hook
calls, no `setState`. If a step can't be reached through the UI, the journey (or the UI) is
wrong: raise it.

```ts
// harness once per suite; journeys share it
render(<App initialRoute="/devices" />, { wrapper: AppProviders })
```

## Happy path — assert the observable end state

Steps mirror the flow table's user actions; the final assertion is the flow's observable
outcome (what the user sees), not an intermediate spy or cache entry.

```ts
test('J-2 · AC-2.1, AC-2.3: user adds a device and sees it listed', async () => {
  await user.click(screen.getByRole('button', { name: /add device/i }))
  await user.type(screen.getByRole('textbox', { name: /name/i }), 'Garage Cam')
  await user.click(screen.getByRole('button', { name: /save/i }))
  expect(await screen.findByRole('row', { name: /garage cam/i })).toBeVisible()
})
```

## Forced-error path — override the handler, assert the recovery

```ts
test('J-2e · AC-2.4: failed save shows the error and keeps the draft', async () => {
  server.use(http.post('/api/devices', () => HttpResponse.json({}, { status: 500 })))
  // …same steps…
  expect(await screen.findByRole('alert')).toHaveTextContent(/could not save/i)
  expect(screen.getByRole('textbox', { name: /name/i })).toHaveValue('Garage Cam')
})
```

## Traceability

Journey id + AC ids in the name per test-quality's label rule — coverage is a grep,
nothing else is bookkept. A journey that proves unautomatable goes back to the caller with
the reason — never silently dropped.
