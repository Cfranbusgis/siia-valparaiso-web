# -*- coding: utf-8 -*-
"""Analisis topografico del DEM y cruce con los humedales de mayor anomalia (z>3).

Deriva del DEM regional (MOD_EToPM-HS, 250 m, EPSG:32719):
  - pendiente (grados),
  - acumulacion de flujo D8 (pysheds) tras rellenar depresiones,
  - indice topografico de humedad TWI = ln( a / tan(beta) ),
    donde a = area de contribucion por unidad de ancho y beta = pendiente.
TWI alto marca posiciones de convergencia hidrica (fondos de valle, vegas):
mayor propension a saturacion/anegamiento.

Combina la EXPOSICION METEOROLOGICA (anomalia z de precipitacion, ya calculada)
con la EXPOSICION TOPOGRAFICA (TWI normalizado) en un indice compuesto simple,
y lo asigna a cada humedal z>3. Salidas:
  humedales_z_gt3_topo.csv / .geojson  (con slope, flow_acc, twi, indices)
  twi_valpo.tif                         (raster TWI para QGIS)
  resumen_topo.json
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
# compatibilidad numpy 2.x: pysheds usa np.in1d (removido) -> alias a np.isin
if not hasattr(np, "in1d"):
    np.in1d = np.isin
import pandas as pd
import geopandas as gpd
import rasterio
from pysheds.grid import Grid

HERE = Path(__file__).resolve().parent
MODEL = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS")
DEM = MODEL / "03_inputs" / "DEM" / "DEM_250m_UTM19S_AOI.tif"
AOI = MODEL / "03_inputs" / "AOI" / "RV.shp"
HU_GEO = HERE / "humedales_z_gt3_valpo.geojson"


def main():
    # --- DEM base ---
    with rasterio.open(DEM) as s:
        dem = s.read(1).astype("float64")
        transform = s.transform
        crs = s.crs
        nodata = s.nodata
        px = abs(transform.a)          # tamano de celda (m)
    dem[dem == nodata] = np.nan
    dem[dem < -100] = np.nan

    # --- pendiente (grados) ---
    gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmin(dem)), px, px)
    slope_deg = np.degrees(np.arctan(np.hypot(gx, gy)))

    # --- acumulacion de flujo D8 con pysheds ---
    grid = Grid.from_raster(str(DEM))
    dem_g = grid.read_raster(str(DEM))
    pit_filled = grid.fill_pits(dem_g)
    flooded = grid.fill_depressions(pit_filled)
    inflated = grid.resolve_flats(flooded)
    fdir = grid.flowdir(inflated)
    acc = grid.accumulation(fdir)          # numero de celdas aguas arriba
    acc = np.asarray(acc, dtype="float64")

    # --- TWI = ln( a / tan(beta) ), a = (acc+1)*px  (area contribuyente/ancho) ---
    tanb = np.tan(np.radians(np.clip(slope_deg, 0.1, None)))  # evita div/0
    a_spec = (acc + 1.0) * px
    twi = np.log(a_spec / tanb)
    twi[np.isnan(dem)] = np.nan

    # normalizado 0..1 (percentiles 2-98 para robustez)
    finite = twi[np.isfinite(twi)]
    lo, hi = np.nanpercentile(finite, 2), np.nanpercentile(finite, 98)
    twi_n = np.clip((twi - lo) / (hi - lo), 0, 1)

    # --- guardar raster TWI ---
    prof = dict(driver="GTiff", height=twi.shape[0], width=twi.shape[1], count=1,
                dtype="float32", crs=crs, transform=transform, nodata=-9999)
    with rasterio.open(HERE / "twi_valpo.tif", "w", **prof) as d:
        d.write(np.where(np.isfinite(twi), twi, -9999).astype("float32"), 1)

    # --- muestreo en los humedales z>3 ---
    hu = gpd.read_file(HU_GEO).to_crs(crs)
    pts = hu.representative_point()
    inv = ~transform
    cols, rows = inv * (pts.x.values, pts.y.values)
    rows = np.clip(rows.astype(int), 0, dem.shape[0] - 1)
    cols = np.clip(cols.astype(int), 0, dem.shape[1] - 1)

    hu = hu.copy()
    hu["elev_m"] = np.round(dem[rows, cols], 1)
    hu["slope_deg"] = np.round(slope_deg[rows, cols], 2)
    hu["flow_acc"] = acc[rows, cols].astype(int)
    hu["twi"] = np.round(twi[rows, cols], 2)
    hu["twi_norm"] = np.round(twi_n[rows, cols], 3)

    # exposicion meteorologica normalizada (z sobre un tope de 6) y compuesta
    zt = np.clip(hu["z_score"].values / 6.0, 0, 1)
    hu["expo_met"] = np.round(zt, 3)
    hu["expo_topo"] = hu["twi_norm"]
    hu["expo_comp"] = np.round(0.5 * zt + 0.5 * hu["twi_norm"].values, 3)

    hu.drop(columns="geometry").to_csv(
        HERE / "humedales_z_gt3_topo.csv", index=False, encoding="utf-8")
    hu.to_crs(4326).to_file(HERE / "humedales_z_gt3_topo.geojson", driver="GeoJSON")

    # --- resumen ---
    q = hu["expo_comp"]
    alto = hu[(hu.expo_comp >= 0.6)]
    resumen = {
        "humedales_z_gt3": int(len(hu)),
        "elev_media_m": round(float(hu.elev_m.mean()), 1),
        "slope_media_deg": round(float(hu.slope_deg.mean()), 2),
        "twi_medio": round(float(hu.twi.mean()), 2),
        "expo_comp_media": round(float(q.mean()), 3),
        "humedales_expo_comp_alta": int(len(alto)),
        "pct_expo_comp_alta": round(len(alto) / len(hu) * 100, 1),
        "top_comunas_expo_comp": (hu.groupby("comuna")["expo_comp"].mean()
                                  .sort_values(ascending=False).head(8)
                                  .round(3).to_dict()),
    }
    (HERE / "resumen_topo.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print("\n-> humedales_z_gt3_topo.csv/.geojson, twi_valpo.tif, resumen_topo.json")


if __name__ == "__main__":
    main()
