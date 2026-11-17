---
name: implement
description: >-
  Use this skill when writing or changing React and TypeScript code: components, hooks, stores,
  services, "make these tests pass", "fix this effect loop", "why does this re-render", "optimize
  this list". Gives the React rules for using, building and optimizing hooks and components, and
  for store and service bodies. Knowledge only: it runs no process (with my-workflow, the
  spec-implementer agent does). Not for deciding unit boundaries or where state lives (use
  my-react:design) or for writing tests (use my-react:test).
---

# implement

React coding rules. What to build and when it is done come from the task; these are the rules for
how. A unit's **contract** is what the design states about it: its interface, the states it exposes
and how it runs in isolation.

- **Capabilities first** — read `package.json` once: the React version,
  `babel-plugin-react-compiler` (it inverts the manual-memoization advice), which state and query
  libraries exist. Skip every rule section for a library that is absent.
- **Priority** — a correctness rule beats a performance rule; a project fact beats generic advice.
- **Hot paths only** — optimize per-frame work, large lists and the main interaction. Clear code
  first; never pre-optimize a cold path.
- **Reuse** — read the target files and their imports first; use the existing component, hook,
  type, query key or store slice. Never add a second one.
- **The design is not yours to change** — never widen a surface, move a fact's owner or cross a
  boundary silently. A case the design missed, a structure that makes the code fight, or a
  decision that is provably wrong → raise it as a gap with `file:line` evidence.

## Rules

Read the card before writing that kind of code. Most changes span levels: a filtered list touches
component and hook rules at once, so apply every card the diff touches.

| Card | Read when |
|---|---|
| [use-hooks.md](./rules/use-hooks.md) | calling hooks: effects, derived values, query and mutation wiring |
| [build-hooks.md](./rules/build-hooks.md) | authoring a custom hook: surface, stable returns, teardown, seam |
| [optimize-hooks.md](./rules/optimize-hooks.md) | a hot path: narrowing subscriptions, splitting hooks, transient values |
| [build-components.md](./rules/build-components.md) | a component's surface, its data states, types, composition |
| [optimize-components.md](./rules/optimize-components.md) | a hot path: memo boundaries, deferral, virtualization, bundle |
| [build-stores-and-services.md](./rules/build-stores-and-services.md) | store actions, persistence, transient subscriptions, service lifecycle, event streams |
