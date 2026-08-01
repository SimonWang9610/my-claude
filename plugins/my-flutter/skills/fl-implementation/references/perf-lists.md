---
title: Long Lists & Grids
impact: CRITICAL
tags: lists, ListView, SliverList, lazy, shrinkWrap, itemExtent, IntrinsicHeight, keys, performance
---

## Long Lists & Grids

> **Conditional — consult when a performance concern surfaces (non-blocking).**

Long lists concentrate several independent performance hazards that compound when violated together. Apply these when profiling shows list-scroll jank or slow first-frame render.

- **Use lazy `.builder` constructors** — `ListView(children: [...])` builds every child before the first frame; `ListView.builder` builds only viewport items plus `cacheExtent`.
- **Never `shrinkWrap: true` on long lists** — it forces layout of all children to measure total height, defeating lazy building entirely; use `SliverList` inside `CustomScrollView` instead.
- **Set `itemExtent` or `prototypeItem` for uniform-height rows** — without a known extent Flutter must lay out every prior item to compute scroll offsets (O(n)); a fixed extent reduces this to O(1) arithmetic.
- **Avoid `IntrinsicHeight`/`IntrinsicWidth` inside list items** — each runs a speculative layout pass before the real one, doubling layout cost per visible item.
- **Use `ValueKey(stableId)` on stateful list items** — without a key Flutter matches elements by position; reorder or insert causes state (selection, animation) to bleed between unrelated items.

```dart
// WRONG — builds every child before the first frame.
ListView(children: items.map((e) => ItemTile(e)).toList());

// RIGHT — builds only visible items; stable keys preserve element state.
ListView.builder(
  itemCount: items.length,
  itemExtent: 72,                            // O(1) scroll offset; omit only for variable heights
  itemBuilder: (context, index) => ItemTile(
    key: ValueKey(items[index].id),          // stable key survives reorders/inserts
    item: items[index],
  ),
);
```

Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://api.flutter.dev/flutter/widgets/ScrollView/shrinkWrap.html
Ref: https://api.flutter.dev/flutter/widgets/ListView/itemExtent.html
Ref: https://api.flutter.dev/flutter/widgets/Key-class.html
