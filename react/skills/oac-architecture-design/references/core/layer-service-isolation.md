---
title: Wrap Side-Effectful Integrations in Service Modules
impact: MEDIUM-HIGH
impactDescription: SDK calls scattered through components can't be swapped, mocked, or lifecycle-managed
tags: services, side-effects, integration, video
---

## Wrap Side-Effectful Integrations in Service Modules

Imperative, stateful integrations — video player engines (hls.js, WebRTC), WebSockets, Electron IPC, hardware control — must live in plain-TypeScript service modules with explicit lifecycles (`create`/`destroy`), exposed to React only through dedicated hooks. Components must never touch the SDK directly.

**Incorrect (SDK driven from component effects):**

```tsx
function CameraTile({ url }) {
  useEffect(() => {
    const hls = new Hls()                  // SDK details in the view layer
    hls.loadSource(url); hls.attachMedia(videoRef.current!)
    hls.on(Hls.Events.ERROR, (e, data) => { /* retry logic in component */ })
    return () => hls.destroy()
  }, [url])
}
```

**Correct:**

```tsx
// services/streamPlayer.ts — framework-free, unit-testable
export function createStreamPlayer(opts: StreamPlayerOptions): StreamPlayer { ... }

// features/playback/hooks/useStreamPlayer.ts — the only React↔service bridge
function useStreamPlayer(url: string, videoRef: RefObject<HTMLVideoElement>) {
  useEffect(() => {
    const player = createStreamPlayer({ url, media: videoRef.current!, onError: ... })
    return () => player.destroy()
  }, [url])
}
```

Payoffs to mention in findings: swappable backends (hls.js → libmpv/WASM), mockable tests, retry/reconnect logic in one place, and a guaranteed destroy path (leaked players are the classic multi-camera bug). The service emits events; stores/refs subscribe (direction per `layer-unidirectional-deps`).
