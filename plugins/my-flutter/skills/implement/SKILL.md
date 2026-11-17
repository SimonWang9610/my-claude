---
name: implement
description: >-
  Use this skill when writing or changing Flutter and Dart widget code: "build this screen", "why
  does this rebuild", "this list janks", "optimize startup", "fix this BuildContext across an await".
  Gives the Flutter rules for rebuilds and build cost, jank and startup, lists, images, animations,
  build-method discipline and theming. Knowledge only: it runs no process (with my-workflow, the
  spec-implementer agent does). Not for layering or where state lives (use my-flutter:design) or
  Riverpod APIs (use my-flutter:riverpod).
---

# implement

Flutter coding rules. What to build and when it is done come from the task; these are the rules for
how to write widget code correctly and cheaply inside a unit.

- **The design is not yours to change** — never move a fact's owner, skip a layer or drop a seam
  silently. A case the design missed, or a structure that makes the code fight → raise it as a gap
  with `file:line` evidence.
- **Measure before optimizing** — profile on a device; fix a visible hazard, never a guess.

## Rules

### Rebuilds & build cost

| Card | Covers |
|-----------|---------------|
| [`rules/perf-rebuilds.md`](rules/perf-rebuilds.md) | `const` widgets, localize `setState`, extract classes, `child:` param, `RepaintBoundary`, narrow provider selectors |
| [`rules/perf-build-cost.md`](rules/perf-build-cost.md) | No expensive work in `build`; avoid `saveLayer`; no `==` on non-leaf widgets |
| [`rules/widget-build-discipline.md`](rules/widget-build-discipline.md) | `const` everywhere; small `build` + localized `setState`; no `BuildContext` across an async gap |

### Jank & startup

| Card | Covers |
|-----------|---------------|
| [`rules/perf-jank-and-startup.md`](rules/perf-jank-and-startup.md) | Profile on device; UI vs raster thread; Impeller; defer init |

### Lists & images & animations

| Card | Covers |
|-----------|---------------|
| [`rules/perf-lists.md`](rules/perf-lists.md) | Lazy `.builder` constructors; no `shrinkWrap` on long lists; `itemExtent`; avoid `Intrinsic*`; `ValueKey` on reordered stateful items |
| [`rules/perf-images.md`](rules/perf-images.md) | Decode at display size; precache; cached network images |
| [`rules/perf-animations.md`](rules/perf-animations.md) | `child:` on `AnimatedBuilder`; implicit animations; `AnimatedOpacity` |

### Theming

| Card | Covers |
|-----------|---------------|
| [`rules/widget-theming.md`](rules/widget-theming.md) | Read colors/typography from `Theme.of(context)` tokens; never hard-coded `Color(0xFF…)` |
