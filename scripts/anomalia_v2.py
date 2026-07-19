"""FASE 4c - Anomalia v2: reciente corregido + percentiles empiricos + z homogeneo.

Cadena v2 (reemplaza el titular '+313% / z=3.74'):
1. Climatologia HOMOGENEA: totales 1-18 jul POR ANHO (2003-2023) por celda,
   Open-Meteo Archive era5_seamless (misma familia que el reciente). Se guarda
   la matriz completa (clim_om_years.npz) para percentiles empiricos; la
   Fase 1 solo habia guardado media/std.
2. Correccion del reciente: el LOO (correccion_loo.py) eligio la correccion
   espacial de residuos (IDW de log(obs/modelo), potencia 2, 14 estaciones
   robustas; RMSE 22.0 vs 54.2 sin corregir, sesgo -2.0 mm). Se aplica el
   campo IDW a cada celda: recent_v2 = recent * exp(IDW log-ratio).
   Supuesto: el sesgo del peak-24h aplica al acumulado 1-18 jul; valido
   porque el evento 15-18 jul aporta >95% del acumulado (dias 1-14 ~ 0).
3. Rareza SIN gaussiana: percentil empirico del recent_v2 dentro de los 21
   anhos (posicion de Weibull r/(n+1)) + z sobre la climatologia homogenea
   (solo como indicador complementario, NO para umbrales de rareza).
4. Humedales: heredan celda (mismo sjoin que analyze_valpo.py).

Salidas: clim_om_years.npz, anomaly_grid_valpo_v2.csv,
         humedales_valpo_anomalia_v2.csv, resumen_valpo_v2.json
"""
from __future__ import annotations

import json
import time
import urllib.request
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from affine import Affine
from shapely.geometry import box

from config import WORK_DIR as HERE, HUMEDALES_SHP as HU
YEARS_NPZ = HERE / "clim_om_years.npz"
ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
CHUNK = 50
YEARS = list(range(2003, 2024))
UTM = 32719
IDW_POWER = 2.0


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def get(url):
    for attempt in range(6):
        try:
            d = json.loads(urllib.request.urlopen(url, timeout=90).read())
            return d if isinstance(d, list) else [d]
        except Exception as exc:                      # noqa: BLE001
            print(f"  reintento {attempt+1}: {exc}", flush=True)
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("fallo la API archive")


def fetch_years(cells):
    n = len(cells)
    sums = np.full((len(YEARS), n), np.nan)
    for yi, year in enumerate(YEARS):
        for i in range(0, n, CHUNK):
            chunk = cells[i:i + CHUNK]
            lats = ",".join(f"{la:.4f}" for _, la in chunk)
            lons = ",".join(f"{lo:.4f}" for lo, _ in chunk)
            url = (f"{ARCHIVE}?latitude={lats}&longitude={lons}"
                   f"&start_date={year}-07-01&end_date={year}-07-18"
                   "&daily=precipitation_sum&models=era5_seamless"
                   "&timezone=America/Santiago")
            for j, one in enumerate(get(url)):
                p = one["daily"]["precipitation_sum"]
                vals = [v for v in p if v is not None]
                sums[yi, i + j] = float(np.sum(vals)) if vals else np.nan
            time.sleep(1)
        print(f"  {year}: media {np.nanmean(sums[yi]):.1f} mm", flush=True)
    return sums


