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

## Role

senior | junior, first match: stated · a `my-workflow role:` line in CLAUDE.md or AGENTS.md ·
inferred (paths, symbols or decisions given → senior; only an outcome → junior). Junior: ground
wider (map, then units, then callers), give a consequence per option, size light only with an
example to copy. Show it, so one word corrects it.

## Skills

Per step, list the installed skills whose description names this stack and the step's job (design,
implement, test, review): `- { name: <skill>, why: <one line> }`; none → `[]`. Never `rephrase`,
`discuss` or another stack's. Remap when the stack or scope changes.

## Delegation

| Agent | When |
|---|---|
| `spec-architect` | several dependent units, screens, several deployables, or a new project |
| `spec-tester` → `spec-implementer` | the plan's Batches name them |
| `spec-reviewer` | review at standard size · a second opinion on a design |

Else run the step's skill yourself.

## Models

`strong` for design, review and a low-confidence diagnosis; a batch takes the plan's model. Claude
Code: strong → `opus`, standard → `sonnet`. Copilot uses the session model.
