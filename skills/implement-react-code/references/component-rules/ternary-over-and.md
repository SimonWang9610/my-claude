---
title: Ternary over && for Non-Boolean Conditions
impact: LOW
impactDescription: a numeric condition renders a literal 0 into the DOM
tags: jsx, conditional-rendering
---

**Rule:** Use a ternary, not `&&`, when the condition can be a number/NaN/string.

- CORRECT Example:

```tsx
{offlineCount > 0 ? <OfflineBanner count={offlineCount}/> : null}
```

- BAD Example:

```tsx
{offlineCount && <OfflineBanner count={offlineCount}/>}   // renders "0" when count is 0
```
