import pandas as pd
import os

def load_data(country):
    """
    Loads local CSVs. Return None if missing.
    """
    path = f"./Data/{country}.csv"
    if not os.path.exists(path):
        return None

    try:
        df = pd.read_csv(path)
        return df
    except Exception:
        return None


def get_top_regions(df, region_col="region", k=5):
    """
    Returns top regions by mean GHI.
    """
    if region_col not in df.columns:
        return pd.DataFrame({"Error": ["region column missing"]})

    if "GHI" not in df.columns:
        return pd.DataFrame({"Error": ["GHI column missing"]})

    return (
        df.groupby(region_col)["GHI"]
        .mean()
        .sort_values(ascending=False)
        .head(k)
        .reset_index()
    )
