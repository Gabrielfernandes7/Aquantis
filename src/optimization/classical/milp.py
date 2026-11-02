"""MILP + CVaR (Pyomo/HiGHS) for the planned-allocation problem.

min (1-λ)·Σ p_s L_s + λ·CVaR_α(L) + ε·Σ spill
CVaR via Rockafellar–Uryasev: η + Σ p_s ζ_s /(1-α),  ζ_s ≥ L_s − η, ζ_s ≥ 0.
Binaries encode the exact min/max of the rationing rule (they make this a MILP).
"""
import numpy as np
import pyomo.environ as pyo

from src.optimization.problem import Instance, SECTORS

EPS_SPILL = 1e-4


def build_milp(inst: Instance, lam: float, alpha: float = 0.8, discretization=None) -> pyo.ConcreteModel:
    n, T = inst.I.shape
    M = inst.cap + float(inst.I.max()) + inst.D.sum() + 100.0
    m = pyo.ConcreteModel()
    m.Sc, m.Tm, m.Kk = pyo.RangeSet(0, n - 1), pyo.RangeSet(0, T - 1), pyo.RangeSet(0, 1)
    m.a = pyo.Var(m.Kk, m.Tm, bounds=lambda m, k, t: (0, float(inst.D[k, t])))
    m.S = pyo.Var(m.Sc, pyo.RangeSet(0, T), bounds=(0, inst.cap))
    m.y = pyo.Var(m.Sc, m.Kk, m.Tm, within=pyo.NonNegativeReals)
    m.av = pyo.Var(m.Sc, m.Tm, within=pyo.NonNegativeReals)
    m.Z = pyo.Var(m.Sc, m.Tm, within=pyo.NonNegativeReals)
    m.c = pyo.Var(m.Sc, m.Tm, within=pyo.Binary)
    m.bu = pyo.Var(m.Sc, m.Tm, within=pyo.Binary)
    m.bi = pyo.Var(m.Sc, m.Tm, within=pyo.Binary)
    m.eta = pyo.Var(within=pyo.Reals)
    m.zeta = pyo.Var(m.Sc, within=pyo.NonNegativeReals)
    I, E, D, w, p = inst.I, inst.E, inst.D, inst.w, inst.p
    m.cons = pyo.ConstraintList()
    if discretization is not None:
        # a[k,t] = D[k,t]·level(group): integer level index per (sector, block) via binaries
        from src.optimization.discrete import BLOCKS, group_index
        nb = discretization.bits_per_group
        m.q = pyo.Var(pyo.RangeSet(0, 3), pyo.RangeSet(0, nb - 1), within=pyo.Binary)
        top = float(2 ** nb - 1)
        for k in range(2):
            for b, months in enumerate(BLOCKS):
                g = group_index(k, b)
                idx = sum((2 ** j) * m.q[g, j] for j in range(nb))
                for t in months:
                    m.cons.add(m.a[k, t] == float(inst.D[k, t]) * idx / top)
    for s in m.Sc:
        m.cons.add(m.S[s, 0] == inst.s0)
        for t in m.Tm:
            X = m.S[s, t] + float(I[s, t] - E[s, t] - inst.v_dead)
            m.cons.add(m.av[s, t] >= X)
            m.cons.add(m.av[s, t] <= X + M * (1 - m.c[s, t]))
            m.cons.add(m.av[s, t] <= M * m.c[s, t])
            m.cons.add(X <= M * m.c[s, t])
            # urban first
            m.cons.add(m.y[s, 0, t] <= m.a[0, t])
            m.cons.add(m.y[s, 0, t] <= m.av[s, t])
            m.cons.add(m.y[s, 0, t] >= m.a[0, t] - M * (1 - m.bu[s, t]))
            m.cons.add(m.y[s, 0, t] >= m.av[s, t] - M * m.bu[s, t])
            rem = m.av[s, t] - m.y[s, 0, t]
            m.cons.add(m.y[s, 1, t] <= m.a[1, t])
            m.cons.add(m.y[s, 1, t] <= rem)
            m.cons.add(m.y[s, 1, t] >= m.a[1, t] - M * (1 - m.bi[s, t]))
            m.cons.add(m.y[s, 1, t] >= rem - M * m.bi[s, t])
            m.cons.add(m.S[s, t + 1] == m.S[s, t] + float(I[s, t] - E[s, t])
                       - m.y[s, 0, t] - m.y[s, 1, t] - m.Z[s, t])
    L = {s: sum(float(w[k]) * (float(D[k, t]) - m.y[s, k, t]) for k in range(2) for t in range(T))
         for s in range(n)}
    for s in m.Sc:
        m.cons.add(m.zeta[s] >= L[s] - m.eta)
    exp_loss = sum(float(p[s]) * L[s] for s in range(n))
    cvar = m.eta + sum(float(p[s]) * m.zeta[s] for s in range(n)) / (1 - alpha)
    m.obj = pyo.Objective(expr=(1 - lam) * exp_loss + lam * cvar
                          + EPS_SPILL * sum(m.Z[s, t] for s in m.Sc for t in m.Tm))
    return m


def solve_milp(inst: Instance, lam: float, alpha: float = 0.8, time_limit: float = 120.0,
               gap: float = 1e-6, discretization=None) -> dict:
    m = build_milp(inst, lam, alpha, discretization)
    opt = pyo.SolverFactory("appsi_highs")
    opt.config.time_limit = time_limit
    opt.config.mip_gap = gap
    opt.config.stream_solver = False
    res = opt.solve(m)  # raises if no solution could be loaded
    term = str(res.solver.termination_condition)
    ok = term.lower().endswith("optimal")
    T = inst.I.shape[1]
    a = np.array([[pyo.value(m.a[k, t]) for t in range(T)] for k in range(2)])
    return dict(a=a, objective=float(pyo.value(m.obj)), optimal=ok,
                termination=term,
                best_bound=float(res.problem.lower_bound) if res.problem.lower_bound is not None else np.nan,
                n_binaries=3 * inst.n_scen * T)
