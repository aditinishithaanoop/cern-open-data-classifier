"""
Reproduce a known physics result from real CMS Open Data as a sanity check.

Run this once you've placed the real dimuon CSV (see docs/DATA.md) at
data/raw/dimuon.csv. It computes the invariant mass of every muon pair and
plots a histogram. You should see visible peaks around:

    J/psi   ~ 3.10 GeV
    Upsilon ~ 9.46 GeV
    Z boson ~ 91.2 GeV

If you don't see these peaks, something is wrong -- either in the data,
the units, or the physics.py implementation -- and that's a genuinely
useful thing to debug, not a sign to just push through.

Usage:
    python scripts/analyze_dimuon_mass.py
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import load_dimuon_csv
from src.physics import invariant_mass

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "dimuon.csv")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs", "dimuon_mass_spectrum.png")


def main():
    if not os.path.exists(DATA_PATH):
        print(f"No data file found at {DATA_PATH}.")
        print("See docs/DATA.md for where to download the real CMS dimuon dataset.")
        print("Generating a small synthetic placeholder instead, just to prove the pipeline runs end-to-end.")
        df = _make_synthetic_placeholder()
    else:
        df = load_dimuon_csv(DATA_PATH)

    mass = invariant_mass(
        df["pt1"], df["eta1"], df["phi1"],
        df["pt2"], df["eta2"], df["phi2"],
    )

    print(f"Computed invariant mass for {len(mass)} events.")
    print(f"Mass range: {mass.min():.2f} - {mass.max():.2f} GeV")

    plt.figure(figsize=(8, 5))
    plt.hist(mass, bins=200, range=(0, 120), histtype="step")
    plt.xlabel("Dimuon invariant mass [GeV]")
    plt.ylabel("Events")
    plt.yscale("log")
    plt.title("Dimuon invariant mass spectrum")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    plt.savefig(OUTPUT_PATH, dpi=150)
    print(f"Saved histogram to {OUTPUT_PATH}")


def _make_synthetic_placeholder():
    """
    NOT real physics data. Purely so the pipeline can be demonstrated before
    you've downloaded the real dataset. Replace with the real CSV ASAP --
    see docs/DATA.md.
    """
    import pandas as pd
    rng = np.random.default_rng(42)
    n = 5000
    return pd.DataFrame({
        "pt1": rng.uniform(5, 50, n),
        "eta1": rng.uniform(-2.4, 2.4, n),
        "phi1": rng.uniform(-np.pi, np.pi, n),
        "pt2": rng.uniform(5, 50, n),
        "eta2": rng.uniform(-2.4, 2.4, n),
        "phi2": rng.uniform(-np.pi, np.pi, n),
    })


if __name__ == "__main__":
    main()
