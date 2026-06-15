---
title: Domain Models Are Immutable, Pure Dart, with Value Equality
impact: HIGH
tags: domain-models, immutability, pure-dart, value-equality, equatable, freezed, dto-separation
---

## Domain Models Are Immutable, Pure Dart, with Value Equality

A domain model represents a business concept. It must be stable across UI-framework changes, testable without Flutter, and comparable by value. Mutable fields allow silent state corruption; Flutter/JSON imports couple the model to infrastructure; missing value equality breaks `distinct()`, set membership, and causes needless rebuilds.

- **All fields `final`; no Flutter or JSON imports** — wire-format parsing belongs in a `*Dto` in the data layer; UI-derived values (colours, labels) belong in widgets or theme extensions.
- **Value equality via `Equatable`, `@freezed`, or `==`/`hashCode` override** — pick one approach and apply it consistently across the project; don't mix strategies within a feature.
- **Wrap exposed collections** — return `List.unmodifiable(...)` from getters that expose internal lists so callers cannot mutate shared state silently.
- **`fromJson` totality** — parsing belongs on the `*Dto`, not the domain model; when writing DTO parsers choose defaults for missing/unknown values — never throw in production parsing.
- **`copyWith` nullable pitfall** — a nullable `T?` copyWith param cannot distinguish "no change" from "set to null"; add a dedicated `clearX()` method or use `@freezed` which generates correct nullable copyWith semantics.
- **Never:** import `package:flutter` in a domain model; hold a raw wire string (`String severity`, `String triggeredAt`) as a domain field; define `fromJson`/`toJson` on a domain model.

```dart
// Pure Dart, no Flutter import
import 'package:equatable/equatable.dart';

class Product extends Equatable {
  const Product({required this.id, required this.name, required this.priceCents});

  final String id;
  final String name;
  final int priceCents;

  Product copyWith({String? id, String? name, int? priceCents}) => Product(
        id: id ?? this.id,
        name: name ?? this.name,
        priceCents: priceCents ?? this.priceCents,
      );

  @override
  List<Object?> get props => [id, name, priceCents]; // value equality
}

// @freezed is the alternative — it generates copyWith with correct nullable semantics:
// @freezed class Product with _$Product { const factory Product({...}) = _Product; }
// Nullable copyWith pitfall: copyWith(discount: null) is ambiguous without @freezed.
```

Ref: https://docs.flutter.dev/app-architecture/recommendations | https://pub.dev/packages/equatable | https://pub.dev/packages/freezed
