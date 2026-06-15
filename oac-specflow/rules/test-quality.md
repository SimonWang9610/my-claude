---
paths: ["**/e2e/**", "**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx"]
---

# Test quality

Apply when writing or editing a test. A test that passes without exercising the real behavior
is worse than no test — it hides the gap.

- **Assert observable outcomes, not implementation.** Check rendered text, returned state, and
  user-visible effects — not that an internal function or mock was called a certain way.
  Ref: https://testing-library.com/docs/guiding-principles/
- **Map each test to an acceptance-criterion ID.** Every AC behavior has a named test; every
  test names the AC it covers, so coverage gaps are visible.
- **Build fixtures from the production type, not hand-written shapes.** A fixture typed as the
  real entity breaks when the type changes; a loose object literal silently drifts.
- **No tautologies.** Don't assert a mock returns what you told it to return. Exercise the
  unit's own logic; if a wholesale mock bypasses the behavior under test, the test is a
  false positive — decompose instead (see architecture-principles P5).
- **Use a real QueryClient when testing query/mutation config.** Mocking TanStack Query erases
  caching, invalidation, and error-state behavior the AC may depend on.
- **Turn one-shot greps into CI guards.** A ban verified once at PR time (no hard-coded hex,
  no banned import) must become an enduring ESLint/Vitest check, or it regresses unseen.
