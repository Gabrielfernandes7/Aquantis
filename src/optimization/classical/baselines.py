"""Reference allocation plans (no optimisation): E01 linear sharing, E02 priority sharing."""
import numpy as np

from src.optimization.problem import Instance


def _expected_available(inst: Instance) -> float:
    """Expected water above dead volume over the horizon (simple stock-flow, no dynamics)."""
    return max(0.0, inst.s0 - inst.v_dead + float(inst.p @ inst.I.sum(1)) - float(inst.p @ inst.E.sum(1)))


def plan_demand(inst: Instance) -> np.ndarray:
    """Demand-following: ask for the full demand every month (no foresight)."""
    return inst.D.copy()


def plan_linear(inst: Instance) -> np.ndarray:
    """E01: the same fraction φ of every demand, φ = min(1, expected availability / total demand)."""
    phi = min(1.0, _expected_available(inst) / inst.D.sum())
    return phi * inst.D


def plan_priority(inst: Instance) -> np.ndarray:
    """E02: urban demand is covered first from the expected availability, irrigation gets the rest."""
    av = _expected_available(inst)
    fu = min(1.0, av / inst.D[0].sum())
    fi = min(1.0, max(0.0, av - fu * inst.D[0].sum()) / inst.D[1].sum())
    return np.vstack([fu * inst.D[0], fi * inst.D[1]])
