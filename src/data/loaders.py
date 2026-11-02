"""Loaders for raw Orós reservoir data."""
from io import StringIO
from pathlib import Path

import pandas as pd


def load_portal_volume(path) -> pd.DataFrame:
    """Portal Hidrológico CE export: columns DateTime;Volume (hm³), decimal comma.

    Returns a DataFrame with columns ``date`` (datetime64) and ``volume_hm3``.
    """
    df = pd.read_csv(path, sep=";", decimal=",", encoding="utf-8-sig")
    df.columns = ["date", "volume_hm3"]
    df["date"] = pd.to_datetime(df["date"])
    return df


def load_ana_history(path) -> pd.DataFrame:
    """ANA/SAR export (an HTML table saved as .xls).

    Returns columns: state, name, capacity_hm3, level_m, useful_volume_hm3,
    volume_pct, date.
    """
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    df = pd.read_html(StringIO(text), decimal=",", thousands=None)[0]
    df.columns = ["state", "name", "capacity_hm3", "level_m",
                  "useful_volume_hm3", "volume_pct", "date"]
    for c in ("state", "name"):
        df[c] = df[c].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"].astype(str).str.strip(), format="%d/%m/%Y")
    return df
