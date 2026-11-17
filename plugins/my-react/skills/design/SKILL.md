---
name: design
description: >-
  Use this skill when designing React and TypeScript units or reviewing such a design: "where does
  this state live", "how should these components be cut", "which way should this dependency
  point", "what should this hook or store expose", or the design step of a React app. Gives the
  React rules for state ownership, cutting components and hooks, services and boundaries, and what
  a unit's interface must state so it can be built and tested. Knowledge only: it writes no design
  file and runs no process (with my-workflow, spec-design does). Not for writing the code (use
  my-react:implement).
---

# design

React design rules. The design's format and steps belong to whoever runs the design; this skill
says what a sound React design decides.

A **unit** is a component, hook, store or service. Its **contract** is what the design states about
it: its interface, the states it exposes and how it runs in isolation.

## Per unit, in order

1. **Data** — what it consumes and produces, from where, to where, by which mechanism (below).
2. **State** — per [rules/state-ownership.md](./rules/state-ownership.md):
   - the facts it owns, and where each initial value comes from;
   - what triggers a change: user · timer · another unit's event · an external event · a
     subscription · another state's change;
   - how the change propagates: props · context · store · server cache · event;
   - then the concrete design: `useState`/`useReducer` · custom hook · context provider · store
     slice · listenable service · query hook.
3. **Cut** — per [rules/decompose-components.md](./rules/decompose-components.md) and
   [rules/services-and-boundaries.md](./rules/services-and-boundaries.md). A split or a merge has
   its own blast radius: pass the right-size test before cutting.
4. **Generalize** only on demonstrated demand with a bounded blast radius, or when told to.

## Mechanism

The loosest coupling that carries the interaction:

| Interaction | Mechanism |
|---|---|
| Server fact shared by many units | the shared query key: no prop-drilling, no client copy |
| Parent and child, local | props down, callbacks up |
| Client fact across an unrelated subtree | a store selector |
| Client fact across a subtree with one owner | a context provider |
| React and an imperative resource or stream | a service event, bridged by one hook |
| Cross-cutting client state with shared invariants | one feature-owned store |

Never a central manager that owns everything.

## What a unit's interface states

For new or changed units; exact types, no `any`.

- **Surface** — component: props and the callbacks it fires · hook: signature and return type ·
  store: state shape and intent-named actions · service: `create<Unit>(opts)`, lifecycle, events.
- **States exposed** — loading · empty · error · success · disabled, each as a signal a test can
  assert (role, label, text). Omit those that do not apply.
- **Test seam** — how it runs in isolation: a component through props and providers, a hook
  through controlled inputs, a store through its actions, a service through its interface; never
  by standing up its host.
- **Must not** — the negative space: "fetches no data", "does not import the store", "holds no
  server-owned fact".
- A stateful unit: every transition is reachable through the surface.

## Rules

Read the card before deciding; cite it in the design.

| Card | Read when |
|---|---|
| [state-ownership.md](./rules/state-ownership.md) | deciding where a fact lives, its concrete state design, URL state, what a write does to the cache |
| [decompose-components.md](./rules/decompose-components.md) | cutting or merging units, sizing props, placing a performance boundary |
| [services-and-boundaries.md](./rules/services-and-boundaries.md) | dependency direction, side effects, parsing at a boundary, races, failure containment |
