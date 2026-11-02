"""Net inflow reconstruction from stored volume (non-saturated periods only).

V[t+1] = V[t] + I[t] - E[t] - R[t] - Z[t]
With Z = 0 (no spill) and E unknown (set to 0 here), the reconstructed series is
    I_net[t] = V[t+1] - V[t] + R[t]   (= I - E, a *lower bound* of inflow).
"""
import pandas as pd

M3S_TO_HM3_DAY = 86400 / 1e6  # 1 m³/s sustained for a day = 0.0864 hm³


def reconstruct_net_inflow(df: pd.DataFrame, release_m3s: float = 5.3,
                           sat_volume: float = 1752.36, tol: float = 0.01) -> pd.DataFrame:
    """df: columns date, volume_hm3 (daily). Returns one row per day t with
    I_net_hm3 = V[t+1]-V[t]+R, flagged ``valid`` only when t and t+1 are consecutive,
    both observed, and both strictly below the saturation volume."""
    d = df.sort_values("date").reset_index(drop=True)
    out = pd.DataFrame({"date": d["date"], "v0": d["volume_hm3"],
                        "v1": d["volume_hm3"].shift(-1),
                        "date1": d["date"].shift(-1)})
    out["R_hm3"] = release_m3s * M3S_TO_HM3_DAY
    out["dV_hm3"] = out["v1"] - out["v0"]
    out["I_net_hm3"] = out["dV_hm3"] + out["R_hm3"]
    consecutive = (out["date1"] - out["date"]) == pd.Timedelta(days=1)
    below = (out["v0"] < sat_volume - tol) & (out["v1"] < sat_volume - tol)
    out["valid"] = consecutive & below & out["v0"].notna() & out["v1"].notna()
    out.loc[~out["valid"], "I_net_hm3"] = float("nan")
    return out[["date", "v0", "v1", "dV_hm3", "R_hm3", "I_net_hm3", "valid"]]
