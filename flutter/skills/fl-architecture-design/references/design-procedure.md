# Design procedure

Step-by-step checklist for authoring `design.md` and `contracts/` against the Flutter specflow
architecture rules. Work through every step in order. All paths are relative to this `references/` directory.

---

## Step 1 — Map the feature into the four layers

Read `core/layering-and-structure.md`. List every unit with its layer (UI / Provider / Data / Service),
role suffix (`*Screen`, `*Widget`, `*Notifier`, `*Repository`, `*ApiClient`, etc.), and domain models
(`*Model`) vs DTOs (`*Dto`) — both under `models/`. Verify dependency arrows point only downward;
redesign any unit that skips or reverses a layer before proceeding.

---

## Step 2 — Choose the state-ownership tier

Read `core/state-ownership-decision.md` and `core/state-placement.md`. For each piece of state:
- **Tier 1 (local setState)** — one widget only, never shared, dies with the widget.
- **Tier 2 (InheritedWidget scope)** — read by a subtree on one page, no navigation crossing.
- **Tier 3 (provider)** — crosses pages, survives navigation, or is app-wide.

Do not lift state beyond its narrowest tier. One owner per fact — derive the rest, never duplicate.
Record each decision in `design.md`.

---

## Step 3 — Design the data path

Read `core/service-isolation.md`, `core/repository-ssot.md`, and `core/domain-models-immutable.md`.

- **Service** — stateless, returns raw DTOs or `Stream<RawPayload>` only, maps transport errors at boundary.
- **Repository** — one per domain type = SSOT; converts `*Dto → domain model` via `dto.toDomain()`; owns caching/retry/throttle; no raw DTOs escape this layer.
- **Domain models** — all fields `final`, `const` constructors, pure Dart, value equality (`Equatable`, `@freezed`, or manual `==`/`hashCode`); typed business values (no raw wire strings or ISO timestamps as `String`); use Dart 3 records for small immutable bundles and `copyWith` for updates.

---

## Step 4 — Design each holder and widget

Read `core/state-flow-and-async.md`, `core/state-boundary-and-lifecycle.md`, `core/dependency-injection.md`,
and `core/widget-composition.md`.

- **Holders** — expose state as a Dart 3 `sealed class` union (`loading | data | error`) consumed with exhaustive `switch` expressions (not `if (x is T)` chains); receive repos via constructor injection (or Riverpod `@riverpod` code-gen with `Notifier`/`AsyncNotifier` and a `build()` method); expose named commands. Call `ref.onDispose()` in `build()` to cancel subscriptions and controllers (Riverpod); for package-agnostic holders dispose every subscription/controller in `dispose()`.
- **Widgets** — compose small named `const StatelessWidget` classes (not `Widget _buildX()` helpers); `build()` is a pure function (no IO, no sorting, no derivation); design for injection of fakes via constructor.

For widget build idioms (const discipline, BuildContext async safety, theming tokens) and performance
rules, load the **`fl-implementation`** skill at the implement stage.

---

## Step 5 — Plan the testability seam per unit (P8)

Read `core/testability-seam.md`. For **every** unit from Step 1, state explicitly how it will be
exercised in isolation: widget → `pumpWidget` with injected fake holder; holder/repo/service →
`dart test` with constructor-injected fakes; domain model → instantiated directly.

A unit with no seam — testable only by mocking its parent, reaching a singleton, or because logic
lives in `build()` — is a **design defect**. Fix it here: add an abstract interface at the boundary
and switch to constructor injection. Record the seam statement in each `contracts/<unit>.md`.

---

## Step 6 — Shared-widget plan

For every shared widget from `lib/core/` or another feature referenced by this feature, classify it
as **Reuse** (use as-is, zero changes) or **Copy** (copy into this feature's `widgets/` and
adapt). Never modify an adopted shared widget. Record classification in `design.md → ## Shared Widget Plan`.

---

## Step 7 — Companion skills

- If the project uses Riverpod, the **`fl-riverpod`** skill carries the package idioms — load it alongside this skill. Package idioms apply behind the provider seam; four-layer structure and testability requirements are unchanged.
- At the implement stage, load **`fl-implementation`** for widget build idioms, performance rules, and theming.

---

## Step 8 — Record and verify

Write `design.md` (layer map, state-ownership decisions, data-path description, widget/holder notes,
Shared Widget Plan, blank `## Architecture Gate — Justifications` section). Write `contracts/<unit>.md`
for every unit (kind/layer, public API, data shapes, AC-IDs traced to this unit, testability seam,
direct dependencies). Then run the **Verify step (§4)** of this skill at phase exit — follow
`gate-procedure.md` to check the three blocking triggers and write PASS or record an extraction plan
/ justification.

---

This skill is the **proactive design pass** — build the structure against the rules before any code is
written — and the **lightweight verification pass** at phase exit. Same rules, one skill, two moments.
