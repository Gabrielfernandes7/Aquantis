import calendar
import numpy as np
import pandas as pd
import pytest

from src.scenarios import historical as H, synthetic as S, temporal as T
from src.scenarios.generator import ScenarioGenerator
from src.scenarios.schema import HORIZON_MONTHS, Scenario, validate_scenario

CFG = S.ScenarioConfig("T", a_full=100.0, k=0.0, e_scale=1.0, r_m3s=1.0)  # k=0 -> A = 100 km²


def make_data(years=(2001, 2002, 3003 - 1000, 2004), slopes=(0.2, 0.5, 0.9, 1.4), start=1000.0,
              drop_day=None, sat_day=None):
    """Daily storage Jan 1 y .. Jan 5 y+1; storage falls by slope*… per day; fake NASA E=8 mm/day."""
    dates, vols = [], []
    for y, sl in zip(years, slopes):
        for d in pd.date_range(f"{y}-01-01", f"{y + 1}-01-05"):
            dates.append(d)
            vols.append(start - sl * (d - pd.Timestamp(f"{y}-01-01")).days * 0.5 + (y - 2001) * 0)
    vol = pd.DataFrame({"date": dates, "volume_hm3": vols}).drop_duplicates("date").sort_values("date")
    # make years independent: later year overwrites overlapping days -> keep last
    vol = pd.DataFrame({"date": dates, "volume_hm3": vols}).drop_duplicates("date", keep="last")
    vol = vol.sort_values("date").reset_index(drop=True)
    if drop_day is not None:
        vol = vol[vol.date != pd.Timestamp(drop_day)].reset_index(drop=True)
    if sat_day is not None:
        vol.loc[vol.date == pd.Timestamp(sat_day), "volume_hm3"] = 1752.36
    met = pd.DataFrame({"date": vol.date, "E_mm_day": 8.0})
    return vol, met


def gen(**kw):
    vol, met = make_data(**kw)
    return ScenarioGenerator(vol, met)


# ---------------- historical family ----------------
def test_horizon_extraction_and_date_alignment():
    vol, _ = make_data()
    sc = H.horizon_scenario(vol, 2002)
    m = sc.months
    assert list(m.month) == HORIZON_MONTHS and m.days.sum() == 184
    v = vol.set_index("date").volume_hm3
    assert m.storage_start_hm3.iloc[0] == v[pd.Timestamp(2002, 7, 1)]
    assert m.storage_end_hm3.iloc[-1] == v[pd.Timestamp(2003, 1, 1)]
    assert np.allclose(m.storage_end_hm3.values[:-1], m.storage_start_hm3.values[1:])  # continuity
    assert not validate_scenario(sc)


def test_historical_has_no_inflow_and_only_observed_storage():
    vol, _ = make_data()
    sc = H.horizon_scenario(vol, 2002)
    assert sc.months.inflow_hm3.isna().all() and (sc.months.inflow_origin == "none").all()
    assert set(sc.months.storage_origin) == {"portal_observed"}


def test_missing_data_kept_with_metadata():
    vol, _ = make_data(drop_day="2002-08-15")
    m = H.horizon_scenario(vol, 2002).months
    aug = m[m.month == 8].iloc[0]
    assert aug.missing_flag and not aug.usable and "missing_observations" in aug.exclusion_reason
    assert len(m) == 6  # exclusion retained, month not dropped


def test_saturation_flagged_and_excluded():
    vol, _ = make_data(sat_day="2002-09-10")
    m = H.horizon_scenario(vol, 2002).months
    sep = m[m.month == 9].iloc[0]
    assert sep.saturated_flag and not sep.usable
    assert m[m.month == 11].iloc[0].usable


def test_sources_not_mixed():
    vol, _ = make_data()
    p = H.horizon_scenario(vol, 2002, "portal")
    a = H.horizon_scenario(vol, 2002, "ana", sat=None)
    assert p.scenario_id != a.scenario_id and set(a.months.storage_origin) == {"ana_observed"}


# ---------------- synthetic family ----------------
def test_units_conversion():
    assert abs(S.M3S_TO_HM3_MONTH(1.0, 31) - 2.6784) < 1e-12
    # 8 mm over 100 km² = 0.8 hm³ per day
    sim = S.simulate(1000.0, [0.0], [8.0 * 31], [31], S.ScenarioConfig("u", 100, 0.0, 1.0, 0.0))
    assert abs(sim.evaporation_hm3.iloc[0] - 0.8 * 31) < 1e-9


def test_implied_inflow_mass_balance_in_replay():
    g = gen()
    sc, tab = g.generate_synthetic([CFG], n_draws=0, include_stress=False)
    assert sc, "expected replay scenarios"
    for s in sc:
        m = s.months
        resid = m.storage_start_hm3 + m.inflow_hm3 - m.evaporation_hm3 - m.withdrawal_hm3 - m.spill_hm3 - m.storage_end_hm3
        assert resid.abs().max() < 1e-6
        assert (m.inflow_origin == "implied_from_portal_dV").all()


