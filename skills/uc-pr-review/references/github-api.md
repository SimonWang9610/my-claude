# GitHub: fetch a PR diff and post a review

Two interchangeable paths. Prefer `gh` (handles auth automatically). Fall back to REST with a `GITHUB_TOKEN` env var.

## Resolving the PR
- URL `https://github.com/OWNER/REPO/pull/N` → OWNER, REPO, N.
- Bare `N` → infer OWNER/REPO from `git remote get-url origin`.
- `gh pr list --state open` to enumerate open PRs.

## Fetch with gh
```bash
gh pr view  N --repo OWNER/REPO --json title,body,headRefName,baseRefName,files,labels
gh pr diff  N --repo OWNER/REPO            # unified diff
```

## Fetch with REST
```bash
# metadata
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/pulls/N
# diff
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3.diff" \
  https://api.github.com/repos/OWNER/REPO/pulls/N
# files (path + patch per file, useful for mapping line numbers)
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/pulls/N/files
```

## Mapping a finding to an inline comment
GitHub inline comments need `path` + `line` (line in the file's new version, RIGHT side) or `position` (offset within the diff hunk). Easiest reliable approach: use `line` + `side: "RIGHT"` for added/modified lines, and `start_line`/`line` for multi-line. Pull `line` numbers from the `+` lines in the per-file `patch`.

## Post one batched review (preferred — single review, not N comments)

### With gh + REST (submit a review object)
```bash
curl -s -X POST \
  -H "Authorization: Bearer $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/pulls/N/reviews \
  -d @review.json
```

`review.json`:
```json
{
  "body": "## Flutter PR review\n\n**Verdict:** REQUEST_CHANGES\n\n**Summary:** ...",
  "event": "REQUEST_CHANGES",
  "comments": [
    {
      "path": "lib/foo/bar_notifier.dart",
      "line": 42,
      "side": "RIGHT",
      "body": "[blocking] `StateNotifierProvider` is a legacy API (riverpod/legacy.dart). Migrate to `@riverpod` code-gen with `Notifier` and a `build()` method. (rule 2)"
    },
    {
      "path": "lib/foo/baz.dart",
      "line": 88,
      "side": "RIGHT",
      "body": "[blocking] `ref.read` in `build()` silently skips rebuilds when state changes (stale-UI bug). Use `ref.watch`, or move the read into an event handler. (rule 5)"
    }
  ]
}
```

`event` values: `APPROVE`, `REQUEST_CHANGES`, `COMMENT`.

### Pure gh alternative (no inline comments)
```bash
gh pr review N --repo OWNER/REPO --approve  --body "..."
gh pr review N --repo OWNER/REPO --request-changes --body "..."
gh pr review N --repo OWNER/REPO --comment  --body "..."
```
Use the REST `reviews` endpoint when inline comments are needed; `gh pr review` for a body-only verdict.

## Notes
- Don't post duplicate reviews on re-runs — check existing reviews (`GET /pulls/N/reviews`) and amend/skip if one already exists from this run.
- If `gh` auth or `$GITHUB_TOKEN` is missing, stop and ask the user to authenticate (`gh auth login`) rather than guessing.
- Never approve a PR with an unresolved `[blocking]` finding.