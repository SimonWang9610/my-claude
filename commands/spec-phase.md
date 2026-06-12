# spec:phase

Orchestrate the decomposition of a specflow design and tasks into actionable phases.

Given requirements, design and tasks from `.specflow/specs/<name>/`:
1. Read through the requirements, design, and tasks to understand the overall scope and objectives.
2. Decompose the requirements, design, and tasks into distinct phases based on logical groupings, dependencies, and milestones. Each phase must have a clear goal and verifiable deliverables.
3. For each phase, define the subagents as explicit `(WorkAgent, TestAgent)` groups. Every WorkAgent MUST be paired with exactly one TestAgent — no WorkAgent may exist without a paired TestAgent. Assign agents based on the expertise each phase requires.
4. Create a high-level plan that outlines the sequence of phases and the coordination between groups.

## Agent Roles & Coordination
- Each phase declares `Subagents: [(WorkAgent, TestAgent), ...]`. The pairing is mandatory and one-to-one.
- **WorkAgent** is responsible for *implementation only*. It does not write or run tests.
- **TestAgent** is responsible for *writing and running tests* against its paired WorkAgent's implementation.
- Coordination loop per group:
  1. WorkAgent implements until its Handoff Criteria are met, then hands off the changed surfaces to its TestAgent.
  2. TestAgent writes tests covering the implemented behavior, runs them, and reports results.
  3. On failure, the TestAgent hands findings back to the WorkAgent; repeat until tests pass and the Pass Criteria are met.
  4. A group is "Completed" only when its tests are green and Pass Criteria are met.
- A phase advances only when all groups in it are "Completed".

Write output to `.specflow/specs/<name>/phases.md`, following the structure in the Phase Example below. This file serves as the roadmap for `/implement`, guiding task execution and agent coordination.

## Phase Example
- Phase Name
- Phase Goal
- Tasks
- Status (Not Started / In Progress / Partially Completed / Completed)
- Subagents: [(WorkAgent, TestAgent), ...]
  - Group 1
    - WorkAgent
      - Name
      - Model
      - Responsibilities (implementation scope only)
      - Implementation Surfaces (files/modules this agent owns)
      - Handoff Criteria (what must be true before handing to the TestAgent)
      - References (design sections, steering files, migration references if found under `.specflow/specs/<name>/references/`)
    - TestAgent
      - Name
      - Model
      - TargetAgent: the paired WorkAgent
      - Test Scope (unit / widget / integration; behaviors and edge cases to cover)
      - Pass Criteria (tests written, all passing, coverage/acceptance bar met)
      - Handoff Criteria (back to WorkAgent on failure; to next phase on pass)
      - References (design sections, steering files, migration references if found under `.specflow/specs/<name>/references/`)
  - Group 2
    - ...
- Dependencies
- Files to be generated/modified
- Phase Exit Criteria (all groups Completed, tests green)
- Handoff Criteria to next phase