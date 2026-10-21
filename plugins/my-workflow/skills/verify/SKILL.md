---
name: verify
description: >-
  Proves a spec's requirements from the outside: writes one black-box acceptance check per behavioural
  requirement at its outermost surface and sees it fail before the code exists, or runs the spec's
  "done when" commands and checks and reports each requirement as done, not done or unverifiable, with
  evidence. Use on "write acceptance tests for this spec", "does it meet the spec", "verify R1–R4", or
  after build. Not for unit tests (they come with build) or code review (use my-workflow:critique).
argument-hint: "[author | run] [R<n>…]"
---

# verify

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

1. **Input** — the spec (Requirements, Done when) in the session or a file the user names, and the
   design's Contracts and data when present. Mode: author for requirements whose checks do not exist
   yet or changed, else run. No spec → the request's stated behaviour is the requirements.
2. **Author** — per behavioural `R`, one check at the outermost surface it names (a command, an
   endpoint, the UI, or a public function from the design's contracts), in the project's test setup
   and patterns (`/my-workflow:audit-truth` to find them). Assert the observable outcome, never
   internals. Run each: it must fail for the missing behaviour, not for a broken setup; a compile or
   import error naming the contract's missing surface counts as the expected failure, any other error
   is a broken setup. A requirement about content or configuration → a grep or read check. Return each
   check's command for its requirement's Done when line.
3. **Run** — a run report for the same code state already in the session → reuse it. Else the spec's
   Done when commands first, in a temp copy when they write; one that cannot run here (never install
   into the real environment) → unverifiable, with the reason. Then per `R`: done (a check that would
   fail without it passed), not done, or unverifiable — what would show it. A check that only
   approximates the outermost surface (a stand-in) is evidence, never done. Last, unless only named
   requirements were asked for, the project's existing tests for the touched area, reported as their
   own regression line.
4. **Guard** — a check is loosened, skipped or deleted only with a `D` that says why.
5. **Report** — per the conventions' Output: a table of `R` · check · result · evidence. `Open:` the
   requirements not done or unverifiable.
