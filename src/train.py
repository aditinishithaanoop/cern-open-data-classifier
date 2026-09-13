"""
Train a simple, interpretable classifier to separate signal from background.

Deliberately using logistic regression / gradient boosting on a handful of
physics-motivated features, not a deep net. At this stage of learning, being
able to explain exactly what every feature means and why the model weights
it the way it does is worth far more than a marginally higher AUC from a
model you can't interrogate.

Expects a labelled CSV with a `label` column (1 = signal, 0 = background)
plus the same pt/eta/phi columns as the dimuon dataset. See docs/DATA.md for
where to get a labelled dataset (e.g. the CMS/ATLAS Higgs education samples).
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


def build_features(df: pd.DataFrame) -> pd.DataFrame:
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to labelled CSV (needs a 'label' column)")
    parser.add_argument("--model-type", choices=["logreg", "gbdt"], default="logreg")
    parser.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "outputs", "model.joblib"))
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    X = build_features(df)
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

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    joblib.dump({"model": clf, "feature_columns": list(X.columns)}, args.out)
    print(f"Saved model to {args.out}")


if __name__ == "__main__":
    main()
