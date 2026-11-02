"""Download daily NASA POWER meteorology at the Orós dam (satellite/reanalysis, NOT INMET)."""
import json, sys, urllib.request
from pathlib import Path

LAT, LON = -6.24, -38.91  # approximate dam location (to be refined)
PARAMS = "T2M,T2M_MAX,T2M_MIN,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PS"


def fetch(start="20061102", end="20261029", out="data/raw/meteo/nasa_power_oros_daily.json"):
    url = ("https://power.larc.nasa.gov/api/temporal/daily/point?"
           f"parameters={PARAMS}&community=AG&longitude={LON}&latitude={LAT}"
           f"&start={start}&end={end}&format=JSON")
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(data))
    return out


if __name__ == "__main__":
    print(fetch(*sys.argv[1:]))
