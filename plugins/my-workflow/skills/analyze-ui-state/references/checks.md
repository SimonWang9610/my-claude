# UI state checks

Each must hold before the section is written.

- server data has one home, the cache; no copies outside a draft
- shareable or back/forward state is in the URL and nowhere else
- no two booleans with an impossible combination; one status instead
- each async command runs idle → running → done or error, with stale-response and double-submit guards
  (and cancel for reads)
- each write names its policy (wait for the server · optimistic with rollback · queued offline), what
  it refreshes, and how two in-flight writes to one entity are ordered
- sign-out clears every user-scoped unit and cache entry
- each data region has loading, empty and error states
