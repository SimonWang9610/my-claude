# tasks

```yaml
skills:
  - /sf-tasks
  - /plan-react-tasks
prompt: >
  run /sf-tasks using /plan-react-tasks to produce tasks.md + the parallel-wave plan — transcribe
  from the design (dependencies from the unit index, test plan from AC → Verification), never
  re-derive
inputs: design.md, contracts/*
outputs: tasks.md
gate: auto
exitWhen: >
  count check holds (MODIFY/NEW units + AC → Verification rows + edge cases); every task carries its
  four fields; parallel-wave plan present; test tasks ordered before impl tasks
```
