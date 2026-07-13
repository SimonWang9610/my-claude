---
title: Render Every Data State, Not Just the Happy Path
impact: HIGH
impactDescription: blank screen on pending, crash on error, ambiguous empty rendering
tags: data-states, loading, error, empty
---

**Rule:** A query-backed component renders all four states — loading · error · empty · success.

- CORRECT Example:

```tsx
if (isPending) return <Skeleton/>
if (isError) return <ErrorPanel error={error}/>
if (!data.length) return <Empty/>
return <>{data.map(renderRow)}</>
```

- BAD Example:

```tsx
// blank on pending, crashes on error, empty array renders nothing distinguishable
return <>{data.map(renderRow)}</>
```
