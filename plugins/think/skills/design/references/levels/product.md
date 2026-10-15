# Product architecture — language-agnostic

**Altitude.** Which systems exist, what each is responsible for, where the boundaries are, who owns
which data, how systems communicate, what is built versus bought, how it runs and scales. Never a
framework, library, or language choice: those are project decisions.

## Settle these
1. Who uses it, from where, with what tolerance for latency and offline (users, devices, geographies).
2. The domains and the one system that owns each fact (a fact with two writers is a design error).
3. Boundaries: which calls cross a network, which are in-process; what is synchronous, what is eventual.
4. Data: sources of truth, replicas and caches, retention, privacy and residency, migration of existing data.
5. Build vs buy for auth, payments, messaging, search, analytics, media, hosting.
6. Run: deployment units, environments, scaling axis (users, data, tenants), failure modes that are acceptable.
7. Non-negotiables: budget, team size and skills, deadline, compliance, platforms that must be supported.

## Options catalogue (when each fits)
- **Monolith with modular boundaries** — one team, one deployable, unclear domains yet; split later along proven seams.
- **Client-server with a thin client** — logic and data on the server; clients render and cache; simplest consistency.
- **Thick client with sync** — offline or latency-critical UX; needs a conflict strategy and a sync protocol.
- **Backend-for-frontend** — several client types with different needs; one API shape per client.
- **Services split by domain** — independent teams or scaling axes; pays only with ownership clarity and tooling.
- **Event-driven integration** — producers must not know consumers; audit trails; accepts eventual consistency.
- **Serverless or edge functions** — spiky load, small units, little state; watch cold starts and vendor coupling.
- **Local-first** — user owns data, runs anywhere; sync is the hard part.

## Pitfalls
Distributed before domains are clear · two writers for one fact · a boundary with no owner · consistency
promised that the topology cannot keep · buying what defines the product, building what does not ·
scaling axis never named · migration of existing data left for later.

## Evaluate — binary checks
- Every fact has exactly one owning system.
- Every boundary names its protocol, its consistency, and its failure behaviour.
- Scaling axis and expected load are stated with numbers.
- Build-vs-buy is decided for each commodity capability, with the reason.
- Deployment units and environments are drawn; one person could operate it.
- The migration or coexistence path from what exists today is stated.
- Non-negotiables (budget, team, platforms, compliance) are honoured, not assumed away.

## Output template
```
<system diagram: boxes = systems, labelled edges = protocol + sync/async, data owners marked>
```
**Responsibilities** — one line per system · **Data ownership** — fact → owner · **Boundaries** —
protocol, consistency, failure · **What exists** (fit) · **Practices and pitfalls** · **Recommendation** —
pick, why (2–3 lines), what would change it · **You decide** (≤3, defaults) · **Next**
