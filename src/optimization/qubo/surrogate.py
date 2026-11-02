"""QUBO surrogate of the exact discretised allocation objective.

The exact objective J(x) (rationing rule + CVaR) is NOT quadratic in the bits. We therefore fit
    Q(x) = c + Σ h_i x_i + Σ_{i<j} q_ij x_ij
by (optionally weighted) least squares on ALL 2^n exact evaluations. This is an approximation whose
quality is MEASURED (R², rank correlation, optimality gap of its minimiser), never assumed.
Limit: needs the full enumeration, so it is only available for instances small enough to enumerate.
"""
from dataclasses import dataclass

import numpy as np
from qiskit.quantum_info import SparsePauliOp
from scipy.stats import spearmanr


@dataclass
class QUBO:
    const: float
    h: np.ndarray       # (n,)
    q: np.ndarray       # (n, n) strictly upper triangular

    @property
    def n(self):
        return len(self.h)

    def energy(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, float)
        return self.const + X @ self.h + np.einsum("ni,ij,nj->n", X, self.q, X)


def design_matrix(X: np.ndarray) -> np.ndarray:
    n = X.shape[1]
    cols = [np.ones(len(X))] + [X[:, i] for i in range(n)] + \
           [X[:, i] * X[:, j] for i in range(n) for j in range(i + 1, n)]
    return np.column_stack(cols).astype(float)


def fit_qubo(X: np.ndarray, J: np.ndarray, tau: float | None = None) -> tuple[QUBO, dict]:
    """Least-squares fit. tau=None → unweighted (uses no knowledge of the optimum).
    tau=float → weights exp(−(J−J_min)/tau): a DIAGNOSTIC that uses the true minimum."""
    n = X.shape[1]
    A = design_matrix(X)
    w = np.ones(len(J)) if tau is None else np.exp(-(J - J.min()) / tau)
    sw = np.sqrt(w)
    coef, *_ = np.linalg.lstsq(A * sw[:, None], J * sw, rcond=None)
    const, h = coef[0], coef[1:1 + n]
    q = np.zeros((n, n)); k = 1 + n
    for i in range(n):
        for j in range(i + 1, n):
            q[i, j] = coef[k]; k += 1
    Q = QUBO(float(const), h.copy(), q)
    pred = Q.energy(X)
    ss_res = float(((J - pred) ** 2).sum()); ss_tot = float(((J - J.mean()) ** 2).sum())
    iq, io = int(np.argmin(pred)), int(np.argmin(J))
    diag = dict(r2=1 - ss_res / ss_tot, spearman=float(spearmanr(J, pred)[0]),
                rmse=float(np.sqrt(ss_res / len(J))), n_params=A.shape[1],
                argmin_qubo=iq, argmin_true=io, gap_true_J=float(J[iq] - J[io]),
                rank_of_qubo_min_in_true=int((J < J[iq] - 1e-12).sum() + 1), tau=tau)
    return Q, diag


def to_ising(Q: QUBO):
    """x = (1−z)/2  →  E = offset + Σ a_i z_i + Σ_{i<j} b_ij z_i z_j."""
    n = Q.n
    a = -Q.h / 2 - (Q.q.sum(axis=1) + Q.q.sum(axis=0)) / 4
    b = Q.q / 4
    offset = Q.const + Q.h.sum() / 2 + Q.q.sum() / 4
    return float(offset), a, b


def to_pauli_op(Q: QUBO) -> SparsePauliOp:
    """Qiskit labels are little-endian: qubit i is the (n−1−i)-th character from the left."""
    n = Q.n
    offset, a, b = to_ising(Q)
    terms = []
    for i in range(n):
        s = ["I"] * n; s[n - 1 - i] = "Z"; terms.append(("".join(s), a[i]))
    for i in range(n):
        for j in range(i + 1, n):
            if b[i, j] != 0:
                s = ["I"] * n; s[n - 1 - i] = "Z"; s[n - 1 - j] = "Z"; terms.append(("".join(s), b[i, j]))
    return SparsePauliOp.from_list(terms), offset


def basis_index(bits) -> int:
    """Little-endian basis index used by Qiskit statevectors."""
    return int(sum(int(b) << i for i, b in enumerate(bits)))


def qiskit_crosscheck(Q: QUBO) -> float:
    """Max |difference| between our Ising energies and qiskit-optimization's on every bitstring."""
    from qiskit_optimization import QuadraticProgram
    qp = QuadraticProgram()
    for i in range(Q.n):
        qp.binary_var(f"x{i}")
    quad = {(f"x{i}", f"x{j}"): float(Q.q[i, j]) for i in range(Q.n) for j in range(i + 1, Q.n) if Q.q[i, j] != 0}
    qp.minimize(constant=Q.const, linear={f"x{i}": float(Q.h[i]) for i in range(Q.n)}, quadratic=quad)
    op, off = qp.to_ising()
    diag = np.real(np.diag(op.to_matrix(sparse=True).toarray())) + off
    ours, offset = to_pauli_op(Q)
    mine = np.real(np.diag(ours.to_matrix(sparse=True).toarray())) + offset
    X = ((np.arange(2 ** Q.n)[:, None] >> np.arange(Q.n)) & 1)  # little-endian bits
    direct = Q.energy(X)
    return float(max(np.abs(diag - direct).max(), np.abs(mine - direct).max()))
