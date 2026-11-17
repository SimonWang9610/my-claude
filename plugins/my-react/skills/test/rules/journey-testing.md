# Journey testing — a flow through the real UI

Stack: Vitest + React Testing Library + MSW + user-event; Playwright where the project uses it.
One journey, one test: a user's path through a screen or flow, pinned at its observable end.

## Mount the whole slice, drive only the UI

Mount the feature with its real providers (router, query client, stores); MSW serves the network.
Drive only with `user-event`. Poking a store, calling a hook or `setState` tests a path no user
has, so the test passes while the screen is broken.

```ts
// ✗ skips the form the user fills in
useDeviceStore.getState().addDevice({ name: 'Garage Cam' })
// ✓ one harness per suite; journeys share it
render(<App initialRoute="/devices" />, { wrapper: AppProviders })
```

Not a violation: seeding the starting state through MSW handlers or the route, since the user
arrives at that state too. A step that cannot be reached through the UI is a finding about the UI:
raise it as a gap.

## Assert the end state the user sees

The steps mirror the user's actions; the last assertion is what is on screen. A spy or a cache
entry can be right while nothing rendered.

```ts
test('a user adds a device and sees it listed', async () => {
  await user.click(screen.getByRole('button', { name: /add device/i }))
  await user.type(screen.getByRole('textbox', { name: /name/i }), 'Garage Cam')
  await user.click(screen.getByRole('button', { name: /save/i }))
  expect(await screen.findByRole('row', { name: /garage cam/i })).toBeVisible()
})
```

Not a violation: an extra assertion on a request body when the criterion is about what is sent.

## Every write journey has its forced-error twin

Create, update and delete each get the failure, forced by overriding the handler, with the
recovery the user sees. Without it the error path ships untested, and it is the path that loses
data.

```ts
test('a failed save shows the error and keeps the draft', async () => {
  server.use(http.post('/api/devices', () => HttpResponse.json({}, { status: 500 })))
  // …the same steps…
  expect(await screen.findByRole('alert')).toHaveTextContent(/could not save/i)
  expect(screen.getByRole('textbox', { name: /name/i })).toHaveValue('Garage Cam')
})
```

Not a violation: a read-only journey with no error twin, when the design gives the screen one
shared error state that a unit test already covers.

## Deterministic, or it is not a test

No sleeps and no dependence on test order: await the signal (`findBy…`, `waitFor`), and reset
handlers and stores between tests. A journey that cannot be automated is reported with the reason,
never dropped silently.
