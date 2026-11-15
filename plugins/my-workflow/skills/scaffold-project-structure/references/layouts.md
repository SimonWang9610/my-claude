# Layouts by project kind

Container names are roles; the stack's conventions rename them. Keep only what the requirements need.
`core` (domain rules and the ports adapters implement) only when rules would survive swapping every I/O
and are complex or reused, or a port is needed;
`adapters` implement ports for the outside world.

| Kind | Slices by | Containers (imports flow left to right) | Homes | Pitfalls |
|---|---|---|---|---|
| UI app | user-facing feature | app (entry, routing, wiring, data-cache client) → screens → features → entities (server data ≥2 features share) → core → shared (UI kit, helpers); adapters (transport, storage, device) | public config, session and auth, error reporting, text and design tokens, feature flags | business rules in rendering code; secrets in client config |
| Backend service | business capability | app (process entry, wiring) → transport (handlers, consumers: parse, authenticate, call one feature) → features → core → shared; adapters (database, other services, queues) | config and secrets validated at startup, error → response mapping, request logging and tracing, migrations beside the owning slice, health checks | rules in handlers; slices coupled through shared tables |
| CLI / tool | subcommand | app (parse, config, dispatch, exit) → commands → core → shared; adapters (files, processes, network, prompts) | one output writer (data to stdout, diagnostics to stderr), error → exit code in app only, config precedence flags > env > file > defaults | printing, prompting or exiting deep in logic |
| Library / SDK | public API area | public entry → internal features → core → shared; adapters for pluggable backends | public error types, versioning and deprecation, a silent-by-default named logger, config passed in by the caller | internals leaking through the public entry; side effects at import |
| Data pipeline | output dataset | app (schedules, jobs) → pipelines → transforms (pure) and schemas → shared; adapters (sources, sinks) | one schema per dataset owned by its producer, idempotent re-runs and checkpoints, data-quality checks | I/O inside transforms; reading another pipeline's intermediates |
| Middleware / plugin | hook point | registration (entry) → handlers per hook → core → shared; adapters (host APIs) | hook order, config, pass-through on failure | blocking the host's hot path; hidden order dependencies |
| Workspace | package | apps (deployables) → packages (each a library with a public entry) → tooling | cross-deployable contracts in their own package, versioning, an owner per package | a catch-all common package; deep imports across packages |

A full-stack repo is a workspace: frame each deployable on its own.

## Import rules for a new layout

Allowed imports, everything else denied:

- entry → features → core
- a feature reaches a sibling only through its public entry
- core imports no I/O or framework: ports named by purpose, adapters implement them
- adapters import core only and are wired by the composition root, never imported by features
- shared holds what ≥2 features use and no domain logic
