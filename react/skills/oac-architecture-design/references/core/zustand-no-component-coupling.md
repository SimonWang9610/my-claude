---
title: Stores Must Not Know About UI
impact: HIGH
impactDescription: UI-aware stores can't be reused or tested in isolation
tags: zustand, coupling, layering
---

## Stores Must Not Know About UI

Stores expose domain state and domain operations. They must not import components, hold refs to DOM/MUI elements, manage toast/snackbar display, or name things after screens ("settingsPageDraft"). UI concerns invert the dependency direction and make the store untestable without rendering.

**Incorrect:**

```tsx
const useCameraStore = create<{
  videoElementRefs: Map<string, HTMLVideoElement>   // DOM in store
  showErrorSnackbar: boolean                        // UI presentation state
}>()((set) => ({
  videoElementRefs: new Map(),
  showErrorSnackbar: false,
  ...
}))
```

**Correct:**

```tsx
// Store: domain facts only
const usePlaybackStore = create<PlaybackState>()((set) => ({
  streamErrors: {} as Record<string, StreamError>,
  reportError: (id: string, error: StreamError) =>
    set((s) => ({ streamErrors: { ...s.streamErrors, [id]: error } })),
}))

// UI layer decides presentation: a component/hook watches streamErrors
// and renders a Snackbar. DOM/video element refs live in the component
// or a service module (see layer-service-isolation), not in the store.
```

Litmus test: the store file should compile and be unit-testable with zero imports from `react`, `react-dom`, or any component/UI library.
