## Rules of Preferences

- When start coding/implementing, ALWAYS delegate to subagents (using Sonnet unless users specify otherwise) to write code
- When researching/finding information, ALWAYS delegate to subagents (using cheap and fast models unless users specify otherwise) to find information, and summarize it for the main session to review and decide on next steps
- The main session should focus on high-level design, architecture, planning, and coordination of subagents, rather than writing code directly
- if you are under a worktree/feature branch for a spec, working under the worktree/branch is mandatory; if you find yourself outside of it, stop and sort that out before writing anything or running any stage
