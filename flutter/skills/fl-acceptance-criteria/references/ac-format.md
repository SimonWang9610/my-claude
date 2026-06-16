# Acceptance-criterion format — IDs, EARS, and observable phrasing

## 1. EARS functional requirements

Write system-level requirements in EARS (Easy Approach to Requirements Syntax). EARS stays
alongside the per-story ACs; it does not replace them.

Patterns:
- **Ubiquitous:** "The system shall [action]"
- **Event-driven:** "When [event], the system shall [action]"
- **State-driven:** "While [state], the system shall [action]"
- **Optional:** "Where [condition], the system shall [action]"
- **Unwanted:** "If [unwanted condition], then the system shall [action]"

## 2. ID format

- **Story ACs:** `AC-<story#>.<n>` — e.g. `AC-1.1`, `AC-2.3`. Story number = order in document; criterion number = sequential within that story.
- **Non-functional requirements:** `NFR-<n>` — e.g. `NFR-1`, `NFR-2`.

Rules:
- IDs must be **unique** within a requirements document.
- IDs are **stable** once written — append new IDs; never renumber. Renumbering silently breaks every test name referencing the old ID.
- Every story must have **≥1** AC. Every NFR must carry an ID.

## 3. Phrasing contract — observable Given/When/Then

```
AC-1.1: Given [precondition], when [action or trigger], then [observable result].
```

The Then clause must be assertable **without reaching into widget or provider internals** —
visible text (`find.text`), a widget type (`find.byType`), presence or absence of a widget
(`findsOneWidget` / `findsNothing`), an accessible semantic label, a navigation event, or
a value/state emitted by a stream or returned by a repository method.

**Reject — implementation steps:**
- `shall call notifyListeners()` — internal call.
- `shall set isLoading to false` — internal state field.
- `shall invoke the API with payload X` — mechanism, not outcome.
- `shall emit a LoadingState` — implementation plumbing; rephrase to what the UI shows.
- `the onTap callback is called with the device id` — mock-call assertion; passes even if nothing navigates.

Litmus test: *if the only way to verify this is to read a provider field directly or spy
on a private method, it is an implementation step.* Rephrase to the user-visible effect or,
for pure logic, to the value/stream emission a consumer would observe.

**Require — observable examples:**
- `AC-2.1: Given the device list has loaded, when the user taps "Add Device", then the add-device bottom sheet opens and the form fields are empty.`
- `AC-3.2: Given the user submits an invalid email, when the form is submitted, then an inline error "Enter a valid email address" appears below the email field.`
- `AC-4.1: Given a network error occurs during save, when the user taps "Save", then a snackbar "Failed to save — please try again" appears and the form remains open with input preserved.`

**NFRs follow the same contract:**
```
NFR-1: Given [condition], when [trigger], then [measurable or verifiable system behaviour].
```
- `NFR-1: Given the app is viewed in system dark-mode, when any screen renders, then no hardcoded Color(0xff…) literals appear in component source — all colours resolve through the design-token ThemeData chain.`

When an NFR is a pattern ban, note it must become an enduring CI guard, not a one-time grep.

## 4. Where the IDs go

- **`requirements.md`** — every AC and NFR carries its ID inline.
- **Task-breakdown** — generates one test task per AC/NFR ID. Missing or malformed IDs block task generation.
- **Test files** — the ID appears in the Flutter `group(...)` description (see `traceability.md`).
- **Validation** — any AC or NFR with no mapped passing test is a blocking FAIL.

## 5. Authoring checklist

Before the requirements phase exits, every criterion must:
- [ ] Carry a unique, stable `AC-<story#>.<n>` or `NFR-<n>` ID.
- [ ] Use Given/When/Then structure.
- [ ] Have an observable Then clause assertable without internal access.
- [ ] Not be an implementation step (no internal call/state/mechanism phrasing).
- [ ] Every story has ≥1 AC; every NFR has an ID.

Any failing criterion is a blocking authoring condition — fix in `requirements.md` before exiting.
