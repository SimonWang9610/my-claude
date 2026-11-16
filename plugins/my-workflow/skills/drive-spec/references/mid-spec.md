# Mid-spec events

What drive-spec does when the user speaks up between gates.

## History

Per the spec rules' History; you add the rows no step does.

- The user asks, challenges a decision or an implementation detail, or offers an idea, and it is not
  an instruction → answer it (ground it first when it rests on a fact), then add a row.
- A gate answer that rejects or changes something → a row.
- It ends in a decision → a `D` in the owning artifact, referenced from the row; a `D` that changes
  the spec is a change of direction.
- Nothing came up → no `history.md`.

## Change of direction

The user says so, at any time: wait for or stop teammates in flight; check what it rests on.

- One item, nothing finished lost → apply it in one line.
- Else → show the impact (story → criterion → functionality → unit → task → files), options and a
  recommendation; ask. On a yes revise the artifacts through their owning steps (new ids; a dropped
  one stays, marked dropped), set the affected steps back to in progress and `current` to the
  earliest, and redo only the changed ids and affected batches.
