"""Cuencas BNA que intersectan la V Región, simplificadas, como GeoJSON para el
mapa interactivo (modo 'Cuenca', representación poligonal).

Entrada: shapefile Cuencas_BNA (DGA/BNA). Salida: public/cuencas.geojson
Requiere definir la ruta del shapefile por env CUENCAS_SHP o editar SRC.
"""
from __future__ import annotations
import os, glob
from pathlib import Path
import geopandas as gpd
import warnings; warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[1]
import config
SRC = os.environ.get("CUENCAS_SHP", "")
AOI = config.AOI_SHP
OUT = REPO / "public" / "cuencas.geojson"

def main():
    src = SRC or (glob.glob(str(Path.home() / "Downloads" / "**" / "Cuencas_BNA*.shp"),
                            recursive=True) or [None])[0]
    if not src or not Path(src).exists():
        print("aviso: shapefile de cuencas no encontrado; define CUENCAS_SHP.")
        return
    cu = gpd.read_file(src)
    aoi = gpd.read_file(AOI).to_crs(cu.crs).union_all()
    cu = cu[cu.intersects(aoi)].to_crs(4326)
    cu["geometry"] = cu.geometry.simplify(0.004, preserve_topology=True)
    cu[["NOM_CUEN", "geometry"]].to_file(OUT, driver="GeoJSON")
    print(f"-> {OUT} ({len(cu)} cuencas)")

if __name__ == "__main__":
    main()
