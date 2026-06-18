# Principle examples — P1–P8 compact reference

For violation signals and trigger crosswalk, see [`principle-checks.md`](principle-checks.md).

---

| ID | Rule summary | RIGHT looks like | WRONG looks like | Ref |
|----|-------------|-----------------|-----------------|-----|
| P1 | Four-layer boundary; UI→Provider→Data→Service only | Widget depends on holder only | Widget imports `*Repository` directly | https://docs.flutter.dev/app-architecture/guide |
| P2 | Service: stateless, raw DTOs, maps transport errors | `ApiClient` returns `DeviceDto`, catches `DioException → ApiException` | Service constructs domain models or caches results | https://docs.flutter.dev/app-architecture/case-study/data-layer |
| P3 | Repository = SSOT per type; `dto.toDomain()`; no DTOs escape | `DeviceRepository.watchAll()` merges all data sources, yields `Device` | Notifier holds its own `_localCache` of `Device` beside the repo | https://docs.flutter.dev/app-architecture/concepts |
| P4 | Holder receives repo via constructor (or `@riverpod` `Notifier`/`AsyncNotifier`); exposes sealed state + named commands; package-agnostic seam | `@riverpod` `DeviceNotifier` with injected `DeviceRepository` ref and `void select(String id)` command; `ref.watch` in `build()`, `ref.read` only in handlers | `ChangeNotifier` injected with raw `Dio`; fetches, caches, paginates in one class; or `ref.read` inside `build()` to avoid rebuilds | https://docs.flutter.dev/app-architecture/guide |
| P5 | Ephemeral state stays local; shared/surviving state lifts to provider | `_hovered` in `StatefulWidget`; device list in `DeviceNotifier` | `hoveredDeviceId` in a shared `AppNotifier` | https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app |
| P6 | Widgets compose; `build` is pure; `const`; theme tokens; `mounted` check after `await` | `const DeviceStatusBadge({...})` with `Theme.of(context).colorScheme.primary` | `Widget _buildBadge()` helper with hard-coded `Color(0xFF...)` and no `mounted` check | https://docs.flutter.dev/perf/best-practices |
| P7 | Dispose every subscription/controller; sealed async type; never swallow errors | Dart 3 `sealed class DeviceState` with exhaustive `switch`; `ref.onDispose(() => _sub.cancel())` in Riverpod `build()` | `bool isLoading + List? devices` (impossible state); leaked `StreamSubscription`; `catch (_) {}`; `ref.read` in `build()` | https://docs.flutter.dev/app-architecture/recommendations |
| P8 | Every unit independently verifiable with injected fakes | Holder tested via `ProviderContainer` override; widget via `pumpWidget` with fake notifier | AC behavior only reachable by pumping the full `AppShell` host tree | https://docs.flutter.dev/app-architecture/case-study/testing |
