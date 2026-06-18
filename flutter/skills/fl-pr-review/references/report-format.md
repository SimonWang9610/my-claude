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

> CONFIRM BEFORE RUNNING any `gh` command below. Posting to GitHub is an outward action.
> The human must explicitly request it and confirm the verdict. Never auto-approve.

### a) Get the PR's head commit SHA

```bash
gh pr view <n> --json headRefOid -q .headRefOid
# outputs: <SHA>
```

### b) Post inline comments at file:line

Repeat this for each finding that has a concrete file:line:

```bash
gh api repos/{owner}/{repo}/pulls/<n>/comments \
  --method POST \
  --field body="**[F-01 Critical — P3 / core/repository-ssot.md]**

Notifier field duplicates the repository's Stream<Device> — two owners for the same fact (P3 SSOT break).

Fix: subscribe to DeviceRepository.devices stream; remove the duplicate field." \
  --field commit_id="<SHA>" \
  --field path="lib/features/devices/providers/device_notifier.dart" \
  --field line=42 \
  --field side="RIGHT"
```

### c) Post a summary review verdict

Choose exactly one command based on the verdict. Never use --approve autonomously.

```bash
# Critical findings present — request changes
gh pr review <n> --request-changes --body "Flutter PR Review: REQUEST CHANGES. <paste summary>"

# Only Major findings — comment, leave merge to human
gh pr review <n> --comment --body "Flutter PR Review: CHANGES RECOMMENDED. <paste summary>"

# Only Minor / no findings — comment only, human approves
gh pr review <n> --comment --body "Flutter PR Review: LOOKS GOOD (minor nits). <paste summary>"
```

**Never use `gh pr review --approve` from this skill.** The human approves the PR
themselves after reviewing the findings.
