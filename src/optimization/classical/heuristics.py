"""Classical heuristics on bitstrings: simulated annealing and random search (budgeted)."""
import numpy as np


def simulated_annealing(f, n_bits: int, n_evals: int, seed: int, t0: float = 1.0, t1: float = 0.01):
    """Single-bit-flip SA minimising f(bits). Temperatures are relative to the std of the first 20
    random evaluations. Returns best bits, best value, evaluations used."""
    rng = np.random.default_rng(seed)
    x = rng.integers(0, 2, n_bits); fx = f(x)
    probe = [f(rng.integers(0, 2, n_bits)) for _ in range(20)]
    scale = float(np.std(probe)) or 1.0
    best, fbest, used = x.copy(), fx, 21
    steps = max(1, n_evals - 21)
    for s in range(steps):
        T = scale * (t0 * (t1 / t0) ** (s / steps))
        y = x.copy(); i = rng.integers(n_bits); y[i] ^= 1
        fy = f(y); used += 1
        if fy < fx or rng.random() < np.exp(-(fy - fx) / T):
            x, fx = y, fy
            if fx < fbest:
                best, fbest = x.copy(), fx
    return best, float(fbest), used


def random_search(f, n_bits: int, n_evals: int, seed: int):
    rng = np.random.default_rng(seed)
    best, fbest = None, np.inf
    for _ in range(n_evals):
        x = rng.integers(0, 2, n_bits); v = f(x)
        if v < fbest:
            best, fbest = x, v
    return best, float(fbest), n_evals
