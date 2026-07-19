"""Extiende la climatologia homogenea de 1-18 jul a 1-19 jul (2003-2023).

La ventana reciente pasa a cerrar a las 03:00 del 19-jul; para no reintroducir
el desajuste de ventanas (hallazgo de la auditoria), la climatologia por anho
debe cubrir la misma ventana. Se descarga SOLO el dia 19 (YYYY-07-19, completo)
de cada anho, por celda (era5_seamless), y se suma al acumulado 1-18 guardado
en clim_om_years.npz -> clim_om_years.npz (1-19) + clim_valpo_om.csv actualizado.

Simetria con el reciente: el dia 19 de la climatologia es completo (00-24h) y el
del reciente es parcial (00-03h) -> anomalia levemente conservadora, igual que
antes con el dia 18.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import numpy as np

from config import WORK_DIR as HERE
NPZ = HERE / "clim_om_years.npz"
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
CHUNK = 50
DAY = 19


def get(url):
    for attempt in range(6):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=90).read())
            return d if isinstance(d, list) else [d]
        except Exception as exc:                      # noqa: BLE001
            print(f"  reintento {attempt+1}: {exc}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fallo la API archive")


def main():
    z = np.load(NPZ)
    sums = z["sums"].copy()          # (n_years, n_cells) acumulado 1-18
    years = list(z["years"])
    lon = z["lon"]; lat = z["lat"]
    n = sums.shape[1]
    print(f"clim previa 1-18: {sums.shape}, media {np.nanmean(sums.sum(axis=0)/len(years) if False else sums):.1f}")

    add = np.zeros_like(sums)
    for yi, year in enumerate(years):
        col = np.zeros(n)
        for i in range(0, n, CHUNK):
            la = ",".join(f"{v:.4f}" for v in lat[i:i+CHUNK])
            lo = ",".join(f"{v:.4f}" for v in lon[i:i+CHUNK])
            url = (f"{ARCHIVE}?latitude={la}&longitude={lo}"
                   f"&start_date={year}-07-{DAY:02d}&end_date={year}-07-{DAY:02d}"
                   "&daily=precipitation_sum&models=era5_seamless"
                   "&timezone=America/Santiago")
            for j, one in enumerate(get(url)):
                p = one["daily"]["precipitation_sum"]
                v = [x for x in p if x is not None]
                col[i + j] = float(np.sum(v)) if v else 0.0
            time.sleep(1)
        add[yi] = col
        print(f"  {year}: dia19 media {col.mean():.1f} mm", flush=True)

    sums19 = sums + add
    mean = np.nanmean(sums19, axis=0)
    std = np.nanstd(sums19, axis=0, ddof=1)
    ny = np.sum(~np.isnan(sums19), axis=0)

    np.savez_compressed(NPZ, sums=sums19, years=np.array(years), lon=lon, lat=lat)

    # actualizar clim_valpo_om.csv (row,col,lon,lat,clim_mean_mm,clim_std_mm,n_years)
    old = (HERE / "clim_valpo_om.csv").read_text(encoding="utf-8").splitlines()
    head, body = old[0], old[1:]
    lines = [head]
    for k, ln in enumerate(body):
        r, c, lo, la, *_ = ln.split(",")
        lines.append(f"{r},{c},{lo},{la},{mean[k]:.2f},{std[k]:.2f},{int(ny[k])}")
    (HERE / "clim_valpo_om.csv").write_text("\n".join(lines), encoding="utf-8")

    print(f"\nclim 1-19 media regional: {mean.mean():.1f} mm "
          f"(antes 1-18: {np.nanmean(sums, axis=0).mean():.1f} mm)")
    print(f"-> clim_om_years.npz (1-19), clim_valpo_om.csv")


if __name__ == "__main__":
    main()
