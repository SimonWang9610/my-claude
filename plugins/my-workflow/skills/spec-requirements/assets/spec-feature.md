# <title>

**Goal:** <the outcome in one sentence>
Kind: feature · Stack: <stack and versions> (stated | detected)

## Stories

Each story, then its criteria: the main path first, then edges and failures.

### US-1 <short title> · must | should | could

- **As a:** <actor>
- **I want:** <capability>
- **So that:** <benefit>

#### AC-1.1 <short title>

- **Given:** <starting state>
- **When:** <action or event>
- **Then:** <what the actor observes>
- **Check:** ⬜ → `<command>`

## Standalone criteria

Criteria no story owns.

### AC-2 <short title>

- **Given:** <starting state>
- **When:** <action or event>
- **Then:** <what is observed>
- **Check:** ⬜ → `<command>`

## Functionalities

What the system does to meet the criteria. The design maps each to units.

| Id | The system | Serves |
|---|---|---|
| FN-1 | <verb + object> | AC-1.1 |

## Limits

| Id | Limit | Checked by |
|---|---|---|
| R-1 | <hard number, compatibility, or what must never happen> | <how> |

## Decisions

| Id | Decision | Why or anchor | From |
|---|---|---|---|
| D-1 | <decision> | <why, `path:line` or doc §> | request · Q-<n> · discussions #<n> |

## Open questions

- Q-1 <question> — default: <answer>

## Context

- Facts: <fact> — <anchor>
- Reuse: <paths to copy or extend>

## Out of scope

- <item>

<!-- Light size only: the design and review live here instead of their own files. -->
## Design

## Review

Open: <questions, and what is still undecided — or nothing>
