---
title: Prefer children/Slots over render Props
impact: MEDIUM
impactDescription: render props for static content add indirection without benefit
tags: composition, render-props, children
---

## Prefer children/Slots over render Props

`renderX` props are warranted only when the parent must inject data the caller can't otherwise access (e.g., virtualizers passing the row index). For static content, plain `children` or slot props (`header={<Toolbar/>}`) compose better, read better, and avoid the inline-function-identity problem.

**Incorrect (no data injected — pure indirection):**

```tsx
<Panel renderHeader={() => <Toolbar />} renderBody={() => <CameraGrid />} />
```

**Correct:**

```tsx
<Panel header={<Toolbar />}>
  <CameraGrid />
</Panel>
```

**Legitimate render prop (parent supplies data):**

```tsx
<VirtualList items={events} renderRow={(event, style) => <EventRow event={event} style={style} />} />
```

The review question is always: does the function parameter receive anything the caller didn't already have? If not, demote it to children/slots.
