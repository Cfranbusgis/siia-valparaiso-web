"""Cadena topografica a 30 m sobre el DEM ALOS AW3D30 (DSM) de la V Region.

Replica el metodo de topo_analysis.py (250 m) sobre el nuevo DEM:
  - pendiente (grados, gradiente central),
  - acumulacion de flujo D8 (pysheds: fill_pits -> fill_depressions ->
    resolve_flats -> flowdir -> accumulation),
  - TWI = ln(a / tan(beta)), a = (acc+1)*px.

Nota metodologica: AW3D30 es un DSM (superficie, incluye dosel/edificaciones);
el efecto sobre TWI en fondos de valle es menor pero se declara en el informe.

Salidas: twi_valpo_30m.tif, slope_valpo_30m.tif, resumen_topo_30m.json
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
if not hasattr(np, "in1d"):          # pysheds usa np.in1d (removido en numpy 2)
    np.in1d = np.isin
import rasterio
from pysheds.grid import Grid

from config import WORK_DIR as HERE, MODEL_DIR
DEM = MODEL_DIR / "03_inputs" / "DEM" / "DEM_AW3D30_30m_UTM19S_RV.tif"


def main():
    if not DEM.exists():
        print(f"aviso: {DEM.name} no existe (ejecuta prep_dem30.py); "
              "paso omitido, exposicion_v2 usara el TWI de 250 m.")
        return
    t0 = time.time()
    with rasterio.open(DEM) as s:
        dem = s.read(1).astype("float64")
        transform = s.transform
        crs = s.crs
        nodata = s.nodata
        px = abs(transform.a)
    dem[dem == nodata] = np.nan
    dem[dem < -100] = np.nan
    print(f"DEM {dem.shape}, px={px:.0f} m, "
          f"validas={np.isfinite(dem).sum():,} ({time.time()-t0:.0f}s)", flush=True)

    gy, gx = np.gradient(np.nan_to_num(dem, nan=np.nanmin(dem)), px, px)
    slope_deg = np.degrees(np.arctan(np.hypot(gx, gy))).astype("float32")
    del gx, gy
    print(f"pendiente lista ({time.time()-t0:.0f}s)", flush=True)

    grid = Grid.from_raster(str(DEM))
    dem_g = grid.read_raster(str(DEM))
    pit_filled = grid.fill_pits(dem_g); del dem_g
    print(f"fill_pits ({time.time()-t0:.0f}s)", flush=True)
    flooded = grid.fill_depressions(pit_filled); del pit_filled
    print(f"fill_depressions ({time.time()-t0:.0f}s)", flush=True)
    inflated = grid.resolve_flats(flooded); del flooded
    print(f"resolve_flats ({time.time()-t0:.0f}s)", flush=True)
    fdir = grid.flowdir(inflated); del inflated
    print(f"flowdir ({time.time()-t0:.0f}s)", flush=True)
    acc = np.asarray(grid.accumulation(fdir), dtype="float64"); del fdir
    print(f"accumulation ({time.time()-t0:.0f}s)", flush=True)

    tanb = np.tan(np.radians(np.clip(slope_deg.astype("float64"), 0.1, None)))
    twi = np.log((acc + 1.0) * px / tanb).astype("float32")
    del acc, tanb
    twi[~np.isfinite(dem)] = np.nan

    prof = dict(driver="GTiff", height=twi.shape[0], width=twi.shape[1],
                count=1, dtype="float32", crs=crs, transform=transform,
                nodata=-9999, compress="lzw", tiled=True)
    with rasterio.open(HERE / "twi_valpo_30m.tif", "w", **prof) as d:
        d.write(np.where(np.isfinite(twi), twi, -9999).astype("float32"), 1)
    with rasterio.open(HERE / "slope_valpo_30m.tif", "w", **prof) as d:
        s_out = np.where(np.isfinite(dem), slope_deg, -9999).astype("float32")
        d.write(s_out, 1)

    fin = twi[np.isfinite(twi)]
    resumen = {
        "dem": DEM.name, "px_m": px, "celdas_validas": int(np.isfinite(dem).sum()),
        "slope_media_deg": round(float(np.nanmean(np.where(np.isfinite(dem),
                                                           slope_deg, np.nan))), 2),
        "twi_min_p2_p50_p98_max": [round(float(v), 2) for v in
                                   (fin.min(), np.percentile(fin, 2),
                                    np.percentile(fin, 50),
                                    np.percentile(fin, 98), fin.max())],
        "segundos": round(time.time() - t0, 1),
    }
    (HERE / "resumen_topo_30m.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print("-> twi_valpo_30m.tif, slope_valpo_30m.tif, resumen_topo_30m.json")


if __name__ == "__main__":
    main()
