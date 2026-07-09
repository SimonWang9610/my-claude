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

The Then clause must be assertable **without reaching into component internals** — rendered
text, an accessible role/state, a navigation, a visible toast, an enabled/disabled control.

**Reject — implementation steps:**
- `shall call updateThing()` — internal call.
- `shall set isPending to false` — internal state.
- `shall invoke the API with payload X` — mechanism, not outcome.
- `shall dispatch an action to the store` — internal plumbing.
- `the onSort callback is called with the column id` — mock-call assertion; passes even if rows never reorder.

Litmus test: *if the only way to verify this is to spy on a function or read internal
state, it is an implementation step.* Rephrase to the user-visible effect.

**Require — observable examples:**
- `AC-2.1: Given the device list has loaded, when the user clicks "Add Device", then the add-device drawer opens and the form fields are empty.`
- `AC-3.2: Given the user submits an invalid email, when the form is submitted, then an inline error "Enter a valid email address" appears below the email field.`
- `AC-4.1: Given a network error occurs during save, when the user clicks "Save", then an error toast "Failed to save — please try again" appears and the form remains open with input preserved.`

**NFRs follow the same contract:**
```
NFR-1: Given [condition], when [trigger], then [measurable or verifiable system behaviour].
```
- `NFR-1: Given the page is viewed with system dark-mode active, when any surface renders, then no hardcoded hex colour values appear — all colours resolve through the design-token CSS-variable chain.`

When an NFR is a pattern ban, note it must become an enduring CI guard, not a one-time grep.

For behaviour that varies only by data, express it as a single **Examples-table AC** rather than
many near-duplicate criteria — see `references/discovery.md` §5.

## 4. Where the IDs go

IDs carried inline in `requirements.md` flow into task-breakdown (missing or malformed IDs
block task generation), then into test names and the coverage gate — full chain in
`references/traceability.md`.

## 5. Authoring checklist

Same gate as `SKILL.md`'s **Hard checks** — run that list before handoff; not restated here.