def test_negative_implied_inflow_is_excluded_not_adjusted():
    g = gen()
    cfg = S.ScenarioConfig("neg", 100.0, 0.0, 0.0, 0.0)  # no E, no R: falling storage => I < 0
    tab = g.eligibility([cfg])
    assert (tab.reason == "negative_implied_inflow").any()
    assert not tab[tab.reason == "negative_implied_inflow"].eligible.any()
    assert (tab[tab.eligible].I_hm3 >= 0).all()
    sc, _ = g.generate_synthetic([cfg], n_draws=3)
    assert sc == []  # nothing generated, parameters never altered to force feasibility


def test_nonnegative_quantities_and_curtailment():
    sim = S.simulate(5.0, [0.0, 0.0], [240.0, 240.0], [31, 30], CFG)  # demand >> storage
    assert (sim[["storage_start_hm3", "storage_end_hm3", "evaporation_hm3", "withdrawal_hm3",
                 "spill_hm3"]] >= -1e-12).all().all()
    assert sim.curtailed_flag.any()


def test_spill_above_cap():
    cfg = S.ScenarioConfig("cap", 100, 0.0, 0.0, 0.0, cap_hm3=100.0)
    sim = S.simulate(90.0, [50.0], [0.0], [30], cfg)
    assert abs(sim.spill_hm3.iloc[0] - 40.0) < 1e-12 and sim.storage_end_hm3.iloc[0] == 100.0


def test_reproducibility_with_fixed_seed_and_seed_sensitivity():
    g = gen()
    a, _ = g.generate_synthetic([CFG], n_draws=15, seed=7)
    b, _ = g.generate_synthetic([CFG], n_draws=15, seed=7)
    c, _ = g.generate_synthetic([CFG], n_draws=15, seed=8)
    ma = pd.concat([s.months for s in a]).reset_index(drop=True)
    mb = pd.concat([s.months for s in b]).reset_index(drop=True)
    mc = pd.concat([s.months for s in c]).reset_index(drop=True)
    pd.testing.assert_frame_equal(ma, mb)
    assert not ma.inflow_hm3.equals(mc.inflow_hm3)


def test_block_bootstrap_uses_whole_blocks_from_history():
    g = gen()
    sc, tab = g.generate_synthetic([CFG], n_draws=20, seed=1, include_replay=False, include_stress=False)
    t = tab.set_index(["year", "month"])
    for s in sc:
        y1, y2 = map(int, s.months.year_or_draw.iloc[0].split("+"))
        want = [t.loc[(y1, m), "I_hm3"] for m in (7, 8, 9)] + [t.loc[(y2, m), "I_hm3"] for m in (10, 11, 12)]
        assert np.allclose(s.months.inflow_hm3.values, want)  # blocks copied intact, in order


def test_stress_picks_extremes():
    g = gen()
    sc, tab = g.generate_synthetic([CFG], n_draws=0, include_replay=False)
    drought = [s for s in sc if s.method == "stress_driest_block"][0]
    tc = tab[tab.eligible]
    tot = tc.groupby("year").I_hm3.sum()
    full = [y for y in tot.index if (tc[tc.year == y].month.nunique() == 6)]
    assert int(drought.scenario_id.rsplit("_", 1)[1]) == min(full, key=lambda y: tot[y])


def test_provenance_and_no_mixing_of_observed_and_synthetic():
    g = gen()
    syn, _ = g.generate_synthetic([CFG], n_draws=3)
    hist = g.generate_historical()
    assert not g.validate(syn + hist)
    assert all(s.scenario_id.startswith("H_") for s in hist) and all(s.scenario_id.startswith("S_") for s in syn)
    for s in syn:
        assert (s.months.R_origin == "hypothesis").all()
        assert not set(s.months.inflow_origin) & {"observed", "measured"}
        if s.method != "conditioned_replay":
            assert (s.months.storage_origin == "simulated").all()
    # tampering is detected
    bad = syn[0]
    bad.months.loc[0, "inflow_origin"] = "observed"
    assert validate_scenario(bad)
    h = hist[0]
    h.months.loc[0, "inflow_hm3"] = 1.0
    assert validate_scenario(h)


def test_mass_balance_violation_detected():
    g = gen()
    syn, _ = g.generate_synthetic([CFG], n_draws=1)
    s = syn[0]
    s.months.loc[2, "storage_end_hm3"] += 5.0
    assert any("mass-balance" in e or "continuous" in e for e in validate_scenario(s))


def test_lag1_autocorr_known_structure():
    rng = np.random.default_rng(0)
    base = rng.normal(size=(200, 1))
    df = pd.DataFrame(np.repeat(base, 6, axis=1) + 0.05 * rng.normal(size=(200, 6)), columns=HORIZON_MONTHS)
    assert T.lag1_autocorr(df)["r_lag1"] > 0.9


def test_blocks_validation():
    assert T.blocks(3) == [[7, 8, 9], [10, 11, 12]]
    with pytest.raises(ValueError):
        T.blocks(4)
