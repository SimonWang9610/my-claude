---
name: uc-pr-review
description: Reviews open Flutter/Dart pull requests against a Riverpod/lifecycle checklist and posts a single batched GitHub review (inline comments + APPROVE or REQUEST_CHANGES verdict). Checks for legacy Riverpod providers (StateNotifier, StateProvider, ChangeNotifierProvider), incorrect ref.watch/ref.read/ref.listen usage, undisposed listenables, unguarded async gaps, and oversized build methods. Trigger on "review this PR", "check PR #N", "review the open PRs", "do a Flutter code review", or any Flutter PR URL or number.
---

# Flutter PR Review

<!-- TOC -->
- [Workflow](#workflow)
- [Verdict legend](#verdict-legend-for-comments)
- [Rule 1 — Listenable disposal](#1-all-listenables-must-be-disposed)
- [Rule 2 — Legacy providers](#2-legacy-providers-must-not-be-introduced)
- [Rule 3 — Provider declaration scope](#3-must-not-declare-any-provider-inside-a-method--function--state-class)
- [Rule 4 — Async providers](#4-be-careful-with-future--async-providers)
- [Rule 5 — ref usage](#5-correct-refwatch--refread--reflisten-usage)
- [Rule 6 — Build method size](#6-avoid-oversized-build-methods)
- [General best practices](#general-best-practices-to-also-check)
- [Output format](#output--review-body-format)
<!-- /TOC -->

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
- In Riverpod providers: cleanup belongs in `ref.onDispose(...)` called inside `build()`, **not** a `dispose()` override. Flag a controller/subscription created in a provider with no `ref.onDispose`.
- Do **not** flag listenables that are passed in (not owned) — the owner disposes them. Note ownership ambiguity as a `[question]` instead of blocking.

### 2. Legacy providers must not be introduced

`StateNotifier`, `StateNotifierProvider`, and `StateProvider` live in `package:riverpod/legacy.dart`; `ChangeNotifierProvider` and `ChangeNotifier`-backed providers live in `package:flutter_riverpod/legacy.dart`. All are legacy. Flag any PR that **adds** these patterns as `[blocking]` and recommend migrating to `@riverpod` code-gen with `Notifier` or `AsyncNotifier`.

- If the PR is touching an existing legacy file and cannot feasibly migrate in scope, downgrade to `[nit]` with a note that it follows existing legacy patterns. Look for cues: the file already saturated with legacy providers, PR description says out-of-scope.
- All new providers must use code-gen (`@riverpod` / `@Riverpod(keepAlive: true)`) with a `build()` method. `autoDispose` is the code-gen default — do **not** flag the absence of `.autoDispose`; only flag if a provider should be kept alive but is missing `@Riverpod(keepAlive: true)`.

### 3. MUST NOT declare any provider inside a method / function / State class

All providers (`@riverpod`-annotated functions/classes, or any remaining legacy `…Provider(…)`) must be declared at file (top-level) scope. A provider declared inside a method, function body, or as a class member creates a new provider per build/instance and leaks.

- This is `[blocking]`.

### 4. Be careful with Future / Async providers

- `AsyncNotifier` / `AsyncNotifierProvider` (and `FutureProvider`) results consumed in the UI must be handled with `.when` / exhaustive `AsyncValue` pattern matching (loading + error + data). Flag bare `.value` / `.requireValue` access with no loading/error branch.
- After any `await` in a widget or provider, re-check liveness before touching `context` or `ref`. In widgets: `if (!mounted) return;`. In providers: `if (!ref.mounted) return;` (use `Ref.mounted`, not a custom flag). Flag omissions.
- Flag side effects (mutations, navigation) performed directly inside an async provider's `build()` body rather than triggered via `ref.listen`.

### 5. Correct `ref.watch` / `ref.read` / `ref.listen` usage

- `ref.watch` — reactive dependency; call only inside `build()` / provider `build()`. Causes rebuild on change.
- `ref.read` — one-shot snapshot; for event handlers and callbacks only, never in `build()`.
- `ref.listen` — side-effect trigger (navigation, snackbars); call inside `build()`, not inside callbacks.
- **Flag `ref.read` inside a `build` method as `[blocking]`** — it silently skips rebuilds when state changes (stale-UI bug), not merely a style issue.
- Flag `ref.watch` inside callbacks / `onPressed` / event handlers (should be `ref.read`).
- Flag side effects driven off `ref.watch` instead of `ref.listen`.
- Flag overly broad watches where `.select()` would narrow rebuilds to a single field: `ref.watch(fooProvider.select((s) => s.field))`.

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
