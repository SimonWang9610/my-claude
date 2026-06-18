# Review procedure — fl-pr-review

Full step-by-step: how to acquire the diff, classify units, run rule passes in order,
filter findings, assemble the report, and optionally post to GitHub.

## Contents

- [Step 1 — Acquire the diff](#step-1--acquire-the-diff)
- [Step 2 — Classify each changed file by unit kind](#step-2--classify-each-changed-file-by-unit-kind)
- [Step 3 — Run rule passes in priority order](#step-3--run-rule-passes-in-priority-order)
  - [Pass 3a — Architecture / verifiable-unit gate (BLOCKING)](#pass-3a--architecture--verifiable-unit-gate-blocking)
  - [Pass 3b — State and ownership](#pass-3b--state-and-ownership)
  - [Pass 3c — Data layer](#pass-3c--data-layer-repository--domain-model)
  - [Pass 3d — Service layer](#pass-3d--service-layer)
  - [Pass 3e — Widget composition and build discipline](#pass-3e--widget-composition-and-build-discipline)
  - [Pass 3f — DI and composition root](#pass-3f--di-and-composition-root)
  - [Pass 3g — Test quality](#pass-3g--test-quality)
  - [Pass 3h — Engineering discipline](#pass-3h--engineering-discipline)
  - [Pass 3i — Conditional packs](#pass-3i--conditional-packs-activate-only-when-relevant)
- [Step 4 — Confidence-filter](#step-4--confidence-filter)
- [Step 5 — Assemble the report](#step-5--assemble-the-report)
- [Step 6 — Optional GitHub posting](#step-6--optional-github-posting-confirm-first)

---

## Step 1 — Acquire the diff

Choose the source that matches what the human provided:

```bash
# GitHub PR by number
gh pr diff <n>

# Local branch vs explicit base
git diff <base>...HEAD

# Current branch vs merge-base with default remote branch (default when nothing specified)
git diff $(git merge-base HEAD origin/HEAD)...HEAD

# Uncommitted working-tree changes
git diff --staged   # staged only
git diff            # unstaged only
```

From the diff output, produce a **file list with hunk summaries**:

```
lib/features/devices/services/device_repository.dart   [modified]   +42 -18
lib/features/devices/screens/device_list_page.dart   [modified]   +87 -5
lib/features/devices/models/device.dart   [added]   +31
test/features/devices/services/device_repository_test.dart   [added]   +68
```

If no Dart files changed, the review is complete (nothing to do).

---

## Step 2 — Classify each changed file by unit kind

Map every changed Dart file to exactly one unit kind. This determines which rules apply.

| Unit kind | Typical path patterns | Primary rules |
|-----------|----------------------|---------------|
| **Widget** | `screens/`, `widgets/`, `_screen.dart`, `_widget.dart`, `_page.dart` | P6, core/widget-*, core/testability-seam |
| **State holder** (notifier/bloc/cubit/controller) | `providers/`, `_provider.dart`, `_notifier.dart`, `_bloc.dart`, `_cubit.dart`, `_controller.dart` | P4, P5, P7, core/state-* |
| **Repository** | `services/`, `_repository.dart` | P3, core/repository-ssot, core/domain-models-immutable |
| **Service** | `services/`, `_service.dart`, `_client.dart`, `_api.dart` | P2, core/service-isolation |
| **Domain model / DTO** | `models/`, `_model.dart`, `_dto.dart` | P3, core/domain-models-immutable |
| **DI / composition root** | `main.dart`, `app.dart`, `injection.dart`, `providers.dart` | P1, core/dependency-injection |
| **Test** | `test/`, `_test.dart`, `integration_test/` | fl-test-contract rules 1–6, fl-test-forensics passes 1–3 |

After classifying, **sketch the data flow** for the changed units: where state lives, who
writes each fact, who reads it, and how widgets compose. Include `build()` size estimate and
`StreamSubscription`/controller counts per state holder. Misdiagnosis comes from skipping
this sketch.

---

## Step 3 — Run rule passes in priority order

Work through the passes below in the listed order. Open the specific rule file to confirm
before citing — never from memory.

### Pass 3a — Architecture / verifiable-unit gate (BLOCKING)

This is the highest-priority pass. Check the three blocking triggers from the Verify step
of `../../fl-architecture-design/SKILL.md` (procedure and report formats in
`../../fl-architecture-design/references/gate-procedure.md`):

**Trigger 1 — God-widget / God-holder / logic-in-build**
Open and confirm against:
- `../../fl-architecture-design/references/core/widget-build-discipline.md`
- `../../fl-architecture-design/references/core/widget-composition.md`
- `../../fl-architecture-design/references/core/testability-seam.md`
- `../../fl-architecture-design/references/core/layering-and-structure.md`

**Trigger 2 — Layer violation / dual-source-of-truth**
Open and confirm against:
- `../../fl-architecture-design/references/core/layering-and-structure.md`
- `../../fl-architecture-design/references/core/repository-ssot.md`
- `../../fl-architecture-design/references/core/state-ownership-decision.md`
- `../../fl-architecture-design/references/core/state-placement.md`
- `../../fl-architecture-design/references/core/service-isolation.md`

**Trigger 3 — Testability seam missing**
Open and confirm against:
- `../../fl-architecture-design/references/core/testability-seam.md`
- `../../fl-architecture-design/references/core/dependency-injection.md`

Any fired trigger = Critical finding. A PR with an unresolved Critical cannot be approved.

### Pass 3b — State and ownership

For state holders and widgets that manage state:
- Open `../../fl-architecture-design/references/core/state-ownership-decision.md` — verify the
  correct tier is used: local `setState` → `InheritedWidget` scope (data down, NOT callbacks)
  → provider (shared / survives navigation). Check that `InheritedWidget` carries data
  downward and does NOT thread callbacks upward.
- Open `../../fl-architecture-design/references/core/state-placement.md` — one owner per fact,
  derive don't duplicate, narrowest possible scope.
- Open `../../fl-architecture-design/references/core/state-flow-and-async.md` — unidirectional
  flow; prefer Dart 3 sealed class with exhaustive switch expression for `loading | data |
  error` variants (impossible states are unrepresentable); check for `if (x is T)` chains
  that should be exhaustive switch expressions.
- Open `../../fl-architecture-design/references/core/state-boundary-and-lifecycle.md` — every
  controller/subscription/listener disposed; `dispose()` order correct (remove listeners
  before dispose). For Riverpod `@riverpod` notifiers use `ref.onDispose()` inside `build()`
  rather than overriding `dispose()`; check `ref.mounted` before acting after `await`.
- For Riverpod notifiers: `ref.watch` in `build()` only; `ref.read` only in event handlers
  (never in `build()` — stale-UI bug); `ref.listen` for side effects; narrow rebuilds with
  `.select()`; `autoDispose` is the default with code-gen (do not instruct to add it; opt out
  with `@Riverpod(keepAlive: true)`); providers must be declared top-level.

### Pass 3c — Data layer (repository + domain model)

For changed repositories and domain models:
- Open `../../fl-architecture-design/references/core/repository-ssot.md` — single source of
  truth per type; DTO→domain mapping; owns caching/retry; no duplicate ownership.
- Open `../../fl-architecture-design/references/core/domain-models-immutable.md` — immutable,
  pure-Dart domain models (no Flutter/JSON/DB imports) with value equality via `==` +
  `hashCode` (or `@freezed` / `Equatable`); prefer `const` constructors, `final` fields, and
  `copyWith`; use Dart 3 records for small immutable bundles.
- Open `../../fl-architecture-design/references/core/service-isolation.md` — raw DTOs only out
  of services; transport errors mapped at the boundary; no domain-model construction inside
  a service.

### Pass 3d — Service layer

For changed services / API clients:
- Open `../../fl-architecture-design/references/core/service-isolation.md` — one stateless
  service per source; returns raw DTOs / `Stream<RawPayload>`; owns connection/reconnect;
  maps transport exceptions to typed errors; no app state.
- Check: is `BuildContext` passed into the service? → Critical (Trigger 3 + P8).

### Pass 3e — Widget composition and build discipline

For changed widgets:
- Open `../../fl-architecture-design/references/core/widget-composition.md` — `const
  StatelessWidget` classes, not `Widget _buildX()` helpers; default `StatelessWidget`.
- Open `../../fl-architecture-design/references/core/widget-build-discipline.md` — `const`
  everywhere; small `build()`; no IO / business logic in `build()`; no `BuildContext` across
  an `await` without `mounted` check.
- Open `../../fl-architecture-design/references/core/widget-theming.md` — colors/typography from
  `Theme.of(context)` tokens, not hard-coded values.

### Pass 3f — DI and composition root

For changes touching dependency wiring:
- Open `../../fl-architecture-design/references/core/dependency-injection.md` — inject via
  constructors; wire once at the composition root; no hidden singletons (`Service.instance`
  looked up inside a class body).

### Pass 3g — Test quality

For changed test files, apply both passes:

**fl-test-contract (six authoring-time rules from `../../fl-test-contract/SKILL.md`):**
1. Observable outcomes, not implementation (no `verify` unless fire-and-forget side effect)
2. Every `group(...)` names the AC/NFR ID it covers
3. Fixtures constructed from the real domain type (not `Map<String,dynamic>`)
4. No tautologies; fakes over mocks; mocked config is not exercised → false positive;
   Mocktail requires `registerFallbackValue(FakeX())` in `setUpAll` for `any()` on custom types
5. Real `StreamController`/`ProviderContainer` + `expectLater(..., emitsInOrder([...]))`;
   `fakeAsync` + `elapse()` for timers (no real `Future.delayed`); `pump()` for one frame;
   `pumpAndSettle()` only when an animation must fully settle — never with live timers
6. One-shot grep bans must become enduring CI guards

**fl-test-forensics (three gap-class passes from `../../fl-test-forensics/SKILL.md`):**
- Pass 1 — No-spec coverage: behaviors with no requirement ID; ACs with no test
- Pass 2 — Tests pass but miss behavior: action never fires, assertion on internal state,
  mock configured but not exercised by the SUT
- Pass 3 — False positive: no `expect`/`expectLater`, tautology, verify-only, over-mocking,
  `pumpAndSettle` with live timers, real async in tests

Reference files for test forensics (use relative paths):
- `../../fl-test-forensics/references/gap-classes.md`
- `../../fl-test-forensics/references/flutter-dart-heuristics.md`
- `../../fl-test-forensics/references/false-positive-signals.md`

### Pass 3h — Engineering discipline

Check the diff against `engineering-discipline`:
- **Scope creep**: code changed outside the AC's stated scope (speculative features,
  unrequested refactors)
- **Non-surgical changes**: unrelated reformatting, renames, or restructuring in the diff
- **Dead code introduced**: new orphaned symbols the diff itself creates (pre-existing dead
  code is a nit to mention, not delete)
- **Duplicate abstractions**: a second pattern introduced where an existing one exists

These are generally Major or Minor unless the scope creep introduces a layer violation
(which escalates to Critical).

### Pass 3i — Conditional packs (activate only when relevant)

Open a conditional pack ONLY when its scenario is clearly present in the diff:

- **`../../fl-architecture-design/references/conditional/performance/`** — activate ONLY when a
  clear, concrete performance hazard is visible in the diff (long lists without `.builder`,
  expensive work in `build()`, heavy images decoded at wrong size, animations without `child:`).
  Performance is NON-BLOCKING. Check the relevant file:
  - `perf-rebuilds.md`, `perf-build-cost.md`, `perf-lists.md`, `perf-images.md`,
    `perf-animations.md`, `perf-jank-and-startup.md`

  Do NOT open the performance pack speculatively. A vague "might be slow" is not enough.

- **`fl-riverpod` skill** — when the diff touches Riverpod-specific code (providers, `ref`,
  `ConsumerWidget`, `Notifier`, etc.), load the `fl-riverpod` skill (`../../fl-riverpod/SKILL.md`)
  for package idioms. Flag as Major any use of `StateNotifier`, `StateNotifierProvider`,
  `StateProvider`, or `ChangeNotifierProvider` — these are legacy (`ChangeNotifierProvider`
  is in `package:flutter_riverpod/legacy.dart`; pure-Dart legacy types are in
  `package:riverpod/legacy.dart`) and should be replaced with `@riverpod` code-gen `Notifier`
  / `AsyncNotifier`. Use an analogous skill for other state-management packages.

---

## Step 4 — Confidence-filter

Before recording a finding, ask:

1. Is this visible in the diff hunks or the immediately surrounding context? (Not an
   assumption about code not shown.)
2. Is the rule violation unambiguous, or is there a plausible correct interpretation?
3. Is the confidence high?

Only record **high-confidence findings**. A noisy review is worse than a short one.
Mark any medium-confidence observation with `(low confidence — verify before actioning)` and
place it in the Minor tier.

---

## Step 5 — Assemble the report

Use the template in `report-format.md`. Sections:

1. One-line verdict + summary
2. Findings table grouped Critical → Major → Minor
3. Coverage note: what was reviewed vs skipped (makes gaps visible)
4. Optional GitHub-posting section (only if requested)

---

## Step 6 — Optional GitHub posting (confirm first)

GitHub posting is **opt-in** and requires explicit human confirmation before any `gh` command
is run. See `references/report-format.md` for the exact `gh` commands.

Never auto-approve (`gh pr review --approve`) based on this review alone. The human owns the
merge decision.
