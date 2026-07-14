# tasks

```yaml
skills:
  - /spec-tasks
  - /plan-react-tasks
prompt: >
  run /spec-tasks using /plan-react-tasks to produce tasks.md + the parallel-wave plan
inputs: design.md, contracts/*
outputs: tasks.md
gate: auto
exitWhen: >
  count check holds (MODIFY/NEW units + AC → Verification rows + edge cases); every task carries its
  four fields; parallel-wave plan present; test tasks ordered before impl tasks
```
