---
title: Unidirectional Flow with Immutable State; Sealed Async
impact: CRITICAL
tags: state, unidirectional, immutability, events, async, sealed-class, error-handling
---

## Unidirectional Flow with Immutable State; Sealed Async

State flows down to widgets; user intent flows up as named commands to the state holder, which emits a new immutable state object. Async operations are modelled as a sealed `loading | data | error` union so the compiler enforces exhaustive handling and swallowed errors become impossible.

- **State down, events up** — widgets receive state and call named commands; they never reach into a holder and mutate a field directly.
- **Replace, don't mutate** — every command produces a new state value (new list, new object) and notifies listeners; in-place mutation silently bypasses listeners.
- **Model async as a sealed union** — three independent nullable booleans (`isLoading`, `data`, `error`) allow ~14 representable states, 13 of them illegal; a sealed `AsyncLoading | AsyncData | AsyncError` type collapses to three.
- **Match exhaustively** — use `switch` on the async union so the compiler catches missing branches; never leave a `default:` that silently ignores new states.
- **Never swallow errors** — a bare `catch (_) {}` leaves the widget frozen on a spinner; always route caught exceptions into the `error` variant with the real exception preserved.

```dart
// Riverpod AsyncNotifier — AsyncValue<T> is the built-in sealed async union
// (AsyncLoading | AsyncData | AsyncError); no custom sealed class needed.
@riverpod
class ProductNotifier extends _$ProductNotifier {
  @override
  Future<List<Product>> build() =>
      ref.watch(productRepositoryProvider).getProducts(); // initial load

  Future<void> reload() async {
    state = const AsyncLoading();                       // state down
    state = await AsyncValue.guard(                     // never swallowed
      () => ref.read(productRepositoryProvider).getProducts(),
    );
  }
}

// Widget build() — exhaustive switch expression on AsyncValue, no default:
return switch (ref.watch(productNotifierProvider)) {
  AsyncLoading() => const CircularProgressIndicator(),
  AsyncData(:final value) => ProductList(items: value),
  AsyncError(:final error) => ErrorView(error: error),
};

// When a custom sealed union is preferred (non-Riverpod holder or richer states):
// Note: names must not collide with Riverpod's AsyncLoading/AsyncData/AsyncError exports.
sealed class FetchState<T> { const FetchState(); }
class FetchLoading<T> extends FetchState<T> { const FetchLoading(); }
class FetchData<T>    extends FetchState<T> { const FetchData(this.value); final T value; }
class FetchError<T>   extends FetchState<T> { const FetchError(this.error); final Object error; }
```

Ref: https://docs.flutter.dev/app-architecture/recommendations
Ref: https://codewithandrea.com/articles/flutter-use-async-value-not-future-stream-builder/
