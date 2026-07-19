"""Parsea el KMZ de suelos CIREN (Estudio Agrológico) V Región y lo deja en el
CRS del proyecto (EPSG:32719), con los atributos edáficos relevantes.

Los atributos vienen embebidos como tabla HTML en el campo `description` del KML.
Se extraen: serie (SIMBSERI/NOMBSERI), variante (DESCVARI), drenaje (DESCDREN),
textura (DESCTEXT), permeabilidad (DESCPERM), inundación (DESCINUN), capacidad de
uso (DESCCAUS), área (AREA_HA). '99' / 'NO CORRESPONDE' = sin dato (p. ej. cajas
de río, afloramientos), que luego se rellenan con órdenes FAO.

Salida: suelos_ciren_rv_32719.gpkg
"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
KMZ = Path(r"C:\Users\cfran\Desktop\Suelos\Ciren kmz\Suelos_05_Region.kmz")
UTM = 32719
FIELDS = ["SIMBSERI", "NOMBSERI", "DESCVARI", "DESCDREN", "DESCTEXT",
          "DESCPERM", "DESCINUN", "DESCCAUS", "AREA_HA"]

_pair = re.compile(r"<td>([A-Z_]+)</td>\s*<td>(.*?)</td>", re.S)


def parse_desc(html: str) -> dict:
    d = {}
    for k, v in _pair.findall(html or ""):
        if k in FIELDS and k not in d:
            d[k] = re.sub(r"<[^>]+>", "", v).strip()
    return d


def main():
    kml = HERE / "_ciren_doc.kml"
    if not kml.exists():
        with zipfile.ZipFile(KMZ) as z:
            data = z.read("doc.kml")
        kml.write_bytes(data)
    print("leyendo KML...", flush=True)
    g = gpd.read_file(kml)
    print(f"polígonos: {len(g)}, CRS {g.crs}", flush=True)

    rows = [parse_desc(x) for x in g["description"]]
    att = pd.DataFrame(rows)
    for c in FIELDS:
        if c not in att:
            att[c] = None
    out = gpd.GeoDataFrame(att[FIELDS].copy(), geometry=g.geometry.values, crs=g.crs)
    out["AREA_HA"] = pd.to_numeric(out["AREA_HA"].str.replace(",", ".", regex=False),
                                   errors="coerce")
    # normaliza "sin dato"
    NA = {"NO CORRESPONDE", "N.C.", "", "99", "SIN INFORMACION", "SIN INFORMACIÓN"}
    for c in ["DESCDREN", "DESCTEXT", "DESCPERM", "DESCINUN", "DESCCAUS"]:
        out[c] = out[c].where(~out[c].isin(NA), other=None)
    out["con_suelo"] = out["NOMBSERI"].fillna("").str.upper().ne("NO SUELOS")

    out = out.to_crs(UTM)
    out.to_file(HERE / "suelos_ciren_rv_32719.gpkg", driver="GPKG")

    print("\n=== drenaje (DESCDREN) ===")
    print(out["DESCDREN"].value_counts(dropna=False).to_string())
    print("\n=== permeabilidad (DESCPERM) ===")
    print(out["DESCPERM"].value_counts(dropna=False).to_string())
    print("\n=== inundación (DESCINUN) ===")
    print(out["DESCINUN"].value_counts(dropna=False).to_string())
    print(f"\npolígonos con suelo: {out.con_suelo.sum()}/{len(out)} "
          f"({100*out.con_suelo.mean():.0f}%)")
    print("-> suelos_ciren_rv_32719.gpkg")


if __name__ == "__main__":
    main()
