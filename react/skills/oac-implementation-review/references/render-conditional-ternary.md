---
title: Ternaries over && for Conditional Rendering
impact: LOW
impactDescription: numeric/NaN left operands leak into the DOM as rendered text
tags: rendering, conditional, jsx
---

## Ternaries over && for Conditional Rendering

`cond && <X/>` renders the *left operand* when it's falsy-but-renderable: `0` renders "0", `NaN` renders "NaN". With numeric values this is a visible bug, not just style.

```tsx
// Incorrect: renders "0" when no cameras are offline
{offlineCount && <OfflineBanner count={offlineCount} />}

// Correct:
{offlineCount > 0 ? <OfflineBanner count={offlineCount} /> : null}
```

`&&` is fine when the left side is a real boolean (`isOpen && <Dialog/>`). Watch only number/possibly-NaN/string left operands. Low severity — a quick, low-risk fix.