def main():
    grid = pd.read_csv(HERE / "anomaly_grid_valpo.csv")
    cells = list(zip(grid.lon, grid.lat))

    if YEARS_NPZ.exists():
        sums = np.load(YEARS_NPZ)["sums"]
        print(f"clim_om_years.npz cacheado ({sums.shape})")
    else:
        print(f"descargando {len(YEARS)} anhos x {len(cells)} celdas (era5_seamless)...")
        sums = fetch_years(cells)
        np.savez_compressed(YEARS_NPZ, sums=sums, years=np.array(YEARS),
                            lon=grid.lon.values, lat=grid.lat.values)

    # --- correccion IDW de residuos (ajustada con las 14 estaciones robustas) ---
    aud = pd.read_csv(HERE / "auditoria_estaciones.csv", encoding="utf-8")
    st = aud[aud.flag.str.startswith("OK")].copy()
    st["logratio"] = np.log(st.agua24h_mm / st.model_win24_mm)
    print(f"correccion IDW con n={len(st)} estaciones; "
          f"factor mediano {np.exp(np.median(st.logratio)):.3f}")

    fac = []
    for lo, la in cells:
        d = np.array([haversine_km(la, lo, a, b) for a, b in zip(st.lat, st.lon)])
        d = np.maximum(d, 1.0)
        w = 1.0 / d ** IDW_POWER
        fac.append(float(np.exp(np.sum(w * st.logratio.values) / np.sum(w))))
    grid["factor_correccion"] = np.round(fac, 3)
    grid["recent_v2_mm"] = np.round(grid.recent_mm * grid.factor_correccion, 1)

    # --- climatologia homogenea + percentil empirico + z ---
    clim_mean = np.nanmean(sums, axis=0)
    clim_std = np.nanstd(sums, axis=0, ddof=1)
    grid["clim_om_mean_mm"] = np.round(clim_mean, 2)
    grid["clim_om_std_mm"] = np.round(clim_std, 2)
    grid["anomaly_v2_pct"] = np.round(
        (grid.recent_v2_mm - clim_mean) / clim_mean * 100, 1)
    grid["z_v2"] = np.round((grid.recent_v2_mm - clim_mean) / clim_std, 2)

    nyr = np.sum(~np.isnan(sums), axis=0)
    rank = np.sum(sums <= grid.recent_v2_mm.values[None, :], axis=0)
    grid["pctl_empirico"] = np.round(100.0 * rank / (nyr + 1), 1)
    grid["anhos_superados"] = rank.astype(int)          # de nyr anhos
    grid["supera_max_21a"] = rank == nyr

    grid.to_csv(HERE / "anomaly_grid_valpo_v2.csv", index=False, encoding="utf-8")

    # --- humedales (mismo sjoin que analyze_valpo.py) ---
    npz = np.load(HERE / "clim_valpo.npz")
    transform = Affine(*npz["transform"][:6])
    polys = []
    for r, c in zip(grid.row, grid.col):
        x0, y0 = transform * (c, r)
        x1, y1 = transform * (c + 1, r + 1)
        polys.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    vcols = ["recent_v2_mm", "anomaly_v2_pct", "z_v2", "pctl_empirico",
             "factor_correccion", "clim_om_mean_mm"]
    g = gpd.GeoDataFrame(grid[vcols].copy(), geometry=polys, crs=UTM)

    hu = gpd.read_file(HU).to_crs(UTM)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].copy()
    hu_pt = hu.copy(); hu_pt["geometry"] = hu.representative_point()
    j = gpd.sjoin(hu_pt, g, how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    miss = j["anomaly_v2_pct"].isna()
    if miss.any():
        jn = gpd.sjoin_nearest(hu_pt[miss], g, how="left")
        jn = jn[~jn.index.duplicated(keep="first")]
        for c in vcols:
            j.loc[miss, c] = jn[c]
    hu_res = hu.drop(columns="geometry").copy()
    for c in vcols:
        hu_res[c] = j[c].values
    hu_res.to_csv(HERE / "humedales_valpo_anomalia_v2.csv",
                  index=False, encoding="utf-8")

    # --- resumen v2 ---
    resumen = {
        "evento": "Rio atmosferico sobre Chile central, 16-18 julio 2026",
        "ventana": "1 julio - 19 julio 03:00 hora local, 2026",
        "climatologia": ("Open-Meteo Archive era5_seamless 2003-2023, 1-19 jul, "
                         "por anho (homogenea con el reciente)"),
        "correccion": ("IDW de residuos log(obs/modelo), 14 estaciones DMC "
                       "robustas; elegida por LOO (RMSE 22.0 vs 54.2 mm)"),
        "celdas": int(len(grid)),
        "reciente_v1_media_mm": round(float(grid.recent_mm.mean()), 1),
        "reciente_v2_media_mm": round(float(grid.recent_v2_mm.mean()), 1),
        "factor_medio": round(float(grid.factor_correccion.mean()), 3),
        "clim_om_media_mm": round(float(grid.clim_om_mean_mm.mean()), 1),
        "anom_v2_pct_media_grilla": round(float(grid.anomaly_v2_pct.mean()), 1),
        "z_v2_medio_grilla": round(float(grid.z_v2.mean()), 2),
        "pctl_empirico_mediano": round(float(grid.pctl_empirico.median()), 1),
        "celdas_sobre_max_21a": int(grid.supera_max_21a.sum()),
        "celdas_pctl_ge_90": int((grid.pctl_empirico >= 90).sum()),
        "humedales_valpo": int(len(hu_res)),
        "anom_v2_pct_media_humedales": round(float(hu_res.anomaly_v2_pct.mean()), 1),
        "z_v2_medio_humedales": round(float(hu_res.z_v2.mean()), 2),
        "humedales_pctl_ge_90": int((hu_res.pctl_empirico >= 90).sum()),
        "humedales_sobre_max_21a": int((hu_res.pctl_empirico >=
                                        100.0 * 21 / 22 - 0.05).sum()),
        "humedales_z_v2_gt_2": int((hu_res.z_v2 > 2).sum()),
        "humedales_z_v2_gt_3": int((hu_res.z_v2 > 3).sum()),
    }
    (HERE / "resumen_valpo_v2.json").write_text(
        json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(resumen, indent=2, ensure_ascii=False))
    print("\n-> anomaly_grid_valpo_v2.csv, humedales_valpo_anomalia_v2.csv, "
          "resumen_valpo_v2.json")


if __name__ == "__main__":
    main()
