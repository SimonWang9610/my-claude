---
title: Explicit Variant Components over Mode Flags
impact: MEDIUM
impactDescription: mode flags create branch-riddled components; variants stay simple
tags: composition, variants, api-design
---

## Explicit Variant Components over Mode Flags

When a "mode" prop makes a component behave like two different things (`<Tile mode="live" />` vs `mode="playback"`), the body becomes parallel branch sets that evolve independently and break each other. Make each mode an explicit component; share the common parts as smaller internals.

**Incorrect:**

```tsx
function CameraTile({ mode, ...props }: { mode: 'live' | 'playback' | 'thumbnail' }) {
  // if (mode === 'live') ... else if (mode === 'playback') ... — everywhere
}
```

**Correct:**

```tsx
function LiveTile(props: LiveTileProps) {
  return <TileFrame {...frameProps(props)}><LiveStreamSurface .../><LiveBadge/></TileFrame>
}

function PlaybackTile(props: PlaybackTileProps) {
  return <TileFrame {...frameProps(props)}><RecordedSurface .../><Timeline/></TileFrame>
}
```

Each variant gets precise props (no `seekTo` on a live tile), and adding a variant is additive instead of threading a new mode through every branch. Conditional *styling* doesn't warrant this; conditional *structure and behavior* does.
