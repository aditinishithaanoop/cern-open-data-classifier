#!/usr/bin/env bash
#
# Sets up a GitHub repo + Issues + a Projects (v2) kanban board for this
# project, using the GitHub CLI (`gh`).
#
# WHAT THIS DOES:
#   1. Creates a GitHub repo from this local folder (skips if it already
#      has a remote).
#   2. Creates one labelled issue per roadmap step, each with a full
#      description, build/test instructions, and "understanding checkpoint"
#      questions.
#   3. Creates a Projects v2 board and adds every issue to it.
#
# WHAT THIS DOES NOT DO:
#   - Set each card's column automatically. GitHub's CLI can do this but it
#     requires looking up field/option IDs per-board, which is fragile
#     across accounts. After running this, open the board and drag the
#     first couple of cards into "To Do" -- takes 30 seconds and is more
#     reliable than a brittle script.
#
# PREREQUISITES:
#   - GitHub CLI installed: https://cli.github.com/
#   - Authenticated: run `gh auth login` first
#   - Run this script from inside the project folder (where this file's
#     parent's parent is the repo root), or adjust paths below.
#
# USAGE:
#   chmod +x scripts_setup/create_github_board.sh
#   ./scripts_setup/create_github_board.sh <your-github-username> <repo-name>
#
# Example:
#   ./scripts_setup/create_github_board.sh alexdoe cern-open-data-classifier

set -euo pipefail

OWNER="${1:?Usage: $0 <github-username-or-org> <repo-name>}"
REPO="${2:?Usage: $0 <github-username-or-org> <repo-name>}"

command -v gh >/dev/null 2>&1 || { echo "GitHub CLI (gh) not found. Install it from https://cli.github.com/ first."; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Not logged in. Run 'gh auth login' first."; exit 1; }

echo "== Step 1: Repo =="
cd "$(dirname "$0")/.."   # move to project root

if [ ! -d .git ]; then
  git init
  git add -A
  git commit -m "Initial commit: project scaffold"
fi

if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$OWNER/$REPO" --public --source=. --remote=origin --push
else
  echo "Remote 'origin' already set, skipping repo creation."
fi

echo "== Step 2: Labels =="
gh label create "physics" --color "1f77b4" --description "Learning/understanding the domain" --force
gh label create "data" --color "2ca02c" --description "Data sourcing and validation" --force
gh label create "ml" --color "d62728" --description "Modelling work" --force
gh label create "infra" --color "9467bd" --description "Packaging, deployment, AWS" --force
gh label create "writeup" --color "ff7f0e" --description "Documentation and reflection" --force

echo "== Step 3: Issues =="

create_issue () {
  local title="$1"
  local label="$2"
  local body="$3"
  echo "Creating: $title"
  gh issue create --repo "$OWNER/$REPO" --title "$title" --label "$label" --body "$body"
}

create_issue "Learn the minimum physics vocabulary" "physics" "$(cat <<'EOF'
## Description
Learn just enough particle physics to understand this project: four-momentum,
transverse momentum (pt), pseudorapidity (eta), azimuthal angle (phi),
invariant mass, and what "signal vs background" means in a collider search.

## Build/test instructions
This is a learning task, not a coding task -- but it has a concrete
checkpoint: you should be able to write, from memory, the formula for
invariant mass of a two-particle system and explain in one sentence what
each variable physically represents.

Resources: ATLAS/CMS masterclass materials linked from opendata.cern.ch,
the physics background section in `src/physics.py`'s docstring.

## Understanding checkpoint (answer these yourself before moving on)
- If eta = 0, where is the particle going relative to the beam line?
- Why does invariant mass, not just energy or momentum alone, indicate a
  resonance like the Z boson?
- What would it mean physically if your computed invariant mass came out
  negative or NaN? (Hint: check `src/physics.py`'s clipping logic and think
  about why it's there.)
EOF
)"

create_issue "Download and validate the real dimuon dataset" "data" "$(cat <<'EOF'
## Description
Replace the synthetic placeholder in `scripts/analyze_dimuon_mass.py` with
the real CMS dimuon education dataset. See `docs/DATA.md` for the source.

## Build/test instructions
1. Download the CSV from the link in `docs/DATA.md`.
2. Place it at `data/raw/dimuon.csv`.
3. Run `python3 -c "import pandas as pd; df = pd.read_csv('data/raw/dimuon.csv'); print(df.columns.tolist()); print(df.describe())"`
   and manually compare column names against `DIMUON_REQUIRED_COLUMNS` in
   `src/data_loader.py`. Update that list if the real file's names differ.
4. Run `python3 scripts/analyze_dimuon_mass.py` and confirm it runs without
   the "no data file found" message.

## Understanding checkpoint
- What are the units of `pt`, `eta`, and mass in this dataset? (Don't
  assume -- check the dataset's own documentation.)
- Does the row count in the CSV match what the dataset's documentation
  claims? If not, why might that be (cuts already applied, sampling, etc.)?
EOF
)"

create_issue "Reproduce known resonance peaks from real data" "physics" "$(cat <<'EOF'
## Description
The core learning checkpoint of this project: confirm that computing
invariant mass on real data reproduces known physics (J/psi ~3.10 GeV,
Upsilon ~9.46 GeV, Z boson ~91.2 GeV appearing as peaks in the histogram).

## Build/test instructions
1. Run `python3 scripts/analyze_dimuon_mass.py` with the real dataset in place.
2. Open `outputs/dimuon_mass_spectrum.png`.
3. Visually confirm peaks near the three masses above. Zoom the plot's
   range (edit the `range=(0, 120)` argument) to inspect the J/psi region
   more closely if needed.

## Understanding checkpoint
- If a peak is missing or in the wrong place, what are the possible causes?
  List at least three before checking any of them (e.g. wrong particle mass
  assumption, unit mismatch, wrong column mapping, cuts needed on the data).
- Why does the histogram use a log scale on the y-axis? What would you miss
  if it were linear?
EOF
)"

