# think

How this user likes to work with agents, and which think skill fits which moment. Preferences, not
rules: project instructions and system prompts take precedence where they differ.

## Working preferences

- Decide small things alone; bring architecture, product behaviour, and physical or visual design
  back with options.
- On a new project, an architecture question, or a vague or open-ended request, discuss before building.
- A proposal: what already exists, good practices and pitfalls, one recommendation with the reason;
  diagram first, then bullets; a brief why with each recommendation.
- Questions: few per turn, each with the default you will assume, so "go" is a complete answer.
- A choice against a stated constraint or a known good practice earns one pushback with evidence;
  then the user's call stands, recorded as the user's decision.
- Blind spots worth asking about early: hard constraints, what already exists, what "done" means, how
  big the work is.
- Short prompts and typos are normal; read through them.

## Skills

- `clarify <request>` — a vague task, requirement, goal, or idea: questions with defaults, candidate
  solutions, a decision, a brief.
- `explore <question>` — understand a codebase at the altitude the question needs.
- `architect <question>` — design, discuss, or evaluate architecture at the level(s) the question
  spans.

(Claude Code: `/think:clarify`, `/think:explore`, `/think:architect`. GitHub Copilot: `/clarify`,
`/explore`, `/architect`.)

## Habits

- Feedback on output is easiest to act on as Observed · Expected · Where · Priority (plus Repro for a
  defect); a mixed list is split first, questions answered before anything is built on them.
- Pausing work (usage limit, break): write `CHECKPOINT.md` with goal, done, in progress, in-flight work,
  next step, how to verify; resuming starts by reading it.
- Briefs and decision records use the forms in the clarify skill (`skills/clarify/forms/`).
