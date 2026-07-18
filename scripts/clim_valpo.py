"""Climatologia de precipitacion 1-18 de julio para Valparaiso, desde el modelo.

Fuente: rasters diarios del modelo ETo del usuario
  MOD_EToPM-HS/03_inputs/ERA5/PM_daily_YYYY.tif  (bandas '..._P_mm_d', mm/dia,
  ERA5-Land, 10 km, EPSG:32719, AOI Region de Valparaiso), anhos 2003-2023.

Para cada celda calcula la suma de precipitacion del 1 al 18 de julio en cada
anho y de ahi la media y desviacion climatologica. Guarda:
  clim_valpo.npz  (mean, std, n, lon, lat, valid, transform)
  clim_valpo.csv  (row,col,lon,lat,clim_mean_mm,clim_std_mm,n_years)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import xy
import geopandas as gpd
from shapely.geometry import Point
from shapely.prepared import prep

import config
MODEL = config.MODEL_DIR
ERA5 = config.ERA5_DIR
AOI = config.AOI_SHP
OUT = config.WORK_DIR
YEARS = range(2003, 2024)          # 2003-2023
DAY_MIN, DAY_MAX = 1, 18           # ventana 1-18 julio (18 completo; reciente corta 09:00)


def july_precip_bands(src) -> list[int]:
    idx = []
    for i, d in enumerate(src.descriptions, start=1):
        if not d or "P_mm" not in d:
            continue
        datestr = d.split("_")[0]          # 'YYYYMMDD'
        if len(datestr) == 8 and datestr[4:6] == "07":
            if DAY_MIN <= int(datestr[6:8]) <= DAY_MAX:
                idx.append(i)
    return idx


def main() -> None:
    per_year = []
    ref_transform = ref_crs = None
    shape = None
    for y in YEARS:
        f = ERA5 / f"PM_daily_{y}.tif"
        with rasterio.open(f) as s:
            if ref_transform is None:
                ref_transform, ref_crs, shape = s.transform, s.crs, (s.height, s.width)
            bands = july_precip_bands(s)
            arr = np.stack([s.read(b) for b in bands]).astype("float64")
            nod = s.nodata
            if nod is not None:
                arr[arr == nod] = np.nan
        ssum = np.nansum(arr, axis=0)
        allnan = np.all(np.isnan(arr), axis=0)
        ssum[allnan] = np.nan
        per_year.append(ssum)
        print(f"  {y}: {len(bands)} bandas P jul1-17 | "
              f"media_celdas={np.nanmean(ssum):.1f} mm")

    stack = np.stack(per_year)                      # (n_years, H, W)
    mean = np.nanmean(stack, axis=0)
    std = np.nanstd(stack, axis=0, ddof=1)
    n = np.sum(~np.isnan(stack), axis=0)

    # centros de celda -> WGS84 y filtro por AOI
    H, W = shape
    rows, cols = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    xs, ys = xy(ref_transform, rows.ravel(), cols.ravel())     # UTM19S centros
    cen = gpd.GeoSeries([Point(x, y) for x, y in zip(xs, ys)], crs=ref_crs)
    cen_wgs = cen.to_crs(4326)
    lon = np.array([p.x for p in cen_wgs]).reshape(H, W)
    lat = np.array([p.y for p in cen_wgs]).reshape(H, W)

    aoi = gpd.read_file(AOI).to_crs(ref_crs).union_all()
    paoi = prep(aoi)
    inside = np.array([paoi.contains(p) for p in cen]).reshape(H, W)
    valid = inside & ~np.isnan(mean) & (n >= 15)

    np.savez(OUT / "clim_valpo.npz", mean=mean, std=std, n=n,
             lon=lon, lat=lat, valid=valid,
             transform=np.array(ref_transform).reshape(-1))

    lines = ["row,col,lon,lat,clim_mean_mm,clim_std_mm,n_years"]
    for r in range(H):
        for c in range(W):
            if not valid[r, c]:
                continue
            lines.append(f"{r},{c},{lon[r,c]:.4f},{lat[r,c]:.4f},"
                         f"{mean[r,c]:.2f},{std[r,c]:.2f},{int(n[r,c])}")
    (OUT / "clim_valpo.csv").write_text("\n".join(lines), encoding="utf-8")

    m = mean[valid]
    print(f"\nceldas validas dentro de AOI Valparaiso: {int(valid.sum())}")
    print(f"clim jul1-17 (mm)  min/media/max: "
          f"{m.min():.1f} / {m.mean():.1f} / {m.max():.1f}")
    print(f"-> clim_valpo.csv ({int(valid.sum())} celdas), clim_valpo.npz")


if __name__ == "__main__":
    main()
