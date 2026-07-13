---
title: Set staleTime Deliberately
impact: MEDIUM
impactDescription: the default staleTime of 0 refetches on every mount and refocus — a storm across shared keys
tags: query, staleTime, refetch, hot-path
---

**Rule:** Set an app-wide `staleTime` default plus per-query tuning per the contract; never leave
the default `0` unexamined.

- CORRECT Example:

```ts
new QueryClient({ defaultOptions: { queries: { staleTime: 30_000 } } })
```

- BAD Example:

```ts
new QueryClient()   // staleTime defaults to 0 — refetch on every mount and refocus
```
