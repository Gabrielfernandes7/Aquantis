"""Family B: synthetic scenarios conditioned on explicit HYPOTHESES (not observed inflow).

Implied monthly inflow  I = dV + E + R   (Z = 0, full unsaturated months only)
  dV : observed storage change (Portal)            -> observation
  E  : scale * Penman(NASA POWER) * A(V)            -> estimate x geometry hypothesis
  R  : constant withdrawal, m³/s                    -> hypothesis
Simulation step (bootstrap/stress):  S' = S + I - E(S) - R - Z with E,R,S >= 0 enforced by
physical limits (curtailment is flagged, never silently balanced) and spill Z above the cap.
"""
import calendar
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from src.hydrology.evaporation import area_km2
from src.scenarios.schema import (FAMILY_SYNTHETIC, HORIZON_MONTHS, Scenario)

M3S_TO_HM3_MONTH = lambda r, days: r * 86400 * days / 1e6


@dataclass(frozen=True)
class ScenarioConfig:
    name: str
    a_full: float      # km², hypothesis
    k: float           # hypothesis
    e_scale: float     # multiplier on Penman estimate (sensitivity)
    r_m3s: float       # hypothesis
    cap_hm3: float = 1752.36  # Portal saturation level used as storage cap (hypothesis)
    v_full: float = 1940.0

    def as_dict(self):
        return asdict(self)


# Recovered from Experiment 04 (notebook section 4 / report 4.4). PROVISIONAL.
CONFIG_A = ScenarioConfig("A_low", 150, 0.8, 0.7, 2.65)
CONFIG_B = ScenarioConfig("B_mid", 200, 0.7, 1.0, 4.5)
CONFIG_C = ScenarioConfig("C_high", 250, 0.5, 1.3, 5.3)
DEFAULT_CONFIGS = [CONFIG_A, CONFIG_B, CONFIG_C]


def _area(v, cfg):
    return area_km2(v, a_full=cfg.a_full, v_full=cfg.v_full, k=cfg.k)


def monthly_implied_table(x: pd.DataFrame, cfg: ScenarioConfig) -> pd.DataFrame:
    """x: output of sensitivity.prepare (valid daily rows: date, v0, dV, vmean, E_mm_day).
    One row per (year, month) for months 7..12. ``complete`` = every calendar day valid."""
    d = x[x.date.dt.month.isin(HORIZON_MONTHS)].copy()
    d["year"], d["month"] = d.date.dt.year, d.date.dt.month
    d["E_day"] = cfg.e_scale * d.E_mm_day * _area(d.vmean.values, cfg) * 1e-3
    g = d.groupby(["year", "month"]).agg(n=("dV", "size"), dV_hm3=("dV", "sum"),
                                         E_hm3=("E_day", "sum"), s0=("v0", "first")).reset_index()
    g["days"] = [calendar.monthrange(y, m)[1] for y, m in zip(g.year, g.month)]
    g["complete"] = g.n == g.days
    g["R_hm3"] = [M3S_TO_HM3_MONTH(cfg.r_m3s, dd) for dd in g.days]
    g["I_hm3"] = g.dV_hm3 + g.E_hm3 + g.R_hm3
    g["eligible"] = g.complete & (g.I_hm3 >= 0)
    g["reason"] = np.where(~g.complete, "incomplete_or_saturated_month",
                           np.where(g.I_hm3 < 0, "negative_implied_inflow", ""))
    g["config"] = cfg.name
    return g


def monthly_e_mm(met: pd.DataFrame) -> pd.DataFrame:
    """Monthly Penman depth (mm) from ALL days (independent of storage validity)."""
    d = met.assign(year=met.date.dt.year, month=met.date.dt.month)
    return d.groupby(["year", "month"]).E_mm_day.sum().rename("e_mm").reset_index()


def simulate(start_storage: float, inflow: list[float], e_mm: list[float], days: list[int],
             cfg: ScenarioConfig) -> pd.DataFrame:
    """Storage simulation with explicit physical limits. Returns monthly rows."""
    s = float(start_storage)
    rows = []
    for I, e, nd in zip(inflow, e_mm, days):
        E = cfg.e_scale * e * float(_area(s, cfg)) * 1e-3
        R = M3S_TO_HM3_MONTH(cfg.r_m3s, nd)
        E_eff = min(E, s + I)
        R_eff = min(R, s + I - E_eff)
        curtailed = (E_eff < E - 1e-12) or (R_eff < R - 1e-12)
        s_pre = s + I - E_eff - R_eff
        Z = max(0.0, s_pre - cfg.cap_hm3)
        s_new = s_pre - Z
        rows.append(dict(storage_start_hm3=s, storage_end_hm3=s_new, inflow_hm3=I,
                         evaporation_hm3=E_eff, withdrawal_hm3=R_eff, spill_hm3=Z,
                         curtailed_flag=curtailed))
        s = s_new
    return pd.DataFrame(rows)


def build_scenario(sid, method, seed, cfg, sim: pd.DataFrame, year_or_draw, inflow_origin,
                   days, usable=True, notes="") -> Scenario:
    m = sim.copy()
    m.insert(0, "scenario_id", sid)
    m.insert(1, "family", FAMILY_SYNTHETIC)
    m.insert(2, "year_or_draw", year_or_draw)
    m.insert(3, "month", HORIZON_MONTHS)
    m.insert(4, "days", days)
    m["dV_hm3"] = m.storage_end_hm3 - m.storage_start_hm3
    m["availability_hm3"] = m.storage_start_hm3 + m.inflow_hm3 - m.evaporation_hm3
    m["storage_origin"] = "simulated" if method != "conditioned_replay" else "portal_observed"
    m["inflow_origin"] = inflow_origin
    m["E_origin"] = "estimate_penman_nasa_power_x_hypothesis_geometry"
    m["R_origin"] = "hypothesis"
    m["missing_flag"] = False
    m["saturated_flag"] = m.spill_hm3 > 0
    m["usable"] = usable
    m["exclusion_reason"] = ""
    return Scenario(sid, FAMILY_SYNTHETIC, method, seed, cfg.as_dict(), m, notes)
