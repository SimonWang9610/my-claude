# Severity model — fl-pr-review

Three tiers, each with Flutter/Dart examples mapped to rule IDs and rule-file paths.
Severity is a **suggestion**; the human reviewer makes the final disposition.

---

## Critical — blocks merge / request changes

A finding is Critical when it directly violates a blocking architecture principle, breaks
testability, introduces a dual-source-of-truth, or creates a false-positive test that masks
a real gap. All three architecture-gate blocking triggers map here.

**Flutter examples:**

| Finding | Rule IDs | Rule file |
|---------|----------|-----------|
| Widget calls a repository or service directly, skipping the Provider layer | P1 | `core/layering-and-structure.md` |
| State holder caches server data in a field already owned by a repository `Stream<T>` (two owners for the same fact) | P3 | `core/repository-ssot.md`, `core/state-placement.md` |
| Business logic or IO inside `build()` — a query, a `Future.wait`, a `setState` calling a repository | P6, P8 | `core/widget-build-discipline.md`, `core/testability-seam.md` |
| `BuildContext` passed into a service or repository method | P8 | `core/testability-seam.md`, `core/dependency-injection.md` |
| Hidden singleton looked up inside a class body (`MyService.instance`) instead of constructor injection | P8 | `core/dependency-injection.md` |
| God-widget: `build()` ≫ 80 lines mixing multiple concerns, data-watching, and IO | P6, P8 | `core/widget-composition.md`, `core/testability-seam.md` |
| Swallowed error — `catch (_) {}` or `catch (e) { /* no error state */ }` on an async operation | P7 | `core/state-flow-and-async.md` |
| No error branch in async state (only `loading` + `data`, no `error`) | P7 | `core/state-flow-and-async.md` |
| A test that is green but a mutation of the deciding production branch still passes (false positive mapped to an AC) | — | `forensics/false-positive-signals.md` |
| An AC-mapped test with no `expect` or `expectLater` (verify-only or empty body) | Test-contract R1 | `test-contract/rules.md §1` |

**The three gate-blocking triggers are all Critical.** If any fires, the report verdict is
"Request changes" and the branch cannot merge until resolved or a justification is recorded.

---

## Major — should fix before merge (reviewer's call)

A Major finding is a real problem that falls short of a hard gate block but leaves the
codebase worse than it was found. The reviewer decides whether to require a fix or accept
it with a recorded justification.

**Flutter examples:**

| Finding | Rule IDs | Rule file |
|---------|----------|-----------|
| Domain model without value equality — no `==` + `hashCode`, no `@freezed`, no `Equatable`; or mutable fields / missing `const` constructor / missing `copyWith` | P3 | `core/domain-models-immutable.md` |
| Wrong state-ownership tier: page-local state in a global/app-wide provider | P5 | `core/state-ownership-decision.md` |
| `InheritedWidget` threading callbacks upward instead of carrying data downward | P5 | `core/state-ownership-decision.md` |
| Missing cleanup for a `StreamSubscription`, `AnimationController`, `TextEditingController`, `ScrollController`, or `ChangeNotifier`: override `dispose()` for plain controllers; use `ref.onDispose()` inside `build()` for Riverpod `@riverpod` notifiers; check `ref.mounted` before acting after `await` | P7 | `core/state-boundary-and-lifecycle.md` |
| Async state is not sealed — `isLoading == true && data != null` is representable; or non-exhaustive `if (x is T)` chain where a Dart 3 sealed class + exhaustive switch expression should be used | P7 | `core/state-flow-and-async.md` |
| An AC in the PR description or spec has no corresponding test | Test-contract R2 | `test-contract/rules.md §2` |
| Test fixture built from a `Map<String,dynamic>` or ad-hoc literal instead of the real domain type | Test-contract R3 | `test-contract/rules.md §3` |
| Mocked-config tautology: test asserts that a stub returns what it was stubbed to return | Test-contract R4 | `test-contract/rules.md §4` |
| Scope creep: significant code changed outside the named AC's scope (unrequested refactor, speculative feature) | — | `engineering-discipline` |
| Service constructs a domain model (DTO→domain mapping should live in the repository) | P2, P3 | `core/service-isolation.md` |
| Two notifiers/state holders own the same entity type | P3, P5 | `core/state-placement.md` |
| Legacy Riverpod API in new code: `StateNotifier`, `StateNotifierProvider`, `StateProvider`, or `ChangeNotifierProvider` (now in `flutter_riverpod/legacy.dart`); replace with `@riverpod` code-gen `Notifier` / `AsyncNotifier` | — | the `fl-riverpod` skill |
| `ref.read` called inside a provider's `build()` method — skips reactivity and causes stale UI; use `ref.watch` in `build()`, `ref.read` only in event handlers | — | the `fl-riverpod` skill |
| Provider declared inside a method, function body, or `State` class instead of top-level — creates a new provider per build/instance and leaks | — | the `fl-riverpod` skill |
| `pumpAndSettle()` used while a live timer or network call is pending (test hangs); prefer `pump()` for a single frame; use `fakeAsync` + `elapse()` for timers | Test-contract R5 | `test-contract/rules.md §5` |
| Mocktail `any()` used on a custom type without `registerFallbackValue(FakeX())` in `setUpAll` | Test-contract R4 | `test-contract/rules.md §4` |

---

## Minor — advisory / nit (non-blocking)

Minor findings are advisory. They represent convention mismatches, non-measured performance
concerns, or nits that do not affect correctness or testability. Report them; do not block.

**Flutter examples:**

| Finding | Rule IDs | Rule file |
|---------|----------|-----------|
| Missing `const` constructors where they could be added | P6 | `core/widget-build-discipline.md` |
| `Widget _buildX()` helper method instead of extracted `const StatelessWidget` class | P6 | `core/widget-composition.md` |
| Hard-coded color or text style instead of `Theme.of(context)` token | P6 | `core/widget-theming.md` |
| `ListView` without `.builder` on a potentially long list (no measured jank) | — | `conditional/performance/perf-lists.md` |
| Image decoded at full resolution without `cacheWidth`/`cacheHeight` (no measured regression) | — | `conditional/performance/perf-images.md` |
| `AnimatedBuilder` without a `child:` argument for the static subtree | — | `conditional/performance/perf-animations.md` |
| Naming or folder convention deviation (file in wrong layer folder) | P1 | `core/layering-and-structure.md` |
| Pre-existing dead code adjacent to (but not created by) the diff — mention, do not delete | — | `engineering-discipline` |
| Non-surgical reformatting of unchanged lines (whitespace, unrelated renames) | — | `engineering-discipline` |
| One-shot grep ban not promoted to a CI guard (low risk path) | Test-contract R6 | `test-contract/rules.md §6` |

---

## Verdict mapping

| Findings present | Suggested verdict | Human's call |
|-----------------|-------------------|--------------|
| Any Critical | **Request changes** — the branch cannot merge as-is | Human confirms and posts, or overrides with recorded justification |
| Only Major | **Reviewer's call** — changes requested or comment with justification | Human decides |
| Only Minor / none | **Approve or Comment** | Human approves if satisfied |

The human owns the final merge decision. This review surfaces findings and suggests a
verdict; it does not approve or block the branch autonomously.
