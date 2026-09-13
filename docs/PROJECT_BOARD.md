# Setting up the project board manually

If you'd rather not run `scripts_setup/create_github_board.sh` (or want to
tweak things), here's the same setup by hand.

## 1. Create the board

1. Go to your GitHub profile > **Projects** tab > **New project**.
2. Choose the **Board** template. This gives you Todo / In Progress / Done
   columns by default (rename or add columns as you like -- e.g. splitting
   "Todo" into "Backlog" and "Todo" if the list feels long).
3. Name it something like "CERN Internship Project".

## 2. Create the issues

For each row below, create a GitHub Issue in your repo (Issues tab > New
issue) with that title, label, and body, then add it to the board (from the
issue page, there's a "Projects" section in the sidebar to add it directly).

The full text for every issue -- title, label, description, build/test
steps, and understanding-checkpoint questions -- is in
`scripts_setup/create_github_board.sh`, inside each `create_issue "..." "..." "$(cat <<'EOF' ... EOF)"`
block. Copy the body content out of there rather than retyping it.

Issue titles, in the order they should roughly be tackled:

1. Learn the minimum physics vocabulary — `physics`
2. Download and validate the real dimuon dataset — `data`
3. Reproduce known resonance peaks from real data — `physics`
4. Source a labelled signal/background dataset — `data`
5. Train and evaluate a baseline classifier — `ml`
6. Compare against a gradient boosting model — `ml`
7. Package the pipeline properly — `infra`
8. Set up AWS account and billing safety net — `infra`
9. Build and test the Docker image locally — `infra`
10. Deploy to AWS and verify external access — `infra`
11. Write the reflection / what-I-learned section — `writeup`

## 3. Work the board

- Move a card to "In Progress" when you actually start it, not before --
  an accurate board is more useful to you than an aspirational one.
- Only one or two cards in "In Progress" at a time. This project has a
  learning component; context-switching between physics, ML, and AWS mid-task
  will slow you down more than it feels like it will.
