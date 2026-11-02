import pandas as pd
from src.hydrology.sensitivity import prepare, implied_inflow
from src.hydrology.water_balance import M3S_TO_HM3_DAY


def test_implied_inflow_formula_and_masking():
    vol = pd.DataFrame({"date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
                        "volume_hm3": [1000.0, 999.0, 1752.36]})
    e = pd.DataFrame({"date": vol.date, "E_mm_day": [5.0, 5.0, 5.0]})
    x = prepare(vol, e)
    assert len(x) == 1  # second day's next volume is saturated
    i = implied_inflow(x, a_full=100.0, k=0.0, e_scale=1.0, r_m3s=1.0)[0]
    # k=0 -> A = 100 km2 -> E = 0.5 hm3; dV = -1
    assert abs(i - (-1.0 + 0.5 + M3S_TO_HM3_DAY)) < 1e-12
