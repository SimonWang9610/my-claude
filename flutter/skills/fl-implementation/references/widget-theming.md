---
title: Read Colors and Typography from Theme Tokens
impact: HIGH
tags: theming, design-tokens, dark-mode, ThemeExtension, accessibility
---

## Read Colors and Typography from Theme Tokens

Every color and text style in a widget must come from `Theme.of(context)` — either standard `ColorScheme`/`TextTheme` tokens or a `ThemeExtension` for domain-specific values. Hard-coded literals and brightness branches scatter design decisions and silently break dark mode.

- **Standard colors from `colorScheme`** — use roles like `primary`, `surface`, `error` from `Theme.of(context).colorScheme`; never write `Colors.blue` or `Color(0xFF...)` in a widget.
- **Typography from `textTheme`** — use named styles (`labelSmall`, `bodyMedium`, etc.) from `Theme.of(context).textTheme`; never construct a bare `TextStyle(fontSize: 12, ...)` inline.
- **Domain tokens via `ThemeExtension`** — for values not covered by `ColorScheme` (alert severity, status indicators), define a `ThemeExtension<T>` and register it in both the light and dark `ThemeData` at the `MaterialApp` root.
- **One light + one dark `ThemeData` at the root** — dark-mode variants belong in `darkTheme`, not in per-widget brightness branches; a `Theme.of(context).brightness ==` branch selecting between two color literals is equivalent to two hard-coded literals.
- **Never:** use `Color(0x...)` or `Colors.*` literals in a widget's `build()`; branch on `brightness` to pick a color; define a `TextStyle` with explicit `fontSize` or `color` outside a `ThemeData`/`ThemeExtension`.

```dart
// WRONG — hard-coded literal, invisible in dark mode
Container(color: const Color(0xFF1976D2), child: label)

// CORRECT — semantic token from colorScheme; adapts to light/dark automatically
Container(
  color: Theme.of(context).colorScheme.primary,
  child: Text(
    label,
    style: Theme.of(context).textTheme.labelMedium,
  ),
)

// Domain-specific token via ThemeExtension (e.g. alert severity colours)
final severity = Theme.of(context).extension<AlertTheme>()!;
Icon(Icons.warning, color: severity.criticalColor)
```

Ref: https://docs.flutter.dev/cookbook/design/themes
