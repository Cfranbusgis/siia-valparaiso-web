"""Modelo de concavidad / depresiones desde el DEM 30 m (AW3D30) para identificar
áreas propensas a inundación (acumulación de agua).

Deriva:
  - curvatura general (Laplaciano del DEM): negativa = cóncavo (acumula),
    positiva = convexo (drena);
  - profundidad de depresión = DEM_relleno - DEM (pysheds fill_depressions);
    marca hoyas endorreicas / vegas donde el agua se estanca.
Combina ambos en un índice de acumulación topográfica 0..1 (1 = cóncavo/hoya),
complementario del TWI.

Salida: concavidad_valpo_30m.tif, depresion_valpo_30m.tif,
        humedales_concavidad.csv (por humedal), resumen_concavidad.json
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
if not hasattr(np, "in1d"): np.in1d = np.isin
import rasterio, geopandas as gpd, pandas as pd
from pysheds.grid import Grid
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
DEM = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\DEM\DEM_AW3D30_30m_UTM19S_RV.tif")
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"

def norm(a, lo, hi):
    return np.clip((a - lo) / (hi - lo), 0, 1)

def main():
    with rasterio.open(DEM) as s:
        dem = s.read(1).astype("float64"); tr = s.transform; crs = s.crs
        nod = s.nodata; px = abs(tr.a)
    dem[dem == nod] = np.nan; dem[dem < -100] = np.nan
    filled = np.nan_to_num(dem, nan=np.nanmin(dem))

    # --- curvatura general = -Laplaciano (positivo = cóncavo) ---
    gy, gx = np.gradient(filled, px, px)
    gyy = np.gradient(gy, px, axis=0); gxx = np.gradient(gx, px, axis=1)
    concav = -(gxx + gyy)                      # cóncavo (hoya) -> positivo
    concav[np.isnan(dem)] = np.nan

    # --- profundidad de depresión (pysheds) ---
    grid = Grid.from_raster(str(DEM)); dg = grid.read_raster(str(DEM))
    dep = np.asarray(grid.fill_depressions(grid.fill_pits(dg)), dtype="float64") - \
          np.asarray(dg, dtype="float64")
    dep[dep < 0] = 0; dep[np.isnan(dem)] = np.nan

    # normalizar (percentiles robustos)
    c = concav[np.isfinite(concav)]
    cn = norm(concav, np.nanpercentile(c, 50), np.nanpercentile(c, 98))  # >mediana
    depn = norm(dep, 0, np.nanpercentile(dep[dep > 0], 95) if (dep > 0).any() else 1)
    acc_topo = np.nanmax(np.dstack([cn, depn]), axis=2)   # unión: cóncavo O hoya
    acc_topo[np.isnan(dem)] = np.nan

    prof = dict(driver="GTiff", height=dem.shape[0], width=dem.shape[1], count=1,
                dtype="float32", crs=crs, transform=tr, nodata=-9999,
                compress="lzw", tiled=True)
    for arr, name in [(concav, "concavidad_valpo_30m.tif"),
                      (dep, "depresion_valpo_30m.tif")]:
        with rasterio.open(HERE / name, "w", **prof) as d:
            d.write(np.where(np.isfinite(arr), arr, -9999).astype("float32"), 1)

    # --- por humedal ---
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True).to_crs(crs)
    rp = hu.representative_point()
    inv = ~tr; cols, rows = inv * (rp.x.values, rp.y.values)
    rows = np.clip(np.asarray(rows, int), 0, dem.shape[0]-1)
    cols = np.clip(np.asarray(cols, int), 0, dem.shape[1]-1)
    def samp(a): return np.array([a[r, c] for r, c in zip(rows, cols)])
    out = pd.DataFrame({
        "nom_humed": hu["nom_humed"].values, "comuna": hu["comuna"].values,
        "concavidad": np.round(samp(concav), 4),
        "depresion_m": np.round(samp(dep), 2),
        "acc_topo": np.round(samp(acc_topo), 3),
    })
    out.to_csv(HERE / "humedales_concavidad.csv", index=False, encoding="utf-8")
    res = {"concavo_pct": round(100*float(np.nanmean(samp(concav) > 0)), 1),
           "acc_topo_media": round(float(np.nanmean(out.acc_topo)), 3),
           "humedales_en_hoya_dep_gt_0_5m": int((out.depresion_m > 0.5).sum())}
    (HERE/"resumen_concavidad.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("-> concavidad/depresion .tif, humedales_concavidad.csv")

if __name__ == "__main__":
    main()
