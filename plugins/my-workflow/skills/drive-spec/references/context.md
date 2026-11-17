# Spec context

## Folder and branch

`specs/<task>/` (kebab-case) under the place the user or the project's context files name, else the
project root; git-ignore a new `specs/` unless asked. Propose branch `<kind>/<task>`, `base` the
branch it is cut from; declined → `branch: none`, `base` the current branch; no git → both `none`.

## Size

- **Light** — a few files, an existing pattern, no open approach.
  `artifacts.design` → `spec.md`; one gate: the first step has no `gate` line, and the design
  step's gate covers both, asked even when the design is skipped.
- **Standard** — the rest: the template as it is.

"Quick" or "deep" sets it; "just do it" sets `gates: auto`.

## Heavy design

Any of: more than 6 units, so it is drawn as groups · 3 or more existing units modified or reused ·
a `D` that departs from an existing pattern · a new project or several deployables. Light size →
never.
