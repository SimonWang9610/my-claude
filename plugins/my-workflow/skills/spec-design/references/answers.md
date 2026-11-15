# What a design must answer

Per project kind; a full-stack repo is a workspace, so answer for each deployable on its own.

| Kind | The design answers |
|---|---|
| UI app | screens and their state; data loading and caching; loading, empty and error states; accessibility |
| Backend service | API contract and version; data owner and schema; consistency and idempotency; failure and retries; who may call it |
| CLI / tool | commands and flags; exit codes; human and machine output; config precedence |
| Library / SDK | public API and its stability; versioning and deprecation; errors; extension points |
| Data pipeline | each dataset's schema and owner; idempotent re-runs; late or bad data; backfill |
| Middleware / plugin | where it hooks in; order with other hooks; behaviour when it fails; overhead budget |
| Workspace | package boundaries and owners; cross-package contracts; release order |
| Any data change | migration steps, each shippable alone; compatibility window; rollback; backfill |
