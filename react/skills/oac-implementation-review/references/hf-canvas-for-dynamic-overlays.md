---
title: Draw Rapidly-Changing Visuals on Canvas
impact: HIGH
impactDescription: hundreds of animated DOM nodes thrash style/layout; one canvas doesn't
tags: high-frequency, canvas, overlays, timeline, video
---

## Draw Rapidly-Changing Visuals on Canvas

When a visual is composed of many elements that move/appear every frame — motion-detection boxes over video, dense timeline tick/segment strips, waveform/audio meters, live charts — DOM elements are the wrong medium: each frame mutates hundreds of nodes and re-runs style/layout. A single `<canvas>` repainted in a rAF loop costs one node and one paint.

**Decision boundary:**
- Few elements (≤ ~20), changing on user interaction → DOM with transforms is fine, keeps accessibility/hit-testing for free.
- Many elements, changing continuously → canvas (or the video pipeline itself, e.g., compositing overlays in the player).

```tsx
function MotionOverlay({ source }: { source: MotionBoxSource }) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  useEffect(() => {
    const ctx = canvasRef.current!.getContext('2d')!
    let raf = 0
    const draw = () => {
      ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height)
      for (const box of source.current()) ctx.strokeRect(box.x, box.y, box.w, box.h)
      raf = requestAnimationFrame(draw)
    }
    raf = requestAnimationFrame(draw)
    return () => cancelAnimationFrame(raf)
  }, [source])
  return <canvas ref={canvasRef} className="overlay" />
}
```

Mind devicePixelRatio for crispness, and pause the loop when the element/tab is hidden (`IntersectionObserver` / `visibilitychange`) — an always-running rAF on a hidden grid page is a battery finding of its own.
