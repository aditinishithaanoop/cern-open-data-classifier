# Learning log

## 2026-09-14 -- Reproduced dimuon resonance peaks from real data

**What I did:** Downloaded the real CMS dimuon dataset and discovered it
was in a per-muon (NanoAOD-style) format, not the pre-paired shape I'd
originally assumed. Wrote pairing logic (`build_dimuon_pairs_from_nanoaod`)
that reconstructs event-level muon pairs, requiring opposite charge as a
physics cut. Ran the analysis and found J/psi (~3.1 GeV), Upsilon
(~9.46 GeV), and the Z boson (~91 GeV) all appearing at their correct
masses.

**What I learned:** Real detector data isn't shaped the way tutorials
assume -- one row per muon, grouped by event, not one row per event with
both muons' info already split out. Opposite-charge pairing matters
physically: same-sign pairs don't come from a real two-body decay and
would dilute the mass spectrum if included.

**What confused me / went wrong first try:** A mid-mass hump (~20-50 GeV)
appeared that I couldn't initially explain. Tested two hypotheses
directly against the data: (1) trigger-threshold selection effects, (2)
combinatorial mispairing in multi-muon events. Neither hypothesis survived
its own test -- the hump region's trigger fingerprint and muon-count
distribution were both nearly identical to the (verified-correct) J/psi
region. Concluded it's most likely a genuine feature of the underlying
continuum physics in this trigger-selected sample, based on indirect
evidence (three independent known resonances all reproduced correctly in
the same population), though this remains an open question rather than a
fully closed one.

**Decisions made (and why):** Used each muon's own `Muon_mass` column
in the invariant mass calculation rather than a fixed muon mass constant,
since the real per-muon mass value was directly available in the data.


## 2026-09-16 -- Sourced the labelled Higgs ML Challenge dataset

**What I did:** Downloaded the ATLAS Higgs Boson Machine Learning
Challenge dataset (818,238 rows, 35 columns) and checked its actual shape
before assuming it matched the dimuon data.

**What I learned:** This is Higgs to tau-tau, a completely different
search channel from the dimuon (Z/J-psi) physics I'd validated earlier --
not an extension of it. The dataset's `DER_*` columns are already
physics-engineered features (visible mass, angular separations, etc.)
rather than raw kinematics, which is different from building features
myself from pt/eta/phi as I did for the dimuon data.

**What confused me / went wrong first try:** Initially assumed I should
just point `src/train.py` at this file without changes -- checking the
actual columns first (rather than assuming) caught that the whole feature
set needed rewriting before it would even run correctly.

**Decisions made (and why):** Kept `dimuon.csv` and the new labelled
dataset as separate files rather than replacing one with the other --
they serve genuinely different pipeline stages (resonance validation vs
classification) and there was no reason to discard already-validated work.


## 2026-09-16 -- Trained and evaluated a baseline classifier on the Higgs ML dataset

**What I did:** Rewrote `src/train.py` to handle the real Higgs ML
Challenge dataset shape (DER_*/PRI_* columns, `Label` s/b) alongside the
original dimuon-features version, with automatic dataset-type detection.
Selected 7 always-explainable features, explicitly handled the -999
missing-value sentinel (dropped affected rows, logged how many). Trained a
logistic regression baseline: ROC AUC 0.78, signal recall only 0.40 at the
default threshold.

**What I learned:** The `-999.0` sentinel in this dataset means "not
applicable" (e.g. jet variables when there are fewer than 2 jets), not a
real value -- feeding it into a linear model unmodified would corrupt the
fit. None of my 7 chosen features actually had missing values in the real
data, which validated deliberately avoiding the jet-dependent columns.
Also: signal recall being low despite decent AUC is a real limitation of
using a 0.5 threshold on an imbalanced dataset (66% background), not a bug.

**What confused me / went wrong first try:** The `PRI_met` coefficient came
out negative, which contradicted my naive physics expectation (more
neutrinos in signal events should mean higher MET, not lower). Checked
mean and median separately -- they disagreed in direction (mean higher for
signal, median lower), which was itself confusing until I actually plotted
the distributions (see next entry, written after this one but investigated
right away).

**Decisions made (and why):** Chose not to use the dataset's `Weight`
column for this baseline -- it exists because signal was oversampled
relative to its true physics rate, and ignoring it means my reported
metrics don't reflect real-world class balance. Documented as a known
simplification rather than silently ignored; a stronger version of this
project would incorporate it.


## 2026-09-16 -- Resolved the PRI_met coefficient contradiction

**What I did:** Plotted the actual `PRI_met` distribution for signal vs
background (normalised histograms), rather than trusting summary
statistics alone.

**What I learned:** The two classes have genuinely different distribution
shapes, not just different centers. Signal peaks earlier and is more
concentrated at low-to-moderate MET (explaining the lower median), but has
a visibly heavier tail out to very high MET (max 2842 GeV vs background's
951 GeV), which drags its mean above background's despite most signal
events having lower MET than most background events. Logistic regression
fits mostly to where the bulk of the data sits, so the negative
coefficient reflects the real, bulk-level relationship (median behaviour),
not the tail-driven mean difference.

**What confused me / went wrong first try:** My first hypothesis was that
the negative coefficient was a multicollinearity artifact (MET's
contribution being distorted by correlation with the other 6 features).
That was a reasonable guess but wasn't well supported once I actually
looked at the distribution shapes -- the simpler explanation (differing
skew between classes) fit the evidence better.

**Decisions made (and why):** Left `StandardScaler` in place rather than
switching to `RobustScaler` for now, despite MET's heavy tail making mean/
std somewhat distorted by outliers -- noted as a worthwhile thing to try
later, not urgent enough to block moving on to the gradient boosting
comparison.

---
