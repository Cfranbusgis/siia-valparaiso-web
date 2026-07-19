# -*- coding: utf-8 -*-
"""Modelo 3D del relieve de Valparaiso con la anomalia de julio 2026 drapeada.

Estilo basado en MOD_GLACIAR/scripts_R/modelo_3d_valparaiso_astgtm.py:
superficie Plotly del DEM con exageracion vertical, camara ortografica, barra de
color y overlay de clic. Aqui el color de la superficie NO es la elevacion sino la
ANOMALIA porcentual de precipitacion (1-17 jul 2026), de modo que el relieve
muestra donde se concentro la senal respecto de la topografia. Los humedales con
z>3 se marcan sobre el terreno, coloreados por su exposicion compuesta.

Salidas:
  modelo_3d_anomalia_valpo.html  (interactivo, plotly.js embebido)
  modelo_3d_anomalia_valpo.png   (figura estatica para informe/paper, matplotlib)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import xy
from scipy.spatial import cKDTree
import plotly.graph_objects as go

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, TwoSlopeNorm
from matplotlib import cm

HERE = Path(__file__).resolve().parent
MODEL = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS")
DEM = MODEL / "03_inputs" / "DEM" / "DEM_250m_UTM19S_AOI.tif"
AOI = MODEL / "03_inputs" / "AOI" / "RV.shp"
VE = 8.0                       # exageracion vertical
MAX_SIDE = 340                 # remuestreo para rendimiento


def load_dem_downsampled():
    with rasterio.open(DEM) as s:
        dem = s.read(1).astype("float64")
        transform = s.transform
        crs = s.crs
        nod = s.nodata
    dem[dem == nod] = np.nan
    dem[dem < -100] = np.nan
    f = max(1, int(np.ceil(max(dem.shape) / MAX_SIDE)))
    dem = dem[::f, ::f]
    transform = transform * transform.scale(f, f)
    return dem, transform, crs


def drape_anomaly(dem, transform, crs):
    """Asigna a cada pixel del DEM la anomalia de la celda mas cercana (KDTree)."""
    g = pd.read_csv(HERE / "anomaly_grid_valpo_v2.csv")
    gpts = gpd.GeoDataFrame(g, geometry=gpd.points_from_xy(g.lon, g.lat), crs=4326)
    gpts = gpts.to_crs(crs)
    tree = cKDTree(np.c_[gpts.geometry.x, gpts.geometry.y])

    H, W = dem.shape
    rr, cc = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    xs, ys = xy(transform, rr.ravel(), cc.ravel())
    xs = np.array(xs); ys = np.array(ys)
    _, idx = tree.query(np.c_[xs, ys])
    anom = gpts["anomaly_v2_pct"].values[idx].reshape(H, W)
    anom[np.isnan(dem)] = np.nan
    # coordenadas locales en km
    x_km = (xs.reshape(H, W) - np.nanmin(xs)) / 1000.0
    y_km = (ys.reshape(H, W) - np.nanmin(ys)) / 1000.0
    return anom, x_km, y_km


def wetlands_xyz(dem, transform, crs):
    hu = gpd.read_file(HERE / "humedales_p90_exposicion_v2.geojson").to_crs(crs)
    pts = hu.representative_point()
    inv = ~transform
    cols, rows = inv * (pts.x.values, pts.y.values)
    rows = np.clip(rows.astype(int), 0, dem.shape[0] - 1)
    cols = np.clip(cols.astype(int), 0, dem.shape[1] - 1)
    elev = dem[rows, cols]
    x_km = (pts.x.values - np.nanmin([xy(transform, 0, c)[0] for c in [0]])) / 1000.0
    return hu, pts, elev


def build_html(dem, anom, x_km, y_km, transform, crs):
    z_plot = (np.nan_to_num(dem, nan=0.0) / 1000.0) * VE
    z_plot[np.isnan(dem)] = np.nan
    xline = x_km[0]
    yline = y_km[:, 0]

    x_span = float(np.nanmax(x_km) - np.nanmin(x_km))
    y_span = float(np.nanmax(y_km) - np.nanmin(y_km))
    z_span = float(np.nanmax(z_plot) - np.nanmin(z_plot))
    mx = max(x_span, y_span, 1.0)
    aspect = dict(x=x_span/mx, y=y_span/mx, z=max(z_span/mx, 0.12))

    surf = go.Surface(
        z=z_plot, x=xline, y=yline, surfacecolor=anom,
        colorscale="YlGnBu", cmin=-50, cmax=250,
        colorbar=dict(title="Anomalía corregida (%)", len=0.7, x=1.02, y=0.5),
        lighting=dict(ambient=0.5, diffuse=0.7, specular=0.1, roughness=0.9),
        lightposition=dict(x=100000, y=100000, z=80000),
        hovertemplate="E-O %{x:.0f} km<br>S-N %{y:.0f} km<br>Anomalía %{surfacecolor:.0f} %<extra></extra>",
        name="relieve")

    # humedales z>3 sobre el terreno
    hu, pts, elev = wetlands_xyz(dem, transform, crs)
    hx = (pts.x.values - float(np.nanmin([xy(transform, r, 0)[0] for r in [0]]))) / 1000.0
    # recomputar x/y km de humedales de forma consistente con la grilla
    x0 = xy(transform, 0, 0)[0]; y0 = xy(transform, dem.shape[0]-1, 0)[1]
    hx = (pts.x.values - x0) / 1000.0
    hy = (pts.y.values - y0) / 1000.0
    hz = (np.nan_to_num(elev, nan=0.0) / 1000.0) * VE + 0.05
    scat = go.Scatter3d(
        x=hx, y=hy, z=hz, mode="markers",
        marker=dict(size=2.4, color=hu["expo_comp_w50"].values, colorscale="Inferno",
                    cmin=0.3, cmax=0.9, showscale=False, opacity=0.85),
        text=[f"{n}<br>percentil P{p:.0f} · exposición compuesta {e:.2f}"
              for n, p, e in zip(hu["nom_humed"], hu["pctl_empirico"],
                                 hu["expo_comp_w50"])],
        hovertemplate="%{text}<extra></extra>", name="humedales ≥ P90")

    fig = go.Figure([surf, scat])
    fig.update_layout(
        title="Relieve de la Región de Valparaíso con la anomalía de precipitación "
              "corregida de julio de 2026<br><sup>Color de la superficie: anomalía corregida "
              "(%) · puntos: humedales ≥ P90 por exposición compuesta "
              "(exageración vertical ×8)</sup>",
        scene=dict(
            xaxis_title="Distancia Este-Oeste (km)",
            yaxis_title="Distancia Sur-Norte (km)",
            zaxis_title="Elevación (m)",
            aspectmode="manual", aspectratio=aspect,
            camera=dict(eye=dict(x=-1.5, y=-1.35, z=0.75), up=dict(x=0, y=0, z=1),
                        projection=dict(type="orthographic")),
            xaxis=dict(showbackground=True, backgroundcolor="rgba(245,247,250,1)"),
            yaxis=dict(showbackground=True, backgroundcolor="rgba(245,247,250,1)"),
            zaxis=dict(showbackground=True, backgroundcolor="rgba(250,250,250,1)",
                       tickvals=[(v/1000)*VE for v in (0,1000,2000,3000,4000,5000)],
                       ticktext=["0","1000","2000","3000","4000","5000"]),
        ),
        margin=dict(l=0, r=0, t=64, b=0), template="plotly_white")

    out = HERE / "modelo_3d_anomalia_valpo.html"
    fig.write_html(str(out), include_plotlyjs=True)
    _add_click_overlay(out)
    print("HTML 3D ->", out.name)


def _add_click_overlay(html_path: Path):
    snippet = """
