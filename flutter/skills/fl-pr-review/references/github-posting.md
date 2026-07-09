# GitHub posting — fl-pr-review

> **Opt-in, confirm-first.** Posting to GitHub is an outward action. Run nothing below unless
> the human explicitly requested posting AND confirmed the verdict after seeing the full
> report. **Never use `event: "APPROVE"` or `gh pr review --approve` from this skill** — the
> human approves the PR themselves after reviewing the findings.

## Contents

- [Resolve the PR](#resolve-the-pr)
- [Fetch the diff and metadata](#fetch-the-diff-and-metadata)
- [Map findings to inline comments](#map-findings-to-inline-comments)
- [Post one batched review (preferred)](#post-one-batched-review-preferred)
- [Body-only fallback](#body-only-fallback-no-inline-comments)
- [Notes](#notes)

---

## Resolve the PR

- URL `https://github.com/OWNER/REPO/pull/N` → OWNER, REPO, N.
- Bare `N` → infer OWNER/REPO from `git remote get-url origin`.
- `gh pr list --state open` to enumerate open PRs; review each one independently.

## Fetch the diff and metadata

Prefer `gh` (handles auth). Fall back to REST with `$GITHUB_TOKEN`.

```bash
gh pr view N --repo OWNER/REPO --json title,body,headRefName,baseRefName,files,labels
gh pr diff N --repo OWNER/REPO            # unified diff
```

REST fallback:

```bash
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
  https://api.github.com/repos/OWNER/REPO/pulls/N          # metadata
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github.v3.diff" \
  https://api.github.com/repos/OWNER/REPO/pulls/N          # unified diff
curl -s -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/pulls/N/files    # per-file patch (for line mapping)
```

If `gh` auth and `$GITHUB_TOKEN` are both missing, stop and ask the human to authenticate
(`gh auth login`) rather than guessing.

## Map findings to inline comments

Inline comments need `path` + `line` (line in the file's NEW version, RIGHT side). Use
`line` + `side: "RIGHT"` for added/modified lines, and `start_line`/`line` for multi-line
ranges. Pull line numbers from the `+` lines in each file's `patch`.

## Post one batched review (preferred)

One review object = summary body + verdict event + all inline comments. Prefer this over N
separate comments plus a separate verdict.

```bash
gh api repos/{owner}/{repo}/pulls/N/reviews --method POST --input review.json
```

`review.json`:

```json
{
  "body": "# Flutter PR Review — <title>\n\n**Verdict (suggested):** REQUEST CHANGES\n\n<report summary>",
  "event": "REQUEST_CHANGES",
  "comments": [
    {
      "path": "lib/features/devices/providers/device_notifier.dart",
      "line": 42,
      "side": "RIGHT",
      "body": "**[F-01 Critical — P3 / core/repository-ssot.md]** Notifier field duplicates the repository's Stream<Device> — two owners for the same fact. Fix: subscribe to the repository stream; remove the duplicate field."
    }
  ]
}
```

Verdict → `event` mapping (severity model owns the verdict):

| Report verdict | `event` |
|----------------|---------|
| Any Critical → REQUEST CHANGES | `REQUEST_CHANGES` |
| Only Major → CHANGES RECOMMENDED | `COMMENT` |
| Only Minor / none | `COMMENT` |

## Body-only fallback (no inline comments)

```bash
gh pr review N --repo OWNER/REPO --request-changes --body "Flutter PR Review: REQUEST CHANGES. <summary>"
gh pr review N --repo OWNER/REPO --comment          --body "Flutter PR Review: CHANGES RECOMMENDED. <summary>"
```

## Notes

- Re-runs: check existing reviews first (`gh api repos/{owner}/{repo}/pulls/N/reviews`) and
  skip or amend rather than posting a duplicate.
- Prefix each inline comment with its finding ID + severity + rule citation (as in the
  example above) so severity is unambiguous on GitHub.
