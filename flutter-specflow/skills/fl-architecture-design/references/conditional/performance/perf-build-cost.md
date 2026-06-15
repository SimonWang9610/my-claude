---
title: Keep build() Cheap
impact: HIGH
tags: build, performance, allocation, sorting, saveLayer, Opacity, operator-equals, reconciliation
---

## Keep build() Cheap

> **Conditional — consult when a performance concern surfaces (non-blocking).**

`build()` is a pure mapping from state to widget tree and runs every time the widget is dirty. Expensive synchronous work or GPU-heavy compositing inside it directly inflates UI and raster thread frame times.

- **No sorting, parsing, or allocation in `build`** — move expensive work to `initState` / `didUpdateWidget` and let `build` read pre-computed values only.
- **Avoid `Opacity` with non-0/1 values** — it allocates an offscreen `saveLayer` buffer every frame; prefer `AnimatedOpacity` for fades or paint color directly with a semi-transparent value.
- **Avoid `Clip.antiAliasWithSaveLayer`** — use `Clip.antiAlias` instead; it clips without the offscreen buffer cost.
- **Don't override `operator==` on non-leaf widgets** — Flutter's reconciler uses `identical()` as an O(1) fast-path; a custom `==` that traverses child props replaces it with a potentially O(n) comparison on every reconciliation pass.

```dart
// WRONG — sort runs every build() call.
@override
Widget build(BuildContext context) {
  final sorted = items.toList()..sort((a, b) => a.name.compareTo(b.name));
  return ListView(children: sorted.map((e) => ItemTile(e)).toList());
}

// RIGHT — sort once when data changes; build() reads the result.
late List<Item> _sorted;

@override
void initState() {
  super.initState();
  _sorted = widget.items.toList()..sort((a, b) => a.name.compareTo(b.name));
}

@override
void didUpdateWidget(MyList old) {
  super.didUpdateWidget(old);
  if (widget.items != old.items) {
    _sorted = widget.items.toList()..sort((a, b) => a.name.compareTo(b.name));
  }
}

@override
Widget build(BuildContext context) =>
    ListView(children: _sorted.map((e) => ItemTile(e)).toList());
```

Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://api.flutter.dev/flutter/widgets/Opacity-class.html