create_issue "Source a labelled signal/background dataset" "data" "$(cat <<'EOF'
## Description
Find and validate a labelled dataset for the classification step (see
`docs/DATA.md` for candidate sources, e.g. the ATLAS Higgs ML Challenge
dataset).

## Build/test instructions
1. Download the dataset and inspect its label column and encoding
   (e.g. 's'/'b' vs 1/0).
2. Write a short conversion step if needed so the label column is 1/0 and
   named `label`, matching what `src/train.py` expects.
3. Confirm the file has the same `pt1, eta1, phi1, pt2, eta2, phi2`-style
   columns `src/train.py`'s `build_features` expects, or adapt
   `build_features` to match the columns you actually have.

## Understanding checkpoint
- Is the dataset balanced (similar numbers of signal and background), or
  imbalanced? Why does that matter for how you'll evaluate the model later
  (accuracy vs. precision/recall/AUC)?
EOF
)"

create_issue "Train and evaluate a baseline classifier" "ml" "$(cat <<'EOF'
## Description
Train the logistic regression baseline in `src/train.py` on the labelled
dataset and understand its output, not just its accuracy number.

## Build/test instructions
```
python3 src/train.py --data data/raw/<your_labelled_file>.csv --model-type logreg
```
Confirm it prints a classification report and ROC AUC, and saves
`outputs/model.joblib`.

## Understanding checkpoint
- Look at the logistic regression's learned coefficients (you'll need to
  add a couple of lines to print `clf.named_steps['model'].coef_` after
  training). Does the sign and magnitude of each feature's weight make
  physical sense given what you know about signal vs background events?
- What does the ROC AUC number actually mean? What would an AUC of 0.5 vs
  1.0 tell you?
EOF
)"

create_issue "Compare against a gradient boosting model" "ml" "$(cat <<'EOF'
## Description
Train the alternative model type and compare against the logistic
regression baseline -- the point isn't "get a better number" but understand
the trade-off between interpretability and performance.

## Build/test instructions
```
python3 src/train.py --data data/raw/<your_labelled_file>.csv --model-type gbdt
```
Compare its ROC AUC and classification report against the logreg run.

