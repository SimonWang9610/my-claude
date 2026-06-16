---
title: Keep build() Small, const, and Async-Safe
impact: HIGH
tags: performance, const, setState, rebuild-optimization, async, buildcontext, mounted
---

## Keep build() Small, const, and Async-Safe

Three disciplines keep `build()` efficient and correct: use `const` at both the class declaration and every call site to let Flutter skip unchanged subtrees; keep `build()` small and push `setState` down to the smallest owning widget; never access `BuildContext` after an `await` without a `mounted` check.

- **`const` at declaration and call site** — declaring a `const` constructor is only half the win; you must also write `const MyWidget()` at the call site so Dart canonicalizes the instance at compile time and Flutter skips diffing the subtree entirely.
- **Keep `build()` small** — flag any `build()` exceeding ~40 lines; decompose into focused child widgets rather than adding more code to the parent.
- **Localize `setState` to the smallest subtree** — a `setState` at the page level rebuilds the whole tree on every interaction, including static elements; push `StatefulWidget` + `setState` as close to the changing UI as possible.
- **Guard `BuildContext` after `await`** — `BuildContext` is only valid while the widget is mounted; either capture context-derived objects before the `await`, or check `if (!context.mounted) return` immediately after.
- **Never:** call `setState` on a root page widget for a toggle that affects only one small region; use `BuildContext` after an `await` without a `mounted` guard; omit `const` at call sites for widgets that support it.
- **Lint enforcement** — enable `prefer_const_constructors`, `prefer_const_literals_to_create_immutables`, and `use_build_context_synchronously`.

```dart
// const child — Dart canonicalizes at compile time; Flutter skips diffing
@override
Widget build(BuildContext context) {
  return Column(
    children: [
      const _Header(title: 'Checkout'), // ← const at call site: subtree skipped
      CheckoutForm(onSubmit: _submit),
    ],
  );
}

Future<void> _submit() async {
  final nav = Navigator.of(context); // ← capture before await
  await _notifier.placeOrder();
  if (!context.mounted) return;      // ← mounted guard after await
  nav.pushNamed('/confirmation');
}
```

Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://dart.dev/tools/linter-rules/use_build_context_synchronously
