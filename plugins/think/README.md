# think — a gated workflow for working with AI agents

For Claude Code and GitHub Copilot. Stack-neutral and project-neutral. Every stage ends by asking you
critical questions or asking to continue; nothing advances without your permission unless the spec says
`gates: auto`. Intermediate output stays in the conversation; files are written only when you ask.

```
 /prompt <raw request> ──► SPEC (code or non-code template, inline)
            │
            ├──► /design   optional: options, or architecture (product · project · module), evaluate
            │
            ├──► /build    code: plan → execute → verify → review (optional)
            └──► /write    non-code: outline → draft → check → review (optional)

 /explore   companion for every stage: facts from the codebase, existing docs, or online sources
```

## Skills

Start with `prompt`. After that, the spec in the conversation is the input of every later stage, so
`design`, `build`, and `write` need no argument; add one only for extra requirements, which are folded
into the spec (`/think:build must use pnpm; no schema migration`).

| Skill | Claude Code | Copilot | Does |
|---|---|---|---|
| prompt | `/think:prompt <request>` | `/prompt <request>` | Classifies code vs non-code, explores before asking, asks ≤3 critical questions per round, returns a compact spec ([code](skills/prompt/templates/code.md), [non-code](skills/prompt/templates/non-code.md)) that replaces the raw request. |
| design | `/think:design [requirements]` | `/design [requirements]` | Optional. Options with pros, cons, and a recommendation; architecture at the level(s) the task spans with diagrams, rationale, trade-offs; or an evaluation with a verdict. Researches only when asked or needed. Also takes a standalone question when there is no spec. |
| build | `/think:build [requirements]` | `/build [requirements]` | Code: ordered subtasks, execution (or hand-off to a project's own driver), roadblock and change handling, verification against `done`, review when `review: on`. |
| write | `/think:write [requirements]` | `/write [requirements]` | Non-code: outline mapped to the spec, draft, checklist check, review when `review: on`. |
| explore | `/think:explore <question>` | `/explore <question>` | Companion: bounded facts from code (map, mechanism, onboarding, locate), docs, or the web, with anchors or dated sources. |

## Agents

| Agent | Use it when | How |
|---|---|---|
| `builder` | You want a whole coding task driven for you: spec, optional design, build, optional review, with a gate after every stage. | Claude Code CLI: `claude --agent think:builder "add rate limiting to the upload API"` starts a session with builder in charge. Copilot: pick **builder** in the Chat agent dropdown, then type the task. |
| `writer` | The same for a document, plan, report, decision record, or research write-up. | `claude --agent think:writer "<task>"`, or pick **writer** in the Copilot agent dropdown. |
| `explorer` | A question needs wide reading across code, docs, or the web and would flood your session. | Spawned by the `explore` skill on large questions. By hand: "use the explorer agent to map how payments flow through `src/billing`". |
| `reviewer` | You want a fresh-eyes check of a finished result against its spec. | Set `review: on` in the spec, or say "review it" at the last gate. By hand: "use the reviewer agent on the current diff against the spec above". |

`builder` and `writer` gate with you only when they are the session's agent (the CLI flag or the Copilot
dropdown). Asked for inside an ordinary Claude Code session, including the VS Code extension, they run
as subagents: each stops at its next gate and hands back the stage output, and the main session asks
you. Running the skills directly (`/think:prompt`, then `/think:build`) gives the same flow without a
driver.

## Skill declarations

Every agent names the skills it uses twice: a `skills:` frontmatter list, which Claude Code preloads into
the agent, and a numbered "Skills" section naming each one in both forms (Claude Code `think:<name>`,
Copilot `/<name>`), which is what Copilot follows. Each skill opens with a `Uses:` line naming the skills
and agents it calls, in the same two forms.

## Working preferences

The preferences that shape every interaction (decide small things, discuss before building on open
questions, diagram-first proposals with one recommendation, at most three questions with defaults, a
gate after every stage, one pushback then your call, no files unless asked) are written into the
`builder` and `writer` agents; the gate and question rules are also in every skill, so running a skill
directly behaves the same. Change them by editing the agent files.

## Install

From a clone of the repo, with the root `setup.py` (it asks which tools and which plugins), or directly:

```
python3 setup.py install --tools claude --plugins think
python3 setup.py install --tools copilot --plugins think
python3 setup.py install --tools claude,copilot --plugins think
```

Claude Code uses the `claude plugin` CLI when it is installed; without it (VS Code extension only), the
installer symlinks `~/.claude/skills/think` to the plugin, which loads as `think@skills-dir`. Inside the
extension you can also type `/plugins`, add the marketplace `SimonWang9610/my-claude`, and install
`think`. For Copilot, the skills are linked into `~/.copilot/skills/`, the agents into
`~/.claude/agents/`, and the routing hint into `~/.copilot/hooks/think.json`; no instructions file is
installed or modified. Everything is a symlink into the clone, so `git pull` updates in place.
`python3 setup.py uninstall --plugins think` removes it. Use one install path per host, or the plugin loads twice.

Copilot has one skill namespace: when `my-react` or `my-flutter` is installed for Copilot too, their
`design` skill and this one share a name, so each is installed with its plugin prefix and this one
becomes `/think-design`.

## Notes

- The prompt hook adds one routing hint for short task requests, design questions, and fact-finding
  questions; silent otherwise, never blocking; needs `python3`.
- Optional stack cards for design: `skills/design/references/stacks/<stack>.md` from the template.
