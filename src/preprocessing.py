
import pandas as pd

def preprocess_polylines(df):

    df = df.copy()

    # ============================================================
    # FORCE POSITIONAL COLUMN INTERPRETATION
    # ============================================================
    if df.shape[1] < 4:
        raise ValueError("Input must have at least 4 columns: x, y, z, polyline_id")

    df = df.iloc[:, :4]  # take first 4 columns by order

    # rename based on position (NOT original names)
    df.columns = ["x", "y", "z", "polyline_id"]

    # ============================================================
    # CONVERT TO NUMERIC
    # ============================================================
    df["x"] = pd.to_numeric(df["x"], errors="coerce")
    df["y"] = pd.to_numeric(df["y"], errors="coerce")
    df["z"] = pd.to_numeric(df["z"], errors="coerce")
    df["polyline_id"] = pd.to_numeric(df["polyline_id"], errors="coerce")

    # ============================================================
    # REMOVE INVALID ROWS
    # ============================================================
    bad_rows = df[["x", "y", "z"]].isna().any(axis=1)
    df = df[~bad_rows]

    # ============================================================
    # SORT FOR CONSISTENCY
    # ============================================================
    df = df.sort_values(by="polyline_id").reset_index(drop=True)

    # ============================================================
    # OPTIONAL FLAG
    # ============================================================
    df["intersect"] = 0


    

    return df

