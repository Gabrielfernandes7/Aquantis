"""Open-water evaporation (Penman) and volume conversion.

Meteorology: NASA POWER (not INMET). Heat storage G is ignored (limitation).
Surface area A(V): the cota-area-volume curve is NOT available yet, so A(V) is an
explicit *assumption*  A = A_full * (V / V_full)**k  explored as a sensitivity range.
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

LAMBDA = 2.45  # MJ/kg


def load_power(path) -> pd.DataFrame:
    d = json.loads(Path(path).read_text())
    df = pd.DataFrame(d["properties"]["parameter"])
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    df = df.replace(-999.0, np.nan).interpolate(limit=3)
    return df.reset_index()


def _ra(doy, lat_deg):
    """Extraterrestrial radiation, MJ m-2 day-1 (FAO-56 eq. 21)."""
    phi = math.radians(lat_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / 365)
    dec = 0.409 * np.sin(2 * np.pi * doy / 365 - 1.39)
    ws = np.arccos(np.clip(-math.tan(phi) * np.tan(dec), -1, 1))
    return 24 * 60 / np.pi * 0.0820 * dr * (ws * math.sin(phi) * np.sin(dec)
                                            + math.cos(phi) * np.cos(dec) * np.sin(ws))


def penman_open_water_mm(df: pd.DataFrame, lat=-6.24, elev=247.0, albedo=0.08) -> pd.Series:
    """Daily open-water evaporation in mm/day (Penman 1948 form, FAO-56 radiation terms)."""
    T, Tx, Tn = df["T2M"], df["T2M_MAX"], df["T2M_MIN"]
    rh, u2, P = df["RH2M"], df["WS2M"], df["PS"]
    rs = df["ALLSKY_SFC_SW_DWN"]  # MJ m-2 day-1
    es = lambda t: 0.6108 * np.exp(17.27 * t / (t + 237.3))
    e_s = (es(Tx) + es(Tn)) / 2
    e_a = es(T) * rh / 100
    vpd = (e_s - e_a).clip(lower=0)
    delta = 4098 * es(T) / (T + 237.3) ** 2
    gamma = 0.000665 * P
    doy = df["date"].dt.dayofyear.values
    ra = _ra(doy, lat)
    rso = (0.75 + 2e-5 * elev) * ra
    rnl = 4.903e-9 * (((Tx + 273.16) ** 4 + (Tn + 273.16) ** 4) / 2) * (
        0.34 - 0.14 * np.sqrt(e_a)) * (1.35 * (rs / rso).clip(upper=1) - 0.35)
    rn = (1 - albedo) * rs - rnl
    f_u = 2.6 * (1 + 0.536 * u2)  # mm/day/kPa
    e = (delta / (delta + gamma)) * rn / LAMBDA + (gamma / (delta + gamma)) * f_u * vpd
    return pd.Series(e.clip(lower=0).values, index=df.index, name="E_mm_day")


def area_km2(volume_hm3, a_full=190.0, v_full=1940.0, k=0.65):
    """ASSUMED area-volume relation (placeholder until the real curve is obtained)."""
    return a_full * (np.asarray(volume_hm3, float) / v_full) ** k


def evaporation_hm3(e_mm_day, volume_hm3, **kw):
    """E[hm3/day] = e[mm] * 1e-3 m * A[km2] * 1e6 m2 / 1e6 = e_mm * A_km2 * 1e-3."""
    return np.asarray(e_mm_day, float) * area_km2(volume_hm3, **kw) * 1e-3
