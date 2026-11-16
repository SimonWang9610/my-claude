# Review — <target>

**Verdict:** accept | accept with fixes | rework — <n> blockers, <n> major, <n> minor
Mode: code | design · Review: independent | same context · Round: 1 | 2

## Tests

| Command | Result |
|---|---|
| `<command>` | exit <n> · or: unverifiable — <reason> |
| lint · format | exit <n> · or: none in this project |
| existing tests (regression) | exit <n> |

## Coverage

`spec-check coverage --run` → exit <n> (checked) · or: judged, not checked — <why>

Only the ids that are not plainly passing:

| Id | Result | Evidence |
|---|---|---|
| AC-1.1 | ⛔ unplanned · unimplemented · untested · failing → I-2 · waived · judged done | <output or `path:line`> |

## Workarounds

- <WA id — approved by whom · ⛔ unapproved → I-<n>> — or none

## Quality

| Axis | Result | Evidence |
|---|---|---|
| <axis> | pass · fail → I-1 · n/a | <run, grep or read (judged)> |

## Issues

### I-1 · blocker | major | minor · `path:line` · ⬜

- **Problem:** <defect>
- **Breaks when:** <input or state>
- **Evidence:** <output or quote> — run · read, not run
- **Fix:** <direction>

+<n> more minor issues, not listed

## Open questions

- Q-<n> <question> — default: <answer>

**Recommended:** <up to 3 bullets: fix order, a missing check, a rule worth encoding as a lint>
Pre-existing defects on unchanged lines: <n>
Open: <issues to fix, most severe first — or nothing>
