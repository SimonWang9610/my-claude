# External sources

Cite these URLs when justifying a finding; paraphrase, never paste substantial text.

## Pass 2 / Pass 3 — outcome over implementation; tests that pass when the app is broken

- Kent C. Dodds — Testing Implementation Details: https://kentcdodds.com/blog/testing-implementation-details
- Kent C. Dodds — Introducing the react-testing-library: https://kentcdodds.com/blog/introducing-the-react-testing-library
- Testing Library — Guiding Principles: https://testing-library.com/docs/guiding-principles/

## Pass 1 — requirement→test traceability

- Cucumber — Better requirements by harnessing the power of examples (Example Mapping; criterion→test link with no overhead): https://cucumber.io/blog/bdd/better-requirements-by-harnessing-the-power-of-exa/
- Vitest — Test Tags (embed criterion IDs; makes an uncovered clause a runnable query): https://vitest.dev/guide/test-tags

## Pass 3 Form 2/3 — mock-shape drift / production-shaped fixtures

- MSW — Using with TypeScript (generics derived from production types; drift becomes a compile error): https://mswjs.io/docs/best-practices/typescript/
- Artem Zakharchenko — Type-safe API mocking with MSW and TypeScript (`satisfies`-typed fixtures): https://dev.to/kettanaito/type-safe-api-mocking-with-mock-service-worker-and-typescript-21bf

## Pass 3 Form 5 — query-config never exercised

- TanStack Query — Does this replace Redux/MobX/Zustand? (server state and config live on the cache, not a mocked hook): https://tanstack.com/query/v5/docs/framework/react/guides/does-this-replace-client-state
- TkDodo — Practical React Query (copying query data into local state opts out of background updates): https://tkdodo.eu/blog/practical-react-query

## Local-evidence notes

- **Form 4 (CSS-class instead of resolved value):** no canonical external source for this JSDOM
  limitation — mark as local-evidence-driven and confirm in the target project's setup before blocking.
- **Mutation-test protocol and on-sight signal catalogue:** general engineering practices distilled into
  React/TS form; not single-source citations.
