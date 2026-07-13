---
title: No Server Data in the Store — Recognize and Raise
impact: CRITICAL
impactDescription: a store copy of server entities disagrees with the server after any write — the UI lies
tags: zustand, server-state, dual-source, design-gap
---

**Rule:** A store holding or fetching server entities is a dual source — recognize it and RAISE a
design gap; never code around it. The query cache owns server data; the store holds only client facts.

- CORRECT Example:

```ts
// the query cache owns the list (useDevices); the store holds only client facts
const useDeviceSelection = create<Selection>(set => ({
  selectedId: null,
  selectDevice: (id) => set({ selectedId: id }),
}))
```

- BAD Example:

```ts
const useDeviceStore = create(set => ({
  devices: [] as Device[],
  loadDevices: async () => set({ devices: await api.getDevices() }),   // dual source — RAISE
}))
```
