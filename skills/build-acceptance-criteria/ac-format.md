# Acceptance-criterion format — IDs and EARS

## 1. EARS functional requirements

Write system-level requirements in EARS (Easy Approach to Requirements Syntax). EARS stays
alongside the per-story ACs; it does not replace them.

Patterns:
- **Ubiquitous:** "The system shall [action]"
- **Event-driven:** "When [event], the system shall [action]"
- **State-driven:** "While [state], the system shall [action]"
- **Optional:** "Where [condition], the system shall [action]"
- **Unwanted:** "If [unwanted condition], then the system shall [action]"

## 2. ID format
- **Story**: `US-<n>` — e.g. `US-1`, `US-2`. Story number = order in document.
- **Story ACs:** `AC-<story#>.<n>` — e.g. `AC-1.1`, `AC-2.3`. Story number = order in document; criterion number = sequential within that story.
- **Non-functional requirements:** `NFR-<n>` — e.g. `NFR-1`, `NFR-2`.

Rules:
- IDs must be **UNIQUE** within a requirements document.
- IDs are **STABLE** once written — append new IDs; never renumber. Renumbering silently breaks every test name referencing the old ID.
- Every story must have **≥1** AC. Every NFR must carry an ID.
