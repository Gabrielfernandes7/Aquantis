"""Quality checks for daily reservoir series."""
import pandas as pd


def validate_daily_series(df: pd.DataFrame, date_col="date", value_col="volume_hm3",
                          lo=0.0, hi=None) -> dict:
    """Report duplicates, missing days, unsorted dates and invalid values."""
    d = df[date_col]
    full = pd.date_range(d.min(), d.max(), freq="D")
    missing = full.difference(pd.DatetimeIndex(d.unique()))
    v = df[value_col]
    bad = v.isna() | (v < lo)
    if hi is not None:
        bad |= v > hi
    return {
        "n_rows": len(df),
        "start": d.min(),
        "end": d.max(),
        "duplicate_dates": d[d.duplicated(keep=False)].drop_duplicates().tolist(),
        "missing_dates": missing.tolist(),
        "is_sorted": bool(d.is_monotonic_increasing),
        "invalid_values": df.loc[bad, [date_col, value_col]].values.tolist(),
    }
