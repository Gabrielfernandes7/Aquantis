"""Temporal-dependence handling: seasonal block resampling (calendar-aligned).

A draw is built from blocks of consecutive months (default 3: Jul–Sep, Oct–Dec); each block is
copied whole from one historical year, so within-block dependence is preserved. Dependence
ACROSS block boundaries is NOT preserved (limitation). A moving-block bootstrap over the
concatenated record is deliberately not used: it would splice December into July of
different years and break the seasonal cycle for a July–December horizon.
"""
import numpy as np
import pandas as pd

from src.scenarios.schema import HORIZON_MONTHS


def blocks(block_len: int) -> list[list[int]]:
    if 6 % block_len:
        raise ValueError("block_len must divide 6")
    return [HORIZON_MONTHS[i:i + block_len] for i in range(0, 6, block_len)]


def eligible_years(elig: pd.DataFrame, block: list[int]) -> list[int]:
    """elig: columns year, month, eligible (bool). Years where ALL months of the block are eligible."""
    e = elig[elig.month.isin(block)].groupby("year").eligible.agg(["all", "size"])
    return sorted(e[(e["all"]) & (e["size"] == len(block))].index.tolist())


def seasonal_block_draw(elig: pd.DataFrame, block_len: int, rng: np.random.Generator) -> list[int] | None:
    """One source year per block (with replacement across draws). None if a block has no eligible year."""
    src = []
    for b in blocks(block_len):
        ys = eligible_years(elig, b)
        if not ys:
            return None
        src.append(int(rng.choice(ys)))
    return src


def lag1_autocorr(series_by_year: pd.DataFrame) -> dict:
    """Pooled lag-1 correlation between consecutive months within the same year.
    series_by_year: index year, columns months (7..12). Returns r and the number of pairs."""
    xs, ys = [], []
    for m0, m1 in zip(HORIZON_MONTHS[:-1], HORIZON_MONTHS[1:]):
        if m0 in series_by_year and m1 in series_by_year:
            d = series_by_year[[m0, m1]].dropna()
            z0 = (d[m0] - series_by_year[m0].mean()) / series_by_year[m0].std()
            z1 = (d[m1] - series_by_year[m1].mean()) / series_by_year[m1].std()
            xs += z0.tolist(); ys += z1.tolist()
    n = len(xs)
    r = float(np.corrcoef(xs, ys)[0, 1]) if n > 2 else np.nan
    return {"r_lag1": r, "n_pairs": n, "approx_95ci_halfwidth": 1.96 / np.sqrt(max(n, 1))}
