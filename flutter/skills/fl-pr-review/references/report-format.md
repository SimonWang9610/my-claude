# Report format — fl-pr-review

Template for the PR review report. Write the sections in this order. Never omit a section
silently — if there is nothing to report, write an explicit "none detected" line so the
reader knows the pass ran.

## Contents

- [Report template](#report-template)
- [Optional GitHub posting](#optional-github-posting)

---

## Report template

```markdown
# Flutter PR Review — <PR title or branch name>

**PR / ref:** `<gh pr #N>` or `<branch>` vs `<base>`
**Reviewed:** <YYYY-MM-DD>
**Verdict (suggested):** <REQUEST CHANGES | CHANGES RECOMMENDED | APPROVE/COMMENT>

> This report is a suggestion, not a disposition. The human reviewer makes the merge decision.
> No finding is confirmed and no branch is approved or blocked until a human acts.

## Summary

<2–4 sentences: what the PR does, how many files / unit kinds were reviewed, top-line verdict
with the key reason.>

## Findings

### Critical

| ID | Severity | Rule (Pn / path) | File : line | Problem | Suggested fix |
|----|----------|-------------------|-------------|---------|---------------|
| F-01 | Critical | P3 / `core/repository-ssot.md` | `lib/.../device_notifier.dart:42` | Notifier field duplicates repository's Stream<Device> — two owners for the same fact | Subscribe to stream; remove duplicate field |

### Major

| ID | Severity | Rule (Pn / path) | File : line | Problem | Suggested fix |
|----|----------|-------------------|-------------|---------|---------------|
| F-02 | Major | P7 / `core/state-boundary-and-lifecycle.md` | `lib/.../device_notifier.dart:31` | StreamSubscription never cancelled — no cleanup registered | For a `@riverpod` notifier: call `ref.onDispose(() => _sub.cancel())` inside `build()`; for a plain controller: override `dispose()` and call `_sub.cancel()` |

### Minor

| ID | Severity | Rule (Pn / path) | File : line | Problem | Suggested fix |
|----|----------|-------------------|-------------|---------|---------------|
| F-03 | Minor | P6 / `core/widget-composition.md` | `lib/.../device_list_page.dart:88` | Widget _buildHeader() helper — should be const StatelessWidget class | Extract class _DeviceListHeader extends StatelessWidget |

## Coverage note

**Reviewed:**
- `lib/features/devices/services/device_repository.dart` — repository (all hunks)
- `lib/features/devices/providers/device_list_notifier.dart` — state holder (all hunks)
- `test/features/devices/services/device_repository_test.dart` — tests (all hunks)

**Not reviewed (not in diff):**
- `lib/features/devices/models/device.dart` — unchanged; not in diff

**Conditional packs consulted:** none (no performance hazard).

**Passes run:** architecture gate (3a), state/ownership (3b), data layer (3c), service layer (3d),
widget composition (3e), DI (3f), test quality (3g), engineering discipline (3h).
```

---

## Optional GitHub posting

> CONFIRM BEFORE RUNNING any posting command. Posting to GitHub is an outward action.
> The human must explicitly request it and confirm the verdict. Never auto-approve.

Full procedure — PR resolution, REST fallback, inline-comment line mapping, and the single
batched review (summary body + verdict event + inline comments in one review object) — lives
in `github-posting.md`.

**Never use `gh pr review --approve` or `event: "APPROVE"` from this skill.** The human
approves the PR themselves after reviewing the findings.
