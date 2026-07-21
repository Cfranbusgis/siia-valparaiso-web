"""Capa web de los 18 humedales urbanos reconocidos (Ley 21.202), con el
cruce espacial contra el inventario 2013, para el mapa interactivo.

Cruce: por humedal urbano (poligonos disueltos por id_solicitud), se
intersecta contra public/humedales_poly.geojson (inventario 2013, 2.916
poligonos) y se calcula el % del area del humedal urbano cubierta por
poligonos 2013 preexistentes. No se fuerza un umbral binario de "nuevo": se
expone el porcentaje continuo (pct2013) mas una clase de 2 niveles para el
color del mapa (sin_solape / con_solape), y los nombres 2013 relacionados
para que el lector juzgue el caso concreto.

Salida: public/humedales_urbanos.geojson
"""
from __future__ import annotations
from pathlib import Path
import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "public" / "humedales_urbanos.geojson"

def main():
    urb = gpd.read_file(HERE.parent / "data" / "humedales_urbanos_geom.geojson").to_crs(32719)
    inv = gpd.read_file(HERE.parent / "public" / "humedales_poly.geojson").to_crs(32719)

    urb_d = urb.dissolve("id_solicitud", aggfunc={
        "nombre": "first", "comuna": "first",
        "tipo_clasificacion": "first", "confianza_geometria": "first",
    }).reset_index()
    urb_d["area_ha"] = urb_d.geometry.area / 10000

    pct2013, n2013, nom2013 = [], [], []
    for geom, area_ha in zip(urb_d.geometry, urb_d.area_ha):
        inter = inv[inv.intersects(geom)]
        if len(inter):
            solape_ha = inter.geometry.intersection(geom).area.sum() / 10000
            pct2013.append(round(min(solape_ha / area_ha * 100, 100), 1))
            n2013.append(len(inter))
            top = inter.assign(_a=inter.geometry.intersection(geom).area).sort_values("_a", ascending=False)
            nom2013.append("; ".join(dict.fromkeys(top["n"].head(3))))  # sin duplicados, preserva orden
        else:
            pct2013.append(0.0); n2013.append(0); nom2013.append("")

    urb_d["pct2013"] = pct2013
    urb_d["n2013"] = n2013
    urb_d["nom2013"] = nom2013
    urb_d["clase"] = ["con_solape" if p > 0 else "sin_solape" for p in pct2013]

    web = urb_d.to_crs(4326).rename(columns={
        "id_solicitud": "id", "nombre": "n", "comuna": "c",
        "tipo_clasificacion": "tc", "confianza_geometria": "cg",
    })[["id", "n", "c", "tc", "cg", "area_ha", "pct2013", "n2013", "nom2013", "clase", "geometry"]]
    web["area_ha"] = web["area_ha"].round(2)

    OUT.parent.mkdir(exist_ok=True)
    web.to_file(OUT, driver="GeoJSON")
    print(f"-> {OUT} ({len(web)} humedales urbanos)")
    print(web["clase"].value_counts().to_string())

if __name__ == "__main__":
    main()
