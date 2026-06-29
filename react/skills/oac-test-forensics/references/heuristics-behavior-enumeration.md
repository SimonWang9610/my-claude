# Behavior enumeration (Pass 1 input)

Grep/read recipes for Pass 1. Targets React 19 + Vitest + RTL + Zustand + TanStack Query v5. Grep commands narrow where to read — confirm every hit by reading the file.

Examples use a neutral "list + detail" feature (`DeviceListPage`, `useDevices`, `DeviceRecord`); substitute your own surfaces.

---

## Behavior enumeration (Pass 1 input)

**Component** — open the file and enumerate:

```bash
# render branches: ternaries, && guards, early returns
grep -nE '\?|&&|return null|return <' <Component>.tsx | grep -vE '//'
# exposed handlers
grep -nE 'on[A-Z]\w+\s*[:=]' <Component>.tsx
```

**Hook** — side-effects and public surface:

```bash
grep -nE 'useEffect|useQuery|useMutation|useInfiniteQuery|subscribe|\.on\(' <hook>.ts
grep -nE 'return \{|return \[' <hook>.ts
```

**api / lib** — exported contracts and error paths:

```bash
grep -nE 'export (async )?function|export const \w+ = (async )?\(' <file>.ts
grep -nE 'catch|throw|assertOk|return (null|undefined|\{)' <file>.ts
```

A behavior that appears here with no criterion ID (`AC-<story>.<n>` / `NFR-<n>`) in `requirements.md` is
a `no-spec-coverage` (improvised) finding.
