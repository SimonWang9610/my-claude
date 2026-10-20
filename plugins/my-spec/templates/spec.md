# Spec

Fast track: the `SPEC` header, `track`/`route`, `goal`, `must`, `done`, `verify` and any `D` line,
shown inline. Full track: every line that applies; omit empty ones.

```text
SPEC · <code | doc | plan | report | research> · <title>
track   fast | full     route   build | write | decide → build | decide → write | critique
gates   ask | auto      review  on | off
goal    <the outcome in one sentence; non-code: what the reader can do or decide after reading>
reader  <non-code: who, what they know, what they will do with it>
context <stack and versions (stated | detected) · paths to read or reuse · facts found · prior decisions>
decide  D1 <decision> — <why>
must    R1 <observable behaviour, or content the deliverable must contain>
limits  <hard numbers, compatibility, "never" items; non-code: length, tone, format>
skip    <out of scope>
done    <named tests green · command exits 0 · what a reader can do>
verify  <exact commands, one per line; non-code: the done checklist>
save    <task folder; non-code: also where the deliverable goes>
open    Q1 <question> — default: <answer>
```
