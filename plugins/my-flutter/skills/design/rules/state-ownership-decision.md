---
title: Choose the State Mechanism by Scope — setState → InheritedWidget → Provider
impact: CRITICAL
tags: state, ownership, scoping, setState, inherited-widget, provider, navigation, design
---

## Choose the State Mechanism by Scope — setState → InheritedWidget → Provider

Pick the narrowest mechanism that satisfies all of a state's readers. Escalate only when the current tier cannot reach every reader. The escalation triggers are concrete: siblings force you past local `setState`; a navigation boundary forces you past an `InheritedWidget` scope.

- **Tier 1 — local `setState`** for ephemeral, single-widget state (hover, expand/collapse, focus, animation progress) that no sibling reads and that dies with the widget.
- **Tier 2 — `InheritedWidget` scope** to share a read-only model down a subtree within one page; carry data, not callbacks — descendants read, the owning `StatefulWidget` above mutates and rebuilds the scope.
- **Tier 3 — provider** for state shared across multiple pages, state that survives navigation, or state held for re-fetch cost reasons.
- **Shared-state justification gate** — a shared provider/cache is justified only when two or more readers share it, or re-fetch is expensive, or it holds business/optimistic state; "might want sharing later" is not a justification.
- **`InheritedWidget` route boundary** — an `InheritedWidget` does not cross a navigation boundary; a dialog, pushed route, bottom sheet, or overlay is a new branch off `Navigator`/`Overlay` and won't see it — if the data must follow the user there, use a provider.
- **Never:** thread mutation callbacks through an `InheritedWidget`; lift ephemeral UI state into a global provider; assume an `InheritedWidget` is visible inside a `showDialog` or pushed route.

```dart
// Tier 2 example: InheritedWidget carries a read-only model down a subtree.
// Descendants read; the owning StatefulWidget above mutates and calls setState.
class _FormScope extends InheritedWidget {
  const _FormScope({required this.formData, required super.child});
  final FormData formData; // data down only — no callbacks

  static FormData of(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<_FormScope>()!.formData;

  @override
  bool updateShouldNotify(_FormScope old) => formData != old.formData;
}

// Usage in a descendant — read only
final data = _FormScope.of(context);
```

Ref: https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html
Ref: https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app
Ref: https://docs.flutter.dev/data-and-backend/state-mgmt/options
