---
name: fl-riverpod
description: >
  Riverpod-specific guidance for the Flutter specflow: ref.watch/read/listen by call site,
  provider declaration & lifetime (autoDispose/keepAlive), AsyncNotifier/AsyncValue,
  .select for narrow rebuilds, and provider testing. Load when the project uses Riverpod,
  detected via `flutter_riverpod`, `hooks_riverpod`, or `riverpod_generator` in
  pubspec.yaml; `@riverpod` annotations; `ProviderScope`; or `ref.watch`/`ref.read` in code.
---

# fl-riverpod

Riverpod-specific companion to the Flutter specflow core. Load this skill when the project
uses Riverpod; skip it otherwise.

**Detect Riverpod:** any of these signals confirms it:
- `pubspec.yaml` contains `flutter_riverpod`, `hooks_riverpod`, or `riverpod_generator`
- Source files contain `@riverpod` annotations, `ProviderScope`, `ref.watch`, or `ref.read`

## Relationship to the agnostic core

The core rules — state-ownership tiers, SSOT, sealed async state, dispose discipline,
dependency injection — still apply and are not repeated here. This skill is the Riverpod
**HOW** for each of those principles: which API to use, where to declare it, and how to
test it.

## Default: code generation

**Always use the Riverpod generator.** Declare every provider and notifier with `@riverpod`
(or `@Riverpod(...)`) and run `build_runner`; the generator produces the provider variable
and `autoDispose`-by-default. Hand-written
`Provider(...)` / `NotifierProvider` / `AsyncNotifierProvider` / `StateNotifierProvider`
declarations are **legacy** — only read or maintain them when you encounter existing code;
never write new ones.

```dart
// ✅ default: function provider
@riverpod
Future<List<Alarm>> alarmList(Ref ref) =>
    ref.watch(alarmRepositoryProvider).getAlarms();

// ✅ default: class notifier
@riverpod
class AlarmList extends _$AlarmList {
  @override
  Future<List<Alarm>> build() =>
      ref.read(alarmRepositoryProvider).getAlarms();

  Future<void> add(Alarm a) async { /* ... */ }
}
// → generates alarmListProvider (autoDispose by default)
```

### Riverpod 3.0

Target `flutter_riverpod ^3` / `riverpod_annotation ^3` / `riverpod_generator ^3`.

- **No per-provider `Ref` types** — every function provider is `ReturnType name(Ref ref, ...)`. `FooRef` / `ExampleRef` / `Ref<T>` generics are gone.
- **`AsyncValue` is sealed** — prefer exhaustive `switch` pattern-matching (no `default`); `.when()` still valid. `valueOrNull` is deprecated → use `.value` (null on loading/error); use `requireValue` to throw-if-not-data.
- **`ref.mounted`** — guard with `if (!ref.mounted) return;` after every `await` in a notifier method before touching `ref`/`state`.
- **Auto-retry** — failed `build()` retries with exponential backoff by default (`Error`/`ProviderException` excluded). Disable with `@Riverpod(retry: (c,e) => null)` or globally via `ProviderScope(retry: ...)`.
- **Legacy providers** (`StateProvider`, `StateNotifierProvider`, `ChangeNotifierProvider`) now require `import 'package:flutter_riverpod/legacy.dart'`; never write new ones.

**EXPERIMENTAL — API may break without notice:**

- **Mutations** (`import 'package:riverpod/experimental/mutation.dart'`) — `final addTodo = Mutation<T>()` observes a notifier method's idle/pending/error/success state in the UI. It wraps notifier methods, doesn't replace them.
- **Offline persistence** (`import 'package:riverpod/experimental/persist.dart'`) — call `persist(...)` inside `AsyncNotifier.build()`; annotate the state class with `@JsonPersist()`. Backend: `riverpod_sqflite`.

## Instructions

When reviewing or generating Riverpod code, apply these five idiom areas in order:

1. **ref.watch vs ref.read** — subscribe in `build`, snapshot in callbacks.
   See `references/ref-watch-vs-read.md`.

2. **Provider declaration & lifetime** — declare with `@riverpod` codegen; `autoDispose`
   is the default; opt into `keepAlive` only when all three gates pass.
   See `references/provider-declaration.md`.

3. **AsyncNotifier + AsyncValue** — user-driven async state uses `AsyncNotifier`; consume
   exhaustively with `switch` pattern-matching (sealed in 3.0); `.when()` is a secondary option.
   See `references/asyncnotifier-async-state.md`.

4. **`.select` for narrow rebuilds** — project only the field a widget reads; avoid full
   state subscriptions on high-frequency providers.
   See `references/select-narrow-rebuilds.md`.

5. **Test override discipline** — override deps, not the unit; subclass Notifier fakes;
   listen before bare-reading autoDispose providers.
   See `references/testing.md`.

## For another package

Any state-management companion skill (e.g. `fl-bloc`, `fl-provider`) should cover the same
five categories with package-appropriate APIs:

| Category | Riverpod | Bloc / Cubit | Provider pkg |
|---|---|---|---|
| Subscribe vs read-once | `ref.watch` / `ref.read` | `BlocBuilder` / `context.read<C>()` | `context.watch` / `context.read` |
| Holder declaration & scoping | `@riverpod` function/class + `build_runner`; `autoDispose` default | `BlocProvider` in tree, `MultiBlocProvider` at root | `ChangeNotifierProvider` in tree |
| Sealed async state | `AsyncValue<T>` + `.when()` from `@riverpod` `AsyncNotifier` | sealed `BlocState` + `BlocBuilder` / `switch` | manual `AsyncSnapshot` from `FutureProvider` |
| Rebuild-narrowing selector | `ref.watch(fooProvider.select((s) => s.field))` | `BlocSelector` / `buildWhen:` | `Selector<M,T>` widget |
| Test override seam | `ProviderContainer.test(overrides:[…])` / `ProviderScope(overrides:[…])` | `BlocProvider.value(fakeBloc)` | `ChangeNotifierProvider.value(fake)` |

To author a new companion skill: copy this directory, replace the five reference files with
your package's idioms (same frontmatter schema), and update this SKILL.md with its detection
signals and description.

## References

| File | Covers |
|---|---|
| `references/ref-watch-vs-read.md` | `ref.watch` in build, `ref.read` in callbacks, `ref.mounted` after await |
| `references/provider-declaration.md` | top-level declaration, `autoDispose`, keepAlive 3-gate, pause/resume, invalidation cascade |
| `references/asyncnotifier-async-state.md` | `AsyncNotifier`, `AsyncValue.guard`, `.when()` exhaustive handling |
| `references/select-narrow-rebuilds.md` | `.select()` projection, `==` short-circuit, derived booleans |
| `references/testing.md` | `ProviderContainer` overrides, Notifier subclass fakes, listen-before-read, pause/resume verify caveat |
