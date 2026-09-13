# CERN Open Data Classifier

A small end-to-end project: learn enough particle physics to be dangerous,
reproduce a known result from real CMS/ATLAS open data, train a simple
classifier to separate signal from background events, and deploy it as a
live demo on AWS.

Built while applying for CERN's Short-Term Internship programme, and
honestly, while learning most of the physics for the first time.

## Why this project

CERN publishes real LHC collision data publicly (opendata.cern.ch). This
project uses the CSV "education" releases -- small, well-documented subsets
of that data -- rather than the full raw datasets, which are far larger than
needed for this.

## What's here

```
src/physics.py      - invariant mass calculation, unit-tested against a
                       hand-derived closed-form case (see tests/)
src/data_loader.py   - loads and validates the input CSVs
src/train.py         - trains a simple, interpretable classifier
tests/               - unit tests
scripts/             - analysis scripts (start with analyze_dimuon_mass.py)
app/                 - FastAPI service + Dockerfile for deployment
docs/DATA.md         - where to get the real datasets
docs/AWS_DEPLOY.md   - step-by-step AWS deployment guide
```

## Status / roadmap

- [x] Physics fundamentals: four-momentum, invariant mass
- [x] Invariant mass calculation, unit tested against a hand-derived case
- [ ] Reproduce known resonance peaks (J/psi, Upsilon, Z) from real dimuon data
- [ ] Train and evaluate a signal/background classifier on real labelled data
- [ ] Deploy live demo on AWS
- [ ] Write up what I learned, including what didn't work first try

I'm leaving this roadmap visible rather than only showing a polished final
state -- the process is most of the point of doing this.

## Running it

```bash
pip install -r requirements.txt
pytest tests/                              # verify the physics is correct
python scripts/analyze_dimuon_mass.py      # runs on synthetic data until you add the real CSV
```

See `docs/DATA.md` for adding real data, and `docs/AWS_DEPLOY.md` for
deployment.

## Tracking progress and backing up work

- `scripts_setup/create_github_board.sh` sets up a GitHub repo, one Issue
  per roadmap step (with descriptions, build/test steps, and understanding
  checkpoints), and a Projects v2 kanban board, using the GitHub CLI.
  `docs/PROJECT_BOARD.md` has the manual equivalent if you'd rather not run
  a script, or want to adjust things first.
- `docs/GIT_WORKFLOW.md` covers a branch-per-issue workflow so work is
  actually pushed and backed up as you go, not just sitting locally.

## What I'd push back on in my own project

Being honest about limitations: the classifier here uses a handful of
simple engineered features, not the full detector information a real
CMS/ATLAS analysis would use, and the physics background I have is a few
weeks deep, not a physics degree. This is meant to demonstrate that I can
learn a new technical domain quickly and build something correct and
reproducible in it -- not that I'm already a particle physicist.
