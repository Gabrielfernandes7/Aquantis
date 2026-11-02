import pandas as pd
from src.data.validators import validate_daily_series


def test_detects_gap_duplicate_and_invalid():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-02", "2025-01-05"]),
        "volume_hm3": [10.0, 11.0, 11.0, -1.0],
    })
    r = validate_daily_series(df)
    assert r["duplicate_dates"] == [pd.Timestamp("2025-01-02")]
    assert r["missing_dates"] == [pd.Timestamp("2025-01-03"), pd.Timestamp("2025-01-04")]
    assert len(r["invalid_values"]) == 1
