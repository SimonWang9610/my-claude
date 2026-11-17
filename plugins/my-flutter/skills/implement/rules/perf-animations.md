---
title: Animations
impact: HIGH
tags: animation, AnimatedBuilder, AnimatedOpacity, child, saveLayer, implicit-animation, rebuild, ticker
---

## Animations

> **Conditional — consult when a performance concern surfaces (non-blocking).**

Animation callbacks fire up to 120 times per second. Unnecessary widget construction inside them and `saveLayer`-triggering opacity widgets compound into sustained raster thread pressure; two patterns account for most animation-related overruns.

- **Pass static subtrees via `child:`** — `AnimatedBuilder.builder` (and `AnimatedWidget.build`) runs every tick; widgets constructed inside it that don't read the animation value are rebuilt at full tick rate; move them to the `child:` parameter so Flutter builds them once and re-uses the element.
- **Prefer `AnimatedOpacity` over animating `Opacity` manually** — `Opacity` with a non-0/1 value forces a `saveLayer` offscreen buffer each frame; `AnimatedOpacity` delegates to the engine's compositor path, which costs far less.
- **Prefer `AnimatedContainer` / `AnimatedPositioned` over driving `ClipRect`/`ClipRRect` with a `Tween` at 60 Hz** — implicit animation widgets avoid triggering `saveLayer` on every tick.

```dart
// Pass static subtree as child — built once, reused on every animation tick.
AnimatedBuilder(
  animation: _controller,
  child: const Icon(Icons.star),             // built once outside the tick loop
  builder: (context, child) => Transform.scale(
    scale: _controller.value,
    child: child,                            // same element every tick
  ),
);
```

Ref: https://api.flutter.dev/flutter/widgets/AnimatedBuilder-class.html
Ref: https://docs.flutter.dev/perf/best-practices
