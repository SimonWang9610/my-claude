---
title: Inject Dependencies via Constructors; Wire Once at a Composition Root
impact: CRITICAL
tags: dependency-injection, constructor, composition-root, testability, interfaces, wiring
---

## Inject Dependencies via Constructors; Wire Once at a Composition Root

Every collaborator a class needs must be injected, not constructed in place. The entire dependency graph is assembled once at a composition root before the widget tree is built. Classes that fetch their own dependencies hide coupling and cannot be tested in isolation.

- **Inject via provider `ref.watch` (Riverpod) or constructor parameters** — inside a Riverpod `Notifier`, read collaborators with `ref.watch(collaboratorProvider)` in `build()`; for non-Riverpod classes, pass collaborators through the constructor typed as abstract interfaces. Either way, collaborators are never constructed inside the class body.
- **No hidden singletons** — `Service.instance` calls and field-initialiser `= ConcreteClass()` expressions are banned; they make the class untestable without side effects.
- **Depend on abstract interfaces** — the seam that allows fake substitution is the interface; the concrete type is chosen once at the composition root, not scattered across the codebase.
- **Wire once at a composition root** — with Riverpod, assemble overrides in one `ProviderScope` at `main()`; spreading concrete-type choices or `override` calls across files duplicates them and prevents environment swaps.
- **Never:** construct a concrete collaborator as a field initialiser; reach for a global `instance` inside a notifier or service body; duplicate a concrete-type choice in more than one file.

```dart
// WRONG — hidden singleton, untestable
@riverpod
class OrderNotifier extends _$OrderNotifier {
  // BAD: reaches for a global directly — cannot be overridden in tests
  final _repo = OrderRepositoryImpl(ApiClient.instance);

  @override
  FutureOr<Order?> build() => null;
}

// CORRECT — injected abstract dependency via Riverpod provider override
abstract interface class OrderRepository {
  Future<Order> getOrder(String id);
}

// Repository provider typed as the abstract interface
@riverpod
OrderRepository orderRepository(Ref ref) {
  final client = ref.watch(httpClientProvider);
  final service = OrderApiService(client);
  return OrderRepositoryImpl(service); // ← concrete only here
}

// Notifier reads the interface provider — never constructs concrete types
@riverpod
class OrderNotifier extends _$OrderNotifier {
  @override
  FutureOr<Order?> build() => null;

  Future<void> load(String id) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(orderRepositoryProvider).getOrder(id),
    );
  }
}

// Composition root (main.dart) — wire once via ProviderScope overrides
void main() {
  final client = HttpApiClient(baseUrl: Env.apiUrl);
  runApp(
    ProviderScope(
      overrides: [
        httpClientProvider.overrideWithValue(client),
      ],
      child: const App(),
    ),
  );
}

// Test — swap the concrete impl without touching production code
testWidgets('shows order', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        orderRepositoryProvider.overrideWithValue(FakeOrderRepository()),
      ],
      child: const OrderScreen(),
    ),
  );
});
```

Ref: https://docs.flutter.dev/app-architecture/case-study/dependency-injection
