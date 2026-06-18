## Rules of Preferences

- When start coding/implementing, ALWAYS delegate to subagents (using Sonnet unless users specify otherwise) to write code
- When researching/finding information, ALWAYS delegate to subagents (using cheap and fast models unless users specify otherwise) to find information, and summarize it for the main session to review and decide on next steps
- The main session should focus on high-level design, architecture, planning, and coordination of subagents, rather than writing code directly
- ONLY run tests on what you changes DURING implementations
- ONLY one full testsuite running one time; MUST NOT run multiple same testsuites in parallel without explicit reasons
