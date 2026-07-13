---
title: Idempotent create/destroy Lifecycle
impact: HIGH
impactDescription: effect teardown runs more than once (StrictMode) — a non-idempotent destroy throws or double-frees
tags: service, lifecycle, teardown, strict-mode
---

**Rule:** `create<Unit>(opts)` acquires; `destroy()` releases everything acquired and tolerates
being called twice. The bridging hook is the only React↔service connection.

- CORRECT Example:

```ts
export function createStreamPlayer(opts: PlayerOpts) {
  let hls: Hls | null = new Hls()
  hls.loadSource(opts.url)
  return {
    destroy() { hls?.destroy(); hls = null },   // safe on second call
  }
}

// the ONLY React↔service bridge:
useEffect(() => { const p = createStreamPlayer({ url }); return () => p.destroy() }, [url])
```

- BAD Example:

```ts
export function createStreamPlayer(opts: PlayerOpts) {
  const hls = new Hls()
  return { destroy() { hls.destroy() } }   // second teardown call double-frees
}
```
