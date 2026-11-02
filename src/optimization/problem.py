"""Allocation problem instance (urban + irrigation, July–December, monthly).

Decision (first stage, identical in every scenario): planned allocation a[k, t] in hm³,
k ∈ {urban, irrigation}, 0 ≤ a ≤ demand.
Operation (implementable rule, no look-ahead): in month t,
    avail = max(0, S + I − E − V_dead)
    y_urban = min(a_urban, avail);  y_irrig = min(a_irrig, avail − y_urban)
    S' = S + I − E − y_urban − y_irrig − spill,   spill = max(0, ·− cap)
Loss of a scenario: L = Σ_k w_k Σ_t (D_kt − y_kt).

HYPOTHESES (not observations): demands, sector weights, V_dead, cap, E fixed along a reference
path (E does not react to the decision), equal weights across historical source years.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from src.scenarios import synthetic as S

SECTORS = ["urban", "irrigation"]
M3S = 86400 / 1e6  # m³/s sustained for one day → hm³

# HYPOTHESIS: demand profile in m³/s (no demand data available).
DEMAND_URBAN_M3S = [1.5] * 6
DEMAND_IRRIG_M3S = [3.0, 4.0, 5.0, 5.0, 4.0, 3.0]
WEIGHTS = np.array([3.0, 1.0])  # HYPOTHESIS: urban priority 3× irrigation


@dataclass
class Instance:
    name: str
    config_name: str
    s0: float
    v_dead: float
    cap: float
    D: np.ndarray          # (2, 6) hm³
    w: np.ndarray          # (2,)
    I: np.ndarray          # (S, 6) implied inflow, hm³  (NOT observed inflow)
    E: np.ndarray          # (S, 6) evaporation along a reference path, hm³
    p: np.ndarray          # (S,) weights (assumption: equal across source years)
    source_years: list
    days: list
    meta: dict = field(default_factory=dict)

    @property
    def n_scen(self):
        return self.I.shape[0]


def demand_matrix(days: list[int]) -> np.ndarray:
    d = np.array([[r * M3S * nd for r, nd in zip(DEMAND_URBAN_M3S, days)],
                  [r * M3S * nd for r, nd in zip(DEMAND_IRRIG_M3S, days)]])
    return d


def make_instance(seq: pd.DataFrame, cfg: S.ScenarioConfig, s0: float, name: str,
                  v_dead: float | None = None, demand_scale: float = 1.0,
                  years: list | None = None) -> Instance:
    """seq: ScenarioGenerator.inflow_sequences output (year, month, days, I_hm3, e_mm).
    The reference evaporation path is simulated with the configuration's baseline withdrawal."""
    v_dead = cfg.dead_volume_hm3 if v_dead is None else v_dead
    ys = sorted(seq.year.unique()) if years is None else list(years)
    days = [int(d) for d in seq[seq.year == ys[0]].sort_values("month").days]
    I, E = [], []
    for y in ys:
        g = seq[seq.year == y].sort_values("month")
        sim = S.simulate(s0, g.I_hm3.tolist(), g.e_mm.tolist(), days, cfg)
        if sim.curtailed_flag.any():
            raise ValueError(f"reference path curtailed for year {y} (s0={s0}); instance unusable")
        I.append(g.I_hm3.values); E.append(sim.evaporation_hm3.values)
    n = len(ys)
    return Instance(name, cfg.name, float(s0), float(v_dead), float(cfg.cap_hm3),
                    demand_matrix(days) * demand_scale, WEIGHTS.copy(), np.array(I), np.array(E),
                    np.full(n, 1.0 / n), ys, days,
                    meta=dict(demand_scale=demand_scale, cfg=cfg.as_dict()))
