# Review template

Returned in the session. Omit sections that do not apply.

```markdown
# Review — <target>

**Verdict:** accept | accept with fixes | rework — <n> blockers, <n> major, <n> minor
Mode: code | design · Spec: <path | session | none> · Review: independent | same context

## Checks
| Command | Result |
|---|---|
| `<command>` | exit <n> · or: unverifiable — <reason> |
| existing tests (regression) | exit <n> |

## Requirements
| Id | Status | Evidence |
|---|---|---|
| R1 | done · not done → I2 · unverifiable | <test, output or path:line> |

## Quality
| Axis | Result | Evidence |
|---|---|---|
| <axis> | pass · fail → I1 · n/a | <run, grep or read> |

## Issues
| Id | Severity | Where | Problem — breaks when | Evidence | Fix |
|---|---|---|---|---|---|
| I1 | blocker · major · minor | `path:line` | <defect> — <input or state> | run · read, not run | <direction> |

+<n> more minor issues, not listed

## Open questions
- Q<n> <question> — default: <answer>

**Recommended:** <up to 3 bullets: fix order, a missing check>
Pre-existing defects on unchanged lines: <n>
Open: <issues to fix, most severe first — or nothing>
```
