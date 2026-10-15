# Project architecture — one codebase, stack-specific

**Altitude.** How one codebase is shaped so that many people can change it safely: the stack and its
version, repo and folder layout, layers and the dependency direction between them, where cross-cutting
concerns live, how modules are composed and wired, how the project is built, tested, and released.
Assumes the product-level boundaries are decided.

## Settle these
1. Stack and versions, and the constraints they bring (platform rules, build tooling, release channel).
2. Layout: single package, monorepo, or workspaces; what is a module; naming and placement rules.
3. Layers and the allowed dependency direction (UI → application → domain → infrastructure, or the
   stack's idiom); how the rule is enforced (lint, module boundaries, build graph).
4. State: where application state lives, how it flows to the UI, what is cached, what is persisted.
5. Cross-cutting concerns, one home each: configuration and secrets, errors, logging and telemetry,
   auth and sessions, i18n, feature flags.
6. Boundaries to the outside: API clients, storage, platform services; each behind one seam that can
   be faked in tests.
7. Quality gates: test strategy per layer, type checking, lint, formatting, CI stages, release steps.

## Options catalogue
- **Layered** — clear dependency direction; fits most apps; enforce the direction or it erodes.
- **Feature-sliced (vertical slices)** — folders by feature with layers inside; scales with team size; shared code needs a home.
- **Hexagonal / ports and adapters** — domain isolated from frameworks and I/O; worth it when the domain is rich or I/O will change.
- **Monorepo with workspaces** — several deployables sharing code; needs a build graph and ownership per package.
- **Plugin / extension architecture** — a stable core with optional modules; needs a versioned contract.
- **Framework-conventional** — follow the framework's layout verbatim; cheapest when the framework is opinionated and the team is small.

## Stack-specific considerations (read the stack card when one exists)
Idiomatic module system and visibility · the framework's lifecycle and where state is allowed to live ·
concurrency model and its rules (main thread, isolates, actors, async runtime) · dependency injection
idiom · error model (exceptions, results, typed errors) · build and packaging constraints · testing
tools per layer · platform rules (app store, browser, server runtime).

## Pitfalls
Layers declared but not enforced · business logic in UI or in I/O adapters · two homes for one concern ·
a shared "utils" that becomes the dependency hub · tests only at one layer · the framework's conventions
fought instead of used · a layout that does not match the team's ownership.

## Evaluate — binary checks
- Dependency direction is stated and mechanically enforced.
- Each cross-cutting concern has exactly one home.
- Every outside boundary sits behind one seam that tests can fake.
- Application state has one documented flow to the UI.
- A newcomer can find where a kind of code belongs from the layout rule alone.
- Build, test, and release run from documented commands; CI gates match them.
- The layout follows or deliberately departs from the framework's convention, with the reason written.

## Output template
```
<layer or slice diagram: boxes = layers/modules, arrows = allowed dependencies, seams marked>
```
**Layout** — folders and what belongs where · **Layers and rules** · **Cross-cutting homes** ·
**State flow** · **Gates** · **What exists** (fit) · **Practices and pitfalls** · **Recommendation** —
pick, why, what would change it · **You decide** (≤3, defaults) · **Next**
