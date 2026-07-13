---
title: Defer Heavy Non-Urgent Updates
impact: MEDIUM
impactDescription: an expensive re-render on the same interaction blocks keystrokes and clicks
tags: useDeferredValue, useTransition, responsiveness, hot-path
---

**Rule:** Mark expensive, non-urgent updates with `useDeferredValue`/`useTransition`; the
deferred subtree must be memo'd to benefit.

- CORRECT Example:

```tsx
const deferred = useDeferredValue(query)
return <EventResults query={deferred}/>    // EventResults is memo'd
```

- BAD Example:

```tsx
return <EventResults query={query}/>       // full-cost render on every keystroke
```
