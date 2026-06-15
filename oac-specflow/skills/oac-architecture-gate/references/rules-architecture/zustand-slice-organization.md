---
title: One Domain per Store; Slice Large Stores
impact: HIGH
impactDescription: mega-stores couple unrelated features; confetti stores fragment one domain
tags: zustand, slices, store-design
---

## One Domain per Store; Slice Large Stores

A store should cover one coherent domain (layout, playback session, auth). Two failure modes:

- **Mega-store**: one `useAppStore` holding everything → every feature imports it, unrelated features become coupled, and selector discipline erodes.
- **Confetti stores**: one store per component → a single domain's invariants are scattered and can't be enforced in one action.

For a large but coherent domain, use the slice pattern within one store:

```tsx
// Slices keep files small while preserving one store with cross-slice actions
const createPlaybackSlice: StateCreator<AppState, [], [], PlaybackSlice> = (set, get) => ({
  isPlaying: false,
  play: () => set({ isPlaying: true }),
})
const createSyncSlice: StateCreator<AppState, [], [], SyncSlice> = (set, get) => ({
  syncMode: 'independent',
  enableSync: () => {
    get().play()                       // cross-slice invariant in one place
    set({ syncMode: 'locked' })
  },
})
export const usePlayerStore = create<AppState>()((...a) => ({
  ...createPlaybackSlice(...a),
  ...createSyncSlice(...a),
}))
```

Boundary test: if two pieces of state never change together and are never read together, they belong in separate stores. If an invariant spans them (sync mode forces playback state), they belong in one store, possibly sliced.
