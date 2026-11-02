"""Plan evaluation by simulation (the single source of truth for hydrological metrics)."""
import numpy as np

from src.optimization.problem import Instance


def simulate_plan(inst: Instance, a: np.ndarray) -> dict:
    """a: (2, 6) planned allocation. Returns per-scenario arrays."""
    n, T = inst.I.shape
    y = np.zeros((n, 2, T)); S = np.zeros((n, T + 1)); Z = np.zeros((n, T))
    S[:, 0] = inst.s0
    for t in range(T):
        X = S[:, t] + inst.I[:, t] - inst.E[:, t] - inst.v_dead
        avail = np.maximum(0.0, X)
        y[:, 0, t] = np.minimum(a[0, t], avail)
        y[:, 1, t] = np.minimum(a[1, t], avail - y[:, 0, t])
        pre = S[:, t] + inst.I[:, t] - inst.E[:, t] - y[:, 0, t] - y[:, 1, t]
        Z[:, t] = np.maximum(0.0, pre - inst.cap)
        S[:, t + 1] = pre - Z[:, t]
    if (S < -1e-9).any():
        raise ValueError("negative storage: instance outside the model's validity")
    d = inst.D[None] - y
    loss = (inst.w[None, :, None] * d).sum(axis=(1, 2))
    return dict(y=y, d=d, S=S, spill=Z, loss=loss)


def cvar(loss: np.ndarray, p: np.ndarray, alpha: float) -> float:
    """Rockafellar–Uryasev CVaR of a discrete distribution (exact, with fractional tail)."""
    order = np.argsort(-loss)
    tail, acc, cv = 1.0 - alpha, 0.0, 0.0
    for i in order:
        take = min(p[i], tail - acc)
        if take <= 0:
            break
        cv += take * loss[i]; acc += take
    return cv / tail


def summarize(inst: Instance, a: np.ndarray, alpha: float = 0.8) -> dict:
    r = simulate_plan(inst, a)
    d = r["d"]; p = inst.p
    return dict(
        exp_loss=float(p @ r["loss"]), cvar_loss=float(cvar(r["loss"], p, alpha)),
        worst_loss=float(r["loss"].max()),
        exp_deficit_urban_hm3=float(p @ d[:, 0].sum(1)), exp_deficit_irrig_hm3=float(p @ d[:, 1].sum(1)),
        exp_deficit_urban_pct=float(100 * (p @ d[:, 0].sum(1)) / inst.D[0].sum()),
        exp_deficit_irrig_pct=float(100 * (p @ d[:, 1].sum(1)) / inst.D[1].sum()),
        exp_served_hm3=float(p @ r["y"].sum(axis=(1, 2))),
        reliability_urban=float(p @ (d[:, 0].sum(1) < 1e-6)),
        reliability_irrig=float(p @ (d[:, 1].sum(1) < 1e-6)),
        reliability_all=float(p @ (d.sum(axis=(1, 2)) < 1e-6)),
        exp_final_storage_hm3=float(p @ r["S"][:, -1]),
        min_final_storage_hm3=float(r["S"][:, -1].min()),
        exp_spill_hm3=float(p @ r["spill"].sum(1)),
    )
