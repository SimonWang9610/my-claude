# my-flutter

> **Under development.** This plugin is not ready for regular use yet; expect gaps and breaking
> changes. The ready one in this repo is [my-workflow](../my-workflow/README.md).

Flutter and Dart knowledge for coding agents: five skills of rules, and no process. It tells an
agent how a Flutter feature should be layered, how to write widget code that does not waste frames,
how to test it, and what to check in a review. It does not drive a spec; pair it with
[my-workflow](../my-workflow/README.md) for that.

- [The skills](#the-skills)
- [With my-workflow](#with-my-workflow)
- [Alone](#alone)
- [Install](#install)
- [Migrating from 1.x](#migrating-from-1x)

## The skills

Each skill is a short index over rule cards in its `rules/` folder.

| Skill | Gives | Rule cards |
|---|---|---|
| `design` | the eight architecture principles (P1 to P8): four layers, one source of truth, state at the right level, sealed async state, disposal, a testability seam for every unit | the principles · 11 cards, one per decision · violation signals per principle |
| `implement` | widget code that is correct and cheap | rebuilds · build cost · build discipline · jank and startup · lists · images · animations · theming |
| `riverpod` | Riverpod 3 with code generation; load it only when the project uses Riverpod | `ref.watch` and `ref.read` · provider declaration · `AsyncNotifier` · `.select` · testing |
| `test` | what makes a Flutter test able to fail | nine rules, each with a check |
| `review` | which rules apply to each kind of unit, the three structural defects that block a change, and how to spot a dishonest test | tests that miss the behaviour · false-positive tests · false-positive signals |

`design` is agnostic of the state-management package. `riverpod` shows how a package skill plugs in
beside it; a Bloc or Provider skill would cover the same five areas.

## With my-workflow

Install both. `my-workflow` names no framework; it looks for installed skills that name your stack
and the job of a step, and hands them to whoever does that step.

| `my-workflow` step | Who | Uses |
|---|---|---|
| design | your session, `spec-design` | `my-flutter:design` |
| design review | `spec-design-reviewer` | `my-flutter:design` |
| test | `spec-tester` | `my-flutter:test` |
| implement | `spec-implementer` | `my-flutter:implement`, `my-flutter:test` |
| review | `spec-code-reviewer` | `my-flutter:review` |

`my-flutter:riverpod` joins any of these steps when the project uses Riverpod.

## Alone

Every skill works in a plain session, with no spec:

```text
/my-flutter:design should the selected device live in a provider or in the page?
/my-flutter:implement this list janks while scrolling
/my-flutter:review the diff on this branch
```

## Install

```text
/plugin marketplace add SimonWang9610/my-claude
/plugin install my-flutter@my-claude
```

Or run the repo's installer; see the [repo README](../../README.md#install).

## Migrating from 1.x

2.0 removes the process `my-flutter` used to carry. `my-workflow` now does that job for any stack.

| Removed or renamed in 2.0 | Use instead |
|---|---|
| `/my-flutter:acceptance-criteria` | `/my-workflow:spec-requirements` |
| `/my-flutter:tasks` | `/my-workflow:spec-plan` |
| `/my-flutter:test-contract` | `/my-flutter:test` |
| `/my-flutter:test-forensics` | `/my-flutter:review` |
| the top-level `rules/` folder | the cards inside `design` and `test` |

What changed in the skills that stay:

- `design` no longer writes `design.md` or contracts and no longer runs a gate with a report. Its
  three blocking triggers are now the "a design is not ready while" list.
- `review` no longer scopes a PR, assigns severity, formats a report or posts to GitHub. The
  reviewer owns those.
- Tests are named by the behaviour they prove. The rule that every `group` label carries a
  requirement id is gone, and so is the coverage pass that depended on it.
- Rule cards live in each skill's `rules/` folder.
