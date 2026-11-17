---
title: "Riverpod: Declare Providers with the @riverpod Generator"
impact: HIGH
impactDescription: a provider declared as a class field escapes Riverpod's lifecycle; skipping code-gen means hand-writing boilerplate the generator owns (Ref types, autoDispose wiring, keepAlive)
tags: state, riverpod, provider, declaration, codegen, autoDispose, lifecycle
---

## Riverpod: Declare Providers with the @riverpod Generator

Use the **Riverpod generator** (`riverpod_annotation ^3` + `riverpod_generator ^3` + `build_runner`)
for every new provider. Annotate a top-level function or class with `@riverpod`; the
generator emits the provider variable and `autoDispose` by default. Never write a
`Provider(...)`, `AsyncNotifierProvider(...)`, or similar constructor by hand — those are
the legacy forms the generator replaces.

**Correct:**
```dart
// ✅ function provider — plain Ref ref (no FooRef in Riverpod 3.0), autoDispose by default
@riverpod
Future<List<Alarm>> alarmList(Ref ref) =>
    ref.watch(alarmRepositoryProvider).getAlarms();

// ✅ class notifier — user-driven mutations + async state
@riverpod
class AlarmList extends _$AlarmList {
  @override
  Future<List<Alarm>> build() =>
      ref.watch(alarmRepositoryProvider).getAlarms();

  Future<void> add(Alarm a) async {
    state = const AsyncValue.loading();
    final result = await AsyncValue.guard(
      () => ref.read(alarmRepositoryProvider).add(a),
    );
    if (!ref.mounted) return; // guard after every await in 3.0
    state = result;
  }
}
// → generator produces alarmListProvider (autoDispose by default)
```

**Incorrect (legacy — read/maintain only, never write new):**
```dart
// ❌ hand-written AsyncNotifierProvider — legacy boilerplate the generator replaces
final alarmListProvider =
    AsyncNotifierProvider<AlarmListNotifier, List<Alarm>>(AlarmListNotifier.new);

// ❌ instance-field declaration — new identity on every build, lifecycle breaks
class AlarmScreen extends StatelessWidget {
  final _provider = AsyncNotifierProvider<AlarmListNotifier, List<Alarm>>(
    AlarmListNotifier.new,
  );
}
```

Review heuristic: grep for `Provider(` inside class bodies or `build` methods — every hit
is a mis-scoped declaration. Grep for hand-written `XxxProvider(` at the top level — every
hit is a candidate for `@riverpod` migration.

Ref: https://riverpod.dev/docs/concepts/about_code_generation  
Ref: https://riverpod.dev/docs/migration/from_riverpod_2_0_0_to_3_0_0

---

### Lifecycle notes

- **autoDispose is the default** with `@riverpod` — the provider disposes when the last
  listener leaves; a new listener in the same tick resumes without re-running `build()`.

- **keepAlive** — opt in with `@Riverpod(keepAlive: true)` only when ALL THREE gates pass:
  few/stable dependencies, state rarely updates, and re-running `build()` is genuinely
  costly. A provider that mutates on user actions does NOT qualify.
  Lint: `only_use_keep_alive_inside_keep_alive` — a keepAlive provider cannot watch an
  autoDispose one.

- **non-codegen autoDispose** — in manual providers (legacy), use `isAutoDispose: true`
  param instead of the old `.autoDispose` modifier.

- **automatic retry** (3.0) — a provider whose `build()` throws retries with exponential
  backoff by default. `Error` subclasses and `ProviderException` are NOT retried. Disable
  per-provider with `@Riverpod(retry: (count, error) => null)` or globally via
  `ProviderScope(retry: (count, error) => null)`.

- **legacy providers** (`StateProvider`, `StateNotifierProvider`, `ChangeNotifierProvider`)
  now require `import 'package:flutter_riverpod/legacy.dart'`; never write new ones.

- **family params** — become annotated function or `build()` parameters:
  ```dart
  @riverpod
  Future<Alarm> alarm(Ref ref, String id) =>
      ref.watch(alarmRepositoryProvider).getById(id);
  // consumed: ref.watch(alarmProvider('alarm-42'))
  ```

- **ref.onDispose** — register cleanup inside `build()` (or a function provider body) to
  run when the provider is disposed or rebuilt. Use it to cancel subscriptions, close
  streams, or dispose controllers:
  ```dart
  @riverpod
  class AlarmPoller extends _$AlarmPoller {
    @override
    Future<List<Alarm>> build() {
      final timer = Timer.periodic(const Duration(seconds: 30), (_) => ref.invalidateSelf());
      ref.onDispose(timer.cancel); // called on dispose or before the next build()
      return ref.watch(alarmRepositoryProvider).getAlarms();
    }
  }
  ```
  `ref.onDispose` replaces the old `dispose()` override on `StateNotifier`. Never store
  cleanup state as a notifier field and override `dispose()` — Riverpod's generator does
  not expose that hook.

- **invalidation cascade direction** — invalidating a downstream provider does nothing to
  upstream providers. To refresh A → B → C, invalidate A and the cascade carries through.

- **naming** — class `AlarmList` → generated `alarmListProvider`. Avoid `XxxNotifier`,
  `Controller`, or `ViewModel` suffixes; the generator strips a trailing `Notifier` suffix
  automatically, but plain noun names produce the cleanest symbols.
