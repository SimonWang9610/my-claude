---
title: Keep High-Frequency Values Out of the Store
impact: HIGH
impactDescription: per-frame values placed in the store force reactive re-renders across the tree
tags: zustand, placement, high-frequency, state-ownership
---

## Keep High-Frequency Values Out of the Store

**Decision:** decide where a fast-changing value lives — playback position/PTS, scrub
position, drag/pointer coordinates, PTZ. It does **not** belong in the Zustand store. The
store holds *discrete session state* — the facts that change on a user action (play/pause,
seek target, selected id), not on every frame. Per-frame values are emitted from the owning
service (player, socket, gesture source) via callback/event; the store keeps only the
discrete state about them.

Record in `design.md`: for each high-frequency signal, name its emitter (the service) and
confirm the store carries only the discrete state, never the per-tick value.

**Store this (discrete):**

```ts
interface PlaybackState {
  isPlaying: boolean
  seekTargetMs: number | null   // set on a seek action, not per frame
  selectedTrackId: string | null
}
```

**Not this (per-frame in the store):**

```ts
interface PlaybackState {
  positionMs: number   // updates 30–60×/s → every subscriber re-renders per tick
}
```

Reading a fast-changing value in a component without re-rendering — the transient
`subscribe`/ref technique — is a coding concern, not a placement one. See the
`oac-implementation` skill (`rerender-transient-subscribe`).
