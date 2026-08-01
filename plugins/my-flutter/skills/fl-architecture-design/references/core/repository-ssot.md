---
title: One Repository Is the Single Source of Truth per Data Type
impact: CRITICAL
tags: repository, ssot, dto, domain-mapping, caching, retry, data-layer, ownership
---

## One Repository Is the Single Source of Truth per Data Type

Each domain entity has exactly one repository that owns and mutates its canonical state. The repository maps DTOs to domain models, enforces caching and retry, and exposes a stream all notifiers observe. No caller above it stores its own copy or applies its own retry. No raw DTO ever escapes this layer.

- **Only the repository mutates** — notifiers subscribe to the repository's stream; they never maintain a long-lived local copy of the data that can diverge.
- **DTO→domain mapping happens here** — `*Dto` types are visible only inside the repository; a `*Dto` appearing in a notifier or widget is a data-layer leak.
- **Caching, retry, and throttle live here** — retry in a service multiplies across every caller; throttle in a widget creates per-screen intervals that leak on dispose; one policy in the repository is inherited by all consumers.
- **Never:** return a raw `*Dto` from a repository method; apply retry inside a service; let a notifier maintain its own copy of server data alongside the repository's stream.

```dart
// DTO — lives only inside the data layer
class UserDto {
  const UserDto({required this.id, required this.fullName});
  final String id;
  final String fullName;
  factory UserDto.fromJson(Map<String, dynamic> j) =>
      UserDto(id: j['id'] as String, fullName: j['full_name'] as String);
}

// Repository — maps DTO→domain, owns the cache, exposes the stream
class UserRepositoryImpl implements UserRepository {
  UserRepositoryImpl(this._service);
  final UserService _service;

  final _cache = <String, User>{};
  final _controller = StreamController<User>.broadcast();

  @override
  Stream<User> watchUser(String id) => _controller.stream;

  @override
  Future<User> getUser(String id) async {
    if (_cache.containsKey(id)) return _cache[id]!;
    final dto = await _service.fetchUser(id);   // raw DTO returned from service
    final user = User(id: dto.id, name: dto.fullName); // ← DTO→domain here only
    _cache[id] = user;
    _controller.add(user);
    return user;
  }
}
```

Ref: https://docs.flutter.dev/app-architecture/concepts | https://docs.flutter.dev/app-architecture/case-study/data-layer
