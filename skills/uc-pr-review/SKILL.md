---
name: uc-pr-review
description: Review open pull requests for a Flutter/Dart project and post an automated review (inline comments + APPROVE or REQUEST_CHANGES) to GitHub. Use this whenever the user asks to review a Flutter PR, check a PR for Riverpod/StateProvider issues, audit listenable disposal, vet Future/Async providers, check ref.watch/ref.read/ref.listen usage, or wants an automated GitHub review posted to a Flutter project's PR. Trigger on phrases like "review this PR", "check PR #N", "review the open PRs", "do a Flutter code review", even when the user only gives a PR URL or number.
---

# Flutter PR Review

Reviews a Flutter/Dart PR against a fixed checklist (general best practices + the project-specific Riverpod/lifecycle rules below), then posts a single GitHub review with inline comments and an APPROVE / REQUEST_CHANGES verdict.

## Workflow

1. **Resolve the PR.** Accept a PR URL, `owner/repo#N`, or a bare number (infer repo from the current git remote with `git remote get-url origin`). If multiple open PRs are requested, loop over each one independently.
2. **Fetch the diff and metadata.** Use the GitHub CLI (`gh`) if available, otherwise the REST API. See `references/github-api.md` for exact commands.
3. **Review the changed lines** against the checklist below. Only flag code that is actually added or modified in the diff (lines prefixed `+`), unless surrounding context clearly shows a regression. Map every finding to a file + line so it can be posted as an inline comment.
4. **Decide the verdict.** Any **blocking** finding → `REQUEST_CHANGES`. Only **nits**/suggestions, or nothing → `APPROVE`. When unsure whether something is a real defect vs. a style preference, post it as a non-blocking comment and do not block on it.
5. **Post the review** as one batched review (summary body + inline comments + event). See `references/github-api.md`. Always show the user the full review text before posting; if the user invoked the skill with explicit intent to post (e.g. "review and approve PR #12"), posting is the expected action, but still surface the verdict and a one-line rationale.

## Verdict legend for comments

Prefix each inline comment so severity is unambiguous:

- `[blocking]` — must fix before merge; drives REQUEST_CHANGES.
- `[nit]` — minor / optional.
- `[question]` — needs author clarification (treat as non-blocking unless the answer could be a defect).

## Project-specific review rules (Riverpod / lifecycle)

These are the rules this team cares about most. Check every one on every PR.

### 1. All listenables must be disposed

Every `ChangeNotifier`, `ValueNotifier`, `TextEditingController`, `ScrollController`, `AnimationController`, `FocusNode`, `StreamSubscription`, `Timer`, and similar listenable/disposable created and _owned_ by a widget or class must be disposed.

- In `State`: created in `initState`/as a field → disposed in `dispose`. Flag any owned listenable with no corresponding `dispose()` call.
- In Riverpod providers: cleanup belongs in `ref.onDispose(...)`. Flag a controller/subscription created in a provider with no `ref.onDispose`.
- Do **not** flag listenables that are passed in (not owned) — the owner disposes them. Note ownership ambiguity as a `[question]` instead of blocking.

### 2. `StateProvider` must be released explicitly via `Legacy.release`

If a `StateProvider` is used, its lifecycle must be ended with an explicit `Legacy.release(...)` call when the consumer is torn down (typically in `dispose`/`ref.onDispose`). Flag any `StateProvider` whose release path is missing — a leaked `StateProvider` is `[blocking]`.

### 3. MUST NOT declare `StateProvider` inside a method / function / State class

Top-level (file-scope) `final fooProvider = StateProvider(...)` is the only acceptable declaration site. A `StateProvider` declared inside a method, function body, or as a `State`/class member creates a new provider per build/instance and leaks.

- This is `[blocking]` **unless** the PR is explicitly working on the legacy codebase that already relies heavily on dynamic `StateProvider`s and cannot be refactored within this PR. In that case downgrade to `[nit]` and note that it follows existing legacy patterns. Look for cues: the touched files are clearly legacy, the PR description says so, or the surrounding code is already saturated with dynamic `StateProvider`s.

### 4. Be careful with Future / Async providers

- `FutureProvider` / `AsyncNotifierProvider` results must be handled with `.when` / `AsyncValue` pattern matching (loading + error + data), not just `.value` / `.requireValue` with no error or loading handling. Flag unhandled error/loading states.
- Watch for unguarded `await` after which `ref`/`context` is used without re-checking `mounted` / provider liveness (use-after-dispose). Flag `if (!mounted) return;` omissions following awaits in widgets, and `ref` reads after await in autoDispose providers that may have been disposed.
- Flag side effects (mutations, navigation) performed directly inside a Future provider's body rather than via `ref.listen`.

### 5. Correct `ref.watch` / `ref.read` / `ref.listen` usage

- `ref.watch` — reactive dependency; use it to read state the widget/provider should rebuild on.
- `ref.read` — one-shot read of current state; for use in callbacks/event handlers, not for values the build output depends on.
- `ref.listen` — side effects in response to change (navigation, snackbars, dialogs).
- **Flag `ref.read` inside a `build` method** as `[blocking]` unless there's a comment documenting why `ref.read` is required there. A `ref.read` in build usually means a missed rebuild dependency.
- Flag `ref.watch` inside callbacks / `onPressed` / event handlers (should be `ref.read`).
- Flag side effects driven off `ref.watch` instead of `ref.listen`.

### 6. Avoid oversized `build` methods

Large `build` methods hurt readability and rebuild performance. Flag a `build` method that is doing too much (rough heuristic: > ~50 lines or > 3–4 levels of nesting with distinct logical sections).

- Recommend extracting cohesive sub-trees into separate widgets (not helper methods returning `Widget`, which don't get their own rebuild boundary).
- If an extracted widget is used only by this parent, recommend making it a **private** widget (`class _Foo extends StatelessWidget`) in the same file.
- This is `[nit]`/suggestion severity unless the size is causing a clear correctness or perf problem.

## General best practices to also check

Const constructors where possible; keys on list items where needed; no business logic in `build`; `BuildContext` not used across async gaps; null-safety soundness (no gratuitous `!`); no `print` in production code (use a logger); avoid rebuilding whole subtrees when a `Consumer`/`select` would scope the rebuild; meaningful widget/file naming; tests updated when behavior changes. Keep general findings proportional — don't bury the project-specific rules under style nits.

## Output / review body format

Post the review body as:

```
## Flutter PR review

**Verdict:** REQUEST_CHANGES | APPROVE

**Summary:** <1–2 sentences>

### Blocking
- <file:line> — <issue> (rule N)

### Suggestions / nits
- <file:line> — <issue>

### Looks good
- <brief positives>
```

Omit empty sections. Keep it tight. Then attach the per-line findings as inline comments via the review's `comments` array.
