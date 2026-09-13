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
