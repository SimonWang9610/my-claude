# Spec context

## Folder and branch

`specs/<task>/` (kebab-case) under the place the user or the project's context files name, else the
project root; git-ignore a new `specs/` unless asked. Propose branch `<kind>/<task>`; declined or no
git → `branch: none`.

## Size

- **Light** — a few files, an existing pattern, no open approach. No agents; design and review live
  in `spec.md` (`artifacts.design` and `artifacts.review` → `spec.md`); one gate, on the design step
  when it runs, else on the first step.
- **Standard** — the rest: the template as it is.

"Quick" or "deep" sets it; "just do it" sets `gates: auto`.

## Delegation

| Agent | When |
|---|---|
| `spec-architect` | several dependent units, screens, several deployables, or a new project |
| `spec-tester` | standard size and the project has a test suite: the acceptance tests, before any code |
| `spec-reviewer` | review at standard size · a second opinion on a design |

Else run the step's skill yourself.
