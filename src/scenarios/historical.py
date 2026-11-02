"""Family A: scenarios built only from observed storage (no inflow, E or R)."""
import calendar

import numpy as np
import pandas as pd

from src.scenarios.schema import FAMILY_HISTORICAL, HORIZON_MONTHS, Scenario

SAT_PORTAL = 1752.36


def _origin(source):
    return {"portal": "portal_observed", "ana": "ana_observed"}[source]


def horizon_scenario(vol: pd.DataFrame, year: int, source: str = "portal",
                     value_col: str = "volume_hm3", sat: float | None = SAT_PORTAL,
                     tol: float = 0.01, cap_flag=None) -> Scenario:
    """July–December of ``year``. Storage at the 1st of each month (Jul 1 .. Jan 1 of year+1).

    vol: columns date, <value_col>. A month is ``usable`` only if both boundary volumes are
    observed, no daily value in the month is missing/saturated and all days are present.
    Exclusion metadata is retained (never dropped). Sources are NOT mixed: one source per scenario.
    """
    v = vol.set_index("date")[value_col]
    rows = []
    for mth in HORIZON_MONTHS:
        d0 = pd.Timestamp(year, mth, 1)
        d1 = pd.Timestamp(year + (mth == 12), mth % 12 + 1, 1)
        ndays = calendar.monthrange(year, mth)[1]
        s0, s1 = v.get(d0, np.nan), v.get(d1, np.nan)
        win = v[(v.index >= d0) & (v.index <= d1)]
        n_present = int(win.notna().sum())
        missing = n_present < ndays + 1
        if cap_flag is not None:
            sat_flag = bool(cap_flag(win).any())
        else:
            sat_flag = bool((win >= sat - tol).any()) if sat is not None else False
        reasons = []
        if missing:
            reasons.append("missing_observations")
        if sat_flag:
            reasons.append("saturated_or_above_nominal")
        rows.append(dict(
            scenario_id=f"H_{source}_{year}", family=FAMILY_HISTORICAL, year_or_draw=year,
            month=mth, days=ndays, storage_start_hm3=s0, storage_end_hm3=s1,
            dV_hm3=s1 - s0, inflow_hm3=np.nan, evaporation_hm3=np.nan, withdrawal_hm3=np.nan,
            spill_hm3=np.nan, availability_hm3=np.nan,
            storage_origin=_origin(source), inflow_origin="none", E_origin="none", R_origin="none",
            missing_flag=missing, saturated_flag=sat_flag,
            usable=not (missing or sat_flag), exclusion_reason=";".join(reasons), curtailed_flag=False))
    m = pd.DataFrame(rows)
    return Scenario(f"H_{source}_{year}", FAMILY_HISTORICAL, f"observed_storage_{source}", None,
                    {"source": source, "year": year, "sat_threshold_hm3": sat},
                    m, notes="Observed STORAGE only; no inflow, evaporation or withdrawal.")


def complete_years(vol: pd.DataFrame, source="portal", **kw) -> list[int]:
    ys = sorted(set(vol.date.dt.year))
    return [y for y in ys if pd.Timestamp(y, 7, 1) >= vol.date.min()
            and pd.Timestamp(y + 1, 1, 1) <= vol.date.max()]
