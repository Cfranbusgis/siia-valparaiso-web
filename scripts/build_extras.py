# -*- coding: utf-8 -*-
"""Cierres finales: (a) mapa modelo-vs-observado, (b) anomalia observada, (c) GeoJSON.

(a) Superpone las estaciones DMC/DGAC (agua caida 24 h observada) sobre el mapa de
    anomalia del modelo, para el contraste espacial.
(b) Para cada estacion, toma la climatologia del modelo (1-17 jul, celda mas
    cercana) y expresa el observado como anomalia: el acumulado de 24 h como % del
    total quincenal normal y en desviaciones estandar climatologicas.
(c) Exporta a GeoJSON (EPSG:4326) los humedales de Valparaiso con z > 3.
"""
from __future__ import annotations

import json
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


def nearest(grid: pd.DataFrame, lon: float, lat: float):
    d2 = (grid.lon - lon) ** 2 + (grid.lat - lat) ** 2
    return grid.loc[d2.idxmin()]


def main():
    grid = pd.read_csv(HERE / "anomaly_grid_valpo.csv")
    dmc = pd.read_csv(HERE / "dmc_observado_valpo.csv")

    # ---- (b) anomalia observada por estacion ----
    recs = []
    for _, s in dmc.iterrows():
        g = nearest(grid, s.lon, s.lat)
        clim = g.clim_mean_mm
        obs = s.agua24h_mm
        recs.append({
            "estacion": s.estacion, "lon": s.lon, "lat": s.lat,
            "obs_24h_mm": obs,
            "clim_1_17jul_mm": round(clim, 1),
            "obs_pct_de_quincena_normal": round(obs / clim * 100, 0) if clim else None,
            "obs_en_sigma_clim": round((obs - clim) / g.clim_std_mm, 2) if g.clim_std_mm else None,
            "modelo_recent_1_17_mm": round(g.recent_mm, 1),
            "modelo_anom_pct": g.anomaly_pct,
            "modelo_z": g.z_score,
        })
    obs = pd.DataFrame(recs).sort_values("obs_24h_mm", ascending=False)
    obs.to_csv(HERE / "estaciones_modelo_vs_obs.csv", index=False, encoding="utf-8")
    print("=== (b) anomalia observada (top) ===")
    print(obs.head(8).to_string(index=False))

    # ---- (a) mapa modelo-vs-observado ----
    npz = np.load(HERE / "clim_valpo.npz")
    transform = Affine(*npz["transform"][:6])
    polys = [box(*sorted([transform*(c, r), transform*(c+1, r+1)])[0],
                 *sorted([transform*(c, r), transform*(c+1, r+1)])[1])
             for r, c in zip(grid.row, grid.col)]
    # box() necesita (minx,miny,maxx,maxy): recomputar limpio
    polys = []
    for r, c in zip(grid.row, grid.col):
        x0, y0 = transform * (c, r); x1, y1 = transform * (c + 1, r + 1)
        polys.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    gcells = gpd.GeoDataFrame(grid.copy(), geometry=polys, crs=UTM).to_crs(4326)
    aoi = gpd.read_file(AOI).to_crs(4326)
    gclip = gpd.clip(gcells, aoi)
    # solo estaciones dentro del limite regional (evita puntos de contexto sueltos)
    dmc_gdf = gpd.GeoDataFrame(
        dmc.copy(), geometry=gpd.points_from_xy(dmc.lon, dmc.lat), crs=4326)
    dmc_in = gpd.clip(dmc_gdf, aoi)

    fig, ax = plt.subplots(figsize=(8.5, 9.5))
    gclip.plot(ax=ax, column="anomaly_pct", cmap="YlGnBu",
               norm=TwoSlopeNorm(vmin=0, vcenter=100, vmax=400),
               edgecolor="white", linewidth=0.15, alpha=.9, legend=True,
               legend_kwds={"label": "Anomalía modelada (%)", "shrink": .55})
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    sc = ax.scatter(dmc_in.geometry.x, dmc_in.geometry.y,
                    s=20 + dmc_in.agua24h_mm * 1.6,
                    c=dmc_in.agua24h_mm, cmap="OrRd", edgecolor="k", linewidth=.6,
                    zorder=5, vmin=0, vmax=120)
    cb = fig.colorbar(sc, ax=ax, shrink=.35, pad=.02)
    cb.set_label("Precipitación observada 24 h (mm) — DMC/DGAC")
    for _, s in dmc_in.sort_values("agua24h_mm", ascending=False).head(6).iterrows():
        ax.annotate(f"{s.agua24h_mm:.0f}", (s.geometry.x, s.geometry.y), fontsize=7,
                    xytext=(3, 3), textcoords="offset points", zorder=6)
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    fig.tight_layout(); fig.savefig(HERE / "mapa_modelo_vs_obs.png", dpi=170)
    plt.close(fig)

    # ---- (c) GeoJSON humedales z>3 ----
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    za = pd.read_csv(HERE / "humedales_valpo_anomalia.csv")
    assert len(hu) == len(za), f"desalineado: {len(hu)} vs {len(za)}"
    hu["z_score"] = za["z_score"].values
    hu["anomaly_pct"] = za["anomaly_pct"].values
    crit = hu[hu["z_score"] > 3].copy()
    keep = ["nom_humed", "comuna", "tipo", "z_score", "anomaly_pct", "geometry"]
    crit = crit[[c for c in keep if c in crit.columns]]
    crit.to_crs(4326).to_file(HERE / "humedales_z_gt3_valpo.geojson", driver="GeoJSON")
    print(f"\n=== (c) GeoJSON: {len(crit)} humedales con z>3 -> humedales_z_gt3_valpo.geojson ===")
    print("mapas/archivos guardados.")


if __name__ == "__main__":
    main()
