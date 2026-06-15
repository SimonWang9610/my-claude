---
paths: ["**/*.ts", "**/*.tsx"]
---

# Architecture principles (P1–P7)

Apply when a spec adds a component, hook, store slice, write path, color/theming
token, selection state, or module-level variable. Cite the principle ID (P3, P6…)
in design notes and violation messages.

- **P1 — Server state lives in TanStack Query, never copied into Zustand/useState/localStorage.**
  Zustand owns client UI state only (open modals, active tab, theme). Prevents
  dual-source-of-truth, where a fact can be true in one store and false in another.
  Ref: https://tanstack.com/query/v4/docs/framework/react/guides/does-this-replace-client-state
- **P2 — Components render; logic lives in named single-responsibility hooks.**
  Soft ceiling ~400 LOC component / ~300 LOC hook; past it, split or add a recorded
  `// ARCH-EXCEPTION: <reason>`. Prevents God-components/hooks that have no isolation seam.
  Ref: https://react.dev/learn/reusing-logic-with-custom-hooks
- **P3 — One authoritative owner per fact; derive client selection from server state.**
  Keep the raw key in client state and resolve the entity at read time; never mirror
  server data or a prop with `useEffect`. Prevents prop-to-state sync and stale frames.
  Ref: https://tkdodo.eu/blog/deriving-client-state-from-server-state
- **P4 — Writes go through `useMutation`; errors surface via `onError`/`isError`.**
  Invalidate in `onSuccess`, clean up in `onSettled`; no un-awaited writes, no
  `console.error`-only swallowing. Prevents silent write failures that pass green in tests.
  Ref: https://tanstack.com/query/v4/docs/framework/react/guides/mutations
- **P5 — Every unit is renderable/invocable in isolation (a testability seam).**
  Each acceptance-criterion behavior must be reachable via `renderWithProviders` or
  `renderHook` controlling its inputs; a unit testable only by mocking its parent fails P5.
  Prevents false-positive proxy tests and uncovered behavior. (P2 underwrites P5.)
  Ref: https://testing-library.com/docs/guiding-principles/
- **P6 — Pick the correct token layer for every color value.**
  Use design tokens / CSS custom properties for themed surfaces; static color constants
  only where the renderer can't resolve CSS vars (e.g. SVG attributes); never hard-coded hex
  or raw utility-scale colors. Prevents the dark-mode regression treadmill.
- **P7 — No module-scope mutable domain state.**
  Use context, Zustand, or `useRef`; if a module-level Map is unavoidable for performance,
  export `_resetForTest()` and call it in `beforeEach`. Prevents untestable singletons and
  test-order-dependent flakes. Ref: https://testing-library.com/docs/guiding-principles/

Worked right/wrong examples and per-principle checks: see
../skills/oac-architecture-gate/references/principle-examples.md and principle-checks.md.
