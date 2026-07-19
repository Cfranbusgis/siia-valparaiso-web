"""Climatología 1-19 jul de 30 años (1995-2025) capturando la megasequía.

Descarga los años que faltan (1995-2002 y 2024-2025) por celda desde Open-Meteo
Archive (era5_seamless) y los fusiona con clim_om_years.npz (2003-2023, ya
descargado) → clim_om_years_1995_2025.npz. Luego COMPARA la rareza del evento
2026 contra ambos baselines (21 vs 31 años) sin sobrescribir nada.
"""
from __future__ import annotations
import json, time, urllib.request
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
BASE = HERE / "clim_om_years.npz"                 # 2003-2023, 1-19 jul
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
CHUNK = 50
FALTAN = list(range(1995, 2003)) + [2024, 2025]   # 1995-2002 + 2024-2025

def get(url):
    for k in range(6):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=90).read())
            return d if isinstance(d, list) else [d]
        except Exception as e:
            print("  retry", k+1, e, flush=True); time.sleep(5*(k+1))
    raise RuntimeError("archive falla")

def fetch_year(lon, lat, year):
    n = len(lon); col = np.full(n, np.nan)
    for i in range(0, n, CHUNK):
        la = ",".join(f"{v:.4f}" for v in lat[i:i+CHUNK])
        lo = ",".join(f"{v:.4f}" for v in lon[i:i+CHUNK])
        url = (f"{ARCHIVE}?latitude={la}&longitude={lo}"
               f"&start_date={year}-07-01&end_date={year}-07-19"
               "&daily=precipitation_sum&models=era5_seamless&timezone=America/Santiago")
        for j, one in enumerate(get(url)):
            p = one["daily"]["precipitation_sum"]; v = [x for x in p if x is not None]
            col[i+j] = float(np.sum(v)) if v else np.nan
        time.sleep(1)
    return col

def main():
    z = np.load(BASE)
    lon, lat = z["lon"], z["lat"]; base_sums = z["sums"]; base_years = list(z["years"])
    n = len(lon)
    add = np.full((len(FALTAN), n), np.nan)
    for yi, y in enumerate(FALTAN):
        add[yi] = fetch_year(lon, lat, y)
        print(f"  {y}: media {np.nanmean(add[yi]):.1f} mm", flush=True)

    years = np.array(sorted(base_years + FALTAN))
    allsums = np.vstack([base_sums, add])
    order = np.argsort(np.array(base_years + FALTAN))
    allsums = allsums[order]
    np.savez_compressed(HERE / "clim_om_years_1995_2025.npz",
                        sums=allsums, years=years, lon=lon, lat=lat)

    # comparación de rareza del evento 2026 (reciente v2 corregido) vs 2 baselines
    grid = pd.read_csv(HERE / "anomaly_grid_valpo_v2.csv")
    rec = grid["recent_v2_mm"].values
    def rareza(sums, yrs):
        mean = np.nanmean(sums, axis=0)
        ny = np.sum(~np.isnan(sums), axis=0)
        rank = np.sum(sums <= rec[None, :], axis=0)
        pctl = 100.0 * rank / (ny + 1)
        anom = (rec - mean) / mean * 100
        return mean.mean(), np.median(pctl), anom.mean(), int((rank == ny).sum())
    b21 = rareza(base_sums, base_years)
    b31 = rareza(allsums, years)
    print("\n=== RAREZA DEL EVENTO 2026 (reciente corregido) ===")
    print(f"{'baseline':22s} {'clim mm':>8s} {'pctl med':>9s} {'anom %':>8s} {'celdas>max':>11s}")
    print(f"{'2003-2023 (21 años)':22s} {b21[0]:8.1f} {b21[1]:9.1f} {b21[2]:8.1f} {b21[3]:11d}")
    print(f"{'1995-2025 (31 años)':22s} {b31[0]:8.1f} {b31[1]:9.1f} {b31[2]:8.1f} {b31[3]:11d}")
    # contexto megasequia: media por decada
    print("\nmedia regional 1-19 jul por periodo (mm):")
    for lo_, hi_ in [(1995,2009),(2010,2025)]:
        m = np.array([np.nanmean(allsums[list(years).index(y)]) for y in range(lo_,hi_+1) if y in years])
        print(f"  {lo_}-{hi_}: {m.mean():.1f}")
    print("-> clim_om_years_1995_2025.npz")

if __name__ == "__main__":
    main()
