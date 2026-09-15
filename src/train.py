"""
Train a simple, interpretable classifier to separate signal from background.

Deliberately using logistic regression / gradient boosting on a handful of
physics-motivated features, not a deep net. At this stage of learning, being
able to explain exactly what every feature means and why the model weights
it the way it does is worth far more than a marginally higher AUC from a
model you can't interrogate.

Supports two dataset shapes, auto-detected from the CSV's columns:
 
1. Dimuon-derived (pt1/eta1/phi1/pt2/eta2/phi2 + a `label` column) -- if you
   ever construct your own signal/background labels from the dimuon data
   (e.g. a mass-window proxy).
2. The real ATLAS Higgs ML Challenge dataset (DER_*/PRI_* columns + a
   `Label` column with 's'/'b' values) -- see docs/DATA.md.
 
IMPORTANT CAVEAT: this baseline does NOT use the Higgs dataset's `Weight`
column. That column exists because signal was oversampled relative to its
true physics rate for statistical power -- ignoring it means our reported
metrics don't reflect real-world class balance. Documented here rather than
silently ignored; a more careful version of this project would incorporate
it into training and evaluation.
"""

import argparse
import os
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.physics import invariant_mass

# The sentinel ATLAS uses to mean "this quantity isn't defined for this
# event" (e.g. jet variables when there are fewer than 2 jets). Not a real
# physical value -- must be treated as missing, not as data.
MISSING_SENTINEL = -999.0
 
# A deliberately small, always-explainable feature set from the Higgs ML
# Challenge dataset. Chosen to be understandable in one sentence each, not
# to maximise performance:
#   DER_mass_vis          - invariant mass of the visible tau+lepton system
#   DER_pt_h               - transverse momentum of the reconstructed Higgs candidate
#   DER_deltar_tau_lep     - angular separation between the tau and the lepton
#   DER_pt_ratio_lep_tau   - ratio of lepton pT to tau pT
#   PRI_tau_pt              - transverse momentum of the tau
#   PRI_lep_pt              - transverse momentum of the lepton
#   PRI_met                 - missing transverse energy (signature of undetected neutrinos)
HIGGS_FEATURE_COLUMNS = [
    "DER_mass_vis",
    "DER_pt_h",
    "DER_deltar_tau_lep",
    "DER_pt_ratio_lep_tau",
    "PRI_tau_pt",
    "PRI_lep_pt",
    "PRI_met",
]

def build_dimuon_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Turn raw kinematics into a small set of physics-motivated features.
    Every one of these should be explainable in a sentence:

    - mass:        invariant mass of the pair -- the primary discriminating
                    variable for resonance searches.
    - pt_sum:       scalar sum of transverse momenta -- signal events often
                    have different overall energy scales than background.
    - delta_eta:    angular separation along the beam axis.
    - delta_phi:    angular separation around the beam axis.
    """
    mass = invariant_mass(df["pt1"], df["eta1"], df["phi1"],
                           df["pt2"], df["eta2"], df["phi2"])
    return pd.DataFrame({
        "mass": mass,
        "pt_sum": df["pt1"] + df["pt2"],
        "delta_eta": np.abs(df["eta1"] - df["eta2"]),
        "delta_phi": np.abs(df["phi1"] - df["phi2"]),
    })

def build_higgs_features(df: pd.DataFrame):
    """
    Select and clean features from the real Higgs ML Challenge dataset.
 
    Handles the -999 missing-value sentinel explicitly: replaces it with
    NaN (so it's not treated as a real extreme value), then reports how
    many rows have at least one missing chosen feature. Rows with any
    missing chosen feature are dropped for this baseline -- simple and
    transparent, at the cost of some data. A more sophisticated version
    could impute instead; that tradeoff is a legitimate future iteration,
    not something to silently paper over.
 
    Returns (X, valid_mask) -- caller is responsible for filtering y with
    the same mask.
    """
    X = df[HIGGS_FEATURE_COLUMNS].copy()
    X = X.replace(MISSING_SENTINEL, np.nan)
 
    missing_counts = X.isna().sum()
    if missing_counts.sum() > 0:
        print("Missing (-999 sentinel) value counts per feature:")
        print(missing_counts[missing_counts > 0])
 
    n_before = len(X)
    valid_mask = ~X.isna().any(axis=1)
    n_dropped = n_before - valid_mask.sum()
    if n_dropped > 0:
        print(f"Dropping {n_dropped} of {n_before} rows ({n_dropped/n_before:.1%}) "
              f"with a missing value in the chosen feature set.")
 
    return X, valid_mask
 
 
def detect_dataset_type(df: pd.DataFrame) -> str:
    if "Label" in df.columns and all(c in df.columns for c in HIGGS_FEATURE_COLUMNS):
        return "higgs"
    if "label" in df.columns and all(c in df.columns for c in ["pt1", "eta1", "phi1", "pt2", "eta2", "phi2"]):
        return "dimuon"
    raise ValueError(
        "Couldn't determine dataset type from columns. Expected either a "
        "'Label' column + Higgs ML Challenge DER_/PRI_ columns, or a "
        "'label' column + dimuon pt1/eta1/phi1/pt2/eta2/phi2 columns."
    )
 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to labelled CSV (needs a 'label' column)")
    parser.add_argument("--model-type", choices=["logreg", "gbdt"], default="logreg")
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "outputs", "model.joblib"))
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    dataset_type = detect_dataset_type(df)
    print(f"Detected dataset type: {dataset_type}")

    if dataset_type == "higgs":
        X, valid_mask = build_higgs_features(df)
        X = X[valid_mask]
        y = (df.loc[valid_mask, "Label"] == "s").astype(int)
    else:
        X = build_dimuon_features(df)
        y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    if args.model_type == "logreg":
        clf = Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000)),
        ])
    else:
        clf = GradientBoostingClassifier(random_state=42)

    clf.fit(X_train, y_train)
    proba = clf.predict_proba(X_test)[:, 1]
    preds = clf.predict(X_test)

    print(classification_report(y_test, preds))
    print(f"ROC AUC: {roc_auc_score(y_test, proba):.4f}")

    if args.model_type == "logreg":
        coefs = clf.named_steps["model"].coef_[0]
        print("\nLogistic regression coefficients (after standard scaling):")
        for name, coef in zip(X.columns, coefs):
            print(f"  {name}: {coef:+.4f}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    joblib.dump({"model": clf, "feature_columns": list(X.columns), "dataset_type": dataset_type}, args.out)
    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()
