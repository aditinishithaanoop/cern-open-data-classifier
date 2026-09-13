# Getting the real data

This sandbox can't reach opendata.cern.ch or zenodo.org directly, so the
scripts here ship with a *synthetic placeholder* generator only, so you can
confirm the pipeline runs. Replace it with real data as your actual first
step -- don't skip this, the synthetic data has no physics in it at all.

## Dimuon events (for `scripts/analyze_dimuon_mass.py`)

CMS Open Data education dataset, "CMS Open Data 2012 datasets for dimuon
exercises":
- https://zenodo.org/records/6538437
- Download either the CSV or PKL version (same content, use one).
- Expected columns (case-insensitive): `pt1, eta1, phi1, pt2, eta2, phi2`
  (there may be additional columns like charge, run/event number -- ignore
  those for this project).
- Place the file at `data/raw/dimuon.csv`.

Also worth browsing directly on the portal itself:
- https://opendata.cern.ch/ -- search `keywords:education`

## Labelled signal/background data (for `src/train.py`)

- ATLAS Higgs Machine Learning Challenge dataset (linked from
  https://opendata.cern.ch/ -- search "Higgs Machine Learning Challenge").
  This has a `Label` column (`s`/`b` for signal/background) you'll need to
  map to 1/0.
- Alternatively, CMS publishes "Higgs candidate events for use in education
  and outreach" -- check the CMS education guide linked from the portal
  for the current record.

**Sanity check before you trust any of this**: dataset formats and exact
column names have changed across portal versions. The first thing you should
do with any new file is `df.columns` and `df.describe()` -- don't assume the
column names in this repo match exactly what you downloaded. Update
`src/data_loader.py`'s column list if they differ, and say so in your
project README rather than silently renaming things.

## A note on scale

Some CERN Open Data releases are many GB to TB (raw ROOT ntuples). You do
not need those for this project. Stick to the CSV "education" releases,
which are typically tens to hundreds of MB -- plenty for learning and for a
demo, and much faster to iterate on.
