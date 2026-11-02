"""QAOA / warm-start QAOA / CVaR-QAOA on a diagonal (Ising) cost, with Qiskit circuits.

Ideal runs use exact statevector probabilities (no sampling noise); sampling and noise are added
explicitly where stated. Energies are standardised (mean 0, std 1) INSIDE the quantum routine so
the angle range is meaningful; this does not change the argmin.
"""
from dataclasses import dataclass

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from scipy.optimize import minimize

from src.optimization.qubo.surrogate import QUBO, basis_index, to_ising


@dataclass
class QAOAProblem:
    n: int
    a: np.ndarray        # Z coefficients (standardised scale)
    b: np.ndarray        # ZZ coefficients (upper triangular)
    energies: np.ndarray  # (2^n,) standardised, little-endian index
    raw_energies: np.ndarray
    scale: float
    shift: float


def make_problem(Q: QUBO) -> QAOAProblem:
    n = Q.n
    X = (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1
    raw = Q.energy(X)
    shift, scale = raw.mean(), raw.std()
    offset, a, b = to_ising(Q)
    return QAOAProblem(n, a / scale, b / scale, (raw - shift) / scale, raw, scale, shift)


def build_circuit(prob: QAOAProblem, p: int, warm_theta: np.ndarray | None = None):
    """Standard QAOA if warm_theta is None; else warm-start (Egger et al. 2021): initial Ry(θ_i)|0>,
    mixer Ry(θ_i)·Rz(−2β)·Ry(−θ_i)."""
    n = prob.n
    g, bt = ParameterVector("g", p), ParameterVector("b", p)
    qc = QuantumCircuit(n)
    if warm_theta is None:
        qc.h(range(n))
    else:
        for i in range(n):
            qc.ry(float(warm_theta[i]), i)
    for l in range(p):
        for i in range(n):
            if prob.a[i] != 0:
                qc.rz(2 * g[l] * float(prob.a[i]), i)
        for i in range(n):
            for j in range(i + 1, n):
                if prob.b[i, j] != 0:
                    qc.rzz(2 * g[l] * float(prob.b[i, j]), i, j)
        for i in range(n):
            if warm_theta is None:
                qc.rx(2 * bt[l], i)
            else:
                qc.ry(-float(warm_theta[i]), i); qc.rz(-2 * bt[l], i); qc.ry(float(warm_theta[i]), i)
    return qc, g, bt


def probabilities(qc, g, bt, params: np.ndarray) -> np.ndarray:
    p = len(g)
    bound = qc.assign_parameters({**{g[l]: params[l] for l in range(p)}, **{bt[l]: params[p + l] for l in range(p)}})
    return Statevector(bound).probabilities()


def cvar_of(prob_vec: np.ndarray, energies: np.ndarray, alpha: float) -> float:
    o = np.argsort(energies)
    cum = np.cumsum(prob_vec[o]); k = int(np.searchsorted(cum, alpha))
    mass = prob_vec[o].copy(); 
    mass_before = cum[k - 1] if k > 0 else 0.0
    mass[k] = alpha - mass_before; mass[k + 1:] = 0
    return float((mass * energies[o]).sum() / alpha)


def run_qaoa(prob: QAOAProblem, p: int, seed: int, variant: str = "standard", cvar_alpha: float = 0.25,
             warm_theta: np.ndarray | None = None, maxiter: int = 300) -> dict:
    qc, g, bt = build_circuit(prob, p, warm_theta if variant == "warm" else None)
    rng = np.random.default_rng(seed)
    x0 = np.concatenate([rng.uniform(0, 1.0, p), rng.uniform(0, np.pi / 2, p)])
    hist = []

    def loss(x):
        pv = probabilities(qc, g, bt, x)
        v = cvar_of(pv, prob.energies, cvar_alpha) if variant == "cvar" else float(pv @ prob.energies)
        hist.append(v); return v

    res = minimize(loss, x0, method="COBYLA", options=dict(maxiter=maxiter, rhobeg=0.3))
    pv = probabilities(qc, g, bt, res.x)
    return dict(params=res.x, probs=pv, nfev=int(res.nfev), loss=float(res.fun),
                exp_energy_raw=float(pv @ prob.raw_energies), circuit=qc, g=g, b=bt)


def circuit_stats(qc, basis=("cx", "rz", "sx", "x")) -> dict:
    t = transpile(qc.decompose(reps=2) if False else qc, basis_gates=list(basis), optimization_level=1, seed_transpiler=0)
    ops = t.count_ops()
    return dict(depth=int(t.depth()), n_cx=int(ops.get("cx", 0)), n_gates=int(sum(ops.values())), n_qubits=qc.num_qubits)


def warm_theta_from_bits(bits: np.ndarray, eps: float = 0.25) -> np.ndarray:
    c = np.clip(np.asarray(bits, float), eps, 1 - eps)
    return 2 * np.arcsin(np.sqrt(c))
