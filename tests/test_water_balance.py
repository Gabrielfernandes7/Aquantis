import pandas as pd
from src.hydrology.water_balance import reconstruct_net_inflow, M3S_TO_HM3_DAY

def test_mass_balance_and_masking():
    df = pd.DataFrame({"date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-05"]),
                       "volume_hm3": [100.0, 99.0, 1752.36, 50.0]})
    r = reconstruct_net_inflow(df, release_m3s=5.0)
    R = 5.0 * M3S_TO_HM3_DAY
    assert abs(r.loc[0, "I_net_hm3"] - (-1.0 + R)) < 1e-12   # V1-V0+R
    assert not r.loc[1, "valid"]   # next volume saturated
    assert not r.loc[2, "valid"]   # saturated
    assert r["I_net_hm3"].iloc[1:].isna().all()
