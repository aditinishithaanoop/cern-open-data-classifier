"""
Loads and validates the CERN Open Data CSV files.

Deliberately strict about column checking: silently proceeding with wrong or
missing columns is how you get a "working" pipeline that produces meaningless
numbers. Fail loudly and early instead.
"""

import pandas as pd

# Column names as they appear in the CMS dimuon education CSV
# (see docs/DATA.md for exact source and download instructions).
DIMUON_REQUIRED_COLUMNS = ["pt1", "eta1", "phi1", "pt2", "eta2", "phi2"]

# Columns present in the real CMS NanoAOD-style per-muon export (one row per
# muon, not per event) -- this is what you get from uproot/awkward-derived
# CSVs, as opposed to the pre-paired "pt1/pt2" education CSVs.
NANOAOD_MUON_COLUMNS = ["entry", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge"]


def is_nanoaod_muon_format(df: pd.DataFrame) -> bool:
    """True if this looks like the per-muon NanoAOD export rather than the
    pre-paired per-event CSV."""
    return all(c in df.columns for c in NANOAOD_MUON_COLUMNS)


def build_dimuon_pairs_from_nanoaod(df: pd.DataFrame, require_opposite_charge: bool = True) -> pd.DataFrame:
    """
    Reconstruct one dimuon pair per event from a per-muon NanoAOD-style
    dataframe (one row per muon, grouped by `entry`).

    For each event with 2 or more reconstructed muons, takes the two
    highest-pt muons ("leading" and "subleading") as the pair.

    require_opposite_charge: physically, muons from a real resonance decay
    (J/psi, Z, ...) are always oppositely charged. Same-sign pairs are not
    a real two-body decay and will dilute/blur the mass spectrum if
    included. Defaults to True -- set False only if you deliberately want
    to see the difference (a good exercise in itself).

    Returns a dataframe with columns: pt1, eta1, phi1, mass1, pt2, eta2,
    phi2, mass2 -- one row per selected event.
    """
    required = ["entry", "Muon_pt", "Muon_eta", "Muon_phi", "Muon_mass", "Muon_charge"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Expected NanoAOD-style columns missing: {missing}")

    pairs = []
    for entry_id, group in df.groupby("entry"):
        if len(group) < 2:
            continue  # need at least 2 muons to form a pair
        top2 = group.sort_values("Muon_pt", ascending=False).iloc[:2]
        mu1, mu2 = top2.iloc[0], top2.iloc[1]

        if require_opposite_charge and (mu1["Muon_charge"] * mu2["Muon_charge"] != -1):
            continue

        pairs.append({
            "entry": entry_id,
            "pt1": mu1["Muon_pt"], "eta1": mu1["Muon_eta"], "phi1": mu1["Muon_phi"], "mass1": mu1["Muon_mass"],
            "pt2": mu2["Muon_pt"], "eta2": mu2["Muon_eta"], "phi2": mu2["Muon_phi"], "mass2": mu2["Muon_mass"],
        })

    result = pd.DataFrame(pairs)
    print(f"Built {len(result)} dimuon pairs from {df['entry'].nunique()} events "
          f"({'opposite-charge only' if require_opposite_charge else 'any charge combination'}).")
    return result


def load_dimuon_csv(path: str) -> pd.DataFrame:
    """
    Load a dimuon events CSV and validate it has the columns we need.

    Raises a clear error rather than failing mysteriously three steps later
    if the file doesn't match what we expect (e.g. wrong dataset downloaded,
    or column names differ by capitalisation across dataset versions).
    """
    df = pd.read_csv(path)

    # Be forgiving of capitalisation differences between dataset versions.
    df.columns = [c.strip() for c in df.columns]
    lower_map = {c.lower(): c for c in df.columns}

    missing = [c for c in DIMUON_REQUIRED_COLUMNS if c not in lower_map]
    if missing:
        raise ValueError(
            f"CSV at {path} is missing expected columns {missing}. "
            f"Found columns: {list(df.columns)}. "
            "Check docs/DATA.md -- you may have downloaded a different "
            "dataset version, or the column names differ."
        )

    # Normalise to lowercase names we control.
    rename = {lower_map[c]: c for c in DIMUON_REQUIRED_COLUMNS}
    df = df.rename(columns=rename)
    return df