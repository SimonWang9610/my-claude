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

Concrete worked example of the structure, from one reference project — **not** a default. Replace every value with your project's tokens; keep the categories.

### Semantic Tokens (mode-aware — use these in output)

| Token | Light Hex | Dark Hex | Role |
|-------|-----------|----------|------|
| `elevation0` | #f0f0f0 | #000000 | Page background |
| `elevation2` | #ffffff | #262526 | Elevated surface, inputs |
| `text` | #151015 | #f9f9f9 | General UI text, labels, icon fills |
| `accent` | #5d3883 | #5d3883 | Borders, button bg, structural |
| `green` / `red` | #459a60 / #b5060e | #5bcc7f / #e54848 | Success/online, error/offline |
| `whitePerma` / `blackPerma` | #ffffff / #000000 | same | Always white/black (logo, overlays) |

### Primary / Secondary

| Token Path | Hex | Use |
|-----------|-----|-----|
| `primary.main` | #330033 | Dark purple — sidebar bg, headers |
| `secondary.main` | #5d3883 | Plum — same as `accent` |

### Status Colors

| Name | Hex | Mapped From |
|------|-----|-------------|
| online / active | #459a60 | `accent.green` |
| warning / pending | #ed6c02 | `accent.orange` |
| critical | #B404FF | `priority.alarm` |

### Neutrals

| Shade | Hex | Common Use |
|-------|-----|-----------|
| 100 | #f0f0f0 | elevation0 (light), sidebar bg |
| 400 | #94939b | Inactive/disabled text |
| 900 | #151015 | `text` (light mode) |

### Space Token Gotcha

This project's Figma `--space-N` tokens do NOT equal N pixels:

| Token | Resolved Value |
|-------|---------------|
| `--space-8` | 6px |
| `--space-16` | 12px |
| `--space-32` | 24px |

Always use the resolved pixel value in output, not the token name.

### Typography

- Font: Basis Grotesque Arabic Pro
- Weights: 400 (body), 600 (heading), 900 (Black — titles)
- Black ≠ 700 bold — it's 900
- Icon naming: Figma `data-name` in snake_case → PascalCase + "Icon" suffix → project icon component
