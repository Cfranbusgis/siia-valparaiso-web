"""Distancia a la red de drenaje desde el DEM 30 m (predictor de inundación, fsm-pk).

Extrae la red de drenaje del flujo D8 (acumulación > umbral) y calcula, por celda,
la distancia euclidiana al cauce más cercano. Cerca del drenaje = más propenso a
inundación por desborde. Se normaliza invertida (0 lejos, 1 sobre el cauce) para
sumarla a la susceptibilidad de acumulación, homogénea con TWI/concavidad/suelo.

Salida: dist_drenaje_valpo_30m.tif, humedales_distdren.csv
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
if not hasattr(np, "in1d"): np.in1d = np.isin
import rasterio, geopandas as gpd, pandas as pd
from pysheds.grid import Grid
from scipy.ndimage import distance_transform_edt
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
DEM = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\DEM\DEM_AW3D30_30m_UTM19S_RV.tif")
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"
ACC_THR = 1000          # celdas aguas arriba para definir cauce (~0,9 km2 a 30 m)

def main():
    with rasterio.open(DEM) as s:
        dem = s.read(1).astype("float64"); tr = s.transform; crs = s.crs
        nod = s.nodata; px = abs(tr.a)
    valid = (dem != nod) & (dem > -100)

    grid = Grid.from_raster(str(DEM)); dg = grid.read_raster(str(DEM))
    inflated = grid.resolve_flats(grid.fill_depressions(grid.fill_pits(dg)))
    fdir = grid.flowdir(inflated)
    acc = np.asarray(grid.accumulation(fdir), dtype="float64")

    streams = (acc >= ACC_THR) & valid
    print(f"celdas de cauce: {streams.sum()} ({100*streams.sum()/valid.sum():.2f}% del área)")

    # distancia euclidiana (en metros) a la celda de cauce más cercana
    dist = distance_transform_edt(~streams, sampling=px).astype("float32")
    dist[~valid] = -9999

    prof = dict(driver="GTiff", height=dem.shape[0], width=dem.shape[1], count=1,
                dtype="float32", crs=crs, transform=tr, nodata=-9999,
                compress="lzw", tiled=True)
    with rasterio.open(HERE / "dist_drenaje_valpo_30m.tif", "w", **prof) as d:
        d.write(dist, 1)

    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True).to_crs(crs)
    rp = hu.representative_point(); inv = ~tr
    cols, rows = inv * (rp.x.values, rp.y.values)
    rows = np.clip(np.asarray(rows, int), 0, dem.shape[0]-1)
    cols = np.clip(np.asarray(cols, int), 0, dem.shape[1]-1)
    dh = dist[rows, cols]
    dh[dh < 0] = np.nan
    # proximidad normalizada: 1 sobre/junto al cauce (<=60 m), 0 a >=1 km
    prox = np.clip(1 - (dh - 60) / (1000 - 60), 0, 1)
    out = pd.DataFrame({"nom_humed": hu["nom_humed"].values, "comuna": hu["comuna"].values,
                        "dist_drenaje_m": np.round(dh, 0), "prox_drenaje": np.round(prox, 3)})
    out.to_csv(HERE / "humedales_distdren.csv", index=False, encoding="utf-8")
    print(f"dist. a drenaje (m) mediana: {np.nanmedian(dh):.0f} | "
          f"humedales a <=120 m del cauce: {(dh<=120).sum()} ({100*np.nanmean(dh<=120):.0f}%)")
    print("-> dist_drenaje_valpo_30m.tif, humedales_distdren.csv")

if __name__ == "__main__":
    main()
