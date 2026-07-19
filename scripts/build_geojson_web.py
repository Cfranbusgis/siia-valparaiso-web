"""GeoJSON compacto de los 2.916 humedales para el mapa interactivo del sitio.

Puntos (punto representativo, WGS84) con los atributos que colorea/consulta el
mapa: nombre, comuna, cuenca, percentil empírico, amenaza de inundación y su
clase, susceptibilidad, retención de suelo y acumulado corregido.

Salida: <repo>/public/humedales.geojson
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd, geopandas as gpd
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"
OUT = Path(r"C:\Users\cfran\Desktop\siia-valparaiso-web\public\humedales.geojson")

def main():
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    sus = pd.read_csv(HERE / "humedales_susceptibilidad.csv", encoding="utf-8")
    ano = pd.read_csv(HERE / "humedales_valpo_anomalia_v2.csv", encoding="utf-8")
    assert len(hu) == len(sus) == len(ano)

    pt = hu.to_crs(4326).representative_point()
    feats = []
    for i in range(len(hu)):
        x, y = round(float(pt.iloc[i].x), 5), round(float(pt.iloc[i].y), 5)
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [x, y]},
            "properties": {
                "n": str(hu["nom_humed"].iloc[i]),
                "c": str(hu["comuna"].iloc[i]),
                "cu": (None if pd.isna(sus["cuenca"].iloc[i]) else str(sus["cuenca"].iloc[i])),
                "p": round(float(ano["pctl_empirico"].iloc[i]), 1),
                "a": round(float(sus["amenaza_inundacion"].iloc[i]), 3),
                "cl": str(sus["clase_amenaza"].iloc[i]),
                "s": round(float(sus["susc_inundacion"].iloc[i]), 3),
                "su": (None if pd.isna(sus["expo_suelo"].iloc[i])
                       else round(float(sus["expo_suelo"].iloc[i]), 3)),
                "mm": round(float(ano["recent_v2_mm"].iloc[i]), 1),
            },
        })
    fc = {"type": "FeatureCollection", "features": feats}
    OUT.write_text(json.dumps(fc, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"-> {OUT} ({len(feats)} humedales, {kb:.0f} KB)")

if __name__ == "__main__":
    main()
