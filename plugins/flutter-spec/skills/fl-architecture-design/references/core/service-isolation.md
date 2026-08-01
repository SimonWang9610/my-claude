---
title: Services Isolate One Raw Source Each
impact: HIGH
tags: services, single-responsibility, stateless, dto, raw-payload, typed-errors, transport
---

## Services Isolate One Raw Source Each

A service is the thinnest possible adaptor between the app and one external data source. It is stateless, knows only transport mechanics, and returns raw wire-shaped data. All policy (caching, retry, throttle) and all domain mapping belong in the repository above.

- **One stateless service per source** — `ApiClient` handles HTTP only; a class importing multiple transports must be split.
- **Return raw DTOs** — never construct a domain model inside a service; that couples wire format to business logic and is the repository's job.
- **Map transport exceptions to typed errors at the boundary** — `SocketException`, `TimeoutException`, and HTTP error codes must not escape the service raw; catch and rethrow as typed app exceptions defined once in `core/`.
- **Service seam shape** — each service is an `abstract interface class` with a file-private `_Impl` via a redirecting factory; never put a `.mock()` factory on the production interface — fakes live in `test/`.
- **Never:** hold a cache field in a service; apply retry logic in a service; return a domain model from a service; let a raw `SocketException` propagate to a repository or notifier.

```dart
// Public seam — redirecting factory; callers get the interface, impl stays private
abstract interface class ProductService {
  factory ProductService(HttpClient client) = _ProductServiceImpl;
  Future<List<ProductDto>> fetchProducts();
}

// File-private implementation — transport details hidden here
class _ProductServiceImpl implements ProductService {
  _ProductServiceImpl(this._client);
  final HttpClient _client;

  @override
  Future<List<ProductDto>> fetchProducts() async {
    try {
      final json = await _client.get('/products');
      return (json as List).map(ProductDto.fromJson).toList();
    } on SocketException catch (e) {
      throw NetworkException(cause: e);   // typed error; never raw exception
    }
  }
}
```

Ref: https://docs.flutter.dev/app-architecture/case-study/data-layer | https://resocoder.com/2019/09/09/flutter-tdd-clean-architecture-course-4-data-layer-overview-models/