<div id="anom-overlay" style="position:fixed;top:12px;right:12px;z-index:9999;padding:10px 12px;background:rgba(10,22,30,0.86);color:#eef7ff;border-radius:10px;font-family:Arial,sans-serif;font-size:13px;line-height:1.35;box-shadow:0 8px 18px rgba(0,0,0,0.25);">Punto seleccionado: --</div>
<script>
(function(){function bind(){var gd=document.querySelector('.plotly-graph-div');var b=document.getElementById('anom-overlay');if(!gd||!b||typeof gd.on!=='function')return false;gd.on('plotly_click',function(ev){var p=ev&&ev.points&&ev.points[0];if(!p)return;if(p.surfacecolor!==undefined&&Number.isFinite(p.surfacecolor)){b.textContent='Anomalía: '+p.surfacecolor.toFixed(0)+' %';}else if(p.text){b.innerHTML=p.text;}});return true;}if(!bind())window.setTimeout(bind,1200);})();
</script>
"""
    t = html_path.read_text(encoding="utf-8")
    t = t.replace("</body>", snippet + "\n</body>", 1) if "</body>" in t else t + snippet
    html_path.write_text(t, encoding="utf-8")


def build_png(dem, anom, x_km, y_km):
    z_plot = (dem / 1000.0) * VE
    x_span = float(np.nanmax(x_km) - np.nanmin(x_km))
    y_span = float(np.nanmax(y_km) - np.nanmin(y_km))
    z_span = max(float(np.nanmax(z_plot) - np.nanmin(z_plot)), 0.2 * max(x_span, y_span))

    norm = TwoSlopeNorm(vmin=-50, vcenter=0, vmax=250)
    face = cm.YlGnBu(norm(np.nan_to_num(anom, nan=0.0)))
    face[..., -1] = np.where(np.isnan(dem), 0.0, 1.0)

    fig = plt.figure(figsize=(11, 6.6), dpi=115)
    ax = fig.add_axes([0.03, 0.06, 0.70, 0.86], projection="3d")
    ax.set_proj_type("ortho")
    ax.plot_surface(x_km, y_km, np.ma.masked_invalid(z_plot), facecolors=face,
                    linewidth=0, antialiased=True, shade=False, rstride=1, cstride=1)
    fig.suptitle("Relieve de Valparaíso con la anomalía de precipitación corregida "
                 "· julio 2026", fontsize=13, fontweight="bold", y=0.97)
    ax.set_xlabel("Este-Oeste (km)", labelpad=12)
    ax.set_ylabel("Sur-Norte (km)", labelpad=12)
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel("Elevación (m)", rotation=90, labelpad=16)
    ax.set_zticks([(v/1000)*VE for v in (0,1000,2000,3000,4000,5000)])
    ax.set_zticklabels(["0","1000","2000","3000","4000","5000"])
    ax.set_box_aspect((x_span, y_span, z_span))
    ax.view_init(elev=27, azim=235)

    cax = fig.add_axes([0.80, 0.22, 0.018, 0.5])
    cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap="YlGnBu"), cax=cax)
    cb.set_label("Anomalía de precipitación corregida (%)", rotation=90, labelpad=12)
    fig.text(0.76, 0.14, f"Exageración vertical: ×{VE:g}", fontsize=9)
    fig.savefig(HERE / "modelo_3d_anomalia_valpo.png", bbox_inches="tight",
                pad_inches=0.1, dpi=115)
    plt.close(fig)
    print("PNG 3D -> modelo_3d_anomalia_valpo.png")


def main():
    dem, transform, crs = load_dem_downsampled()
    anom, x_km, y_km = drape_anomaly(dem, transform, crs)
    build_html(dem, anom, x_km, y_km, transform, crs)
    build_png(dem, anom, x_km, y_km)


if __name__ == "__main__":
    main()
