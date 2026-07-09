---
name: oac-figma-decompose
description: >
  Decomposes a Figma screen into a compact component map for planning: discovers the layer tree,
  matches every element against the existing codebase, and classifies each EXISTING / PARTIAL /
  NEW at ~150 tokens each (a planning doc, not raw Figma JSON) — fanning out parallel agents to
  spec only the genuinely new components. Use on any Figma URL, or "what components do I need for
  this screen" / "break down the figma" / "plan from figma".
---

# oac-figma-decompose

Turn a Figma screen + the codebase into one compact **component map** — never raw Figma JSON, never
pixel-perfect code. **Reuse discovery first; extract only what's new.**

## Seams — resolve per project, nothing is hardcoded

| Seam | Resolve from |
|------|--------------|
| **Figma fileKey + nodeId** | parse the Figma URL the caller gave (preferred, always current); else a project `.claude/figma-reference.md` screen→node table; else ask the caller |
| **Component inventory dirs** | discover — glob `src/components/**`, read design-system notes, find large domain files that hold inline sub-components. Never assume a fixed layout |
| **Hex→token map** | build from the project's own tokens source (`src/lib/design-tokens.ts`, the MUI theme, CSS custom properties) into `references/token-map.md` before extraction runs |

## Procedure

1. **Discover the tree** — `get_metadata` on the target node returns the layer hierarchy cheaply.
   Full-page nodes (1440×900+) return empty from `get_design_context`, so always start with metadata.
   Stale-node recovery + which layers to keep vs skip → `references/figma-extraction.md`.
2. **Inventory + classify** — scan the codebase for reusable **and** inline components, match each
   Figma element, tag it EXISTING / PARTIAL / NEW (rubric below). Scan-agent prompt + inline
   sub-component hunting → `references/matching.md`.
3. **Extract NEW + PARTIAL only** — never `get_design_context` an EXISTING component. Fan out one
   parallel agent per NEW/PARTIAL node in a single message; each returns a <200-token spec, not JSON.
   Agent prompt + spec format → `references/figma-extraction.md`. If Step 1 found no valid Figma data,
   skip this step — the codebase-only map from Step 2 is a valid output.
4. **Assemble** — one compact doc (shape below). EXISTING = 2-3 lines each; only NEW gets a full spec.
   Return it to the caller, who decides where to persist it; if invoked with no destination, output inline.

## Classification rubric

| Tag | Means | Output |
|-----|-------|--------|
| **EXISTING** | confident match to a codebase component | cite import + props; **skip extraction** |
| **PARTIAL** | close component exists, needs a new prop / variant / slot | cite it + name the exact gap; extract only the gap |
| **NEW** | nothing in the codebase matches | extract a full ~150-token spec |

Match signals (any one is enough for EXISTING):

| Signal | Trigger | Example |
|--------|---------|---------|
| Name | Figma name ≈ an export name | Figma "StatusBadge" → `Badge` / `StatusBadge` |
| Pattern | visual shape matches a known component | pill + count → `Pill` |
| Icon | Figma `data-name` → project icon component | `data-name="grid_view"` → `GridViewIcon` |
| Structural | Figma control maps to a form primitive | switch → the project's toggle component |

## Output shape

```markdown
# Figma Decompose: {Screen}
Source: {URL or screen ref} · {YYYY-MM-DD} · {N} existing / {N} partial / {N} new

## Component Map
| Figma Element | Status   | Codebase Component            | Notes                     |
|---------------|----------|-------------------------------|---------------------------|
| PersonCard    | EXISTING | `SelectableCard`+`PersonAvatar`| —                        |
| StatusPill    | EXISTING | `Badge preset="status"`       | value="Online"            |
| FilterWidget  | PARTIAL  | `PageFilterBar`               | needs a date-range slot   |
| ActivityGraph | NEW      | —                             | spec below                |

## Existing — use as-is
### PersonCard → `SelectableCard`
- import `@/components/shared/SelectableCard`; wrap `PersonAvatar` + name stack as children
- node 221:19652 (for later visual verify)

## Partial — existing + gap
### FilterWidget → `PageFilterBar`
- import `@/components/shared/PageFilterBar`; covers title/search/actions
- MISSING: date-range slot — new `dateRange` prop or composition · node 445:12345

## New — needs implementation
### ActivityGraph (NEW)
- node 667:89012 | 400×200 · layout column, gap=8, pad=16 · bg=elevation2
- text Basis/400/12/16 color=text · border 6px radius, no stroke
- children ChartHeader, BarGroup, Legend · notes animated bars, tooltip on hover
```

Budget the whole doc under ~200 lines. Over budget = the EXISTING entries are too verbose; trim them.

## Gotchas

- **Layers stack** — check a child frame for a background override before assuming the parent's color.
- **Don't over-decompose, and inline sub-components are EXISTING** — the two most common mis-tags;
  `references/matching.md` owns the why/how.
- **Per-project quirks live in `references/token-map.md`** — space tokens whose pixel value ≠ their
  number, font weights ("Black" = 900 vs 700), snake_case→PascalCase icon naming. Fill it in first.
