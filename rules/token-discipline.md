# Token discipline

Applies when authoring or refining any skill, rule, agent, command, or prompt file, and when
writing artifacts other agents will re-read. Full verbatim text:

- **Compress what compounds.** Text loaded every session (agent bodies, skill descriptions,
  rules) and artifacts re-read across phases earn the most trimming. Lazily-loaded references
  cost only when invoked — trim them opportunistically while touching them anyway, never as a
  bulk rewrite pass.
- **Cut real overhead only.** Drop filler, hedging, restated context, and decorative formatting.
  Never invent abbreviations (`cfg`, `impl`) or arrow-chains as "compression" — tokenizers split
  them the same as full words: zero tokens saved, clarity lost.
- **Technical content is exact.** Code, commands, paths, IDs, and error strings are never
  compressed or paraphrased.
- **Human-facing output stays clear.** Gate summaries, review reports, warnings, and multi-step
  instructions use full sentences — clarity beats compression wherever a human decides.
