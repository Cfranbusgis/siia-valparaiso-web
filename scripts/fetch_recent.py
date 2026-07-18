"""Precipitacion reciente 1-17 julio 2026 en las celdas del modelo (Valparaiso).

El archivo ERA5 (reanalisis) solo llega ~9-jul por su rezago, justo antes del
rio atmosferico del 16-17 jul. Por eso la ventana reciente se toma de la API
forecast de Open-Meteo (past_days), que integra el analisis casi-tiempo-real y
SI cubre el evento. Es el 'parche' de datos actuales sobre la climatologia ERA5
del modelo.

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
D0, D1 = "2026-07-01", "2026-07-17"


def load_cells():
    rows = CLIM.read_text(encoding="utf-8").splitlines()[1:]
    cells = []
    for ln in rows:
        r, c, lon, lat, *_ = ln.split(",")
        cells.append((int(r), int(c), float(lon), float(lat)))
    return cells


def fetch(chunk):
    lats = ",".join(f"{la:.4f}" for *_, la in [(r, c, lo, la) for r, c, lo, la in chunk])
    lons = ",".join(f"{lo:.4f}" for r, c, lo, la in chunk)
    url = (f"{FORECAST}?latitude={lats}&longitude={lons}"
           "&daily=precipitation_sum&past_days=25&forecast_days=1"
           "&timezone=America/Santiago")
    for attempt in range(6):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=90).read())
            return d if isinstance(d, list) else [d]
        except Exception as exc:                      # noqa: BLE001
            print(f"  reintento {attempt+1}: {exc}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fallo la API forecast")


def july_sum(one):
    t = one["daily"]["time"]; p = one["daily"]["precipitation_sum"]
    tot, cover, last = 0.0, 0, ""
    for a, b in zip(t, p):
        if D0 <= a <= D1 and b is not None:
            tot += b; cover += 1; last = a
    return round(tot, 1), cover, last


def main():
    cells = load_cells()
    print(f"celdas a consultar: {len(cells)}")
    out = ["row,col,lon,lat,recent_mm,cover_days,last_day"]
    for i in range(0, len(cells), CHUNK):
        chunk = cells[i:i + CHUNK]
        locs = fetch(chunk)
        for (r, c, lo, la), one in zip(chunk, locs):
            tot, cover, last = july_sum(one)
            out.append(f"{r},{c},{lo:.4f},{la:.4f},{tot},{cover},{last}")
        print(f"  {min(i+CHUNK,len(cells))}/{len(cells)}", flush=True)
        time.sleep(2)
    (OUT / "recent_valpo.csv").write_text("\n".join(out), encoding="utf-8")
    vals = [float(l.split(",")[4]) for l in out[1:]]
    print(f"recent jul1-17 (mm) min/media/max: "
          f"{min(vals):.1f} / {sum(vals)/len(vals):.1f} / {max(vals):.1f}")
    print(f"-> recent_valpo.csv ({len(out)-1} celdas)")


if __name__ == "__main__":
    main()
