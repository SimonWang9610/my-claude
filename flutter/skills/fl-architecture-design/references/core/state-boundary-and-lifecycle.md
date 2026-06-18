---
title: Package-Agnostic Provider Boundary; Dispose Everything
impact: HIGH
tags: state, provider, package-agnostic, seam, lifecycle, dispose, memory-leak
---

## Package-Agnostic Provider Boundary; Dispose Everything

The UI sees only observable state flowing in and named commands flowing out. How those are wired — subscription model, selector syntax, holder declaration — lives behind the provider seam and changes only when the package changes. Every subscription and resource a widget or notifier allocates must be released when the scope ends.

- **Holders own all logic** — filtering, sorting, and business rules belong in the holder, not in `build()`; the widget is a pure function of its inputs.
- **With Riverpod: use `ref.watch`, `ref.listen`, `ref.onDispose`** — `ref.watch` in `build()` drives rebuilds; `ref.listen` in `build()` runs side effects (snackbars, navigation) without causing a rebuild; `ref.onDispose()` inside `build()` releases any resource allocated there (e.g. a raw `StreamSubscription`). Manual `addListener`/`removeListener`/`dispose()` overrides are not needed for Riverpod-managed state.
- **`ref.read` only in event handlers** — calling `ref.read` in `build()` reads a stale snapshot and causes the widget to miss future updates; use `ref.watch` instead.
- **Cancel every raw subscription** — if a non-Riverpod `StreamSubscription` is opened, store it in a field and call `cancel()` in `dispose()`, or open it in `build()` and pass `cancel` to `ref.onDispose()`; a `.listen(` with no stored handle is a leak.
- **Never:** embed business logic in `build()`; call `ref.read` in `build()` to "avoid rebuilds" (that is a stale-UI bug); leave a raw `StreamSubscription` with no cleanup path.
- **Package-specific rules** live in the project's state-management skill (e.g. the **`fl-riverpod`** skill, loaded when Riverpod is detected).

```dart
// With Riverpod: use ref.watch (rebuilds on state change) and ref.listen
// (side effects) — manual addListener / removeListener is not needed.
// ref.onDispose() in build() cleans up any resource allocated there.
class FeedScreen extends ConsumerWidget {
  const FeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // ref.watch — rebuilds the widget when state changes
    final feed = ref.watch(feedNotifierProvider);

    // ref.listen — side effect only; never drives rebuild
    ref.listen<AsyncValue<Feed>>(feedNotifierProvider, (_, next) {
      if (next case AsyncError(:final error)) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('$error')));
      }
    });

    return switch (feed) {
      AsyncData(:final value) => FeedList(items: value.items),
      AsyncError(:final error) => ErrorView(error: error),
      _ => const CircularProgressIndicator(),
    };
  }
}

// When a raw StreamSubscription must be held (e.g. a non-Riverpod stream),
// allocate it inside build() and release it with ref.onDispose():
class FeedScreenWithRawSubscription extends ConsumerWidget {
  const FeedScreenWithRawSubscription({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sub = someExternalStream.listen((_) {});
    ref.onDispose(sub.cancel); // ← paired disposal; no dispose() override needed
    // ...
  }
}
```

Ref: https://verygood.ventures/blog/very-good-flutter-architecture/
Ref: https://dcm.dev/blog/2024/10/21/lets-talk-about-memory-leaks-in-dart-and-flutter/
