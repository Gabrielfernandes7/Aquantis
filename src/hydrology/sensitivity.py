"""Sensitivity of the implied inflow to hypothetical E, A(V) and R.

Implied inflow (Z = 0, valid non-saturated days only):
    I_implied = dV + E + R,    E = scale * e_mm * A(V) * 1e-3
Negative I_implied => combination incompatible with the observed storage change
(under the stated hypotheses).
"""
import itertools

import numpy as np
import pandas as pd

from src.hydrology.evaporation import area_km2
from src.hydrology.water_balance import M3S_TO_HM3_DAY

# Provenance of every input: keep observation / estimate / hypothesis separate.
PROVENANCE = {
    "volume_portal": "observação (Cogerh/Portal; curva batimétrica; saturada em 1752,36 hm³)",
    "volume_ana": "observação (ANA/SAR; curva diferente)",
    "meteorologia": "estimativa (NASA POWER, grade — não é medição local)",
    "evaporacao_mm": "estimativa (Penman água livre, sem armazenamento de calor)",
    "area_espelho": "hipótese (A = A_full·(V/1940)^k; sem curva cota–área)",
    "retirada": "hipótese (4,5 / 5,3 m³/s de notícias; outros valores = cenários)",
    "vertimento": "hipótese (Z = 0; não identificável nos dias saturados)",
}

A_FULL = [150, 175, 200, 225, 250]
K = [0.5, 0.6, 0.7, 0.8]
E_SCALE = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
R_M3S = [0.0, 2.65, 4.5, 5.3]


def prepare(vol: pd.DataFrame, e_mm: pd.DataFrame, sat=1752.36, tol=0.01) -> pd.DataFrame:
    """One row per valid day t: dV, mean volume, e_mm. Valid = consecutive, observed, unsaturated."""
    d = vol.sort_values("date").reset_index(drop=True)
    x = pd.DataFrame({"date": d.date, "v0": d.volume_hm3, "v1": d.volume_hm3.shift(-1),
                      "d1": d.date.shift(-1)})
    ok = ((x.d1 - x.date) == pd.Timedelta(days=1)) & x.v0.notna() & x.v1.notna() \
        & (x.v0 < sat - tol) & (x.v1 < sat - tol)
    x = x[ok].merge(e_mm[["date", "E_mm_day"]], on="date")
    x["dV"] = x.v1 - x.v0
    x["vmean"] = (x.v0 + x.v1) / 2
    return x.drop(columns="d1").reset_index(drop=True)


def implied_inflow(x: pd.DataFrame, a_full, k, e_scale, r_m3s) -> np.ndarray:
    area = area_km2(x.vmean.values, a_full=a_full, k=k)
    e = e_scale * x.E_mm_day.values * area * 1e-3
    return x.dV.values + e + r_m3s * M3S_TO_HM3_DAY


def grid(x: pd.DataFrame, dry_months=(8, 9, 10, 11)) -> pd.DataFrame:
    """Metrics for every combination. Dry-season monthly sums use the assumption that
    regional inflow is small in Aug–Nov (hypothesis)."""
    dry = x.date.dt.month.isin(dry_months).values
    ym = x.date.dt.to_period("M").values
    rows = []
    for a, k, s, r in itertools.product(A_FULL, K, E_SCALE, R_M3S):
        i = implied_inflow(x, a, k, s, r)
        m = pd.Series(i[dry]).groupby(ym[dry]).sum()
        rows.append(dict(a_full=a, k=k, e_scale=s, r_m3s=r,
                         frac_neg_days=float((i < 0).mean()),
                         frac_neg_days_dry=float((i[dry] < 0).mean()),
                         frac_neg_months_dry=float((m < 0).mean()),
                         median_dry_hm3_day=float(np.median(i[dry]))))
    return pd.DataFrame(rows)
