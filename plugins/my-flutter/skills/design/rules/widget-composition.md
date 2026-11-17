---
title: Compose Small Widgets; Extract Classes, Not Helper Methods
impact: HIGH
tags: composition, widgets, inheritance, const, stateless, stateful, rebuild-optimization, purity
---

## Compose Small Widgets; Extract Classes, Not Helper Methods

Flutter's composition model rewards many small, focused widgets over large monoliths. Accept `Widget` parameters to customize rather than subclassing; extract named `StatelessWidget` classes instead of `Widget _buildX()` helpers; default to `StatelessWidget` and promote to stateful only for genuinely owned ephemeral state.

- **Compose, don't subclass** — extending a concrete widget couples to its internals; wrap it in a `StatelessWidget` that accepts a `child` or callback instead.
- **Extract classes, not helpers** — a `Widget _buildX()` method runs inside the parent's `build()` on every rebuild and cannot be `const`; a named class with a `const` constructor gives Flutter a stable element identity and enables subtree skipping.
- **Default `StatelessWidget`** — promote to `StatefulWidget` only when the widget genuinely owns mutable ephemeral state (`AnimationController`, `TextEditingController`, a local toggle); a `State` subclass with no fields and no `setState` call is dead weight.
- **Push purity downward** — keep reactive reads (`ref.watch`, `ListenableBuilder`) at the leaves; pure widgets above them rebuild only when their inputs change, not on every state notification.
- **A "pure" widget one subscribe away from working is a smell** — if the only reason a `StatelessWidget` becomes reactive is that it's *convenient*, pass the value in as a parameter instead.
- **Default file-private** — new widget classes are `_Private` by default; promote to public only on a second call site or a test that targets the inner widget directly.
- **Split on signals** — extract a subtree when `build()` exceeds ~80 lines, an async-value switch is inlined, or a subtree is reusable elsewhere.
- **Never:** return a `Widget` from a helper method when a named class would do; subclass `ElevatedButton`, `ListTile`, or any other concrete widget.

```dart
// WRONG — helper method: parent rebuilds on every frame, cannot be const
Widget _buildHeader(String title) => Padding(
      padding: const EdgeInsets.all(16),
      child: Text(title, style: const TextStyle(fontSize: 20)),
    );

// CORRECT — file-private const class: Flutter skips the subtree when title is unchanged
class _Header extends StatelessWidget {
  const _Header({required this.title});
  final String title;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.all(16),
        child: Text(title, style: Theme.of(context).textTheme.titleLarge),
      );
}

// Call site — const-constructible, stable element identity
const _Header(title: 'Orders'),
```

Ref: https://docs.flutter.dev/ui/widgets-intro
Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://docs.flutter.dev/ui/interactivity
