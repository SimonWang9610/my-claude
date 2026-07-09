# Figma-side mechanics: discovery → extraction

Everything that talks to the Figma MCP. SKILL.md points here from Step 1 (discover) and Step 3
(extract). The target node comes from the caller per the SKILL's Seams table (URL, screen ref, or
raw nodeId+fileKey).

## Discover the layer tree

Call `get_metadata` on the target node — it returns the layer hierarchy cheaply. **Full-page nodes
(1440×900+) return empty from `get_design_context`**, so metadata is always the entry point; use it to
find the meaningful child node IDs.

### Which layers are components

From the metadata tree, keep **meaningful UI elements**, not every frame:

- Keep: named component instances (Figma "Instance"), frames with semantic names (`PersonCard`,
  `FilterBar` — not `Frame 427`), groups that form one coherent UI element.
- Skip: auto-layout wrapper frames, padding/spacing frames, decorative backgrounds, and deep children
  of an already-identified component (its extraction agent handles those).

Build a flat list: `{ name, nodeId, type, parentContext }` per kept element.

### Stale-node recovery (budget: max 5 Figma calls)

Node IDs in a reference file go stale as files are reorganized. If `get_metadata` returns "invalid
node ID":

1. `get_metadata` on the page root (`0:1`) for the full page tree.
2. Search that tree for the screen name as a text node or frame name.
3. Walk up from the text node to its parent page frame.
4. Check the project's design-reference / planning files for newer node IDs.

After 5 calls with no node, **fall back to codebase-only**: Step 2 still produces a valid component
map; you simply skip extraction and NEW components carry no pixel spec.

## Extract (NEW + PARTIAL only)

One parallel agent per NEW/PARTIAL node, all fanned out in a single message. Each agent returns **only**
its compact spec — no raw JSON, no code, no asset URLs. Adapt this prompt per component:

```
Extract component "{name}" from Figma for planning. Output under 200 tokens.

1. Call get_design_context(fileKey="{fileKey}", nodeId="{nodeId}").
2. Extract ONLY:
   - dimensions (w × h)
   - layout: direction, gap, padding, alignment
   - colors → design TOKEN names (never raw hex) — read references/token-map.md
   - typography: weight / size / line-height / letter-spacing
   - border: radius, color, width
   - visual states if variants exist (hover, active, disabled)
   - child component names (names only)
   - any design annotations
3. Emit exactly:

## {Name} (NEW)
- node {nodeId} | {w}×{h}
- layout {dir}, gap={gap}, pad={padding}
- bg {token}
- text {font}/{weight}/{size}/{lh}, color={token}
- border {radius} {color} {width}
- states {if any}
- children {names}
- notes {non-obvious details}
```

For a **PARTIAL** node, narrow the agent to the gap only — the new variant/prop/slot the existing
component lacks — not a full re-spec.

Colors and spacing MUST come out as token names, using the project map in `token-map.md`; that map also
records space-token pixel quirks and font-weight conventions the raw Figma values don't reveal.
