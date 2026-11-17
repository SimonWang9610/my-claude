---
title: Place State at the Right Level; One Owner per Fact
impact: CRITICAL
tags: state, ownership, ephemeral, local, provider, scoping, single-source-of-truth
---

## Place State at the Right Level; One Owner per Fact

State belongs in the most local scope that satisfies all its readers. Ephemeral single-widget concerns stay local; state that crosses widget boundaries or survives navigation lifts to a scoped provider. Every stored fact has exactly one owner — values computable from other fields are getters, never stored fields.

- **Place ephemeral state locally** — hover flags, animation progress, and focus state belong in a `StatefulWidget`'s own fields, not in a shared provider that couples unrelated widgets.
- **Lift only when necessary** — promote to a provider only when siblings or routes need the value, or when it must outlive the widget.
- **Derive, don't duplicate** — `isLoggedIn`, `itemCount`, `hasErrors` are getters over their source field; storing them separately creates drift under concurrent updates.
- **Never:** store a field whose value is always `someOtherField != null` or `list.length`; push single-widget concerns into a shared notifier.
- **Mechanism choice lives elsewhere** — which holder to use (local `setState` → scoped `InheritedWidget` → provider) is a decision tree in `state-ownership-decision.md`; this rule covers discipline *inside* whichever holder wins.

```dart
// Riverpod Notifier with code-gen
// State is an immutable value object; derived booleans are getters on it.
class SessionState {
  const SessionState({this.user, this.errors = const []});
  final User? user;
  final List<String> errors;

  // CORRECT — derived getters; source of truth is user / errors
  bool get isLoggedIn => user != null;
  bool get hasErrors  => errors.isNotEmpty;
  int  get errorCount => errors.length;
}

@Riverpod(keepAlive: true)
class SessionNotifier extends _$SessionNotifier {
  @override
  SessionState build() => const SessionState();

  void setUser(User? user) =>
      state = SessionState(user: user, errors: state.errors);

  // WRONG — never store a field whose value duplicates another field:
  // state = state.copyWith(isLoggedIn: user != null); // ← redundant, can diverge
}
```

Ref: https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app
Ref: https://docs.flutter.dev/app-architecture/concepts
