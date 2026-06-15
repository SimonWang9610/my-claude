---
title: Inject Dependencies via Constructors; Wire Once at a Composition Root
impact: CRITICAL
tags: dependency-injection, constructor, composition-root, testability, interfaces, wiring
---

## Inject Dependencies via Constructors; Wire Once at a Composition Root

Every collaborator a class needs must arrive through its constructor, typed as an abstract interface. The entire dependency graph is assembled once at a composition root before the widget tree is built. Classes that fetch their own dependencies hide coupling and cannot be tested in isolation.

- **Constructor injection only** — all collaborators (repositories, services, clocks, loggers) are constructor parameters typed as abstract interfaces; they are never constructed inside a class body.
- **No hidden singletons** — `Service.instance` calls and field-initialiser `= ConcreteClass()` expressions are banned; they make the class untestable without side effects.
- **Depend on abstract interfaces** — the seam that allows fake substitution is the interface; the concrete type is chosen once at the composition root, not scattered across the codebase.
- **Wire once at a composition root** — assemble the full Service → Repository → Notifier graph in one place (`lib/main.dart` or an `AppFactory`); spreading concrete-type choices across files duplicates them and prevents environment swaps.
- **Never:** reach into a global registry inside a method; construct a concrete collaborator as a field initialiser; duplicate a concrete-type choice in more than one file.

```dart
// WRONG — hidden singleton, untestable
class OrderNotifier extends ChangeNotifier {
  final _repo = OrderRepository(ApiClient.instance); // ← concrete, hidden
}

// CORRECT — injected abstract dependency
abstract interface class OrderRepository {
  Future<Order> getOrder(String id);
}

class OrderNotifier extends ChangeNotifier {
  OrderNotifier(this._repo);               // ← typed as interface
  final OrderRepository _repo;
}

// Composition root (main.dart / AppFactory) — wired once
void main() {
  final client  = HttpApiClient(baseUrl: Env.apiUrl);
  final service = OrderApiService(client);
  final repo    = OrderRepositoryImpl(service);
  runApp(App(orderNotifier: OrderNotifier(repo)));
}
```

Ref: https://docs.flutter.dev/app-architecture/case-study/dependency-injection
