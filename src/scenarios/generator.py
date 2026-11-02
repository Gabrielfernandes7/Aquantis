"""ScenarioGenerator: reproducible scenario generation (no optimisation here)."""
from pathlib import Path

import numpy as np
import pandas as pd

from src.hydrology.sensitivity import prepare
from src.scenarios import historical as H
from src.scenarios import synthetic as S
from src.scenarios import temporal as T
from src.scenarios.schema import HORIZON_MONTHS, MONTH_COLUMNS, Scenario, validate_scenario


class ScenarioGenerator:
    def __init__(self, portal_vol: pd.DataFrame, met: pd.DataFrame, ana: pd.DataFrame | None = None):
        """portal_vol: date, volume_hm3. met: date, E_mm_day (+ meteorology). ana: loader output."""
        self.vol = portal_vol.sort_values("date").reset_index(drop=True)
        self.met = met
        self.ana = ana
        self.x = prepare(self.vol, met)
        self.e_month = S.monthly_e_mm(met).set_index(["year", "month"]).e_mm
        self._v = self.vol.set_index("date").volume_hm3

    # ---- Family A -------------------------------------------------------------------
    def generate_historical(self) -> list[Scenario]:
        out = [H.horizon_scenario(self.vol, y, "portal") for y in H.complete_years(self.vol)]
        if self.ana is not None:
            a = self.ana.rename(columns={"useful_volume_hm3": "volume_hm3"})[["date", "volume_hm3"]]
            out += [H.horizon_scenario(a, y, "ana", sat=None,
                                       cap_flag=lambda w: w > 1940.0)
                    for y in H.complete_years(a)]
        return out

    # ---- Family B -------------------------------------------------------------------
    def eligibility(self, cfgs, negative_policy="exclude") -> pd.DataFrame:
        tab = pd.concat([S.monthly_implied_table(self.x, c) for c in cfgs], ignore_index=True)
        return S.apply_negative_policy(tab, negative_policy)

    def inflow_sequences(self, cfg, negative_policy="exclude") -> pd.DataFrame:
        """Jul–Dec implied-inflow sequences, one block per source year, for the optimisation stage.
        Columns: year, month, days, I_hm3, I_raw_hm3, floored, e_mm. Only complete-and-eligible years."""
        tab = self.eligibility([cfg], negative_policy)
        ok = T.eligible_years(tab, HORIZON_MONTHS)
        d = tab[tab.year.isin(ok)][["year", "month", "days", "I_hm3", "I_raw_hm3", "floored"]].copy()
        d["e_mm"] = [float(self.e_month.loc[(y, m)]) for y, m in zip(d.year, d.month)]
        d["storage_jul1_hm3_source"] = [float(self._v.loc[pd.Timestamp(y, 7, 1)]) for y in d.year]
        return d.sort_values(["year", "month"]).reset_index(drop=True)

    def _days(self, year_months):
        import calendar
        return [calendar.monthrange(y, m)[1] for y, m in year_months]

    def _simulate_from_sources(self, cfg, tab, src_years, block_len, sid, method, seed, origin, notes=""):
        """Build one synthetic path from blocks copied from ``src_years`` (one per block).
        Start storage = observed Jul-1 volume of the first block's source year; target year labels
        are synthetic (calendar days from a non-leap reference year 2001)."""
        t = tab[tab.config == cfg.name].set_index(["year", "month"])
        infl, emm = [], []
        for b, y in zip(T.blocks(block_len), src_years):
            for m in b:
                infl.append(float(t.loc[(y, m), "I_hm3"]))
                emm.append(float(self.e_month.loc[(y, m)]))
        s0 = float(self._v.loc[pd.Timestamp(src_years[0], 7, 1)])
        days = self._days([(2001, m) for m in HORIZON_MONTHS])
        sim = S.simulate(s0, infl, emm, days, cfg)
        return S.build_scenario(sid, method, seed, cfg, sim, "+".join(map(str, src_years)), origin, days,
                                notes=notes)

    def generate_synthetic(self, cfgs=None, n_draws=50, seed=20260101, block_len=3,
                           include_replay=True, include_stress=True) -> tuple[list[Scenario], pd.DataFrame]:
        cfgs = cfgs or S.DEFAULT_CONFIGS
        tab = self.eligibility(cfgs)
        out = []
        for ci, cfg in enumerate(cfgs):
            tc = tab[tab.config == cfg.name]
            # (i) conditioned replay: observed dV + assumed E,R -> implied I; storage = observed
            if include_replay:
                for y, g in tc.groupby("year"):
                    g = g.set_index("month")
                    if all(m in g.index and g.loc[m, "eligible"] for m in HORIZON_MONTHS):
                        s = g.s0.iloc[0]
                        rows, st = [], float(g.loc[7, "s0"])
                        for m in HORIZON_MONTHS:
                            rows.append(dict(storage_start_hm3=st, storage_end_hm3=st + g.loc[m, "dV_hm3"],
                                             inflow_hm3=g.loc[m, "I_hm3"], evaporation_hm3=g.loc[m, "E_hm3"],
                                             withdrawal_hm3=g.loc[m, "R_hm3"], spill_hm3=0.0,
                                             curtailed_flag=False))
                            st = st + g.loc[m, "dV_hm3"]
                        out.append(S.build_scenario(
                            f"S_{cfg.name}_replay_{y}", "conditioned_replay", None, cfg,
                            pd.DataFrame(rows), y, "implied_from_portal_dV",
                            [int(g.loc[m, "days"]) for m in HORIZON_MONTHS],
                            notes="Observed dV + hypothesised E,R; inflow is IMPLIED, not observed."))
            # (ii) seasonal block bootstrap
            for d in range(n_draws):
                sd = seed + ci * 1000 + d
                src = T.seasonal_block_draw(tc.rename(columns={}), block_len, np.random.default_rng(sd))
                if src is None:
                    break
                out.append(self._simulate_from_sources(
                    cfg, tab, src, block_len, f"S_{cfg.name}_sbb{block_len}_{d:03d}",
                    f"seasonal_block_bootstrap_L{block_len}", sd, "resampled_implied",
                    "Blocks of implied inflow copied from historical years; synthetic, not a forecast."))
            # (iii) stress: driest / drought→recovery from eligible years (deterministic)
            if include_stress:
                y_ok = T.eligible_years(tc, HORIZON_MONTHS)
                if y_ok:
                    tot = {y: tc[tc.year == y].I_hm3.sum() for y in y_ok}
                    dry = min(tot, key=tot.get)
                    out.append(self._simulate_from_sources(
                        cfg, tab, [dry, dry], 3, f"S_{cfg.name}_stress_drought_{dry}",
                        "stress_driest_block", None, "resampled_implied",
                        f"Driest eligible Jul–Dec under this config (year {dry})."))
                ya, yb = T.eligible_years(tc, [7, 8, 9]), T.eligible_years(tc, [10, 11, 12])
                # recovery must START from a low-storage state (lowest tercile of Jul-1 storage)
                if ya:
                    st0 = {y: float(self._v.loc[pd.Timestamp(y, 7, 1)]) for y in ya}
                    thr = np.quantile(list(st0.values()), 1 / 3)
                    ya = [y for y in ya if st0[y] <= thr]
                if ya and yb:
                    s1 = {y: tc[(tc.year == y) & tc.month.isin([7, 8, 9])].I_hm3.sum() for y in ya}
                    s2 = {y: tc[(tc.year == y) & tc.month.isin([10, 11, 12])].I_hm3.sum() for y in yb}
                    dry, wet = min(s1, key=s1.get), max(s2, key=s2.get)
                    out.append(self._simulate_from_sources(
                        cfg, tab, [dry, wet], 3, f"S_{cfg.name}_stress_recovery_{dry}_{wet}",
                        "stress_drought_then_recovery", None, "resampled_implied",
                        f"Driest Jul–Sep ({dry}) among low-storage starts, then wettest Oct–Dec ({wet}); a COMPOSITE, "
                        "not a historical sequence."))
        return out, tab

    # ---- validation / IO --------------------------------------------------------------
    @staticmethod
    def validate(scenarios) -> dict:
        return {s.scenario_id: e for s in scenarios if (e := validate_scenario(s))}

    @staticmethod
    def to_tables(scenarios) -> tuple[pd.DataFrame, pd.DataFrame]:
        meta = pd.DataFrame([s.meta() for s in scenarios])
        months = pd.concat([s.months[MONTH_COLUMNS] for s in scenarios], ignore_index=True)
        return meta, months

    @staticmethod
    def save(scenarios, eligibility, outdir="data/processed/scenarios"):
        Path(outdir).mkdir(parents=True, exist_ok=True)
        meta, months = ScenarioGenerator.to_tables(scenarios)
        meta.to_csv(f"{outdir}/scenario_metadata.csv", index=False)
        months.to_csv(f"{outdir}/scenario_months.csv", index=False)
        eligibility.to_csv(f"{outdir}/block_eligibility.csv", index=False)
        return meta, months
