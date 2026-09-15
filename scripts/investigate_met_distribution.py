"""
Compare the PRI_met distribution shape between signal and background.

Motivation: mean(signal) > mean(background) but median(signal) <
median(background) -- a genuine contradiction that summary statistics
alone can't explain. Need to see the actual distribution shape.
"""

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("data/raw/higgs_labelled.csv")

signal = df[df["Label"] == "s"]["PRI_met"]
background = df[df["Label"] == "b"]["PRI_met"]

plt.figure(figsize=(8, 5))
plt.hist(background, bins=100, range=(0, 200), histtype="step", density=True, label="background")
plt.hist(signal, bins=100, range=(0, 200), histtype="step", density=True, label="signal")
plt.xlabel("PRI_met [GeV]")
plt.ylabel("Density (normalised, so shapes are comparable despite different counts)")
plt.legend()
plt.title("PRI_met distribution: signal vs background")
plt.savefig("outputs/pri_met_comparison.png", dpi=150)
print("Saved outputs/pri_met_comparison.png")

# A few more percentiles, to pin down where the distributions actually differ
for label, series in [("background", background), ("signal", signal)]:
    print(f"\n{label}:")
    print(series.describe(percentiles=[0.25, 0.5, 0.75, 0.9, 0.99]))