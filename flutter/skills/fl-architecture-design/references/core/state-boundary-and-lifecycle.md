---
title: Package-Agnostic Provider Boundary; Dispose Everything
impact: HIGH
tags: state, provider, package-agnostic, seam, lifecycle, dispose, memory-leak
---

## Package-Agnostic Provider Boundary; Dispose Everything

The UI sees only observable state flowing in and named commands flowing out. How those are wired — subscription model, selector syntax, holder declaration — lives behind the provider seam and changes only when the package changes. Every controller, subscription, and listener a widget allocates must be released in `dispose()`.

- **Keep the seam package-agnostic** — widgets depend on a state type and a set of command methods, not on package-specific globals, annotations, or registry lookups; this lets the package swap without touching UI code.
- **Holders own all logic** — filtering, sorting, and business rules belong in the holder, not in `build()`; the widget is a pure function of its inputs.
- **Prefer lifecycle-managing builders** — `StreamBuilder`, `ListenableBuilder`, and equivalent package builders manage their own subscriptions; reach for manual `addListener`/`listen` only when no builder covers the use case.
- **Remove listeners before disposing** — call `removeListener` before `dispose()` on the same object; reversing the order risks a callback firing on a dead object.
- **Cancel every subscription** — store each `StreamSubscription` in a field and call `cancel()` in `dispose()`; a `.listen(` with no stored handle is a leak.
- **Never:** embed business logic in `build()`; reach into a package's global registry from a widget; leave `addListener` without a paired `removeListener`.
- **Package-specific rules** live in the project's state-management skill (e.g. the **`fl-riverpod`** skill, loaded when Riverpod is detected).

```dart
class _FeedState extends State<FeedScreen> {
  late final FeedNotifier _notifier;
  StreamSubscription<Alert>? _alertSub;

  @override
  void initState() {
    super.initState();
    _notifier = context.read<FeedNotifier>();
    _notifier.addListener(_onStateChange);          // ← paired below
    _alertSub = _notifier.alerts.listen(_onAlert);  // ← paired below
  }

  void _onStateChange() => setState(() {});
  void _onAlert(Alert a) { /* show snackbar */ }

  @override
  void dispose() {
    _notifier.removeListener(_onStateChange); // remove BEFORE dispose
    _alertSub?.cancel();                      // cancel subscription
    super.dispose();
  }
}
```

Ref: https://verygood.ventures/blog/very-good-flutter-architecture/
Ref: https://dcm.dev/blog/2024/10/21/lets-talk-about-memory-leaks-in-dart-and-flutter/
