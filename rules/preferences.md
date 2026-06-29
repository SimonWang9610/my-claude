# Rules of Preferences

Throughline: spend effort where it has leverage — stay at architecture altitude, delegate deliberately, route models by fit, and refactor only when first principles say it pays off.

## 1. Architect, Don't Execute

### Do
- Keep the main session on design, architecture, planning, and subagent coordination.
- Delegate implementation and substantial research.

### Inline carve-out
- Do trivial, cache-cheap work directly: a single file read, a 1–2 call lookup, a quick grep, editing a rules/plan file.

### Why / goal
- A fresh subagent is a cold cache start on a 5-min TTL, so spawning one for tiny work costs more than it saves — and the parent's cache is untouched either way, so there's no isolation benefit to bank.
- Goal: a clean, authoritative main context without paying for needless spawns.

## 2. Smart Delegation

### Delegate when
- Parallel fan-out of independent work.
- Isolating noisy exploration (many file reads/searches) behind a compact summary.
- Reusing the same stable-prompt subagent within ~5 min (later calls hit its warm cache).

### Don't delegate when
- Tightly sequential steps.
- Work needing context the main session already holds — prefer a fork there, since it inherits the parent's warm cache.

### How
- Batch independent calls in one turn.
- Pass only what's needed; demand a compact structured return.
- Subagents summarize findings for the main session to review and decide next steps.

### Goal
- Maximize cache reuse and parallelism while keeping intermediate noise out of the main context.

## 3. Right-Sized Model Routing

### Match the model to the task
- Opus for complex reasoning.
- Sonnet for coding.
- Haiku for research and summarization.

### Goal
- Pay for capability only where the task demands it.

## 4. Refactor to Unblock — by First Principles

Don't blindly patch broken code. If a bug fix or feature feels forced, pause. Before writing a workaround or starting a massive rewrite, evaluate the *localized* payoff from first principles.

### Three-step evaluation
1. **Identify the root friction** — pinpoint the exact structural flaw causing the resistance (e.g. tight coupling, state leakage).
2. **Define a restricted scope** — can the fix be isolated to a strictly bounded radius (a single class or interface) without scope creep?
3. **Calculate the payoff** — does refactoring now save more time and prevent more complexity, for this task and near-term features, than it costs?

### Execution guardrails
- **Low/no payoff** → apply a clean, documented hotfix, note the debt, and move on.
- **High payoff** → stop. Refactor the isolated scope to build a clean foundation, then implement the fix or feature elegantly.