## Understanding checkpoint
- If GBDT performs better, can you explain *why* it might, given the
  features you engineered? If it performs about the same or worse, is that
  actually surprising given how few features you have?
- Which model would you actually choose to deploy, and why? There's a
  legitimate case for either -- be ready to defend your choice.
EOF
)"

create_issue "Package the pipeline properly" "infra" "$(cat <<'EOF'
## Description
Make sure the repo is reproducible by someone who isn't you: dependencies
pinned, tests passing, README accurate.

## Build/test instructions
```
pip install -r requirements.txt
pytest tests/
```
Both should succeed on a clean checkout. Update `requirements.txt` with
exact versions (`pip freeze`) if you want full reproducibility.

## Understanding checkpoint
- If you handed this repo to a classmate with no context, could they get
  it running from the README alone? Actually try this if you can.
EOF
)"

create_issue "Set up AWS account and billing safety net" "infra" "$(cat <<'EOF'
## Description
Account setup and cost-safety steps before touching any deployment.
See `docs/AWS_DEPLOY.md` section 1.

## Build/test instructions
1. Create AWS account.
2. Set a Budget alert at low thresholds (e.g. $5, $20).
3. Create an IAM admin user for daily use instead of the root login.

## Understanding checkpoint
- What's the difference between stopping and terminating an EC2 instance,
  cost-wise? (You'll need this later.)
EOF
)"

create_issue "Build and test the Docker image locally" "infra" "$(cat <<'EOF'
## Description
Containerize the FastAPI app and confirm it works locally before deploying
anywhere.

## Build/test instructions
```
docker build -t cern-demo -f app/Dockerfile .
docker run -d -p 8000:8000 cern-demo
curl http://localhost:8000/health
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"pt1": 30, "eta1": 0.5, "phi1": 0.1, "pt2": 25, "eta2": -0.3, "phi2": 2.0}'
```
Confirm `/health` reports `model_loaded: true` (meaning your trained model
from the earlier step is present at `outputs/model.joblib`) and `/predict`
returns a sensible probability.

## Understanding checkpoint
- If `/predict` returns a 503 error, what does that tell you is missing?
  (Check `app/main.py`'s error message.)
EOF
)"

create_issue "Deploy to AWS and verify external access" "infra" "$(cat <<'EOF'
## Description
Deploy the container per `docs/AWS_DEPLOY.md` (App Runner recommended for
a first AWS deployment) and confirm it's actually reachable from outside
your own machine.

## Build/test instructions
Follow `docs/AWS_DEPLOY.md`. Then, from a device NOT on your home network
(e.g. phone on mobile data), run:
```
curl https://<your-deployed-url>/health
```

## Understanding checkpoint
- What would you tell an interviewer costs money here, and what doesn't?
  Be able to explain your own deployment's cost profile.
EOF
)"

create_issue "Write the reflection / what-I-learned section" "writeup" "$(cat <<'EOF'
## Description
Update the README's status section and add a short, honest reflection:
what worked first try, what didn't, what you'd do differently with more
time. This is often the part that makes a student project credible rather
than generic.

## Build/test instructions
No code -- just make sure the README accurately reflects the finished
state of the repo (update the checklist, remove anything that's no longer
true).

## Understanding checkpoint
- Could you talk through this project for 5 minutes in an interview without
  reading from notes? If not, what part are you shakiest on -- and is that
  the physics, the ML, or the AWS piece?
EOF
)"

echo "== Step 4: Projects v2 board =="
PROJECT_URL=$(gh project create --owner "$OWNER" --title "CERN Internship Project" --format json | python3 -c "import json,sys; print(json.load(sys.stdin)['url'])")
echo "Created project: $PROJECT_URL"

echo "Adding issues to the board..."
for issue_url in $(gh issue list --repo "$OWNER/$REPO" --json url --jq '.[].url'); do
  gh project item-add --owner "$OWNER" "$(echo "$PROJECT_URL" | grep -oE '[0-9]+$')" --url "$issue_url"
done

echo ""
echo "Done. Open $PROJECT_URL and drag cards into To Do / In Progress / Done as you go."
