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
// Sealed async union — three legal states, compiler-enforced
sealed class AsyncState<T> {
  const AsyncState();
}
class AsyncLoading<T> extends AsyncState<T> { const AsyncLoading(); }
class AsyncData<T>    extends AsyncState<T> { const AsyncData(this.value); final T value; }
class AsyncError<T>   extends AsyncState<T> { const AsyncError(this.error); final Object error; }

// illustrative — your state-management package applies the same principle
class ProductNotifier extends ChangeNotifier {
  AsyncState<List<Product>> state = const AsyncLoading();

  Future<void> load() async {
    state = const AsyncLoading(); notifyListeners();
    try {
      state = AsyncData(await _repo.getProducts());
    } catch (e) {
      state = AsyncError(e);          // never swallowed
    }
    notifyListeners();
  }
}

// Widget — exhaustive switch, no default:
switch (notifier.state) {
  case AsyncLoading() => const CircularProgressIndicator(),
  case AsyncData(:final value) => ProductList(items: value),
  case AsyncError(:final error) => ErrorView(error: error),
}
```

Ref: https://docs.flutter.dev/app-architecture/recommendations
Ref: https://codewithandrea.com/articles/flutter-use-async-value-not-future-stream-builder/
