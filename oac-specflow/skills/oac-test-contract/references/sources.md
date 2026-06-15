# test-contract — external sources

Cite as links when justifying a rule; paraphrase, never paste substantial text.

## Rule 1 — Clause→test mapping

- Cucumber — Example Mapping (requirement→test traceability):
  https://cucumber.io/blog/bdd/better-requirements-by-harnessing-the-power-of-exa/
- Semaphore CI — BDD and Acceptance Testing (Given/When/Then maps ACs to test descriptions):
  https://semaphore.io/blog/bdd-acceptance-testing
- Vitest — Test Tags (label tests with an ID, filter with `--tag`):
  https://vitest.dev/guide/test-tags

## Rule 2 — Outcome, not implementation

- Testing Library — Guiding Principles (query by role/label/text, not internals):
  https://testing-library.com/docs/guiding-principles/
- Kent C. Dodds — Testing Implementation Details (tests that pass when the app is broken):
  https://kentcdodds.com/blog/testing-implementation-details
- Kent C. Dodds — Introducing react-testing-library (design intent: accessing internals is deliberately hard):
  https://kentcdodds.com/blog/introducing-the-react-testing-library

## Rule 3 — Production-shaped fixtures

- MSW — Introduction (network-level interception; single source of truth for mocks):
  https://mswjs.io/docs/
- MSW — Using with TypeScript (`http.get<Params, RequestBody, ResponseBody>` generics):
  https://mswjs.io/docs/best-practices/typescript/
- Artem Zakharchenko — Type-safe API mocking with MSW and TypeScript (`satisfies`-typed fixtures):
  https://dev.to/kettanaito/type-safe-api-mocking-with-mock-service-worker-and-typescript-21bf
- isqua.ru — Scalable mocking architecture with MSW and TypeScript (per-endpoint ownership):
  https://isqua.ru/blog/2025/05/17/scalable-mocking-architecture/

## Rule 4 — No tautologies / no arrange-act-no-assert

- Kent C. Dodds — Testing Implementation Details (the false-positive failure mode):
  https://kentcdodds.com/blog/testing-implementation-details

## Rule 5 — Real QueryClient for query-config NFRs

- TanStack Query — Does this replace Redux/Zustand? (server state and cache config live on the client, not a mocked hook):
  https://tanstack.com/query/v4/docs/framework/react/guides/does-this-replace-client-state
- TkDodo — Practical React Query (copying query data opts out of background updates):
  https://tkdodo.eu/blog/practical-react-query

## Rule 6 — One-shot greps become enduring CI guards

- Vitest — general assertions (a checked-in Vitest glob assertion is the resident form of a one-shot grep):
  https://vitest.dev/guide/test-tags
