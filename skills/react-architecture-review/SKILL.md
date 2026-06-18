---
name: react-architecture-review
description: Reviews React codebases for architecture and state-management problems, then produces a prioritized findings report and a phased remediation plan. Targets React 19 + Vite + TypeScript + Zustand + TanStack Query v5 + MUI (client-side apps, no Next.js/RSC). Trigger when the user asks to review, audit, refactor, or restructure React/TypeScript code involving state management (Zustand, TanStack Query, Context, useState), component composition, store design, data flow, or project layering — including "review my React code", "is my state management OK", "clean up this component", or "how should I structure this feature".
---

# React Architecture Review

<!-- TOC -->
- [Review Workflow](#review-workflow)
- [Rule Categories by Priority](#rule-categories-by-priority)
- [Quick Reference](#quick-reference)
- [How to Use the Rules](#how-to-use-the-rules)
- [Review Report Format](#review-report-format)
- [Development Plan Format](#development-plan-format)
<!-- /TOC -->

Reviews React codebases for architecture and state-management problems, then produces two deliverables: a **Review Report** (prioritized findings) and a **Development Plan** (phased remediation). Targets client-side React 19 apps built with Vite, Zustand for client state, TanStack Query v5 for server state, and MUI — not Next.js/RSC.

Performance issues (wasted re-renders, bundle size, frame-rate) belong to the sibling skill `react-performance-review`. If a review surfaces both kinds of issues, note the performance ones briefly and recommend running that skill; don't duplicate its analysis here.

## Review Workflow

1. **Scope the review.** Identify what to review: a feature folder, a store, a component tree, or the whole app. If the user didn't specify, ask or infer from context (e.g., recently discussed files). List the files in scope before reading them.
2. **Map the structure first.** Before judging anything, sketch the actual data flow: where state lives (component state, Zustand stores, Query cache, Context), who writes it, who reads it, and how components compose. Misdiagnosis usually comes from skipping this step.
3. **Check against the rules.** Walk the rule categories below in priority order. Read a rule file (`rules/<name>.md`) when code in scope looks like it might violate it — each file has the rationale and incorrect/correct examples needed to confirm or dismiss a suspicion. Don't cite a rule from memory of its one-line summary alone.
4. **Confirm before reporting.** For each candidate finding, verify it against the actual code (not assumption), note the file/line, and assess severity honestly. A pattern that's technically "wrong" but harmless in context (e.g., a tiny static Context) is a Low or not a finding at all.
5. **Write the Review Report**, then the **Development Plan** (formats below).

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | State Ownership & Placement | CRITICAL | `state-` |
| 2 | Zustand Store Design | HIGH | `zustand-` |
| 3 | Server State (TanStack Query) | HIGH | `query-` |
| 4 | Component Composition | MEDIUM-HIGH | `compose-` |
| 5 | Layering & Module Structure | MEDIUM | `layer-` |
| 6 | React 19 Idioms | LOW-MEDIUM | `react19-` |

## Quick Reference

### 1. State Ownership & Placement (CRITICAL)

Wrong state placement is the root cause of most architecture pain — fix these before anything else.

- `state-ownership-decision` - Decision tree: local useState → lifted → Zustand → TanStack Query; keep state as local as possible
- `state-no-server-data-in-stores` - Server data lives in TanStack Query, never mirrored into Zustand/useState
- `state-derive-dont-store` - Values computable from existing state/props are derived in render or selectors, never stored
- `state-no-prop-to-state-copy` - Don't copy props into state; use the prop directly or a `key` reset
- `state-single-source-of-truth` - Each fact has exactly one owner; duplication across stores/components is a defect

### 2. Zustand Store Design (HIGH)

- `zustand-actions-in-store` - Mutation logic lives in store actions, not scattered `setState` calls in components
- `zustand-slice-organization` - One domain per store/slice; split mega-stores, merge confetti stores
- `zustand-no-component-coupling` - Stores expose domain operations, never know about components or UI concerns
- `zustand-transient-subscribe` - High-frequency values (playback position, drag coords) use `subscribe`/refs, not reactive hooks
- `zustand-persist-discipline` - `persist` only whitelisted fields via `partialize`; version + migrate

### 3. Server State / TanStack Query (HIGH)

- `query-no-effect-fetching` - No `useEffect` + fetch + setState; data fetching goes through `useQuery`
- `query-key-factory` - Centralized, typed query-key factories per domain; no inline string keys
- `query-mutation-invalidation` - Mutations invalidate or update affected queries; no manual refetch choreography
- `query-select-transform` - Shape/derive server data with `select`, not in components or by storing transformed copies

### 4. Component Composition (MEDIUM-HIGH)

- `compose-avoid-boolean-props` - Don't accrete `isX`/`hideY` boolean props; restructure with composition
- `compose-compound-components` - Multi-part widgets share state via internal context (Tabs.List/Tabs.Panel style)
- `compose-children-over-render-props` - Prefer `children`/slots over `renderX` props for static content
- `compose-extract-hooks` - Components over ~150 lines of mixed logic+JSX: extract logic into custom hooks
- `compose-explicit-variants` - Divergent behavior → separate variant components sharing internals, not mode flags

### 5. Layering & Module Structure (MEDIUM)

- `layer-feature-folders` - Organize by feature (components/hooks/store/api per feature), not by file type
- `layer-unidirectional-deps` - Dependencies point one way: ui → hooks/state → services; no upward or cross-feature reach-ins
- `layer-service-isolation` - Side-effectful integrations (WebSocket, player SDKs, IPC) wrapped in service modules, accessed via hooks/stores

### 6. React 19 Idioms (LOW-MEDIUM)

- `react19-modern-apis` - `ref` as a prop (no `forwardRef`); plain typed functions (no `React.FC`/`FunctionComponent`); `use(Context)` over `useContext`; consider `useActionState`/`useOptimistic` where samples hand-roll them; no `useMemo` ceremony where the React Compiler handles it

## How to Use the Rules

Read individual rule files for the rationale and incorrect/correct examples:

```
rules/state-ownership-decision.md
rules/zustand-actions-in-store.md
```

## Review Report Format

```markdown
# Architecture Review: <scope>

## Summary
2–4 sentences: overall health, the dominant problem theme, what's already good.

## Findings

| # | Severity | Rule | Location | Finding |
|---|----------|------|----------|---------|
| 1 | Critical | state-no-server-data-in-stores | src/stores/cameraStore.ts:42 | Camera list fetched then copied into Zustand |

### Finding details
For each finding: what the code does now, why it's a problem **in this codebase**
(concrete consequence, not just rule citation), and the target pattern with a short
code sketch. Reference the rule file for the full pattern.
```

Severity scale: **Critical** = causes bugs/data inconsistency or blocks the stated goal (e.g., migration); **High** = will compound as code grows; **Medium** = friction, harder maintenance; **Low** = style/idiom.

## Development Plan Format

After the report, produce a plan the user can execute incrementally:

```markdown
# Development Plan

## Phase 1 — Quick wins (low risk, independent)
- [ ] <change> — files touched, expected effort (S/M/L), verification step

## Phase 2 — Structural changes (ordered; note dependencies between items)
- [ ] ...

## Phase 3 — Follow-ups / nice-to-have
- [ ] ...
```

Plan rules: every item maps back to finding numbers; order items so the codebase stays working after each step (no big-bang rewrites); state how to verify each step (existing behavior preserved, tests, manual check). If the user has a migration or feature deadline, weigh the plan toward unblocking that.
