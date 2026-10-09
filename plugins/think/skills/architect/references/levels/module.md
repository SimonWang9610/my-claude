# Module architecture — inside one unit, stack-specific

**Altitude.** One unit (package, service, screen, component tree, subsystem): its public interface,
its internal structure, its state and lifecycle, what it depends on and what depends on it, the
patterns it uses, and how it is tested. Assumes the project-level layout and layer rules.

## Settle these
1. Responsibility in one sentence; what the module explicitly does not do.
2. Public interface: the operations, their inputs and outputs, the errors they can return, the
   invariants callers may rely on.
3. State: what the module owns, its lifecycle (created, updated, disposed), concurrency rules.
4. Dependencies: what it needs injected, which boundaries it crosses, what may not depend on it.
5. Internal structure: the two or three parts inside and how they talk; what is private.
6. Failure: how it reports errors, retries, degrades; what it never does silently.
7. Tests: the unit-level contract tests, the fakes it needs, the one integration path worth covering.

## Options catalogue
- **Facade over internals** — one entry point, private parts; default for any non-trivial unit.
- **Strategy / policy objects** — a varying behaviour behind one interface; avoid for a single case.
- **State machine** — explicit states and transitions when behaviour depends on history.
- **Pipeline / middleware** — ordered stages over one payload; good for transforms and request handling.
- **Repository / gateway** — one seam per external resource; fakeable in tests.
- **Observer / stream** — many readers of one changing fact; mind subscription lifecycle.
- **Command / intent-named actions** — mutations named by intent, not by field; keeps callers honest.

## Stack-specific considerations (read the stack card when one exists)
Value vs reference semantics and immutability idioms · the framework's component or widget lifecycle ·
async and cancellation idiom · how dependencies are injected in this stack · typed errors vs exceptions
· serialization and schema evolution · the test framework's fakes and fixtures.

## Pitfalls
Interface exposes internals · state with two owners or no disposal · dependencies on siblings instead of
the seam · a pattern used because it is known, not because the variation exists · error paths untested
· a module that mirrors another's data instead of deriving it.

## Evaluate — binary checks
- Responsibility fits one sentence and the interface matches it.
- Every public operation documents inputs, outputs, errors, and invariants.
- State ownership and lifecycle are explicit; no leaked subscriptions or timers.
- Dependencies arrive through the seam the project level defines; nothing reaches around it.
- Each pattern present answers a real variation in the requirements.
- Contract tests exist for the interface; the error paths are among them.
- Nothing outside the module depends on its private parts.

## Output template
```
<module diagram: the unit's boundary, its public operations, internal parts, dependencies in/out>
```
**Responsibility** · **Interface** (operations, errors, invariants) · **State and lifecycle** ·
**Dependencies** · **Internal structure** · **Tests** · **What exists** (fit) · **Practices and
pitfalls** · **Recommendation** — pick, why, what would change it · **You decide** (≤3, defaults) · **Next**
