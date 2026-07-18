"""Precipitacion reciente 1 jul - 18 jul 09:00 (local) en las celdas del modelo.

El archivo ERA5 (reanalisis) tiene rezago de dias y no cubre el rio atmosferico
del 16-18 jul. Por eso la ventana reciente se toma de la API forecast de
Open-Meteo (past_days), que integra el analisis casi-tiempo-real. Es el 'parche'
de datos actuales sobre la climatologia ERA5 del modelo.

Los dias 1-17 se acumulan con los totales diarios; el 18 se agrega parcial con
datos horarios acumulados entre las 00:00 y las 09:00 hora de Chile.

Entrada:  clim_valpo.csv (centros de celda).
Salida:   recent_valpo.csv (row,col,lon,lat,recent_mm,cover_days,last_day)
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import config
OUT = config.WORK_DIR
CLIM = OUT / "clim_valpo.csv"
FORECAST = "https://api.open-meteo.com/v1/forecast"
CHUNK = 50
D0, D1 = "2026-07-01", "2026-07-17"        # dias completos (totales diarios)
HP_DAY = "2026-07-18"                       # dia parcial (horario)
H0, H1 = f"{HP_DAY}T00:00", f"{HP_DAY}T09:00"


def load_cells():
    rows = CLIM.read_text(encoding="utf-8").splitlines()[1:]
    cells = []
    for ln in rows:
        r, c, lon, lat, *_ = ln.split(",")
        cells.append((int(r), int(c), float(lon), float(lat)))
    return cells


def get(url):
    for attempt in range(6):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=90).read())
            return d if isinstance(d, list) else [d]
        except Exception as exc:                      # noqa: BLE001
            print(f"  reintento {attempt+1}: {exc}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fallo la API forecast")


def fetch_daily(chunk):
    lats = ",".join(f"{la:.4f}" for *_, la in chunk)
    lons = ",".join(f"{lo:.4f}" for r, c, lo, la in chunk)
    url = (f"{FORECAST}?latitude={lats}&longitude={lons}"
           "&daily=precipitation_sum&past_days=25&forecast_days=1"
           "&timezone=America/Santiago")
    return get(url)


def fetch_hourly18(chunk):
    lats = ",".join(f"{la:.4f}" for *_, la in chunk)
    lons = ",".join(f"{lo:.4f}" for r, c, lo, la in chunk)
    url = (f"{FORECAST}?latitude={lats}&longitude={lons}"
           f"&hourly=precipitation&start_hour={H0}&end_hour={H1}"
           "&timezone=America/Santiago")
    return get(url)


def july_sum(one):
    t = one["daily"]["time"]; p = one["daily"]["precipitation_sum"]
    tot, cover, last = 0.0, 0, ""
    for a, b in zip(t, p):
        if D0 <= a <= D1 and b is not None:
            tot += b; cover += 1; last = a
    return tot, cover, last


def partial18(one):
    """mm acumulados 00:00-09:00 del 18-jul (cada valor cubre la hora previa)."""
    t = one["hourly"]["time"]; p = one["hourly"]["precipitation"]
    return sum(b for a, b in zip(t, p) if a > H0 and b is not None)


def main():
    cells = load_cells()
    print(f"celdas a consultar: {len(cells)}")
    out = ["row,col,lon,lat,recent_mm,cover_days,last_day"]
    p18_all = []
    for i in range(0, len(cells), CHUNK):
        chunk = cells[i:i + CHUNK]
        locs_d = fetch_daily(chunk)
        time.sleep(2)
        locs_h = fetch_hourly18(chunk)
        for (r, c, lo, la), one_d, one_h in zip(chunk, locs_d, locs_h):
            tot, cover, _ = july_sum(one_d)
            p18 = partial18(one_h)
            p18_all.append(p18)
            tot = round(tot + p18, 1)
            out.append(f"{r},{c},{lo:.4f},{la:.4f},{tot},{cover},{H1}")
        print(f"  {min(i+CHUNK,len(cells))}/{len(cells)}", flush=True)
        time.sleep(2)
    (OUT / "recent_valpo.csv").write_text("\n".join(out), encoding="utf-8")
    vals = [float(l.split(",")[4]) for l in out[1:]]
    print(f"recent 1jul-18jul09:00 (mm) min/media/max: "
          f"{min(vals):.1f} / {sum(vals)/len(vals):.1f} / {max(vals):.1f}")
    print(f"parcial 18-jul 00-09h (mm) min/media/max: "
          f"{min(p18_all):.1f} / {sum(p18_all)/len(p18_all):.1f} / {max(p18_all):.1f}")
    print(f"-> recent_valpo.csv ({len(out)-1} celdas)")


if __name__ == "__main__":
    main()
