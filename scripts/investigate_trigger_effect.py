"""
Test whether the mid-mass hump (~20-50 GeV) is a trigger-selection effect.

Idea: HLT flags are per-EVENT (same value for every muon row belonging to
that event). If different mass regions are dominated by different
triggers -- e.g. the hump region mostly fired by lower-pT-threshold
triggers that the Z-peak region rarely uses -- that's fairly direct
evidence the hump reflects trigger selection, not new physics or a bug.

This does NOT modify src/data_loader.py -- it's a one-off investigation,
kept separate so the core pipeline stays simple.
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import build_dimuon_pairs_from_nanoaod
from src.physics import invariant_mass

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "dimuon.csv")

# A representative spread of triggers with different pT thresholds --
# lower thresholds first, higher thresholds last.
TRIGGERS_TO_CHECK = [
    "HLT_DoubleMu5_IsoMu5",
    "HLT_Mu8",
    "HLT_Mu13_Mu8",
    "HLT_Mu17_Mu8",
    "HLT_Mu17_TkMu8",
    "HLT_Mu22_TkMu22",
]


def main():
    raw = pd.read_csv(DATA_PATH)

    # HLT flags are constant within an event, so take the first row per entry.
    hlt_cols = [c for c in TRIGGERS_TO_CHECK if c in raw.columns]
    if not hlt_cols:
        print("None of the expected trigger columns were found -- check column names in your file.")
        return
    event_triggers = raw.groupby("entry")[hlt_cols].first()

    pairs = build_dimuon_pairs_from_nanoaod(raw, require_opposite_charge=True)
    pairs["mass"] = invariant_mass(
        pairs["pt1"], pairs["eta1"], pairs["phi1"],
        pairs["pt2"], pairs["eta2"], pairs["phi2"],
        mass1=pairs["mass1"], mass2=pairs["mass2"],
    )
    pairs = pairs.join(event_triggers, on="entry")

    regions = {
        "J/psi region (2.5-3.5 GeV)": (2.5, 3.5),
        "Hump region (20-50 GeV)": (20, 50),
        "Z peak region (80-100 GeV)": (80, 100),
    }

    for label, (lo, hi) in regions.items():
        subset = pairs[(pairs["mass"] >= lo) & (pairs["mass"] < hi)]
        print(f"\n{label}: {len(subset)} events")
        for col in hlt_cols:
            frac = subset[col].mean() if len(subset) else float("nan")
            print(f"  {col}: {frac:.1%} of events fired this trigger")

    # Second hypothesis test: is the hump caused by combinatorial mispairing
    # in events with 3+ muons, where "top-2 by pT" isn't necessarily the
    # pair that came from the same real decay?
    nmuon_by_entry = raw.groupby("entry")["nMuon"].first()
    pairs["nMuon"] = pairs["entry"].map(nmuon_by_entry)

    print("\n--- nMuon distribution by mass region (checking for mispairing) ---")
    for label, (lo, hi) in regions.items():
        subset = pairs[(pairs["mass"] >= lo) & (pairs["mass"] < hi)]
        exactly_2 = (subset["nMuon"] == 2).mean() if len(subset) else float("nan")
        three_plus = (subset["nMuon"] >= 3).mean() if len(subset) else float("nan")
        print(f"{label}: {exactly_2:.1%} have exactly 2 muons, {three_plus:.1%} have 3+ muons")


if __name__ == "__main__":
    main()