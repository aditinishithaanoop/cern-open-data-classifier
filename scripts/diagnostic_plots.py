"""
Follow-up diagnostic plots for the dimuon mass spectrum.

Two views the first plot didn't give you:
1. A zoomed, finer-binned low-mass region (0-15 GeV) to actually resolve
   J/psi and Upsilon as distinct peaks, rather than one dominant spike.
2. A log-x version over the full range, which is how this spectrum is
   conventionally plotted in HEP outreach material (e.g. search "CMS
   dimuon spectrum 13 orders of magnitude") -- easier to compare your
   result against the canonical shape and spot anything unusual.

Run this after scripts/analyze_dimuon_mass.py has already produced a
dimuon pair dataframe -- this script recomputes it the same way.
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.data_loader import is_nanoaod_muon_format, build_dimuon_pairs_from_nanoaod, load_dimuon_csv
from src.physics import invariant_mass

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "dimuon.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "outputs")


def get_mass():
    raw = pd.read_csv(DATA_PATH)
    if is_nanoaod_muon_format(raw):
        df = build_dimuon_pairs_from_nanoaod(raw, require_opposite_charge=True)
        return invariant_mass(df["pt1"], df["eta1"], df["phi1"],
                               df["pt2"], df["eta2"], df["phi2"],
                               mass1=df["mass1"], mass2=df["mass2"])
    else:
        df = load_dimuon_csv(DATA_PATH)
        return invariant_mass(df["pt1"], df["eta1"], df["phi1"],
                               df["pt2"], df["eta2"], df["phi2"])


def main():
    mass = get_mass()

    # 1. Zoomed low-mass region, fine binning
    plt.figure(figsize=(8, 5))
    plt.hist(mass, bins=300, range=(0, 15), histtype="step")
    plt.xlabel("Dimuon invariant mass [GeV]")
    plt.ylabel("Events")
    plt.yscale("log")
    plt.title("Low-mass region (zoomed) -- look for J/psi (~3.10) and Upsilon (~9.46)")
    plt.axvline(3.10, color="red", linestyle="--", alpha=0.5, label="J/psi (3.10 GeV)")
    plt.axvline(9.46, color="green", linestyle="--", alpha=0.5, label="Upsilon (9.46 GeV)")
    plt.legend()
    path1 = os.path.join(OUT_DIR, "dimuon_mass_lowmass_zoom.png")
    plt.savefig(path1, dpi=150)
    print(f"Saved {path1}")

    # 2. Full range, log-x -- the conventional HEP outreach presentation
    plt.figure(figsize=(8, 5))
    mass_positive = mass[mass > 0.1]  # log axis can't show zero/near-zero
    plt.hist(mass_positive, bins=np.logspace(np.log10(0.2), np.log10(200), 200), histtype="step")
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("Dimuon invariant mass [GeV]")
    plt.ylabel("Events")
    plt.title("Full spectrum, log-log (compare shape against canonical CMS plot)")
    path2 = os.path.join(OUT_DIR, "dimuon_mass_full_logx.png")
    plt.savefig(path2, dpi=150)
    print(f"Saved {path2}")


if __name__ == "__main__":
    main()