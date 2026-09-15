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

**Important -- there are two different shapes this data can come in:**

1. **Per-muon (NanoAOD-style) format** -- what you'll most likely get.
   One row per muon, not per event. Key columns: `entry` (event ID,
   shared by muons from the same event), `Muon_pt`, `Muon_eta`,
   `Muon_phi`, `Muon_mass`, `Muon_charge`, `nMuon`. `src/data_loader.py`'s
   `build_dimuon_pairs_from_nanoaod()` reconstructs event-level pairs from
   this automatically (taking the two leading muons per event, requiring
   opposite charge by default), and `scripts/analyze_dimuon_mass.py`
   detects and handles this format on its own.

2. **Pre-paired (education) format** -- an older/simplified layout with
   columns already split as `pt1, eta1, phi1, pt2, eta2, phi2` per row,
   one row per event. Also handled automatically if you have this instead.

Place whichever version you have at `data/raw/dimuon.csv` -- the analysis
script figures out which format it is.

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

## Record what you actually got (fill this in once you've downloaded)

Generic instructions above; this section is for the specifics of the real
file you ended up with -- future you (or an interviewer) will want this,
and it's also the fastest way to spot a wrong download.

- **Source URL:**
- **Date downloaded:**
- **File size / row count:**
- **Actual column names (paste `df.columns.tolist()` output):**
- **Any differences from what this doc assumed:**

## A note on scale

Some CERN Open Data releases are many GB to TB (raw ROOT ntuples). You do
not need those for this project. Stick to the CSV "education" releases,
which are typically tens to hundreds of MB -- plenty for learning and for a
demo, and much faster to iterate on.