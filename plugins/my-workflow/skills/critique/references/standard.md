# Quality standard

Pick at most 5 axes: correctness always; each other axis only where "Applies when" holds for the
target (its kind in `shared/kinds.md`, the spec's limits, what the change touches). Each check is
binary; a failed check is a finding only once reproduced. Evidence: run (a command or test), grep or
read.

| Axis | Applies when | Checks | Evidence |
|---|---|---|---|
| Correctness | always | every `R` done; each changed branch has a test that fails without the change | run |
| Reliability | I/O, concurrency or external calls | each failure path handled or surfaced; retries bounded and safe to repeat; no swallowed error | read, run |
| Security | input crosses a trust boundary; auth; secrets | input validated at the boundary; permission checked on every path to the sink; no secret in code, logs or client | read, grep |
| Performance | a limit names latency, size or throughput; a hot path | no per-item I/O inside a loop; work bounded by input size; the spec's number measured | run, read |
| Maintainability | code | follows the exemplar's pattern; one owner per fact; no duplicated logic or dead code added; every changed line traces to a task or requirement; no unrequested option, single-use abstraction or handling for impossible states | grep, read |
| Scalability | a growth axis named in the limits or design | state lives outside the process where instances scale; no unbounded in-memory collection | read |
| Operability | services, jobs, deployables | failures logged with context; health or exit status reflects failure; config checked at start | read, run |
| Compatibility | a public API, schema, file format or flag changes | existing callers and data still work; a breaking change is versioned or migrated | run, grep |
| Testability | new units | dependencies replaceable at seams; tests run without network or the real home folder | read, run |
