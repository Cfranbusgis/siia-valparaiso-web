"""Relleno FAO de la retención edáfica donde falta CIREN, desde HWSD2 (FAO/IIASA).

El raster HWSD2 (Suelos_FAO.tif) trae códigos SMU; la base HWSD2.sqlite los
enlaza a las propiedades del suelo dominante (mayor SHARE): textura USDA,
drenaje, capacidad de agua aprovechable (AWC) y densidad aparente. Se construye
una retención 0..1 homogénea con la de CIREN (1 = retiene) y se rellenan los
humedales sin dato CIREN. Fuente etiquetada CIREN / FAO / none.

Entradas: humedales_suelo.csv (CIREN), HWSD2.sqlite, Suelos_FAO.tif (zip).
Salida:   humedales_suelo.csv (actualizado, con columna densidad_aparente FAO).
"""
from __future__ import annotations
import sqlite3
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd, rasterio
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
DB = HERE / "HWSD2.sqlite"
ZIP = "C:/Users/cfran/Downloads/Raster - Suelos FAO-20260719T181705Z-1-001.zip"
TIF = f"zip://{ZIP}!Raster - Suelos FAO/Suelos_FAO.tif"
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"

TEX_RET = {1:1.0,2:0.95,3:0.90,4:0.80,5:0.75,6:0.65,7:0.60,8:0.60,
           9:0.50,10:0.40,11:0.30,12:0.15,13:0.0}
DREN_RET = {"E":0.0,"SE":0.1,"W":0.2,"MW":0.4,"I":0.7,"P":0.9,"VP":1.0}

def main():
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    rp = hu.to_crs(4326).representative_point()
    sue = pd.read_csv(HERE / "humedales_suelo.csv", encoding="utf-8")
    assert len(sue) == len(hu)
    falta = sue["expo_suelo"].isna().to_numpy()
    print(f"humedales sin suelo CIREN: {falta.sum()} de {len(sue)}")

    # muestrear SMU del raster HWSD2 en los humedales sin CIREN
    with rasterio.open(TIF) as s:
        pts = [(p.x, p.y) for p in rp]
        smu = np.array([v[0] for v in s.sample(pts)], dtype="float64")
        smu[smu == s.nodata] = np.nan

    # lookup: SMU -> dominante (mayor SHARE) -> propiedades
    con = sqlite3.connect(DB)
    need = sorted({int(x) for x in smu[falta] if np.isfinite(x)})
    q = ("SELECT HWSD2_SMU_ID,SHARE,WRB2,TEXTURE_USDA,DRAINAGE,AWC,BULK_DENSITY "
         "FROM HWSD2_SMU WHERE HWSD2_SMU_ID IN (%s)" % ",".join(map(str, need)))
    db = pd.read_sql(q, con)
    db = db.sort_values("SHARE", ascending=False).drop_duplicates("HWSD2_SMU_ID").set_index("HWSD2_SMU_ID")

    def fao_ret(sid):
        if sid not in db.index: return (np.nan, np.nan, np.nan, np.nan)
        r = db.loc[sid]
        t = TEX_RET.get(int(r.TEXTURE_USDA)) if pd.notna(r.TEXTURE_USDA) else np.nan
        d = DREN_RET.get(str(r.DRAINAGE)) if pd.notna(r.DRAINAGE) else np.nan
        a = np.clip(r.AWC / 170.0, 0, 1) if pd.notna(r.AWC) and r.AWC >= 0 else np.nan
        vals = [v for v in (t, d, a) if pd.notna(v)]
        ret = float(np.mean(vals)) if vals else np.nan
        bd = r.BULK_DENSITY if pd.notna(r.BULK_DENSITY) and r.BULK_DENSITY > 0 else np.nan
        return ret, str(r.WRB2), bd, (int(r.TEXTURE_USDA) if pd.notna(r.TEXTURE_USDA) else np.nan)

    ret = np.full(len(sue), np.nan); wrb = np.array([None]*len(sue), dtype=object)
    bd = np.full(len(sue), np.nan)
    for i in np.where(falta)[0]:
        if np.isfinite(smu[i]):
            ret[i], wrb[i], bd[i], _ = fao_ret(int(smu[i]))

    sue["expo_suelo"] = sue["expo_suelo"].where(~falta, other=np.round(ret, 3))
    sue["grupo_wrb"] = np.where(sue["fuente_suelo"].eq("CIREN"), None, wrb)
    sue["densidad_aparente_fao"] = np.round(bd, 2)
    sue["fuente_suelo"] = np.where(sue["expo_suelo"].notna(),
                                   np.where(falta, "FAO", "CIREN"), "none")
    sue.to_csv(HERE / "humedales_suelo.csv", index=False, encoding="utf-8")

    vc = pd.Series(sue["fuente_suelo"]).value_counts()
    print("fuente de suelo:", vc.to_dict())
    print(f"cobertura total de retención edáfica: {sue['expo_suelo'].notna().mean()*100:.0f}%")
    print("grupos WRB rellenados (FAO):",
          pd.Series(wrb[falta]).dropna().value_counts().head(8).to_dict())
    print("-> humedales_suelo.csv (con relleno FAO)")

if __name__ == "__main__":
    main()
