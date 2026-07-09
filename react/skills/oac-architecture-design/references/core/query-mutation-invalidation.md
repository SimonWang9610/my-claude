---
title: Design the Mutation's Invalidation Graph
impact: HIGH
impactDescription: an undesigned invalidation graph leaves the UI showing pre-mutation data
tags: query, mutations, invalidation, cache
---

## Design the Mutation's Invalidation Graph

**Decision:** for every write, decide up front which cached query families it makes stale —
its *invalidation graph* — and record it. A mutation owns its consequences: on success it
either invalidates the affected families or writes them directly (`setQueryData`). Manual
choreography — components calling `refetch()`, "reload" callbacks passed down props, full
page-state resets — is the signature of a missing invalidation graph, and belongs in the
design as a defect to remove.

Record in `design.md` / the mutation's contract, per mutation:

| Mutation | Invalidates (families) | Updates directly (`setQueryData`) |
|----------|------------------------|-----------------------------------|
| `renameCamera` | `cameraKeys.lists()` | `cameraKeys.detail(id)` |

Design decides *what* is invalidated; implementation wires *how*. The exact
`onSuccess`/`onError`/`onSettled` callback placement, optimistic application, and rollback are
coding concerns — see the `oac-implementation` skill (`query-mutation-wiring`).
