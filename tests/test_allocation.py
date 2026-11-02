import itertools
import numpy as np
import pytest

from src.evaluation.metrics import cvar, simulate_plan, summarize
from src.optimization.classical.baselines import plan_demand, plan_linear, plan_priority
from src.optimization.classical.milp import solve_milp
from src.optimization.problem import Instance


def tiny(seed=0, n=3, T=3, s0=60.0, v_dead=10.0, cap=200.0):
    rng = np.random.default_rng(seed)
    D = np.array([[8.0] * T, [12.0] * T])
    return Instance("t", "T", s0, v_dead, cap, D, np.array([3.0, 1.0]),
                    rng.uniform(0, 15, (n, T)), rng.uniform(1, 4, (n, T)),
                    np.full(n, 1.0 / n), list(range(n)), [30] * T)


def test_rationing_rule_by_hand():
    inst = Instance("h", "T", 30.0, 10.0, 100.0, np.array([[8.0], [12.0]]), np.array([3.0, 1.0]),
                    np.array([[2.0]]), np.array([[2.0]]), np.array([1.0]), [0], [30])
    r = simulate_plan(inst, np.array([[8.0], [12.0]]))
    # avail = 30+2-2-10 = 20 ; urban gets 8, irrigation min(12, 12)=12
    assert np.allclose(r["y"][0, :, 0], [8.0, 12.0]) and abs(r["S"][0, 1] - 10.0) < 1e-12
    inst.s0 = 20.0  # avail = 10 -> urban 8, irrigation 2 (priority to urban)
    r = simulate_plan(inst, np.array([[8.0], [12.0]]))
    assert np.allclose(r["y"][0, :, 0], [8.0, 2.0]) and abs(r["S"][0, 1] - 10.0) < 1e-12
    assert abs(r["loss"][0] - (3 * 0 + 1 * 10)) < 1e-12


def test_dead_volume_never_breached_by_withdrawals():
    inst = tiny(s0=40.0)
    r = simulate_plan(inst, inst.D)
    # evaporation may still lower storage below V_dead, but WITHDRAWALS never do:
    before = r["S"][:, :-1] + inst.I - inst.E            # storage before withdrawals
    floor = np.minimum(inst.v_dead, before)
    assert (r["S"][:, 1:] >= floor - 1e-9).all()
    assert (r["y"].sum(axis=1) <= np.maximum(0, before - inst.v_dead) + 1e-9).all()


def test_spill_above_cap_and_storage_nonneg():
    inst = tiny(s0=195.0, cap=200.0)
    r = simulate_plan(inst, np.zeros_like(inst.D))
    assert (r["S"] <= inst.cap + 1e-9).all() and (r["spill"] >= 0).all() and r["spill"].sum() > 0
    mass = inst.s0 + inst.I.sum(1) - inst.E.sum(1) - r["y"].sum(axis=(1, 2)) - r["spill"].sum(1) - r["S"][:, -1]
    assert np.abs(mass).max() < 1e-9


def test_cvar_known_values():
    loss = np.array([0.0, 10.0, 20.0, 30.0]); p = np.full(4, 0.25)
    assert abs(cvar(loss, p, 0.5) - 25.0) < 1e-12      # mean of worst 50 %
    assert abs(cvar(loss, p, 0.0) - 15.0) < 1e-12      # alpha=0 -> expectation
    assert abs(cvar(loss, p, 0.875) - 30.0) < 1e-12    # fractional tail still the max


def test_milp_objective_matches_simulation_and_beats_grid():
    for seed in range(4):
        inst = tiny(seed)
        for lam in (0.0, 0.6):
            r = solve_milp(inst, lam, alpha=0.7)
            assert r["optimal"]
            sm = summarize(inst, r["a"], alpha=0.7)
            sim_obj = (1 - lam) * sm["exp_loss"] + lam * sm["cvar_loss"]
            assert abs(sim_obj - r["objective"]) < 1e-4 + 1e-3 * 1e-1 * 0  # simulator == MILP model
            # no plan on a coarse grid does better than the MILP optimum
            levels = [np.linspace(0, inst.D[k, 0], 4) for k in range(2)]
            best = np.inf
            for a_u, a_i in itertools.product(itertools.product(levels[0], repeat=1), itertools.product(levels[1], repeat=1)):
                a = np.array([[a_u[0]] * 3, [a_i[0]] * 3])
                s = summarize(inst, a, alpha=0.7)
                best = min(best, (1 - lam) * s["exp_loss"] + lam * s["cvar_loss"])
            assert r["objective"] <= best + 1e-6


def test_baselines_feasible_and_priority_favours_urban():
    inst = tiny(s0=40.0)
    for f in (plan_demand, plan_linear, plan_priority):
        a = f(inst)
        assert (a >= -1e-12).all() and (a <= inst.D + 1e-9).all()
    lin, pri = plan_linear(inst), plan_priority(inst)
    assert pri[0].sum() >= lin[0].sum() - 1e-9 and pri[1].sum() <= lin[1].sum() + 1e-9


def test_lambda_one_never_worse_cvar_than_lambda_zero():
    inst = tiny(2, n=5)
    r0, r1 = solve_milp(inst, 0.0, 0.6), solve_milp(inst, 1.0, 0.6)
    s0, s1 = summarize(inst, r0["a"], 0.6), summarize(inst, r1["a"], 0.6)
    assert s1["cvar_loss"] <= s0["cvar_loss"] + 1e-6 and s0["exp_loss"] <= s1["exp_loss"] + 1e-6
