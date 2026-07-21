"""Capa web de los humedales urbanos reconocidos (Ley 21.202) con
incluir_capa=True (18 de 21 - ver data/humedales_urbanos_valpo.csv; excluye
los 2 artificiales y el mixto, que no tienen contraparte directa y
comparable en la capa "Humedales"), con el cruce espacial contra el
inventario 2013 y los mismos campos de amenaza/susceptibilidad/percentil/
suelo (p/cl/s/su) que la capa base, para que el mapa interactivo pueda
colorear los humedales urbanos con las mismas variables (ver
humedales-urbanos-amenaza).

Cruce con 2013: por humedal urbano (poligonos disueltos por id_solicitud),
se intersecta contra public/humedales_poly.geojson (inventario 2013, 2.916
poligonos) y se calcula el % del area del humedal urbano cubierta por
poligonos 2013 preexistentes. No se fuerza un umbral binario de "nuevo": se
expone el porcentaje continuo (pct2013) mas una clase de 2 niveles (clase:
sin_solape / con_solape, usada solo para el estilo del borde, no del
relleno) y los nombres 2013 relacionados para que el lector juzgue el caso
concreto.

p/cl/s/su/cf: tomados de data/humedales_urbanos_amenaza.csv (herencia
ponderada por area si hay solape, muestreo directo de la misma metodologia
si no; cf = nivel de confianza de ese valor, ver humedales-urbanos-amenaza).

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
    incluir = pd.read_csv(HERE.parent / "data" / "humedales_urbanos_valpo.csv", encoding="utf-8")
    incluir["id_solicitud"] = incluir["id_solicitud"].astype(int)
    ids_incluidos = set(incluir.loc[incluir["incluir_capa"] == True, "id_solicitud"])  # noqa: E712

    urb_d = urb.dissolve("id_solicitud", aggfunc={
        "nombre": "first", "comuna": "first",
        "tipo_clasificacion": "first", "confianza_geometria": "first",
    }).reset_index()
    urb_d = urb_d[urb_d["id_solicitud"].isin(ids_incluidos)].reset_index(drop=True)
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

    amz = pd.read_csv(HERE.parent / "data" / "humedales_urbanos_amenaza.csv", encoding="utf-8")
    amz["id_solicitud"] = amz["id_solicitud"].astype(int)
    urb_d = urb_d.merge(
        amz[["id_solicitud", "pctl_empirico", "clase_amenaza", "susc_inundacion",
             "expo_suelo", "confianza"]],
        on="id_solicitud", how="left")

    web = urb_d.to_crs(4326).rename(columns={
        "id_solicitud": "id", "nombre": "n", "comuna": "c",
        "tipo_clasificacion": "tc", "confianza_geometria": "cg",
        "pctl_empirico": "p", "clase_amenaza": "cl", "susc_inundacion": "s",
        "expo_suelo": "su", "confianza": "cf",
    })[["id", "n", "c", "tc", "cg", "area_ha", "pct2013", "n2013", "nom2013", "clase",
        "p", "cl", "s", "su", "cf", "geometry"]]
    web["area_ha"] = web["area_ha"].round(2)

    OUT.parent.mkdir(exist_ok=True)
    web.to_file(OUT, driver="GeoJSON")
    print(f"-> {OUT} ({len(web)} humedales urbanos)")
    print(web["clase"].value_counts().to_string())
    print(web["cl"].value_counts(dropna=False).to_string())

if __name__ == "__main__":
    main()
