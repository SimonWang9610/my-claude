---
name: fl-implementation
description: >
  Applies Flutter performance and widget-build idioms while implementing the code inside a unit
  (the contract/architecture is already fixed) — rebuilds, build cost, jank and startup, images,
  lists, animations, build-method discipline, and theming. Use at the spec-implement stage or
  whenever writing or optimizing widget/render code behind a fixed contract.
---

# fl-implementation

Implementation-altitude skill: the design and contracts are fixed; this skill governs how to
write the Dart/widget code correctly and efficiently inside each unit.

Riverpod idioms (provider annotations, Notifier/AsyncNotifier patterns, ref lifecycle) live in
the separate **fl-riverpod** skill — do not duplicate or reference it here.

---

## Reference index

### Rebuilds & build cost

| Reference | What it covers |
|-----------|---------------|
| [`references/perf-rebuilds.md`](references/perf-rebuilds.md) | `const` widgets, localize `setState`, extract classes, `child:` param, `RepaintBoundary`, narrow provider selectors |
| [`references/perf-build-cost.md`](references/perf-build-cost.md) | No expensive work in `build`; avoid `saveLayer`; no `==` on non-leaf widgets |
| [`references/widget-build-discipline.md`](references/widget-build-discipline.md) | `const` everywhere; small `build` + localized `setState`; no `BuildContext` across an async gap |

### Jank & startup

| Reference | What it covers |
|-----------|---------------|
| [`references/perf-jank-and-startup.md`](references/perf-jank-and-startup.md) | Profile on device; UI vs raster thread; Impeller; defer init |

### Lists & images & animations

| Reference | What it covers |
|-----------|---------------|
| [`references/perf-lists.md`](references/perf-lists.md) | Lazy `.builder` constructors; no `shrinkWrap` on long lists; `itemExtent`; avoid `Intrinsic*`; `ValueKey` on reordered stateful items |
| [`references/perf-images.md`](references/perf-images.md) | Decode at display size; precache; cached network images |
| [`references/perf-animations.md`](references/perf-animations.md) | `child:` on `AnimatedBuilder`; implicit animations; `AnimatedOpacity` |

### Theming

| Reference | What it covers |
|-----------|---------------|
| [`references/widget-theming.md`](references/widget-theming.md) | Read colors/typography from `Theme.of(context)` tokens; never hard-coded `Color(0xFF…)` |
