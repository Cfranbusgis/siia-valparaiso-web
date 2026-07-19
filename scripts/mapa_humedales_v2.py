"""FASE 4e - Figura 4 v2: humedales coloreados por percentil empirico (21 anhos).

Reemplaza el mapa v1 (z-score gaussiano) del informe. Mismo estilo grafico que
analyze_valpo.py FIGURA 2. Ademas imprime la tabla comunal v2 (anomalia
corregida media y percentil medio por comuna) para el informe.

Salida: mapa_humedales_valpo_v2.png + filas HTML por consola.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from affine import Affine
from shapely.geometry import box

HERE = Path(__file__).resolve().parent
AOI = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\AOI\RV.shp")
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"
UTM = 32719


def main():
    hv = pd.read_csv(HERE / "humedales_valpo_anomalia_v2.csv", encoding="utf-8")
    hu = gpd.read_file(HU).to_crs(UTM)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    assert len(hu) == len(hv), (len(hu), len(hv))
    hu["pctl_empirico"] = hv.pctl_empirico.values
    hu["anomaly_v2_pct"] = hv.anomaly_v2_pct.values

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
    hu_clip = gpd.clip(hu.to_crs(4326), aoi)

    from map_deco import decorate
    fig, ax = plt.subplots(figsize=(8.5, 9.5))
    grid_clip.plot(ax=ax, color="#f4f4f4", edgecolor="#e2e2e2", linewidth=0.2)
    hu_clip.plot(ax=ax, column="pctl_empirico", cmap="viridis", vmin=50, vmax=100,
                 edgecolor="black", linewidth=0.12, alpha=0.9, legend=True,
                 legend_kwds={"label": "Percentil empírico del acumulado corregido "
                                       "(registro 1995–2025)", "shrink": 0.62})
    aoi.boundary.plot(ax=ax, color="#111", linewidth=1.1)
    ax.set_title("Exposición meteorológica de los humedales\n"
                 "Percentil empírico del acumulado (registro 1995–2025)",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud"); ax.set_aspect(1.18)
    decorate(ax, km=50)
    fig.tight_layout()
    fig.savefig(HERE / "mapa_humedales_valpo_v2.png", dpi=170)
    plt.close(fig)
    print("-> mapa_humedales_valpo_v2.png")

    top = (hu.groupby("comuna")
             .agg(anom=("anomaly_v2_pct", "mean"), pctl=("pctl_empirico", "mean"),
                  n=("anomaly_v2_pct", "size"))
             .sort_values("pctl", ascending=False).head(10))
    wmax = top.pctl.max()
    rows = ["  <tbody>"]
    for com, r in top.iterrows():
        w = int(round(100 * r.pctl / wmax))
        rows.append(f'<tr><td>{com}</td><td class="num">P{r.pctl:.0f}</td>'
                    f'<td class="num">{r.anom:+.0f} %</td>'
                    f'<td class="bar"><span style="width:{w}%"></span></td></tr>')
    rows.append("</tbody>")
    print("".join(rows))


if __name__ == "__main__":
    main()
