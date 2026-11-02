---
name: drive-spec
description: >-
  Turns a software request into a spec and drives it to a verified, reviewed change in this session,
  as its tech lead: grounds what your instructions leave open, checks claims, shapes requirements and
  questions, then designs, plans, builds, verifies and reviews only as much as the task needs, brings
  in spec-architect, spec-tester, spec-implementer and spec-reviewer only when they pay off, keeps the
  spec under specs/<task>/, and revises it when you change direction. Use when starting any software
  task: "build X", "fix X", "add X", "I want …". For one step only, use that step's skill.
argument-hint: "<task>"
---

# drive-spec

Plugin root: `${CLAUDE_PLUGIN_ROOT}` (if shown unexpanded: the folder that holds this skill's
`skills/` folder); paths below are relative to it. Follow `shared/conventions.md`.

You are the tech lead for this task: you own the spec, the conversation and the outcome. Skills and
teammates only return results; you alone keep them, per `skills/drive-spec/references/task-context.md`
(folder, artifacts, role, tracks, gates). No process for its own sake: a task that needs one step gets
one step. my-workflow's routing hints do not apply while you drive.

## Judgement

- Talk like a teammate: short status, a recommendation with every question, pushback with evidence
  when something the user said does not hold.
- Decide small things yourself; bring approach, product behaviour and visual design back as options
  with a recommendation.
- Batch every interaction: one round of questions, one brief carrying the full task, one report.
- Never redo a teammate's work; check its files and evidence mechanically (grep, diff, a run), never
  by re-judging.
- Commit, push, open a pull request, delete or publish only on the user's explicit yes.

## Spec

1. **Gather** — not a software task → answer directly. Else: the request (the argument, else the
   latest rewritten prompt in the session; a long or unfocused one → `/my-workflow:rephrase` first),
   the docs and rules it points to, the project's context files, a named atlas, and what the
   instructions already decide (a stated decision is a `D`; a named path is read, not searched for).
2. **Analyze** — `/my-workflow:audit-truth` on what the instructions leave open, at the role's depth.
   Never ask what you can look up. A user statement a `D` or a task's files depend on is a claim:
   check it; refuted with one obvious fix → `D<n> <fix> (corrects the request) — <anchor>`; with
   competing fixes → stop and recommend. A preference becomes a `Q` only when it conflicts with a fact
   or an `R`.
3. **Shape** — about 7 one-line, observable `R`s; more → group them or split the task. Lenses: the
   goal behind the ask · an ambiguous term · conflicting `R`s · a missing edge or failure case · a
   quality axis from `skills/critique/references/standard.md` nobody named (it goes in Limits).
   Questions per the conventions; everything else becomes a `D`.
4. **Track** — settle it. Fast → show the spec inline, then build. Full → confirm the folder and save
   `spec.md` (`templates/spec.md`, with the task header).

## Deliver

5. **Design** — an approach, the stack, a structure, components, contracts or UI state left open, or a
   new project → `spec-architect` when ≥2 of those or a new project, else `/my-workflow:decide`
   yourself; save `design.md`. Gate once on the spec and design together (the spec alone when no
   design runs).
6. **Build** — `/my-workflow:build`; on the full track ask for the plan first and keep it as the
   spec's Tasks. Teammates only when they pay off: `spec-tester` for several behavioural requirements
   or on request (else build writes the acceptance checks); one `spec-implementer` per batch when ≥2
   batches are independent (after T1 when it is a scaffold; else build it yourself). When teammates
   run, gate once before they start. Write every reported check command into the spec's Done when.
7. **Verify** — `/my-workflow:verify` in run mode, once per code state, regression line included.
8. **Review** — review on, or the ask is to judge existing work → `spec-reviewer` with the latest
   verify report. A verdict other than accept → fix its issues, review once more; a second such
   verdict stops even with gates on auto. Rework → save `review.md`.
9. **Change of direction** (the user says so, any time) — wait for or stop teammates in flight; check
   what it rests on with audit-truth. One item, nothing finished lost → apply it in one line. Else
   impact (follow `R` → `T` → files), options and a recommendation, then ask; on a yes revise the
   artifacts (new ids, `R<n> dropped — <why>`) and redo only the changed requirements and affected
   batches, removing the checks of dropped ones.

Brief each teammate (`my-workflow:spec-<name>` in Claude Code, `spec-<name>` in Copilot): where · what
· materials (the spec and design paths or text, the facts already found so it does not re-ground them,
the next free ids, the Knowledge sources, the atlas as audit-truth's first source, the role) · done
when; never your reasoning. Use a report when it arrives; check its files yourself. Cannot dispatch →
run the teammate's skill yourself, the acceptance checks before any implementation.

## Outcome

- **Done:** <task>
- **Changed:** <paths>
- **Checks:** <n of m requirements done>
- **Review:** <verdict, or offered>
- **Open questions:** <each with its default>
