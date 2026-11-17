# query — answer from the atlas, heal on a miss

Read as little as possible. Whether the atlas covers the question is found here, not judged before:
a miss heals, a wide one is returned as a gap. A bare pointer (`path:symbol`, a unit id) skips to
Heal on that spot.

## Steps

1. **Route** — read `INDEX.md`, then scan every entry's frontmatter without opening bodies:

   ```bash
   grep -rHE '^(id|title|keywords|owns|depends):' --include='*.md' <atlas>
   ```

2. **Open** — only the entries whose `keywords` or `owns` match the question.
3. **Answer** — at most about 15 lines:
   - the facts, each with its `path:symbol` anchor;
   - a claim: confirmed, refuted (with the true fact) or unclear → a `Q` with a default. Look first
     for what would refute it;
   - what a unit needs: its Depends on;
   - what depends on a unit, or what a change would break: the entries whose `depends` names it,
     its edges in the Graph and the flows that pass through it;
   - `Dive:` the pointers to read for deeper detail.
4. **Widen** — not answered → recheck the frontmatter of the entries skipped; open any that now match.
5. **Heal** — still missing → read source for exactly that spot (`build.md` § Walk), at most 3 reads
   per question. Fold each new fact back per `format.md`: a new argument or deeper fact into its
   unit's entry; a newly found dependent into its own entry and index row, never into the entry of
   the unit it depends on; a unit inside, once opened, into its own entry and index row. Run the
   Format check. Say what was folded where.

## Stop

- Budget spent, or the question spans many unaudited units → return the partial answer, the gap, and
  a build suggestion for that scope.
- Never re-scan blindly; never guess.
