import numpy as np
import pytest
from qiskit.quantum_info import Statevector

from src.optimization import discrete as Dd
from src.optimization.classical.heuristics import random_search, simulated_annealing
from src.optimization.classical.milp import solve_milp
from src.optimization.qubo.surrogate import (QUBO, basis_index, design_matrix, fit_qubo,
                                             qiskit_crosscheck, to_ising, to_pauli_op)
from src.optimization.quantum import qaoa as Q
from tests.test_allocation import tiny


def random_qubo(n=4, seed=0):
    rng = np.random.default_rng(seed)
    q = np.triu(rng.normal(size=(n, n)), 1)
    return QUBO(float(rng.normal()), rng.normal(size=n), q)


def bits_le(n):
    return (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1


# ---------------- discretisation ----------------
def test_discretization_levels_and_decode():
    dz = Dd.Discretization(2)
    assert dz.n_bits == 8 and np.allclose(dz.levels, [0, 1 / 3, 2 / 3, 1])
    inst = tiny(T=6)
    inst.D = np.array([[6.0] * 6, [12.0] * 6])
    bits = [1, 1, 0, 0, 1, 0, 0, 1]   # groups: 3 -> 1.0 ; 0 -> 0 ; 1 -> 1/3 ; 2 -> 2/3 (little-endian per group)
    a = dz.decode(bits, inst)
    assert np.allclose(a[0, :3], 6.0) and np.allclose(a[0, 3:], 0.0)
    assert np.allclose(a[1, :3], 12.0 / 3) and np.allclose(a[1, 3:], 12.0 * 2 / 3)


def test_relax_to_bits_roundtrip():
    for b in (1, 2, 3):
        dz = Dd.Discretization(b)
        for i, f in enumerate(dz.levels):
            bits = dz.relax_to_bits([f] * 4)
            assert np.allclose(dz.fractions(bits), f)


def test_little_endian_reindexing():
    dz = Dd.Discretization(1)
    X = dz.all_bitstrings()
    vals = np.arange(len(X), dtype=float)
    le = Dd.to_little_endian(vals, X)
    for row, x in enumerate(X):
        assert le[basis_index(x)] == vals[row]


# ---------------- QUBO ----------------
def test_fit_recovers_exact_quadratic():
    Qt = random_qubo(5, 1)
    X = bits_le(5); J = Qt.energy(X)
    Qf, d = fit_qubo(X, J)
    assert d["r2"] > 1 - 1e-12 and d["gap_true_J"] < 1e-9 and d["argmin_qubo"] == d["argmin_true"]
    assert np.allclose(Qf.energy(X), J)


def test_fit_is_approximate_for_cubic_objective():
    X = bits_le(4)
    J = X[:, 0] * X[:, 1] * X[:, 2] + 0.3 * X[:, 3]   # genuinely cubic term
    _, d = fit_qubo(X, J.astype(float))
    assert d["r2"] < 1.0 - 1e-6  # QUBO cannot represent it exactly: must be reported, not hidden


def test_ising_conversion_matches_qubo_energies():
    Qt = random_qubo(4, 3)
    op, offset = to_pauli_op(Qt)
    diag = np.real(np.diag(op.to_matrix(sparse=True).toarray())) + offset
    assert np.allclose(diag, Qt.energy(bits_le(4)))
    assert qiskit_crosscheck(Qt) < 1e-9   # also agrees with qiskit-optimization


# ---------------- QAOA ----------------
def test_probabilities_normalised_and_reproducible():
    prob = Q.make_problem(random_qubo(4, 2))
    r1, r2 = Q.run_qaoa(prob, 2, seed=5), Q.run_qaoa(prob, 2, seed=5)
    assert abs(r1["probs"].sum() - 1) < 1e-9 and (r1["probs"] >= -1e-12).all()
    assert np.allclose(r1["params"], r2["params"]) and np.allclose(r1["probs"], r2["probs"])


def test_qaoa_beats_uniform_and_energy_scale_is_standardised():
    prob = Q.make_problem(random_qubo(5, 4))
    assert abs(prob.energies.mean()) < 1e-9 and abs(prob.energies.std() - 1) < 1e-9
    r = Q.run_qaoa(prob, 2, seed=0)
    assert r["probs"] @ prob.raw_energies < prob.raw_energies.mean()      # better than uniform sampling


def test_gamma_beta_zero_standard_is_uniform():
    prob = Q.make_problem(random_qubo(3, 0))
    qc, g, b = Q.build_circuit(prob, 1)
    pv = Q.probabilities(qc, g, b, np.zeros(2))
    assert np.allclose(pv, 1 / 8)


def test_warm_start_initial_state_matches_theta():
    prob = Q.make_problem(random_qubo(3, 0))
    bits = np.array([1, 0, 1]); theta = Q.warm_theta_from_bits(bits, eps=0.2)
    qc, g, b = Q.build_circuit(prob, 1, warm_theta=theta)
    pv = Q.probabilities(qc, g, b, np.zeros(2))   # γ = β = 0 → mixer is identity
    c = np.clip(bits, 0.2, 0.8)
    want = np.array([np.prod([c[i] if (k >> i) & 1 else 1 - c[i] for i in range(3)]) for k in range(8)])
    assert np.allclose(pv, want)


def test_cvar_of_known_values():
    pv = np.array([0.25, 0.25, 0.25, 0.25]); e = np.array([3.0, 0.0, 1.0, 2.0])
    assert abs(Q.cvar_of(pv, e, 0.5) - 0.5) < 1e-12     # mean of the two lowest
    assert abs(Q.cvar_of(pv, e, 1.0) - e.mean()) < 1e-12  # alpha = 1 -> expectation
    assert abs(Q.cvar_of(pv, e, 0.25) - 0.0) < 1e-12     # lowest quarter


def test_circuit_stats_scale_with_p():
    prob = Q.make_problem(random_qubo(4, 0))
    s = [Q.circuit_stats(Q.build_circuit(prob, p)[0]) for p in (1, 2, 3)]
    assert s[0]["n_cx"] < s[1]["n_cx"] < s[2]["n_cx"] and s[0]["depth"] < s[2]["depth"]


# ---------------- discrete MILP vs enumeration, heuristics ----------------
def test_discrete_milp_equals_enumeration():
    dz = Dd.Discretization(1)
    inst = tiny(n=3, T=6, s0=80.0)
    inst.D = np.array([[8.0] * 6, [14.0] * 6])
    df = Dd.enumerate_all(inst, dz, 0.5, 0.7)
    r = solve_milp(inst, 0.5, 0.7, discretization=dz)
    assert r["optimal"] and abs(r["objective"] - df.J.min()) < 1e-6


def test_heuristics_reproducible_and_find_easy_optimum():
    f = lambda x: float(np.sum((np.asarray(x) - np.array([1, 0, 1, 1, 0, 1])) ** 2))
    b1, v1, u1 = simulated_annealing(f, 6, 400, seed=3)
    b2, v2, u2 = simulated_annealing(f, 6, 400, seed=3)
    assert (b1 == b2).all() and v1 == v2 and u1 == u2 and u1 <= 400
    assert v1 == 0.0
    br, vr, ur = random_search(f, 6, 200, seed=1)
    assert ur == 200 and vr == f(br)
