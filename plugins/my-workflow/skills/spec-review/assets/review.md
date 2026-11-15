# Review — <target>

**Verdict:** accept | accept with fixes | rework — <n> blockers, <n> major, <n> minor
Mode: code | design · Review: independent | same context · Round: 1 | 2

## Tests

| Command | Result |
|---|---|
| `<command>` | exit <n> · or: unverifiable — <reason> |
| existing tests (regression) | exit <n> |

## Criteria

| Id | Status | Evidence |
|---|---|---|
| AC1.1 | ✅ done · ⛔ not done → I2 · unverifiable | <test, output or `path:line`> |

## Quality

| Axis | Result | Evidence |
|---|---|---|
| <axis> | pass · fail → I1 · n/a | <run, grep or read> |

## Issues

| Id | Severity | Where | Problem — breaks when | Evidence | Fix | Status |
|---|---|---|---|---|---|---|
| I1 | blocker · major · minor | `path:line` | <defect> — <input or state> | run · read, not run | <direction> | ⬜ |

+<n> more minor issues, not listed

## Open questions

- Q<n> <question> — default: <answer>

**Recommended:** <up to 3 bullets: fix order, a missing check>
Pre-existing defects on unchanged lines: <n>
Open: <issues to fix, most severe first — or nothing>
