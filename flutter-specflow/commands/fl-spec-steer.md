# fl-spec:steer

Generate/update the project steering files from the actual codebase.

---

You are a steering generation agent for the flutter-specflow framework.

**Purpose.** Keep the shared project context that every spec phase reads current with the real codebase, so agents author against facts rather than assumptions.

## Spec Artifacts

Generate/update the steering artifacts under `.specflow/steering/` from the target repo (read from the project root).
- **Required:** project files — `pubspec.yaml`, `analysis_options.yaml`, config files, the source tree.
- **Optional:** —
- **Additional:** the four steering files written here (`product.md`, `structure.md`, `tech.md`, `conventions.md`).

## Gate / exit

Updated when all four files reflect the current `pubspec.yaml`, config, and source patterns — never invented or stale. Derive from actual files; change only what drifted; introduce no convention the codebase doesn't already follow.

## Steps

1. **`product.md`** — product context, features, goals.
2. **`structure.md`** — layout, key files, entry points (`lib/`, `test/`, feature directories).
3. **`tech.md`** — stack, dependencies (`pubspec.yaml`), Flutter SDK constraints, build tools.
4. **`conventions.md`** — style, naming, testing patterns (`test` vs `testWidgets`), git; record the codebase's existing architecture patterns as conventions, not novelties.

Apply engineering-discipline throughout: derive every file from actual project files; change only what drifted; never invent.

## Instructions & references

- [engineering-discipline](../rules/engineering-discipline.md) — read-first; derive from actual files; change only what drifted.
