# Gate procedure — fl-architecture-design (verify step)

Full review procedure, report formats, trigger detail, and scope boundary. Read when running the gate.

<!-- TOC -->
- [Why this gate exists](#why-this-gate-exists)
- [Procedure](#procedure)
- [The three blocking triggers](#the-three-blocking-triggers)
  - [Trigger 1 — God-widget / God-holder / logic-in-build](#trigger-1--god-widget--god-holder--logic-in-build)
  - [Trigger 2 — Layer violation / dual-source-of-truth](#trigger-2--layer-violation--dual-source-of-truth)
  - [Trigger 3 — Testability seam missing](#trigger-3--testability-seam-missing)
- [Review Report format](#review-report-format)
- [Scope boundary](#scope-boundary)
<!-- /TOC -->

---

## Why this gate exists

A God-widget has no isolation seam — the only way to "test" it is to mock the entire host, which
exercises nothing inside it. A dual-source-of-truth lets an AC be true in the repository and false
in the holder simultaneously. A spec flow that never asks the verifiable-unit question lets feature
specs pile behavior into whichever large widget already exists, and agents improvise unspecced logic
with no testable seam. This gate inserts that question into the lifecycle.

**External practice:**
- Flutter architecture guide — four layers, dependency direction: https://docs.flutter.dev/app-architecture/guide
- Flutter case study — data layer (service vs repository): https://docs.flutter.dev/app-architecture/case-study/data-layer
- Flutter concepts — repositories, domain models: https://docs.flutter.dev/app-architecture/concepts
- Flutter recommendations — dispose, async state, error handling: https://docs.flutter.dev/app-architecture/recommendations
- Flutter testing — widget tests with fakes: https://docs.flutter.dev/app-architecture/case-study/testing
- Flutter performance best practices — build(), const, keys: https://docs.flutter.dev/perf/best-practices

---

## Procedure

Run the review at **gate altitude** (architecture, not line-by-line):

1. **Scope.** Take the file list from `design.md` → layer map (Step 8 of `design-procedure.md`), plus any
   files modified or created during implementation. List them before reading.

2. **Map the structure first.** Sketch actual data flow for the surfaces in scope across the four
   layers (UI → Provider → Data → Service): where state lives (local `StatefulWidget`, shared
   notifier/bloc, repository stream), who writes each fact, who reads it, and how widgets compose.
   Note the `build()` size, `StreamSubscription` counts, and dispose coverage for each unit in
   scope. Misdiagnosis comes from skipping this step.

3. **Check against bundled rules in priority order.** Read the specific rule file in `core/`
   whenever a surface looks like it might violate it. Priority: layering/structure (CRITICAL) →
   service isolation (HIGH) → repository SSOT (HIGH) → state placement/flow (HIGH) →
   dependency injection (MEDIUM-HIGH) → widget composition/build discipline (MEDIUM-HIGH) →
   state boundary/lifecycle (MEDIUM) → testability seam (anchors all three triggers). The three
   blocking triggers map onto the highest-priority categories — see the crosswalk in
   `principle-checks.md`. Do not cite a rule from memory — confirm against the file's
   incorrect/correct examples. When a clear performance hazard is visible, also consult the
   `conditional/performance/` pack (non-blocking).

4. **Confirm against the code.** For each candidate trigger, verify against the actual code (not
   assumption), note the file path, and assess honestly. A pattern that is technically "wrong" but
   harmless in context is not a blocking trigger.

5. **Write the Review Report and run the extraction/justification gate** (formats below).

---

## The three blocking triggers

These are **hard blocks**. A phase cannot close while any trigger is unresolved. Resolve via an
extraction plan or a recorded justification.

### Trigger 1 — God-widget / God-holder / logic-in-build

**Condition:** A widget whose `build()` method is very large and mixes concerns (data watching,
business logic, IO, multiple distinct UI sections), or a state holder (`Notifier`/`AsyncNotifier`/
Bloc/Cubit) mixing data-fetching, UI-state management, and lifecycle side-effects with no
isolation seam.

**Confirm against:** `core/widget-build-discipline.md`,
`core/widget-composition.md`,
`core/testability-seam.md`,
`core/layering-and-structure.md`.

**Required extraction pattern:** Extract named `const StatelessWidget` classes for distinct
sections of `build()`. Move business logic and data-fetching calls out of `build()` and into the
state holder. The holder exposes named commands (methods); the widget calls them. The holder
becomes independently testable via `dart test` with constructor-injected fakes.

**The check:** "Can this widget's or holder's behavior be exercised in an isolated test without
pumping or mocking the entire host?"

### Trigger 2 — Layer violation / dual-source-of-truth

**Condition:** The spec introduces or preserves: a widget calling a repository or service directly
(skipping the Provider layer — P1 break); a state holder field that caches server data that is
already owned by a repository's `Stream` (two owners for the same fact — P3 break); or two
notifiers/holders owning the same entity type.

**Confirm against:** `core/layering-and-structure.md`,
`core/repository-ssot.md`,
`core/state-placement.md`,
`core/service-isolation.md`.

**Required fix pattern:** The widget talks only to the Provider layer (its notifier/bloc). The
notifier subscribes to the repository's `Stream<DomainModel>` and exposes derived state at read
time. Client selection is kept as a key (`selectedId`) in the notifier and resolved at read time:
`state.devices.firstWhere((d) => d.id == state.selectedId)`. Writes go through the repository
command; the repository updates its stream; the notifier's subscription fires.

**The check:** "Is there a single authoritative owner for every fact this spec touches?"

### Trigger 3 — Testability seam missing

**Condition:** A behavior the spec introduces can only be tested by mocking the entire host
widget or holder. Signals: test plan requires pumping the full parent widget tree; the behavior
is nested inside a holder with no injectable boundary; a hidden singleton is looked up inside
a class body (`Service.instance`); or `BuildContext` is passed into a repository or service.

**Confirm against:** `core/testability-seam.md`,
`core/dependency-injection.md`.

**Required fix:** Every unit the spec introduces must expose a testability seam — a widget
independently pumpable in a test with injected fakes, or a state holder / repository / service
independently constructable in `dart test` with constructor-injected fakes. Singletons move to
the composition root and are passed in by constructor. `BuildContext` is removed from service
and repository method signatures.

**The check:** "Could a test writer exercise each behavior without mocking or pumping the
entire host?"

> **Performance note:** this gate is architecture-first. If a clear performance hazard surfaces
> while mapping structure, read the relevant rule in
> `conditional/performance/` and note it
> briefly as a **non-blocking** observation. Performance is not a blocking trigger here.

---

## Review Report format

Record the gate result in the shape below, then write it into `design.md` (gate at design) or the
validate report (gate at validate).

```markdown
## Architecture Gate — Review

### Structure map
<state ownership / data flow for the surfaces in scope; build() size + subscription counts per unit>

### Findings
| # | Trigger | Rule (bundled) | Unit / path | Finding |
|---|---------|----------------|-------------|---------|
| 1 | God-widget | widget-small-build-localize-setstate | lib/.../DeviceListPage.dart (480 LOC build) | mixes repo watch + filter logic + 3 distinct sections, no extracted widget seam |
```

### PASS

```markdown
## Architecture Gate — Result
PASS. Checked: God-widget/holder/logic-in-build, layer-violation/dual-source-of-truth, testability seam.
No triggers fired on: [list of surfaces checked].
```

The phase may close.

### FAIL (blocking)

Record under `## Architecture Gate — Findings`:

```markdown
FAIL — [Trigger name]
Unit: [WidgetName / HolderName] at [file path]
Reason: [one sentence: why this unit fails the trigger]
Rule confirmed against: core/<name>.md (or conditional/...)
Required action: [extraction plan | move data to repository stream | expose testability seam]
```

The phase **cannot close** until the finding is resolved or a justification is recorded.

### Justification (recorded exception)

Record under `## Architecture Gate — Justifications`:

```markdown
JUSTIFICATION — [Trigger name]
Unit: [WidgetName / HolderName] at [file path]
Why extraction is deferred: [specific reason — not "too large", but e.g. "being extracted in a
separate refactor spec; this spec only adds a read-only field to the existing surface"]
Test strategy without extraction: [how the behavior will be tested despite the missing seam]
Approved by: [author / reviewer]
```

A recorded justification satisfies the gate. The validate command checks for this block; if absent
and the trigger fires, the gate reports `FAIL (blocking)`.

---

## Scope boundary

This gate does NOT:
- Review code line-by-line for style, correctness, or over-engineering.
- Replace post-implementation test-quality forensics (those run after implementation).
- Enforce the shared-widget immutability rule (that stays in the design / validate / implement commands).
- Define the target architecture principles (those are P1–P8 in `principle-examples.md`).

It does ONE thing: asks whether each spec maps onto an independently verifiable unit, at
architecture altitude, using the bundled rules, before a phase closes.
