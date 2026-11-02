"""Discretised decision space for the QUBO/QAOA experiments.

4 groups = {urban, irrigation} × {Jul–Sep, Oct–Dec}, in order (urban,B1),(urban,B2),(irrig,B1),(irrig,B2).
Each group picks a fraction of its block demand from 2**b equally spaced levels in [0, 1]
(b = bits per group; b=2 → {0, 1/3, 2/3, 1}); index = Σ_j bit[b*g + j]·2**j  (little-endian per group).
Total bits = 4·b. The objective remains the EXACT simulated one (rationing + CVaR); only the
decision grid is coarse.
"""
import itertools
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.evaluation.metrics import summarize
from src.optimization.problem import Instance

BLOCKS = [[0, 1, 2], [3, 4, 5]]
N_GROUPS = 4


def group_index(sector: int, block: int) -> int:
    return sector * 2 + block


@dataclass(frozen=True)
class Discretization:
    bits_per_group: int = 2

    @property
    def levels(self) -> np.ndarray:
        return np.linspace(0.0, 1.0, 2 ** self.bits_per_group)

    @property
    def n_bits(self) -> int:
        return N_GROUPS * self.bits_per_group

    def level_index(self, bits, g: int) -> int:
        b = self.bits_per_group
        return int(sum(int(bits[b * g + j]) << j for j in range(b)))

    def fractions(self, bits) -> np.ndarray:
        return np.array([self.levels[self.level_index(bits, g)] for g in range(N_GROUPS)])

    def decode(self, bits, inst: Instance) -> np.ndarray:
        fr = self.fractions(bits)
        a = np.zeros_like(inst.D)
        for k in range(2):
            for b, months in enumerate(BLOCKS):
                for t in months:
                    a[k, t] = fr[group_index(k, b)] * inst.D[k, t]
        return a

    def all_bitstrings(self) -> np.ndarray:
        return np.array(list(itertools.product([0, 1], repeat=self.n_bits)), dtype=np.int8)

    def relax_to_bits(self, fractions) -> np.ndarray:
        out = []
        for f in fractions:
            i = int(np.argmin(np.abs(self.levels - f)))
            out += [(i >> j) & 1 for j in range(self.bits_per_group)]
        return np.array(out, int)


def block_fractions(a: np.ndarray, inst: Instance) -> np.ndarray:
    """Continuous plan → fraction of block demand per group."""
    return np.array([a[k, months].sum() / inst.D[k, months].sum() for k in range(2) for months in BLOCKS])


def objective(inst: Instance, dz: Discretization, bits, lam: float, alpha: float = 0.8) -> float:
    s = summarize(inst, dz.decode(bits, inst), alpha)
    return (1 - lam) * s["exp_loss"] + lam * s["cvar_loss"]


def enumerate_all(inst: Instance, dz: Discretization, lam: float, alpha: float = 0.8) -> pd.DataFrame:
    X = dz.all_bitstrings()
    rows = []
    for x in X:
        s = summarize(inst, dz.decode(x, inst), alpha)
        rows.append(dict(bits="".join(map(str, x)), J=(1 - lam) * s["exp_loss"] + lam * s["cvar_loss"],
                         exp_loss=s["exp_loss"], cvar_loss=s["cvar_loss"]))
    return pd.DataFrame(rows)


def to_little_endian(J_rows: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Re-index values listed in ``all_bitstrings`` order into Qiskit's little-endian basis order."""
    out = np.empty(len(J_rows))
    for row, x in enumerate(X):
        out[int(sum(int(b) << i for i, b in enumerate(x)))] = J_rows[row]
    return out
