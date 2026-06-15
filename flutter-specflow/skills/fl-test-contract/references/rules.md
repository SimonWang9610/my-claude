# fl-test-contract — rule reference

Six core rules + four additional assertions that must pass before a test task is marked complete.

---

## §1 — Observable outcomes, not implementation

Assert `find.text`, `find.byType`, enabled/disabled state, or visible/absent presence. `verify(...)` is only acceptable for a fire-and-forget side effect (navigation, analytics) that has no other observable — and even then it must accompany a visible assertion.

Wrong → right: `verify(() => mockRepo.sort(...)).called(1)` alone → assert rendered list order with `find.text(...)`.

**Check.** Scan for bare `verify(...)` calls with no accompanying `find.*` / `expect(find.*, ...)`. Mutation mindset: "If I invert the sorted flag in production, does this test fail?"

---

## §2 — Clause→test mapping

Every `group(...)` description names the AC or NFR ID it covers. A green suite with unmapped tests is not a PASS for the ACs those tests could cover.

Wrong → right: `test('calls sort', ...)` → `group('AC-14.3: header tap sorts by column', () { ... })`.

**Check.** Grep the file for each AC ID the task covers; every ID must appear in at least one `group(...)` label and that test must be independently runnable and green.

---

## §3 — Production-shaped fixtures

Every fixture is constructed from the real domain model (or a `freezed` `.copyWith(...)`) — not a loose `Map<String,dynamic>` or ad-hoc literal. A shape mismatch must be a compile error.

Wrong → right: `final d = {'id': '1', 'name': 'Front Door'}` → `final d = Device(id: '1', name: 'Front Door', status: DeviceStatus.online, ...)`.

**Check.** No bare `Map<String,dynamic>` fixture literals. Adding a required field to the prod type must break the fixture at compile time.

---

## §4 — No tautologies; prefer fakes over mocks

Don't assert a mock returns what you stubbed it to return. Use an in-memory fake implementing the real interface so interacting methods are genuinely exercised. `mocktail` (no codegen) is the default; `verify` is used sparingly for side effects only.

Wrong → right: `when(() => mock.getDevices()).thenAnswer(...); expect(await mock.getDevices(), ...)` → implement `FakeDeviceRepository` with real filter logic and assert the output.

**Check.** Grep for `test(`/`testWidgets(` blocks with no `expect`. For every `Mock` class, confirm at least one assertion is not a restatement of the stub.

---

## §5 — Real async/stream machinery for async ACs

ACs that depend on async behavior use a real `StreamController`/`ProviderContainer`/`Bloc` with `expectLater(..., emitsInOrder([...]))`. Drive time with `fakeAsync`/`elapse` — never real `Future.delayed`. Never call `pumpAndSettle()` while a live network call or infinite timer is pending (hangs to 30 s timeout); advance with `pump(Duration)` instead.

Wrong → right: `await Future.delayed(Duration(milliseconds: 100)); expect(cubit.state, ...)` → `expectLater(cubit.stream, emitsInOrder([isA<Loading>(), isA<Loaded>()]))`.

**Check.** For every AC naming async behavior or timing: no `Future.delayed`; no `pumpAndSettle()` with a timer or polling loop; stream ordering asserted with `emitsInOrder`.

---

## §6 — One-shot greps become enduring CI guards

Any ban verified once at review time (no hard-coded hex, no `Widget _buildX()` helper, no service import in a widget, no business logic in `build`) must become an enduring `flutter analyze` lint, `custom_lint`/DCM rule, or checked-in test. A one-shot PR-review grep is not sufficient.

Wrong → right: reviewer runs `grep -r '#[0-9a-fA-F]' lib/` and moves on → add a checked-in `test/nfr/no_hardcoded_hex_test.dart` or a DCM rule in `analysis_options.yaml`.

**Check.** For every "no occurrences of X" NFR, a corresponding checked-in test file or `analysis_options.yaml` entry must exist.

---

## §7 — Dual-assert for service tests

Assert the return value AND the specific client endpoint + args. An over-general stub (`any()`) hides routing bugs.

Wrong → right: `expect(result, isNotNull)` alone → also `verify(() => client.get('/devices', params: {'status': 'online'})).called(1)`.

---

## §8 — Three-assert for state-holder/cache command tests

Assert resulting state + notify/emit count + the collaborator interaction. One missing leg hides a real failure mode.

Wrong → right: `expect(cubit.state, isA<Loaded>())` alone → also check `verify(() => repo.fetch(...)).called(1)` and that the stream emitted exactly once.

---

## §9 — Negative equality per field for model tests

Test that changing each field individually breaks equality. A missing field in `props`/`==` is invisible to the positive test alone.

Wrong → right: `expect(device, device.copyWith())` alone → also `expect(device, isNot(equals(device.copyWith(id: 'other'))))` for each field.

---

## §10 — Error path is a first-class test

If a test catches an error the production code silently swallows, fix the production code, not the test.

Wrong → right: wrapping `expect(...)` in a try-catch to avoid a thrown exception → surface the throw in the production path and assert the error state explicitly.
