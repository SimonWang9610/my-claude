# ast-grep — structural walk queries

Used by the Locate + Walk passes ([build.md](./build.md) §§ 1–2, **ast-grep mode**) to map
structure mechanically. Language-agnostic — pick `--lang` from the source. (The mode gate
and grep fallback live in build.md § 1, not here.)

**When a form below is missing or a command errors, ask the tool, not memory:**
`ast-grep -h` for the command list, `ast-grep <command> -h` (`ast-grep run -h`,
`ast-grep scan -h`, `ast-grep outline -h`) for a command's exact flags. Trust `-h` over any
form here — versions drift.

## Language — `--lang <L>`

Pick per source: `tsx` (React/JSX — MUST, `ts` won't parse JSX) · `ts` · `js` · `jsx` · `tsx`
`dart` · `python` · `go` · `rust` · `java` · `c` · `cpp` · `kotlin` · `swift`. Any grammar
ast-grep ships works. Confirm a node's `kind` with `--debug-query=cst` before relying on it
(kind names come from the grammar and differ per language).

## Metavariables

`$A` one named node — reused means same text (`$A == $A` matches `a == a`, not `a == b`) ·
`$$$ARGS` zero-or-more nodes (arg lists, bodies) · `$_X` non-capturing. A metavar must be a
whole AST node — it can't sit inside a string or identifier (`"hi $X"`, `on$EVENT` fail).

## The three queries — surface, callers, touch points

- **Surface** — exported symbols with line ranges:
  `ast-grep outline <dir> --items exports --view signatures`
- **Caller chain** — call sites of a symbol, structural (no comment/string false hits):
  `ast-grep run -p '<symbol>($$$)' --lang <L> --json <root>`
- **Fact touch points** — who writes / reads a store · field · key (couplings):
  `ast-grep run -p '<owner>.<field> = $V' --lang <L> --json <root>` + the read form

`--json` gives precise ranges → feed them into targeted Reads; never re-scan whole files.

## When a pattern isn't enough — inline rule

Relational/composite questions a bare pattern can't express (e.g. an awaited call with no
enclosing try/catch): `ast-grep scan --inline-rules '<yaml>' --json <root>`. Rule grammar:
atomic (`pattern` · `kind` · `regex`) · relational (`inside` · `has` · `follows` ·
`precedes`, each with `stopBy: end`) · composite (`all` · `any` · `not`). Keep rules inline
in the prompt, never committed files.
