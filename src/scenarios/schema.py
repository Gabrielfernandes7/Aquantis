"""Scenario data model for the Orós case study.

UNITS: volumes and flows per month in hm³ (hm³/month); rates in m³/s only in configs.
HORIZON: July–December (calendar months 7..12), 6 monthly steps.

Provenance vocabulary (never 'observed inflow' anywhere):
  storage_origin : portal_observed | ana_observed | simulated
  inflow_origin  : none | implied_from_portal_dV | resampled_implied | simulated_block
  E_origin       : none | estimate_penman_nasa_power x hypothesis_geometry
  R_origin       : none | hypothesis
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

HORIZON_MONTHS = [7, 8, 9, 10, 11, 12]
FAMILY_HISTORICAL = "historical_storage"
FAMILY_SYNTHETIC = "synthetic"
FORBIDDEN_INFLOW_ORIGINS = {"observed", "measured", "historical_inflow"}

MONTH_COLUMNS = [
    "scenario_id", "family", "year_or_draw", "month", "days",
    "storage_start_hm3", "storage_end_hm3", "dV_hm3",
    "inflow_hm3", "evaporation_hm3", "withdrawal_hm3", "spill_hm3",
    "availability_hm3", "dead_volume_hm3", "operational_availability_hm3",
    "storage_origin", "inflow_origin", "E_origin", "R_origin",
    "missing_flag", "saturated_flag", "usable", "exclusion_reason", "curtailed_flag",
    "inflow_floored_flag",
]


@dataclass
class Scenario:
    scenario_id: str
    family: str
    method: str
    seed: int | None
    config: dict
    months: pd.DataFrame
    notes: str = ""

    def meta(self) -> dict:
        m = self.months
        return {
            "scenario_id": self.scenario_id, "family": self.family, "method": self.method,
            "seed": self.seed, "config": str(self.config),
            "initial_storage_hm3": float(m["storage_start_hm3"].iloc[0]),
            "n_months": len(m), "n_unusable_months": int((~m["usable"]).sum()),
            "any_saturated": bool(m["saturated_flag"].any()),
            "any_missing": bool(m["missing_flag"].any()),
            "total_inflow_hm3": float(m["inflow_hm3"].sum(skipna=False)) if m["inflow_hm3"].notna().all() else np.nan,
            "storage_origin": ",".join(sorted(m["storage_origin"].unique())),
            "inflow_origin": ",".join(sorted(m["inflow_origin"].unique())),
            "notes": self.notes,
        }


def validate_scenario(sc: Scenario, tol: float = 1e-9) -> list[str]:
    """Return a list of violations (empty = valid). Checks horizon, units/columns,
    non-negativity, provenance and (synthetic) mass-balance identity."""
    errs = []
    m = sc.months
    if list(m["month"]) != HORIZON_MONTHS:
        errs.append("horizon must be months 7..12 in order")
    missing = [c for c in MONTH_COLUMNS if c not in m.columns]
    if missing:
        errs.append(f"missing columns {missing}")
        return errs
    for c in ["storage_start_hm3", "storage_end_hm3", "evaporation_hm3", "withdrawal_hm3",
              "spill_hm3", "availability_hm3", "inflow_hm3", "dead_volume_hm3",
              "operational_availability_hm3"]:
        if (m[c].dropna() < -tol).any():
            errs.append(f"negative values in {c}")
    if set(m["inflow_origin"]) & FORBIDDEN_INFLOW_ORIGINS:
        errs.append("inflow labelled as observed")
    if sc.family == FAMILY_HISTORICAL:
        if m["inflow_hm3"].notna().any() or set(m["inflow_origin"]) != {"none"}:
            errs.append("historical-storage scenario must not carry inflow")
        if not set(m["storage_origin"]) <= {"portal_observed", "ana_observed"}:
            errs.append("historical scenario with non-observed storage")
    elif sc.family == FAMILY_SYNTHETIC:
        if (m["inflow_origin"] == "none").any():
            errs.append("synthetic scenario without inflow origin")
        if (m["R_origin"] != "hypothesis").any():
            errs.append("synthetic withdrawals must be labelled hypothesis")
        bal = (m.storage_start_hm3 + m.inflow_hm3 - m.evaporation_hm3 - m.withdrawal_hm3
               - m.spill_hm3 - m.storage_end_hm3).abs()
        if (bal > 1e-6).any():
            errs.append("mass-balance identity violated")
        if not np.allclose(m.storage_end_hm3.values[:-1], m.storage_start_hm3.values[1:], atol=1e-6):
            errs.append("storage not continuous between months")
    else:
        errs.append("unknown family")
    return errs
