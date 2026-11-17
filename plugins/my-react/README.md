# my-react

> **Under development.** This plugin is not ready for regular use yet; expect gaps and breaking
> changes. The ready one in this repo is [my-workflow](../my-workflow/README.md).

React and TypeScript knowledge for coding agents: five skills of rules, and no process. It tells
an agent what a sound React design decides, how to write hooks and components correctly, how to
test them, and what to check in a review. It does not drive a spec; pair it with
[my-workflow](../my-workflow/README.md) for that.

- [The skills](#the-skills)
- [With my-workflow](#with-my-workflow)
- [Alone](#alone)
- [Install](#install)
- [TypeScript language server](#typescript-language-server)
- [Migrating from 1.x](#migrating-from-1x)

## The skills

Each skill is a short index over rule cards. A card states the code shape it catches, why that
shape is a bug at runtime, and a look-alike that is fine.

| Skill | Gives | Rule cards |
|---|---|---|
| `design` | where a fact lives, how to cut components and hooks, which way dependencies point, what a unit's interface must state | state ownership · decomposing components · services and boundaries |
| `implement` | calling, building and optimizing hooks and components; store and service bodies | using hooks · building hooks · optimizing hooks · building components · optimizing components · stores and services |
| `test` | the harness per kind of unit, mocking at the boundary, journey tests over the mounted app, what makes a green test honest | unit testing · journey testing · test quality |
| `review` | the React checks for a diff and its tests, and a performance diagnostic | checklist · behaviour · quality · performance check |
| `figma` | a Figma screen as a map of existing, partial and new components | — |

The testing cards assume Vitest, React Testing Library, MSW and user-event. Every skill reads
`package.json` first and skips rules for a library the project does not use.

## With my-workflow

Install both. `my-workflow` names no framework; it looks for installed skills that name your stack
and the job of a step, and hands them to whoever does that step.

| `my-workflow` step | Who | Uses |
|---|---|---|
| design | your session, `spec-design` | `my-react:design`, `my-react:figma` |
| design review | `spec-design-reviewer` | `my-react:design` |
| test | `spec-tester` | `my-react:test` |
| implement | `spec-implementer` | `my-react:implement`, `my-react:test` |
| review | `spec-code-reviewer` | `my-react:review` |

For the agent steps, `drive-spec` lists the skills per step in the spec's `workflow.yaml`, where
you can edit them.

## Alone

Every skill works in a plain session, with no spec:

```text
/my-react:design where should the selected-device state live?
/my-react:implement fix the effect loop in useDeviceStream
/my-react:review the diff on this branch
```

## Install

```text
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-react@my-claude
```

Or run the repo's installer; see the [repo README](../../README.md#install).

## TypeScript language server

`my-react` registers a TypeScript LSP ([`.lsp.json`](.lsp.json)), giving the agent exact
go-to-definition, find-references, and type diagnostics pushed into context after each edit. The
binaries are not bundled; `setup.py` warns when they are missing:

```bash
npm install -g typescript-language-server typescript
```

Without them the plugin still works: Claude Code lists the server in the `/plugin` Errors tab and
everything else loads. If another enabled plugin already claims `.ts` and `.tsx`, the first server
registered wins and this one stays idle.

## Migrating from 1.x

2.0 removes the process `my-react` used to carry. `my-workflow` now does that job for any stack.

| Removed in 2.0 | Use instead |
|---|---|
| `my-react:driver` agent | `/my-workflow:drive-spec` |
| `/my-react:requirements`, `/my-react:plan` | `/my-workflow:spec-requirements`, `/my-workflow:spec-plan` |
| `/my-react:audit`, `my-react:auditor` | `/my-workflow:audit-truth`, `my-workflow:code-auditor` |
| `/my-react:evaluate`, `my-react:evaluator` | `my-workflow:spec-design-reviewer`, `my-workflow:spec-code-reviewer`, with `my-react:review` |
| `my-react:architect`, `tester`, `implementer`, `e2e` agents | `my-workflow`'s `spec-design` skill and its `spec-tester` and `spec-implementer` agents |

What changed in the skills that stay:

- `design`, `implement`, `test` and `review` no longer write `design.md`, contracts or reports, and
  no longer run a procedure. They are rules.
- The `e2e` agent's rules are now the journey-testing card of `test`.
- Tests are named by the behaviour they prove. The rule that every test label starts with a
  requirement id is gone.
- The scored rubric (axis scores, PASS, CONDITIONAL, BLOCK, the foundation signal) is gone; its
  React checks are the `review` checklist.
- Agents no longer keep a per-codebase memory.
