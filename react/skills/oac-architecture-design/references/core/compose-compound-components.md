---
title: Compound Components for Multi-Part Widgets
impact: MEDIUM-HIGH
impactDescription: gives flexible structure without prop explosions
tags: composition, compound-components, context
---

## Compound Components for Multi-Part Widgets

Widgets with cooperating parts (tabs, toolbars-with-panels, a player with surface/controls/timeline) work best as a parent that owns shared state in an internal context, plus part-components that consume it. Callers control structure and ordering; the parts coordinate invisibly.

```tsx
const PlayerContext = createContext<PlayerContextValue | null>(null)

function Player({ children, source }: PlayerProps) {
  const player = usePlayerSession(source)        // state + actions
  return <PlayerContext value={player}>{children}</PlayerContext>
}

function usePlayerContext() {
  const ctx = use(PlayerContext)
  if (!ctx) throw new Error('Player.* must be used within <Player>')
  return ctx
}

Player.Surface = function Surface() { const { videoRef } = usePlayerContext(); ... }
Player.Controls = function Controls() { const { isPlaying, toggle } = usePlayerContext(); ... }
Player.Timeline = function Timeline() { ... }

// Caller decides layout:
<Player source={stream}>
  <Player.Surface />
  <Player.Controls />
</Player>
```

The guard-throwing `usePlayerContext` hook matters: it converts misuse into an immediate, named error instead of a null-deref. Note the React 19 forms (`use(Context)`, context as provider) — see `react19-modern-apis`.
