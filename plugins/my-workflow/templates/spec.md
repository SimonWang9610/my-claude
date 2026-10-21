# Spec template

Every section that applies; a small change needs only the title, Goal, Requirements, Decisions,
Done when and Open. Omit empty sections; one line per bullet. The task header is added only when the
spec is kept as a file for a team.

```markdown
# <title>

**Goal:** <the outcome in one sentence>
Track: full · Role: senior (inferred) · Gates: ask · Review: on · Atlas: <path or none> ·
Knowledge: <sources> · Next ids: R<n> D<n> Q<n> T<n> I<n>

## Requirements
- R1 <observable behaviour>
- R2 dropped — <why>

## Decisions
- D1 <decision> — <why or anchor>

## Open questions
- Q1 <question> — default: <answer>

## Context
- Stack: <stack and versions> (stated | detected)
- Facts: <fact> — <anchor>
- Reuse: <paths to copy or extend>

## Limits
- <hard numbers, compatibility, things that must never happen>

## Out of scope
- <item>

## Done when
- <outcome: what the user can do, or what must hold> — `<exact command that checks it>`

## Tasks
- T1 <what> — R<n> — <files> — <check> — <todo | done>

Open: <questions, and what is still undecided — or nothing>
```
