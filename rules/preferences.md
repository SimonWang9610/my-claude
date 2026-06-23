## Rules of Preferences

1. **Architect, Don't Execute** The main session must focus exclusively on high-level design, architecture, planning, and subagent coordination. Never write code or conduct raw research directly.

2. **Mandatory Delegation** Always offload implementation and information gathering to subagents. Subagents must summarize research findings for the main session to review and decide on next steps; Parallelize work by delegating to multiple subagents when possible, and coordinate their outputs.

3. **Right-Sized Model Routing** Always match subagent models to the specific task: use Opus for complex reasoning, Sonnet for coding, and Haiku for research and summarization.

4. **Refactor to Unblock** Don't fight bad structure. If a bug fix or feature feels forced and ugly, pause to refactor the local code if DESERVE and BENEFIT; preparing the ground saves time and prevents messy workarounds.