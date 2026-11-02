import numpy as np, pandas as pd
from src.hydrology.evaporation import evaporation_hm3, area_km2, penman_open_water_mm


def test_unit_conversion():
    # 5 mm over 100 km2 = 5e-3 m * 1e8 m2 = 5e5 m3 = 0.5 hm3
    assert abs(evaporation_hm3(5.0, 1940.0, a_full=100.0, v_full=1940.0) - 0.5) < 1e-12


def test_area_monotonic():
    assert area_km2(500.0) < area_km2(1500.0)


def test_penman_range_semiarid():
    df = pd.DataFrame({"date": pd.to_datetime(["2025-01-01"]), "T2M": [32.0], "T2M_MAX": [38.0],
                       "T2M_MIN": [25.0], "RH2M": [50.0], "WS2M": [4.0],
                       "ALLSKY_SFC_SW_DWN": [22.0], "PS": [98.0]})
    e = penman_open_water_mm(df).iloc[0]
    assert 4.0 < e < 10.0
