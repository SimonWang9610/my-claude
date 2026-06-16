---
title: Diagnose Jank & Startup
impact: HIGH
tags: profiling, jank, startup, devtools, profile-mode, real-device, ui-thread, raster-thread, impeller, initstate
---

## Diagnose Jank & Startup

> **Conditional — consult when a performance concern surfaces (non-blocking).**

Applying optimizations without first identifying the correct thread or measuring in the correct mode routinely produces zero improvement. Measure first, fix second.

- **Profile in profile mode on a real device** — debug mode disables AOT and adds observatory overhead; a simulator has no GPU hardware path; both distort frame times by 2–10×; use `flutter run --profile` on the minimum supported hardware.
- **Read UI-thread vs raster-thread bars** — the performance overlay top bar is UI (Dart build + layout), bottom bar is raster (GPU compositing); the fix differs per thread and applying the wrong one has zero effect.
- **Don't disable Impeller** — Impeller ships pre-compiled shaders eliminating runtime compilation stalls; reverting to Skia re-introduces first-frame shader jank; file a bug and work around the specific regression instead.
- **Defer heavy init to after first paint** — `initState` runs before the first `build`; blocking work (DB open, network connect, large asset loads) delays the first frame; move it into `WidgetsBinding.instance.addPostFrameCallback` and show a loading skeleton until ready.

```dart
// Defer heavy init until after the first frame is on screen.
@override
void initState() {
  super.initState();
  // Heavy work here would block the first build.
  WidgetsBinding.instance.addPostFrameCallback((_) async {
    await _database.open();          // runs after first paint; show skeleton until ready
    setState(() => _ready = true);
  });
}
```

Profile on real hardware, not simulator: `flutter run --profile`

Ref: https://docs.flutter.dev/perf/ui-performance
Ref: https://docs.flutter.dev/perf/impeller
Ref: https://docs.flutter.dev/perf/best-practices
