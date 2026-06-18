---
name: oac-figma-decompose
description: Decomposes a Figma screen into a compact component map by discovering the layer tree via get_metadata, matching Figma elements against existing codebase components, and extracting only genuinely new components via parallel agents. Produces a ~150-token-per-component planning document (EXISTING / PARTIAL / NEW classification) instead of raw Figma JSON. Use when given a Figma URL, "decompose design", "break down the figma", "what components do I need for this screen", "plan from figma", "look at this figma" + URL, or any request to map a Figma design to React components for planning or implementation. Stack: React 19 + TypeScript + MUI + Zustand + TanStack Query v5.
---

# oac-figma-decompose

Turns an expensive Figma design-context pull into a compact, planning-friendly component map by:
1. Discovering the component tree cheaply via `get_metadata`
2. Matching Figma elements to existing codebase components (no extraction needed for matches)
3. Extracting only genuinely new components via parallel agents
4. Producing a ~150 token-per-component summary instead of ~2000

The output is a compact component map for planning and implementation — what *exists* vs. what's *new* — not pixel-perfect implementation detail.

---

## Contents

- [Project configuration](#project-configuration-the-per-project-seam)
- [Input](#input)
- [Step 1 — Discover the Component Tree](#step-1--discover-the-component-tree)
- [Step 2 — Match Against Existing Components](#step-2--match-against-existing-components)
- [Step 3 — Parallel Extraction (NEW and PARTIAL only)](#step-3--parallel-extraction-new-and-partial-only)
- [Step 4 — Assemble the Planning Document](#step-4--assemble-the-planning-document)
- [Tips and Gotchas](#tips-and-gotchas)

---

## Project configuration (the per-project seam)

This skill carries **no hardcoded project values**. Three seams are resolved per project before running:

**Figma fileKey** — resolve in this order:
  1. Parse from the Figma URL the user provided (preferred — always current)
  2. Read the project's `.claude/figma-reference.md` if present — for a master fileKey and a named-screen → nodeId table
  3. If neither, ask the user

  Some projects keep a single master fileKey for their entire design file (e.g. `lAw9BelULsiHFvpPAlLeur` is an *example* from one project, not a default — never hardcode it).

**Component inventory locations** — DISCOVER the project's component directories rather than assuming a fixed layout. Glob `src/components/**`, read any architecture/design-system notes, and look for large domain files that hold inline sub-components. As an *illustrative example*, one project organizes as `src/components/shared/`, `src/components/layout/`, `src/components/icons/FigmaIcons.tsx`, plus domain directories — your project may differ.

**Design-token map** — build or confirm the hex→token map from the project's own tokens source (e.g. `src/lib/design-tokens.ts`, the MUI theme, or CSS custom properties). The map lives at `references/token-map.md`; treat the values there as a per-project template to replace.

---

## Input

Accept any of:
- **Figma URL** → parse fileKey and nodeId per the URL rules in the MCP instructions
- **Screen name** from the project's Figma reference file (see Project configuration) → look up the nodeId + fileKey
- **Raw nodeId + fileKey** pair

Resolve the project's fileKey using the order described in Project configuration above.

---

## Step 1 — Discover the Component Tree

Call `get_metadata` on the target node. This returns the layer hierarchy cheaply.

**Important**: Full-page nodes (1440×900+) return empty from `get_design_context`. Always start with `get_metadata` to find the meaningful child node IDs.

### Stale Node Recovery

Figma files get reorganized — node IDs in the Figma reference file may be outdated. If `get_metadata` returns "invalid node ID":

1. **Try `get_metadata` on the page root** (`0:1`) to get the full page tree
2. **Search for the screen name** as a text node or frame name in the metadata (e.g., grep for the screen name)
3. **Walk up from the text node** to find the parent page frame
4. **Check the project's design-reference or planning files** for newer node IDs — they sometimes reference updated nodes

**Budget: max 5 Figma API calls on stale-node recovery.** If you can't find the node after 5 calls, fall back to codebase-only analysis (Step 2 still works — you just skip Step 3 extraction). A codebase-only decomposition with proper component matching is still far more useful than no output at all.

### Identifying Components

From the metadata tree, identify **meaningful UI components** — not every frame. Look for:
- Named component instances (Figma "Instance" type)
- Frames with semantic names (e.g., "PersonCard", "FilterBar", not "Frame 427")
- Groups that represent a coherent UI element

Skip:
- Auto-layout wrapper frames (just structural)
- Padding/spacing frames
- Decorative backgrounds
- Deeply nested children of already-identified components (the extraction agent handles those)

Build a flat list: `{ name, nodeId, type, parentContext }` for each identified component.

---

## Step 2 — Match Against Existing Components

Before calling `get_design_context` on anything, scan what already exists. Spawn a single agent to do a quick inventory:

```
Scan the codebase for ALL reusable components — shared AND domain-specific.

First, DISCOVER the project's component directories:
- Glob src/components/** to find subdirectories
- Read any architecture/design-system notes in .claude/ or the project root
- Look for a project-level index or barrel file that re-exports components

Then scan what you find. As an example, one project organizes as:
- src/components/shared/ (all .tsx files — read exports and brief description)
- src/components/layout/ (AppShell, HeaderBar, Sidebar, e.g.)
- src/components/icons/FigmaIcons.tsx (list all exported icon names, e.g.)
- Domain directories (notifications, people, hardware, dashboard, etc.)

IMPORTANT: Also scan domain-specific files for INLINE sub-components.
Large files like a modal or page component often contain 10-15 inline
sub-components (CredentialCard, PinDisplay, StatCard, etc.) that are not
exported but ARE already implemented. Read the top ~100 lines of large domain
files to find these — they count as EXISTING.

For each component, note: file path, exported name, what it renders in one line.
For inline sub-components: file path, function name, "inline in {ParentComponent}".
Return as a flat list.
```

Then match each Figma component against this inventory:

| Match Type | Signal | Example |
|-----------|--------|---------|
| **Name match** | Figma name ≈ export name | Figma "StatusBadge" → `Badge` or `StatusBadge` |
| **Pattern match** | Visual shape matches a known component | Pill shape with count → `Pill` component |
| **Icon match** | `data-name` attribute → project icon component | `data-name="grid_view"` → `GridViewIcon` |
| **Structural match** | Figma toggle/select/input → the project's form component | Switch control → a project toggle component |

Classify each Figma component as:
- **EXISTING** — confident match to codebase component
- **PARTIAL** — similar component exists but needs customization or new props
- **NEW** — nothing in the codebase matches this

---

## Step 3 — Parallel Extraction (NEW and PARTIAL only)

**Do NOT call `get_design_context` on EXISTING components.** The whole point of matching is to skip extraction for components that already exist in the codebase. Only extract components classified as NEW or PARTIAL.

For each NEW or PARTIAL component, spawn a parallel agent. Each agent:

1. Calls `get_design_context` with the component's fileKey and nodeId
2. Maps all colors to design tokens (read `references/token-map.md` for the project's filled-in map)
3. Distills the response into compact format (see output format below)
4. Returns **only** the compact summary — not raw Figma JSON, not code snippets, not asset URLs

If Step 1 failed (stale node, no valid Figma data), skip this step entirely. The codebase-only component map from Step 2 is the output.

**Agent prompt template** (adapt per component):

```
Extract component "{name}" from Figma for planning. Keep output under 200 tokens.

1. Call get_design_context(fileKey="{fileKey}", nodeId="{nodeId}")
2. From the response, extract ONLY:
   - Dimensions (width × height)
   - Layout direction, gap, padding, alignment
   - Colors — map to design token names (see token map below)
   - Typography: font-weight, size, line-height, letter-spacing
   - Border: radius, color, width
   - Visual states if variants exist (hover, active, disabled)
   - Child component names (just names, not details)
   - Any design annotations

3. Output in this exact format:

## {Name} (NEW)
- node: {nodeId} | {w}×{h}
- layout: {dir}, gap={gap}, pad={padding}
- bg: {token}
- text: {font}/{weight}/{size}/{lh}, color={token}
- border: {radius} {color} {width}
- states: {if any}
- children: {names}
- notes: {non-obvious details}

Token map: read `references/token-map.md` (the project's filled-in map).
```

Fan out all agents in a single message — don't wait between them.

---

## Step 4 — Assemble the Planning Document

**Output budget: aim for under 200 lines.** EXISTING components should be 2-3 lines each (import + key props + node ID). Only NEW components get full specs. If you're over 200 lines, the EXISTING entries are too verbose — trim them.

Combine everything into a compact document:

```markdown
# Figma Decompose: {Screen/Feature Name}

Source: {Figma URL or screen reference}
Date: {YYYY-MM-DD}
Components: {N existing} / {N partial} / {N new}

## Component Map

| Figma Element | Status | Codebase Component | Notes |
|--------------|--------|-------------------|-------|
| PersonCard | EXISTING | `SelectableCard` + `PersonAvatar` | — |
| StatusPill | EXISTING | `Badge preset="status"` | pass value="Online" |
| FilterWidget | PARTIAL | `PageFilterBar` | needs new date-range slot |
| ActivityGraph | NEW | — | see spec below |

## Existing — Use As-Is

### PersonCard → `SelectableCard`
- import: `@/components/shared/SelectableCard`
- props: `selectable`, wrap `PersonAvatar` + name stack as children
- node: 221:19652 (for later visual verification)

### StatusPill → `Badge`
- import: `@/components/shared/Badge`
- props: `preset="status" value="Online"`

## Partial — Existing + Customization

### FilterWidget → `PageFilterBar`
- import: `@/components/shared/PageFilterBar`
- existing props cover: title, search, actions
- MISSING: date range picker slot — needs new `dateRange` prop or composition
- node: 445:12345

## New — Need Implementation

### ActivityGraph (NEW)
- node: 667:89012 | 400×200
- layout: column, gap=8, pad=16
- bg: elevation2
- text: Basis/400/12/16, color=text
- border: 6px radius, no stroke
- children: ChartHeader, BarGroup, Legend
- notes: animated bars, tooltip on hover
```

### Where to Save

This skill **returns** the planning document to its caller; the caller decides where to persist it (e.g. a planning or spec folder). If invoked directly with no caller destination, output it in the conversation.

---

## Tips and Gotchas

- **Space-token and font-weight conventions vary by project** — one project's `--space-N` tokens don't equal N pixels; another's "Black" font weight is 900, not 700; icon naming conventions (e.g. snake_case → PascalCase + suffix) differ per design system. These project-specific quirks are captured in `references/token-map.md` — fill that file in per project before extraction agents run.
- **Figma layers stack**: Check child frames for background overrides before assuming the parent's color applies.
- **Don't over-decompose**: A card with a name, subtitle, and avatar is ONE component (probably `SelectableCard`), not three. Match at the semantic level.
- **Partial matches are valuable**: "Use `Badge` but add a new `size='xs'` variant" is more useful for planning than extracting the full design from scratch.
- **Inline sub-components count as EXISTING**: Large domain files (modals, pages) contain 10+ inline sub-components that aren't exported but ARE implemented. Don't classify these as NEW.
- **Codebase-only fallback is fine**: If Figma nodes are stale, a component map built purely from codebase analysis is still valuable for planning — you just won't have pixel specs for NEW components.
