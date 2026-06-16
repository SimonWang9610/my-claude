---
title: Respect the Four-Layer Boundary; Dependencies Point One Way
impact: CRITICAL
tags: layers, dependency-direction, coupling, structure, feature-first, naming
---

## Respect the Four-Layer Boundary; Dependencies Point One Way

The four layers — UI → Provider → Data → Service — form a strict one-way chain. Each layer calls only the one immediately below it. Skipping or reversing a layer collapses the testability seam and scatters business logic across transport code.

- **Enforce strict descent** — a widget calls a provider/notifier; a notifier calls a repository; a repository calls a service. No widget imports a repository or service.
- **No sibling-layer awareness** — repositories do not inject other repositories; one notifier does not read another; when siblings share data, a composite owner at the layer above coordinates.
- **One owner per fact** — if two places hold the same value, one is a stale copy waiting to diverge.
- **Role-based feature folders** — group by feature, then by role: `<feature>/{screens, widgets, providers, models, services, utils}/`, and each folder may nest subfolders to group related logic. Shared infra lives in `lib/core/`. Filenames carry their role suffix (`*Screen`, `*Widget`, `*Provider`/`*Notifier`, `*Model`, `*Dto`, `*Service`, `*Repository`); data-access/repositories live under `services/`. Folders are physical roles — the logical four-layer dependency direction still holds.
- **Feature self-containment** — one feature never reaches into another feature's folders; cross-feature access goes through that feature's public provider/route only.
- **Wrap native SDKs** — put a third-party native SDK behind its own in-repo package `packages/<vendor>_sdk_wrapper/`; feature code never imports native bindings directly.
- **Split signal** — a class that answers more than one layer question is doing too much; split it.
- **Module deletion test** — if deleting a module concentrates complexity at its call sites it earns its place; if it just flattens them, fold it in.
- **Never:** import a service or repository directly in a widget; reverse a dependency upward; name a file without its architectural role suffix.

```
lib/
  features/
    auth/
      screens/      # *Screen — full pages / routes
      widgets/      # *Widget — reusable UI pieces
      providers/    # *Provider / *Notifier — state holders
      models/       # *Model (domain, immutable) + *Dto (wire shape)
      services/     # *Service (raw sources) + *Repository (SSOT / data access)
      utils/        # feature-local helpers
  core/             # shared infra (http client, error types, shared utils)
  # any role folder may nest subfolders, e.g. services/api/, providers/settings/
```

```dart
// Correct direction: widget → notifier → repository → service
// Widget
class ProfileScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    // reads from notifier only
    final state = context.watch<ProfileNotifier>().state;
    return Text(state.displayName);
  }
}

// Notifier (illustrative — your state-management package applies the same principle)
class ProfileNotifier extends ChangeNotifier {
  ProfileNotifier(this._repo);
  final ProfileRepository _repo;          // ← depends on repo, not service

  ProfileState state = const ProfileState.loading();

  Future<void> load(String id) async {
    state = await _repo.getProfile(id)    // ← repo returns domain model
        .then(ProfileState.data)
        .catchError(ProfileState.error);
    notifyListeners();
  }
}

// Repository calls service — domain model never leaks below this line
// Service returns raw DTO — repository maps it
```

Ref: https://docs.flutter.dev/app-architecture/guide | https://docs.flutter.dev/app-architecture/concepts | https://codewithandrea.com/articles/flutter-project-structure/
