# Matching Figma elements against the codebase

The reuse-discovery half of decomposition. Goal: tag as many Figma elements EXISTING as honestly
possible so Step 3 extracts the smallest set. A missed match wastes an extraction agent and invents a
duplicate component.

## 1. Build the inventory (one scan agent)

Spawn a single agent to inventory reusable components before touching `get_design_context`:

```
Scan the codebase for ALL reusable components — shared AND domain-specific.

First DISCOVER the project's component layout (don't assume one):
- Glob src/components/** for subdirectories
- Read any architecture/design-system notes in .claude/ or the project root
- Find a barrel/index file that re-exports components

Then scan what you find. For each component note: file path, exported name,
what it renders in one line.

CRITICAL: also scan large domain files for INLINE sub-components. A modal or page
file often holds 10-15 sub-components (CredentialCard, PinDisplay, StatCard, …)
that are NOT exported but ARE implemented — read the top ~100 lines of each large
domain file to find them. For each: file path, function name, "inline in {Parent}".

Return a single flat list.
```

## 2. Match each Figma element

Walk the flat component list from Step 1 for each Figma element and apply the signal table (see
SKILL.md). Notes per signal:

- **Name** — normalize both sides (drop "Figma", casing, plural). "PersonCard" ≈ `PersonAvatar` only
  if the render matches; a name near-miss with a different render is PARTIAL, not EXISTING.
- **Pattern** — describe the shape, then search for a component that renders it: "rounded pill with a
  count" → grep for `Pill`, `Chip`, `Badge`.
- **Icon** — the Figma `data-name` (snake_case) maps to a project icon component via the naming rule
  in `token-map.md` (e.g. `grid_view` → `GridViewIcon`). An icon is almost always EXISTING.
- **Structural** — a switch/select/checkbox/text-input in Figma maps to the project's form primitive
  even when the name differs.

## 3. Tag

Apply the rubric in SKILL.md. For PARTIAL, the gap note beats a from-scratch spec — "use `Badge` but
add `size='xs'`" is more actionable than restating the whole component.

## Anti-patterns

- **Over-decomposing** — a card = name + subtitle + avatar is ONE component (probably a
  `SelectableCard`), not three. Match at the semantic level, not per leaf node.
- **Tagging inline sub-components NEW** — they are implemented; they are EXISTING. This is the most
  common false-NEW, which is why Step 1 reads the top of every large domain file.
- **Extracting an EXISTING match "to be safe"** — the whole point of matching is to avoid the
  `get_design_context` call. If it's EXISTING, cite it and move on.
