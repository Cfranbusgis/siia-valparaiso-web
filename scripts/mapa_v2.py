"""FASE 4d - Mapa v2: anomalia corregida (IDW de residuos) + percentil empirico.

Dos paneles sobre la grilla v2 (anomaly_grid_valpo_v2.csv), mismo estilo grafico
que analyze_valpo.py (YlGnBu, limite regional, WGS84):
  izquierda: anomalia porcentual v2 (reciente corregido vs clim homogenea)
  derecha:   percentil empirico (21 anhos, Weibull); celdas que superan el
             maximo del registro con hatching.

Salida: mapa_anomalia_valpo_v2.png
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from affine import Affine
from shapely.geometry import box

HERE = Path(__file__).resolve().parent
AOI = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\AOI\RV.shp")
UTM = 32719


def main():
    df = pd.read_csv(HERE / "anomaly_grid_valpo_v2.csv")
    npz = np.load(HERE / "clim_valpo.npz")
    transform = Affine(*npz["transform"][:6])
    polys = []
    for r, c in zip(df.row, df.col):
        x0, y0 = transform * (c, r)
        x1, y1 = transform * (c + 1, r + 1)
        polys.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    grid = gpd.GeoDataFrame(df, geometry=polys, crs=UTM).to_crs(4326)

    aoi = gpd.read_file(AOI).to_crs(4326)
    grid_clip = gpd.clip(grid, aoi)

    from map_deco import decorate
    fig, axes = plt.subplots(1, 2, figsize=(15, 9))

    ax = axes[0]
    norm = TwoSlopeNorm(vmin=-50, vcenter=0, vmax=250)
    grid_clip.plot(ax=ax, column="anomaly_v2_pct", cmap="YlGnBu", norm=norm,
                   edgecolor="white", linewidth=0.15, legend=True,
                   legend_kwds={"label": "Anomalía corregida (%)", "shrink": 0.62})
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    ax.set_title("Anomalía corregida (reciente corregido por obs. DMC)\n"
                 "1–19 jul 2026 vs climatología homogénea 1995–2025",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    decorate(ax, km=50)

    ax = axes[1]
    grid_clip.plot(ax=ax, column="pctl_empirico", cmap="YlGnBu",
                   vmin=50, vmax=100, edgecolor="white", linewidth=0.15,
                   legend=True,
                   legend_kwds={"label": "Percentil empírico (registro 30 años)",
                                "shrink": 0.62})
    sup = grid_clip[grid_clip.supera_max_21a]
    if len(sup):
        sup.plot(ax=ax, facecolor="none", edgecolor="#b5341f",
                 hatch="///", linewidth=0.6)
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    ax.set_title("Rareza empírica del acumulado corregido\n"
                 "(percentil dentro del registro 1995–2025)",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    decorate(ax, km=50)

    fig.suptitle("Río atmosférico jul-2026, Región de Valparaíso — anomalía corregida "
                 "(corrección espacial de residuos validada por LOO)",
                 fontsize=12.5, fontweight="bold", y=0.98)
    fig.tight_layout()
    fig.savefig(HERE / "mapa_anomalia_valpo_v2.png", dpi=170)
    plt.close(fig)
    print("-> mapa_anomalia_valpo_v2.png")


if __name__ == "__main__":
    main()
