# Domains

A domain is what a deployable is; `scaffold-project-structure` lays each one out. A full-stack repo
is a workspace: each deployable has its own domain, and `Workspace` is only for work on the packages
and the build themselves. A schema or data migration is `Data change`,
whichever deployable holds it. None fits → the nearest, said in one line.

The concerns are examples of what usually matters in a domain, never a checklist: keep those the
work touches, add what this spec raises.

| Domain | Discipline | Typical concerns |
|---|---|---|
| UI app | front-end | screens and their state; data loading and caching; loading, empty and error states; accessibility |
| Backend service | backend | API contract and version; data owner and schema; consistency and idempotency; failure and retries; who may call it |
| CLI / tool | CLI and tooling | commands and flags; exit codes; human and machine output; config precedence |
| Library / SDK | library and API | public API and its stability; versioning and deprecation; errors; extension points |
| Data pipeline | data | each dataset's schema and owner; idempotent re-runs; late or bad data; backfill |
| Middleware / plugin | platform integration | where it hooks in; order with other hooks; behaviour when it fails; overhead budget |
| Workspace | build and release | package boundaries and owners; cross-package contracts; release order |
| Data change | database | migration steps, each shippable alone; compatibility window; rollback; backfill |
