---
paths: ["**/*.ts", "**/*.tsx"]
---

# Architecture principles (P1–P8)

Applies when adding a component, hook, store, write path, color, module-level variable, or
cross-layer import. Cite the ID (P3, P6…) in design notes and violations. Why + examples:
`../skills/oac-architecture-design/references/` (`principle-examples.md`, `principle-checks.md`;
P8: `core/layer-*.md`).

- **P1 — Server state lives in TanStack Query, never copied into Zustand/useState/localStorage.**
  Zustand holds client UI state only (modals, active tab, theme).
- **P2 — Components render; logic lives in named single-responsibility hooks.** Soft ceiling ~400
  LOC component / ~300 LOC hook — past it, split or add `// ARCH-EXCEPTION: <reason>`.
- **P3 — One owner per fact; derive, don't sync.** Keep the raw key in client state and resolve the
  entity at read time; never mirror server data or a prop with `useEffect`.
- **P4 — Writes go through `useMutation`; errors surface via `onError`/`isError`.** Invalidate in
  `onSuccess`, clean up in `onSettled`; no un-awaited or silently-swallowed writes.
- **P5 — Every unit is renderable/invocable in isolation.** Each AC behavior reachable via
  `renderWithProviders`/`renderHook`; a unit testable only by mocking its parent fails P5.
- **P6 — Pick the right token layer for every color.** Design tokens / CSS vars for themed surfaces;
  static hex only where the renderer can't resolve CSS vars (e.g. SVG); never raw hex or scale colors.
- **P7 — No module-scope mutable domain state.** Use context/Zustand/`useRef`; an unavoidable module
  Map exports `_resetForTest()` (reset in `beforeEach`).
- **P8 — Dependencies point one way (`app → features → shared → services`); integrations behind
  services.** Lower never imports upper; wrap SDKs/WebSocket/IPC in service modules reached via
  hooks; no deep cross-feature imports — use the feature's `index.ts`.
