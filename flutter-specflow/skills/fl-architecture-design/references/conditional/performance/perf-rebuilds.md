---
title: Minimize Rebuilds
impact: HIGH
tags: rebuild, const, setState, widget-extraction, listenable, repaint, selectors, performance
---

## Minimize Rebuilds

> **Conditional — consult when a performance concern surfaces (non-blocking).**

Flutter re-runs `build()` on every dirty widget. Every avoidable rebuild wastes UI-thread time and risks missing the 16 ms budget. Apply these techniques from cheapest to most surgical once profiling identifies rebuild overhead.

- **Use `const` widgets** — compile-time constants are never reconciled; the framework skips them entirely via object identity.
- **Localize `setState`** — extract mutable state into a small `StatefulWidget` so only that subtree rebuilds, not its heavy siblings.
- **Extract widget classes, not helper methods** — a `Widget _buildFoo()` method inlines into the parent tree every build; a `StatelessWidget` subclass gets its own `Element` and can be `const`.
- **Pass static subtrees via `child:` on `ListenableBuilder`/`AnimatedBuilder`** — the framework builds the `child` once and re-uses the element on every notification or tick.
- **`RepaintBoundary` at animated hot-spots** — promotes the subtree to a separate GPU layer so static siblings are not re-rasterized.
- **Narrow state selectors** — subscribe only to the slice rendered (e.g. `context.select`) so unrelated field mutations don't trigger a rebuild.

```dart
// Pass a static subtree as child — built once, reused every tick.
AnimatedBuilder(
  animation: _controller,
  child: const HeavyStaticWidget(),          // built once
  builder: (context, child) => Transform.rotate(
    angle: _controller.value * 2 * pi,
    child: child,                            // reused element
  ),
);

// Isolate a frequently-repainting hot-spot onto its own GPU layer.
RepaintBoundary(
  child: AnimatedProgressBar(value: _progress),
)
```

Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://api.flutter.dev/flutter/widgets/ValueListenableBuilder-class.html
Ref: https://api.flutter.dev/flutter/widgets/RepaintBoundary-class.html
