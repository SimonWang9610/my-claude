---
name: decompose-figma
description: >
  Turns a Figma screen into a compact component map — every element classified
  EXISTING / PARTIAL / NEW against the codebase, with specs extracted only for what's
  genuinely new (never raw Figma JSON). Use whenever a design must become buildable
  work: a Figma URL to break down, "what components does this screen need", or a spec
  carrying design links.
---

# decompose-figma

Turn a Figma screen + the codebase into one compact **component map**. Reuse discovery
first; extract only what's new. Downstream: EXISTING / PARTIAL / NEW feed the design
phase's unit inventory as REUSE / MODIFY / NEW proposals.

## Resolve per project — nothing hardcoded

- **fileKey + nodeId** — parse the caller's Figma URL; else a project screen→node table;
  else ask.
- **Component inventory** — discover the layout (glob `src/components/**`, design-system
  notes, barrel files); never assume one.
- **Hex→token map** — build from the project's own tokens source (theme, CSS custom
  properties) before extraction; note per-project quirks (icon naming case, weight names).

## Procedure

1. **Discover the tree** — `get_metadata` on the target node (cheap; full-page nodes
   return empty from `get_design_context`, so always start with metadata). No valid Figma
   data → skip to step 4 with the codebase-only map.
2. **Inventory + classify** — one scan agent inventories reusable AND inline components
   (large domain files hide 10–15 unexported sub-components — read their top ~100 lines);
   match each Figma element by any one signal: **name** (normalized ≈ an export),
   **pattern** (visual shape → known component), **icon** (`data-name` → icon component),
   **structural** (form control → the project's primitive). Tag:
   - **EXISTING** — confident match; cite import + props; **never extract**.
   - **PARTIAL** — close match with a named gap (prop/variant/slot); extract the gap only.
   - **NEW** — nothing matches; extract a full spec.
3. **Extract NEW + PARTIAL only** — fan out one agent per node in a single message; each
   returns a <200-token spec (layout, tokens, children, behaviors), never JSON.
4. **Assemble** — the map below; EXISTING entries 2–3 lines, only NEW gets a full spec.
   Whole doc under ~200 lines — over budget means the EXISTING entries are too verbose.

## Output shape

```markdown
# Figma Decompose: <Screen>
Source: <URL> · <date> · <N> existing / <N> partial / <N> new

| Figma Element | Status | Codebase Component | Notes |
|---------------|--------|--------------------|-------|
| StatusPill | EXISTING | `Badge preset="status"` | — |
| FilterWidget | PARTIAL | `PageFilterBar` | needs date-range slot · node 445:12345 |
| ActivityGraph | NEW | — | spec below |

## Partial — existing + gap
### FilterWidget → `PageFilterBar`
- covers title/search/actions · MISSING: date-range slot (new prop or composition)

## New
### ActivityGraph
- node 667:89012 · 400×200 · column, gap=8, pad=16 · bg=elevation2
- text Basis/400/12/16 · radius 6 · children: ChartHeader, BarGroup, Legend
- behaviors: animated bars, tooltip on hover
```

## Anti-patterns

- **Over-decomposing** — a card of name + subtitle + avatar is ONE component, not three;
  match at the semantic level, not per leaf node.
- **Tagging inline sub-components NEW** — implemented means EXISTING; the most common
  false-NEW (that's why step 2 reads large domain files).
- **Extracting an EXISTING match "to be safe"** — the point of matching is skipping that
  call; cite it and move on.
- **Layers stack** — check a child frame for a background override before assuming the
  parent's color.
