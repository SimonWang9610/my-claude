# Quality — code standards, scope, build

## Code standards (per changed unit)

Correctness findings outrank style; cap advisory notes so the top severities stay
visible.

- **State:** one owner per fact — no copies kept in sync by effects; server data never
  duplicated into stores/local state; no state seeded from a prop snapshot; no
  module-scope mutable state.
- **Effects:** every subscription/timer returns its teardown; no effect-fetching where a
  query layer exists; no derived values mirrored into state.
- **Components:** all data states rendered (loading · error · empty · success); no
  component defined inside a component; stable list keys (never index on reorderable
  lists); interactive elements are semantic and role-queryable.
- **Boundaries:** dependencies point inward (ui → hooks/state → api/services); imperative
  side effects live behind services with create/destroy lifecycles; external data parsed
  at the boundary; errors typed — no `any`, no `as`/`!` laundering.
- **Hot paths only:** memo boundaries defeated by inline object/arrow props; unbounded
  lists unvirtualized; per-frame values routed through React state.

## Scope creep (feature PRs)

Each of these in a feature PR is a finding — governance surfaces re-verified via the
authoritative primitive first:

- touches governance surfaces: CODEOWNERS, CI workflows, `.claude/`, steering docs
- rewrites workflow/template files while claiming to be a feature
- replaces real docs with placeholder templates (`[Describe ...]`)
- unrelated runtime deps (test/faker libraries under `dependencies`), unrelated route
  changes, project renames to placeholders

## Build verification (mandatory)

- Run `npx tsc --noEmit` (or the project's build command) on the PR branch. New TS errors
  absent from base → **CRITICAL** — reviews are often the only build check.
- Scope-limited re-reviews, at minimum: no file the PR deletes or renames is still
  imported elsewhere — `grep -r "from '.*/<name>'" src/`.
