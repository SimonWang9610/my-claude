---
title: Images & Assets
impact: HIGH
tags: images, memory, cacheWidth, cacheHeight, precache, cached-network-image, thumbnail, first-paint
---

## Images & Assets

> **Conditional — consult when a performance concern surfaces (non-blocking).**

Image handling has two independent cost centres: GPU memory from decoding at the wrong resolution, and frame-time spikes from decoding at the wrong moment. Address each independently when profiling shows image-related memory pressure or stutter.

- **Decode at display size** — pass `cacheWidth`/`cacheHeight` (physical pixels: `(size * devicePixelRatio).round()`) so the codec scales during decode; a 4K image decoded for a 100 px thumbnail uses ~64× more memory than needed.
- **Precache above-the-fold images** — call `precacheImage()` in `initState` or during a loading state so the first `build` that needs the image hits a warm cache instead of triggering a decode stall.
- **Use `cached_network_image` for network images** — `Image.network` re-downloads and re-decodes on every navigation; `CachedNetworkImage` persists decoded bitmaps to disk and memory across sessions.

```dart
// Decode at display size — pass physical pixels to avoid decoding a full-res image.
final px = (100 * MediaQuery.devicePixelRatioOf(context)).round();
Image.network(
  imageUrl,
  cacheWidth: px,    // codec scales during decode; ~64× less memory than 4K at 100 px
  cacheHeight: px,
);

// For network images, prefer cached_network_image to avoid re-download on navigation.
CachedNetworkImage(imageUrl: imageUrl, width: 100, height: 100);
```

Ref: https://docs.flutter.dev/perf/best-practices
Ref: https://api.flutter.dev/flutter/widgets/precacheImage.html
Ref: https://pub.dev/packages/cached_network_image
