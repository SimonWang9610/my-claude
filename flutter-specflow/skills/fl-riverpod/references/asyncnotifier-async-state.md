---
title: "Riverpod: Use @riverpod AsyncNotifier + AsyncValue for User-Driven Async State"
impact: CRITICAL
impactDescription: FutureProvider is read-only; manual bool flags allow partial handling that silently drops loading or error states; hand-written AsyncNotifierProvider is the legacy form the generator replaces
tags: state, riverpod, async, AsyncValue, AsyncNotifier, FutureProvider, sealed, codegen
---

## Riverpod: Use @riverpod AsyncNotifier + AsyncValue for User-Driven Async State

When the UI triggers async operations (acknowledge, delete, refresh), declare an
`AsyncNotifier` with `@riverpod` — the generator wires up the provider and `autoDispose`.
Named command methods drive state through `AsyncValue.loading / data / error`.

`FutureProvider` is read-only (no command surface). Ad-hoc `bool isLoading` + nullable
result allow partial handling: forgotten loading guards flash stale data; omitted error
branches silently swallow exceptions.

**Correct:**
```dart
// ✅ @riverpod class notifier — sealed async state, named commands, autoDispose default
@riverpod
class AlarmList extends _$AlarmList {
  @override
  Future<List<Alarm>> build() =>
      ref.watch(alarmRepositoryProvider).getAlarms();

  Future<void> acknowledgeAll() async {
    state = const AsyncValue.loading();
    // AsyncValue.guard captures exceptions as AsyncError — no try/catch boilerplate
    state = await AsyncValue.guard(
      () => ref.read(alarmRepositoryProvider).acknowledgeAll(),
    );
    if (!ref.mounted) return; // ← guard after every await (3.0)
  }
}
// → generator produces alarmListProvider
```

**Consuming — exhaustive `switch` is the primary idiom in 3.0 (`AsyncValue` is sealed):**
```dart
// ✅ primary: exhaustive switch, no default needed (sealed)
switch (ref.watch(alarmListProvider)) {
  case AsyncData(:final value):
    return AlarmListView(alarms: value);
  case AsyncError(:final error):
    return ErrorBanner(error: error);
  case AsyncLoading():
    return const CircularProgressIndicator();
}

// ✅ secondary: .when() still valid (params unchanged), less concise
ref.watch(alarmListProvider).when(
  loading: () => const CircularProgressIndicator(),
  error:   (e, st) => ErrorBanner(error: e),
  data:    (alarms) => AlarmListView(alarms: alarms),
);
```

**`AsyncValue` accessors — 3.0:**
- `.value` — returns `T?`, null while loading or on error (replaces deprecated `valueOrNull`).
- `requireValue` — returns `T`, throws if not in data state.
- `isFromCache` / `retrying` — new in 3.0; inspect whether data is stale or a retry is in progress.

**Auto-retry note:** a provider in `AsyncError` may automatically retry back to `AsyncLoading`
(exponential backoff, on by default). Disable with `@Riverpod(retry: (count, error) => null)`.

**Incorrect (legacy / mis-scoped — do not write new):**
```dart
// ❌ FutureProvider — read-only, no command surface
final alarmListProvider = FutureProvider<List<Alarm>>(
  (ref) => ref.read(alarmRepositoryProvider).getAlarms(),
);

// ❌ hand-written AsyncNotifierProvider — legacy boilerplate the generator replaces
final alarmListProvider =
    AsyncNotifierProvider<AlarmListNotifier, List<Alarm>>(AlarmListNotifier.new);

// ❌ manual bool flags — partial handling guaranteed
class AlarmListNotifier extends StateNotifier<AlarmListState> {
  bool isLoading = false;
  List<Alarm>? alarms;
  String? error;
}
```

Review heuristic: any `bool isLoading` field on a notifier is a smell — replace with
`AsyncValue<T>` on `state`. Any `valueOrNull` reference is deprecated — replace with `.value`.
Any hand-written `AsyncNotifierProvider(...)` is a candidate for `@riverpod` migration.

Ref: https://riverpod.dev/docs/providers/notifier_provider  
Ref: https://riverpod.dev/docs/migration/from_riverpod_2_0_0_to_3_0_0
