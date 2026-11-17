# <group> — <what these units do together>

<!-- design/<group>.md. A group = units that work together (a slice, a layer, a deployable): at most
6 nodes in its diagram, the outside units it touches included. Phrases, one line each; omit a
section that does not apply. -->

## Dependencies

Only when design.md draws groups: this group's units and the outside units they touch.

```mermaid
flowchart LR
  UNIT_2["UNIT-2 <name>"] -->|"<what crosses>"| UNIT_1["UNIT-1 <name>"]
  UNIT_1 -->|"<what crosses>"| UNIT_3["UNIT-3 <name>"]
```

## UNIT-<n> <name>

### Boundary

- <what it never does or exposes>
- <error · empty · race> → <result>

### Interface

New or changed surface only.

```text
<signatures only, in the project's language>
```

### Inside

Only when a builder could not guess it: state it owns, an async path, units inside it.

| Id | Unit | Anchor | Responsibility |
|---|---|---|---|
| UNIT-<n>.1 | <name> | `path:symbol` | <what it solely owns> |
