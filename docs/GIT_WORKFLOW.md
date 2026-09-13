# Git workflow: backing up changes systematically

The board tracks *what* to do; this is about making sure your actual work
is safely backed up as you go, not just sitting on your laptop.

## The basic loop, per issue/card

1. Pick a card, move it to "In Progress".
2. Create a branch named after it:
   ```
   git checkout -b reproduce-resonance-peaks
   ```
3. Commit as you go, in small chunks -- not one giant commit at the end.
   A reasonable rule: commit whenever something that worked a moment ago
   still works, plus something new.
   ```
   git add -A
   git commit -m "Add real dimuon CSV loading, validate against schema"
   ```
4. Push the branch regularly -- this is your actual backup, not just local
   git history:
   ```
   git push -u origin reproduce-resonance-peaks
   ```
5. When the card's done, open a Pull Request into `main` (even working
   solo, this gives you a clean history of "this issue = this PR = this
   diff", which is genuinely useful when you write up the project later).
   ```
   gh pr create --fill
   ```
6. Merge it, move the card to "Done", delete the branch.

## Why bother with branches/PRs solo

- If an experiment goes badly (e.g. a refactor that breaks the physics
  tests), you can abandon the branch without touching `main`.
- Your PR history becomes a readable log of "what did I actually do, in
  what order" -- useful both for your own reflection write-up and as
  something you could show in an interview if asked how you work.

## Commit message habits worth having

- Reference the card/issue when relevant: `Fix eta sign convention (closes #3)`
  -- GitHub will auto-link and even auto-close the issue on merge.
  For issues created via the CLI, the issue numbers are shown in that
  script's output on the run that created it.
- Write commits assuming a stranger (or you, in six months) will read them
  with no other context. "Fix bug" is not that; "Fix invariant mass sign
  error for negative eta values" is.

## Don't skip this bit

Push at least once per working session, even if the card isn't finished.
An uncommitted afternoon of debugging is the single most common way people
lose work right before a deadline.
