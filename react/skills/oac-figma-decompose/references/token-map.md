# Design Token Map

This file is the project's design-token map. Extraction agents map Figma hex colors to the token names listed here — **always use the token name in output, never raw hex**.

**Replace the example below with your project's tokens**, sourced from the project's design-tokens file, MUI theme, or CSS custom properties. The structure (semantic tokens, primary/secondary, status colors, neutrals, space scaling, typography) should be preserved; the values and names will differ per project.

---

## How to build this map

1. **Read the project's tokens source** — typically `src/lib/design-tokens.ts`, a MUI theme file, or CSS custom properties declared in a global stylesheet.
2. **List semantic (mode-aware) tokens** — for each token, record the light-mode hex, dark-mode hex, and its semantic role (e.g. page background, card background, primary text, accent/interactive). Mode-aware tokens are the most important: extraction agents see a single hex in a design and must map it to the right token regardless of mode.
3. **Capture space-token scaling quirks** — some design systems use abstract space tokens (e.g. `--space-N`) whose resolved pixel value is NOT N. Record the actual resolved values here so extraction agents use correct pixel values, not token names, in layout output.
4. **Capture typography/font-weight conventions** — font family names, which numeric weight maps to which named weight (e.g. "Black" = 900 in some systems, 700 in others), and any icon naming convention (e.g. snake_case Figma `data-name` → PascalCase + suffix in code).

---

## Example — reference project (replace with yours)

The content below is from one reference project. It is a concrete worked example of the structure; it is **not** a default. Replace every value with your project's tokens.

### Semantic Tokens (mode-aware — use these in output)

| Token | Light Hex | Dark Hex | Role |
|-------|-----------|----------|------|
| `elevation0` | #f0f0f0 | #000000 | Page background |
| `elevation1` | #fcfcfc | #141314 | Card/panel background |
| `elevation2` | #ffffff | #262526 | Elevated surface, inputs |
| `body` | #2b0030 | #f9f9f9 | Headings, person names |
| `text` | #151015 | #f9f9f9 | General UI text, labels, icon fills |
| `textSecondary` | — | #e4e1e4 | Subdued labels |
| `accent` | #5d3883 | #5d3883 | Borders, button bg, structural |
| `accentContents` | #8057c2 | #8057c2 | Interactive text (toggles, links) |
| `green` | #459a60 | #5bcc7f | Success, online |
| `red` | #b5060e | #e54848 | Error, offline, danger |
| `badgeRed` | — | #e54848 | Badge danger |
| `badgeYellow` | — | #ede159 | Badge warning |
| `whitePerma` | #ffffff | #ffffff | Always white (logo, overlays) |
| `blackPerma` | #000000 | #000000 | Always black |

### Primary / Secondary

| Token Path | Hex | Use |
|-----------|-----|-----|
| `primary.main` | #330033 | Dark purple — sidebar bg, headers |
| `primary.light` | #5C2D5E | Lighter purple accent |
| `primary.dark` | #2b0030 | Darkest purple — same as `body` light |
| `secondary.main` | #5d3883 | Plum — same as `accent` |
| `secondary.light` | #7e5ca6 | Lighter plum |

### Status Colors

| Name | Hex | Mapped From |
|------|-----|-------------|
| online / active | #459a60 | `accent.green` |
| offline / suspended | #b5060e | `accent.red` |
| warning / pending | #ed6c02 | `accent.orange` |
| error | #dc1919 | `accent.redBright` |
| inactive / low | #94939b | `neutral.400` |
| critical | #B404FF | `priority.alarm` |
| medium | #ed6c02 | `accent.orange` |

### Neutrals

| Shade | Hex | Common Use |
|-------|-----|-----------|
| 50 | #fcfcfc | elevation1 (light) |
| 100 | #f0f0f0 | elevation0 (light), sidebar bg |
| 200 | #edeef0 | Hover states, sidebar hover |
| 300 | #d5d6d8 | Borders, dividers |
| 400 | #94939b | Inactive/disabled text |
| 500 | #6b6a72 | Secondary text |
| 600 | #4a4950 | — |
| 700 | #333139 | — |
| 800 | #1e1c24 | — |
| 900 | #151015 | `text` (light mode) |

### Space Token Gotcha

This project's Figma `--space-N` tokens do NOT equal N pixels:

| Token | Resolved Value |
|-------|---------------|
| `--space-4` | 3px |
| `--space-8` | 6px |
| `--space-12` | 9px |
| `--space-16` | 12px |
| `--space-24` | 18px |
| `--space-32` | 24px |
| `--space-48` | 30px |

Always use the resolved pixel value in output, not the token name.

### Typography

- Font: Basis Grotesque Arabic Pro
- Weights: 400 (body), 600 (heading), 900 (Black — titles)
- Black ≠ 700 bold — it's 900
- Icon naming: Figma `data-name` in snake_case → PascalCase + "Icon" suffix → project icon component
