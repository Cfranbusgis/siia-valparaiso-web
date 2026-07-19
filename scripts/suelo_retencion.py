"""Índice de retención hídrica edáfica por humedal, uniendo:
  - CIREN KMZ (por polígono): textura, permeabilidad, drenaje, serie (NOMBSERI)
  - Estudio Agrológico CIREN V Región (PDF, por serie): capacidad de campo
    (humedad retenida 1/3 atm), % de arcilla (<0,002 mm), agua aprovechable.
La densidad aparente NO está poblada en CIREN; se sustituye por la curva de
retención real (capacidad de campo + arcilla), físicamente más directa.

expo_suelo (0..1, 1 = suelo retentivo/agua se acumula) = media de los
componentes normalizados disponibles. Complementa el TWI y la concavidad.

Salidas: ciren_series_retencion.csv, humedales_suelo.csv (reemplaza al previo)
"""
from __future__ import annotations
import re
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
import pypdf, warnings
warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
PDF = Path(r"C:\Users\cfran\Desktop\Suelos\Ciren kmz\CIREN V Región .pdf")
SUELO = HERE / "suelos_ciren_rv_32719.gpkg"
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"

TEXT = {"GRUESA":0.0,"MODERADAMENTE GRUESA":0.25,"MEDIA":0.5,
        "MODERADAMENTE FINA":0.75,"FINA":1.0}
PERM = {"MUY RAPIDA":0.0,"RAPIDA":0.15,"MODERADAMENTE RAPIDA":0.3,"MODERADA":0.5,
        "MODERADAMENTE LENTA":0.7,"LENTA":0.85,"MUY LENTA":1.0}
DREN = {"EXCESIVO":0.0,"BUENO":0.2,"MODERADO":0.45,"IMPERFECTO":0.7,
        "POBRE":0.9,"MUY POBRE":1.0}


def parse_pdf():
    r = pypdf.PdfReader(str(PDF))
    def first(line, after=None):
        s = line.split(after)[-1] if after and after in line else line
        m = re.findall(r"\d+\.?\d*", s)
        return float(m[0]) if m else None
    ser, cur = {}, None
    for pg in r.pages:
        for ln in (pg.extract_text() or "").splitlines():
            ms = re.search(r"SERIE\s*:\s*([A-ZÑÁÉÍÓÚ ]+?)\s*$", ln.strip())
            if ms:
                cur = ms.group(1).strip(); ser.setdefault(cur, {})
            if not cur: continue
            if "1/3 atm" in ln: ser[cur]["fc"] = first(ln, "%")
            if "15 atm" in ln: ser[cur]["pwp"] = first(ln, "%")
            if "APROVECHABLE" in ln: ser[cur]["aw"] = first(ln, "%")
            if re.search(r"<\s*0[.,]002", ln): ser[cur]["clay"] = first(ln, "002")
    df = pd.DataFrame(ser).T.reset_index().rename(columns={"index":"serie"})
    df.to_csv(HERE / "ciren_series_retencion.csv", index=False, encoding="utf-8")
    return df


def main():
    ser = parse_pdf()
    print(f"series del PDF: {len(ser)} (con fc: {ser['fc'].notna().sum()}, "
          f"clay: {ser['clay'].notna().sum()})")

    suelo = gpd.read_file(SUELO)
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True).to_crs(32719)
    pt = hu.copy(); pt["geometry"] = hu.representative_point()
    j = gpd.sjoin(pt, suelo[["NOMBSERI","DESCTEXT","DESCPERM","DESCDREN","DESCINUN","geometry"]],
                  how="left", predicate="within")
    j = j[~j.index.duplicated(keep="first")].reset_index(drop=True)

    # match serie (NOMBSERI) -> fc/clay del PDF
    key = j["NOMBSERI"].fillna("").str.upper().str.strip()
    smap = ser.set_index(ser["serie"].str.upper().str.strip())
    fc = key.map(smap["fc"]); clay = key.map(smap["clay"])
    matched = fc.notna().sum()
    print(f"humedales con serie emparejada al PDF: {matched} ({100*matched/len(j):.0f}%)")

    # normalizaciones (todas: alto = retiene)
    t = j["DESCTEXT"].map(TEXT); p = j["DESCPERM"].map(PERM); d = j["DESCDREN"].map(DREN)
    fcn = np.clip((fc - 15) / (40 - 15), 0, 1)          # capacidad de campo ~15-40%
    clayn = np.clip(clay / 45.0, 0, 1)                   # arcilla 0-45%
    comp = pd.concat([t, p, d, fcn, clayn], axis=1)
    comp.columns = ["textura","perm","drenaje","cap_campo","arcilla"]
    expo = comp.mean(axis=1, skipna=True)
    fuente = np.where(expo.notna(), "CIREN", "none")

    out = pd.DataFrame({
        "nom_humed": hu["nom_humed"].values, "comuna": hu["comuna"].values,
        "serie_suelo": j["NOMBSERI"].values, "textura": j["DESCTEXT"].values,
        "permeabilidad": j["DESCPERM"].values, "drenaje": j["DESCDREN"].values,
        "cap_campo_pct": fc.round(1).values, "arcilla_pct": clay.round(1).values,
        "inundacion": j["DESCINUN"].values,
        "expo_suelo": expo.round(3).values, "fuente_suelo": fuente,
    })
    out.to_csv(HERE / "humedales_suelo.csv", index=False, encoding="utf-8")
    print(f"expo_suelo disponible: {expo.notna().sum()} ({100*expo.notna().mean():.0f}%); "
          f"media {expo.mean():.2f}")
    # validación: capacidad de campo vs textura categórica
    v = comp.dropna(subset=["cap_campo","textura"])
    if len(v) > 5:
        print(f"corr(cap_campo, textura categórica): {v.cap_campo.corr(v.textura):+.2f} "
              "(esperado +, ambas miden retención)")
    print("-> ciren_series_retencion.csv, humedales_suelo.csv")

if __name__ == "__main__":
    main()
