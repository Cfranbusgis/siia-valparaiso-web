"""Anomalia de precipitacion 1-17 julio 2026 en Valparaiso y contraste humedales.

Combina la climatologia del modelo (clim_valpo.csv, ERA5 2003-2023) con el dato
reciente casi-tiempo-real (recent_valpo.csv) para calcular, por celda de 10 km:
    anomaly_pct = (reciente - clim_media)/clim_media * 100
    z_score     = (reciente - clim_media)/clim_std
Luego asigna la anomalia a los humedales de Valparaiso y produce mapas, una
linea de tiempo del rio atmosferico y un resumen.
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from rasterio.transform import Affine
from shapely.geometry import box

import config
HERE = config.WORK_DIR
MODEL = config.MODEL_DIR
AOI = config.AOI_SHP
HU = config.HUMEDALES_SHP
UTM = 32719


def cell_polys(df, transform):
    polys = []
    for r, c in zip(df.row, df.col):
        x0, y0 = transform * (c, r)
        x1, y1 = transform * (c + 1, r + 1)
        polys.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    return gpd.GeoSeries(polys, crs=UTM)


def event_timeline():
    """Serie diaria media de ~6 celdas centrales para ver el pulso del AR."""
    pts = [(-33.05, -71.40), (-33.05, -71.20), (-32.80, -71.20),
           (-33.20, -71.30), (-32.95, -71.05), (-33.40, -71.40)]
    lats = ",".join(str(a) for a, _ in pts)
    lons = ",".join(str(b) for _, b in pts)
    url = ("https://api.open-meteo.com/v1/forecast?latitude=" + lats +
           "&longitude=" + lons + "&daily=precipitation_sum&past_days=25"
           "&forecast_days=1&timezone=America/Santiago")
    d = json.loads(urllib.request.urlopen(url, timeout=60).read())
    locs = d if isinstance(d, list) else [d]
    days = locs[0]["daily"]["time"]
    mat = np.array([l["daily"]["precipitation_sum"] for l in locs], dtype=float)
    mean = np.nanmean(mat, axis=0)
    keep = [(a, m) for a, m in zip(days, mean) if "2026-07-01" <= a <= "2026-07-17"]
    return keep


def main():
    clim = pd.read_csv(HERE / "clim_valpo.csv")
    rec = pd.read_csv(HERE / "recent_valpo.csv")
    df = clim.merge(rec[["row", "col", "recent_mm", "cover_days", "last_day"]],
                    on=["row", "col"])
    df["anomaly_pct"] = (df.recent_mm - df.clim_mean_mm) / df.clim_mean_mm * 100
    df["z_score"] = (df.recent_mm - df.clim_mean_mm) / df.clim_std_mm
    df["anomaly_pct"] = df.anomaly_pct.round(1)
    df["z_score"] = df.z_score.round(2)
    df.to_csv(HERE / "anomaly_grid_valpo.csv", index=False, encoding="utf-8")

    npz = np.load(HERE / "clim_valpo.npz")
    transform = Affine(*npz["transform"][:6])
    cells_u = cell_polys(df, transform)
    grid = gpd.GeoDataFrame(df.copy(), geometry=cells_u.values, crs=UTM)
    grid_wgs = grid.to_crs(4326)

    # --- humedales de Valparaiso ---
    hu = gpd.read_file(HU).to_crs(UTM)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].copy()
    hu_pt = hu.copy(); hu_pt["geometry"] = hu.representative_point()
    j = gpd.sjoin(hu_pt, grid[["anomaly_pct", "z_score", "recent_mm",
                               "clim_mean_mm", "geometry"]],
                  how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")]
    miss = j["anomaly_pct"].isna()
    if miss.any():                                   # los de borde: nodo mas cercano
        jn = gpd.sjoin_nearest(hu_pt[miss], grid[["anomaly_pct", "z_score",
                               "recent_mm", "clim_mean_mm", "geometry"]], how="left")
        jn = jn[~jn.index.duplicated(keep="first")]
        for c in ["anomaly_pct", "z_score", "recent_mm", "clim_mean_mm"]:
            j.loc[miss, c] = jn[c]
    hu_res = hu.copy()
    for c in ["anomaly_pct", "z_score", "recent_mm", "clim_mean_mm"]:
        hu_res[c] = j[c].values
    hu_res.drop(columns="geometry").to_csv(
        HERE / "humedales_valpo_anomalia.csv", index=False, encoding="utf-8")
    hu_res_wgs = hu_res.to_crs(4326)

    # --- resumen ---
    z = hu_res["z_score"]
    resumen = {
        "evento": "Rio atmosferico sobre Chile central, 16-17 julio 2026",
        "ventana": "1-17 julio 2026",
        "climatologia": "modelo MOD_EToPM-HS (ERA5-Land 10 km), 2003-2023",
        "reciente": "Open-Meteo forecast (past_days, casi-tiempo-real)",
        "celdas": int(len(df)),
        "clim_media_mm": round(float(df.clim_mean_mm.mean()), 1),
        "reciente_media_mm": round(float(df.recent_mm.mean()), 1),
        "anom_pct_media_grilla": round(float(df.anomaly_pct.mean()), 1),
        "z_medio_grilla": round(float(df.z_score.mean()), 2),
        "humedales_valpo": int(len(hu_res)),
        "anom_pct_media_humedales": round(float(hu_res.anomaly_pct.mean()), 1),
        "z_medio_humedales": round(float(z.mean()), 2),
        "humedales_z_gt_2": int((z > 2).sum()),
        "humedales_z_gt_3": int((z > 3).sum()),
        "top_comunas": (hu_res.groupby("comuna")["anomaly_pct"].mean()
                        .sort_values(ascending=False).head(10).round(0).to_dict()),
    }
    timeline = event_timeline()
    resumen["serie_diaria_mm_media"] = {a: round(m, 1) for a, m in timeline}
    (HERE / "resumen_valpo.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))

    # Recorte de todas las capas al limite regional (sin fragmentos externos).
    aoi = gpd.read_file(AOI).to_crs(4326)
    grid_clip = gpd.clip(grid_wgs, aoi)
    hu_clip = gpd.clip(hu_res_wgs, aoi)

    # --- FIGURA 1: anomalia porcentual ---
    norm = TwoSlopeNorm(vmin=0, vcenter=100, vmax=400)
    fig, ax = plt.subplots(figsize=(8.5, 9.5))
    grid_clip.plot(ax=ax, column="anomaly_pct", cmap="YlGnBu", norm=norm,
                   edgecolor="white", linewidth=0.15, legend=True,
                   legend_kwds={"label": "Anomalía (%)", "shrink": 0.62})
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    fig.tight_layout(); fig.savefig(HERE / "mapa_anomalia_valpo.png", dpi=170)
    plt.close(fig)

    # --- FIGURA 2: exposicion de humedales (puntuacion estandarizada z) ---
    znorm = TwoSlopeNorm(vmin=0, vcenter=2, vmax=6)
    fig, ax = plt.subplots(figsize=(8.5, 9.5))
    grid_clip.plot(ax=ax, color="#f4f4f4", edgecolor="#e2e2e2", linewidth=0.2)
    hu_clip.plot(ax=ax, column="z_score", cmap="viridis", norm=znorm,
                 edgecolor="black", linewidth=0.12, alpha=0.9, legend=True,
                 legend_kwds={"label": "Puntuación estandarizada (z)", "shrink": 0.62})
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    fig.tight_layout(); fig.savefig(HERE / "mapa_humedales_valpo.png", dpi=170)
    plt.close(fig)

    # --- FIGURA 3: evolucion diaria de la precipitacion ---
    days = [str(int(a[8:10])) for a, _ in timeline]; vals = [m for _, m in timeline]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(days, vals, color=["#b5341f" if v > 20 else "#3a7ca5" for v in vals])
    ax.set_ylabel("Precipitación media regional (mm/día)")
    ax.set_xlabel("Día (julio de 2026)")
    ax.grid(axis="y", color="#e6e6e6", linewidth=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(HERE / "evento_rio_atmosferico.png", dpi=150)
    plt.close(fig)
    print("\nfiguras guardadas.")


if __name__ == "__main__":
    main()
