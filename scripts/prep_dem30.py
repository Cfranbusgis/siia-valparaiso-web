"""Preparacion del DEM 30 m (ALOS AW3D30 DSM, export GEE) para el SIIA.

Respuesta al hallazgo de auditoria externa: con humedales pequenos, el DEM de
250 m es grueso; se incorpora AW3D30 (~30 m). Alcance de este paso (acotado):
  1. Verificar CRS del export GEE  -> EPSG:4326, res 0.000269 grados (~30 m).
  2. Mosaicar SOLO las teselas que intersectan el AOI, acotado al bbox.
  3. Reproyectar a EPSG:32719 (UTM 19S) a 30 m exactos, remuestreo bilineal.
  4. Enmascarar con el limite regional RV.shp (nodata -9999 fuera).

NO se recalcula aqui la cadena topografica (pendiente/flujo/TWI); eso es un
paso posterior explicito.

Salida: MOD_EToPM-HS/03_inputs/DEM/DEM_AW3D30_30m_UTM19S_RV.tif
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import geopandas as gpd
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.merge import merge
from rasterio.warp import Resampling, calculate_default_transform, reproject

import os
from config import AOI_SHP as AOI, DEM_TIF as DEM250, MODEL_DIR
ZIP = os.environ.get("SIIA_DEM30_ZIP",
                     "C:/Users/cfran/Downloads/GEE_exports-20260719T051716Z-1-001.zip")
OUT = MODEL_DIR / "03_inputs" / "DEM" / "DEM_AW3D30_30m_UTM19S_RV.tif"
NODATA = -9999.0
RES = 30.0
BUF = 0.03            # grados de holgura alrededor del bbox del AOI


def main():
    if not Path(ZIP).exists():
        print(f"aviso: export GEE no disponible ({ZIP}); paso omitido. "
              "Define SIIA_DEM30_ZIP para habilitarlo.")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    aoi = gpd.read_file(AOI)
    aoi_ll = aoi.to_crs(4326)
    ab = aoi_ll.total_bounds
    bbox = (ab[0] - BUF, ab[1] - BUF, ab[2] + BUF, ab[3] + BUF)

    names = [i.filename for i in zipfile.ZipFile(ZIP).infolist()
             if i.filename.endswith(".tif")]
    srcs = []
    for n in names:
        s = rasterio.open(f"zip://{ZIP}!{n}")
        b = s.bounds
        if b.right < bbox[0] or b.left > bbox[2] or b.top < bbox[1] or b.bottom > bbox[3]:
            s.close()
            continue
        assert s.crs.to_epsg() == 4326, f"CRS inesperado: {s.crs}"
        srcs.append(s)
    print(f"teselas usadas: {len(srcs)}")

    mosaic, mtrans = merge(srcs, bounds=bbox, nodata=NODATA, dtype="float32")
    for s in srcs:
        s.close()
    mosaic = mosaic[0]
    print(f"mosaico 4326: {mosaic.shape}, "
          f"min/max={np.nanmin(mosaic[mosaic > NODATA]):.0f}/"
          f"{np.nanmax(mosaic):.0f} m")

    # --- reproyeccion a UTM 19S, 30 m ---
    dst_crs = "EPSG:32719"
    tr, w, h = calculate_default_transform(
        "EPSG:4326", dst_crs, mosaic.shape[1], mosaic.shape[0],
        left=bbox[0], bottom=bbox[1], right=bbox[2], top=bbox[3],
        resolution=RES)
    dst = np.full((h, w), NODATA, dtype="float32")
    reproject(mosaic, dst, src_transform=mtrans, src_crs="EPSG:4326",
              dst_transform=tr, dst_crs=dst_crs,
              src_nodata=NODATA, dst_nodata=NODATA,
              resampling=Resampling.bilinear)
    print(f"reproyectado 32719 @ {RES:.0f} m: {dst.shape}")

    # --- mascara al limite regional ---
    prof = dict(driver="GTiff", height=h, width=w, count=1, dtype="float32",
                crs=dst_crs, transform=tr, nodata=NODATA,
                compress="lzw", tiled=True)
    tmp = OUT.with_suffix(".tmp.tif")
    with rasterio.open(tmp, "w", **prof) as d:
        d.write(dst, 1)
    with rasterio.open(tmp) as s:
        geoms = [g for g in aoi.to_crs(dst_crs).geometry]
        clipped, ctrans = rio_mask(s, geoms, crop=True, nodata=NODATA)
    tmp.unlink()
    clipped = clipped[0]

    prof.update(height=clipped.shape[0], width=clipped.shape[1], transform=ctrans)
    with rasterio.open(OUT, "w", **prof) as d:
        d.write(clipped, 1)

    valid = clipped[clipped > NODATA]
    print(f"\n-> {OUT.name}")
    print(f"   grilla: {clipped.shape[1]} x {clipped.shape[0]} px @ {RES:.0f} m")
    print(f"   celdas validas: {valid.size:,} "
          f"({valid.size * RES * RES / 1e6:,.0f} km2)")
    print(f"   elevacion min/media/max: {valid.min():.0f} / "
          f"{valid.mean():.0f} / {valid.max():.0f} m")

    # --- sanidad rapida contra el DEM 250 m vigente ---
    with rasterio.open(DEM250) as s250:
        d250 = s250.read(1).astype("float64")
        nod = s250.nodata
        d250[(d250 == nod) | (d250 < -100)] = np.nan
        print(f"   DEM 250 m (referencia): media {np.nanmean(d250):.0f} m | "
              f"max {np.nanmax(d250):.0f} m")


if __name__ == "__main__":
    main()
