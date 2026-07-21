"""Amenaza y susceptibilidad de inundacion aplicada a los 21 humedales urbanos
de Valparaiso (Ley 21.202), reutilizando la MISMA metodologia de
susceptibilidad.py / exposicion_v2.py sobre el inventario base de 2.916
humedales (public/humedales_poly.geojson).

Para los humedales urbanos que se solapan con el inventario 2013, se heredan
pctl_empirico/amenaza_inundacion/susc_inundacion/expo_suelo por promedio
ponderado por area de interseccion de los poligonos base solapados; la clase
de amenaza se reclasifica sobre ese promedio usando los MISMOS quintiles de
amenaza_inundacion de la poblacion completa (nunca se re-quintiliza sobre
n=21). Se expone pct_solape_2013 y una etiqueta de confianza explicita: la
herencia por area ponderada representa bien el humedal cuando el solape es
alto, y debe leerse con cautela cuando es parcial.

Para los sin solape (Canal Waddington #47, Kan Kan #170, Entre Cerros #177,
El Bato #1237 - ver build_humedales_urbanos_web.py), se muestrea
directamente sobre el punto representativo:
  - expo_met: percentil empirico de la celda de anomaly_grid_valpo_v2.csv
    (mismo sjoin de anomalia_v2.py, con respaldo sjoin_nearest);
  - TWI: twi_valpo_30m.tif, normalizacion P2-P98 regional (exposicion_v2.py);
  - concavidad/depresion: concavidad_valpo_30m.tif + depresion_valpo_30m.tif,
    misma normalizacion que concavidad_30m.py;
  - suelo: suelos_ciren_rv_32719.gpkg (sjoin within) con relleno FAO/HWSD2
    (suelo_retencion.py + suelo_fao_fill.py) si no hay serie CIREN;
  - cercania a rio oficial: rios_rv_32719.gpkg, sjoin_nearest (dist_rios.py).

Ademas, para los 21: comuna (ya en el CSV de origen) y estacion DMC/DGAC mas
cercana (dmc_observado_valpo.csv, 33 estaciones), con su acumulado 24h
observado, para poder vincular cada humedal a lo que realmente se registro
en su entorno cercano durante el evento.

Fuente de los insumos intermedios (rasters/gpkg/csv ya calculados sobre el
inventario completo): carpeta de trabajo resuelta via config.WORK_DIR.

Salidas: data/humedales_urbanos_amenaza.csv,
         data/humedales_urbanos_amenaza_resumen.json
"""
from __future__ import annotations
import json
import sqlite3
from math import radians, sin, cos, atan2, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from affine import Affine
from shapely.geometry import box
import warnings; warnings.filterwarnings("ignore")

from config import WORK_DIR

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
UTM = 32719

URB_GEOM = ROOT / "data" / "humedales_urbanos_geom.geojson"
URB_CSV = ROOT / "data" / "humedales_urbanos_valpo.csv"
BASE_POLY = ROOT / "public" / "humedales_poly.geojson"
DMC = WORK_DIR / "dmc_observado_valpo.csv"
GRID_CSV = WORK_DIR / "anomaly_grid_valpo_v2.csv"
GRID_NPZ = WORK_DIR / "clim_valpo.npz"
TWI_TIF = WORK_DIR / "twi_valpo_30m.tif"
CONCAV_TIF = WORK_DIR / "concavidad_valpo_30m.tif"
DEPRES_TIF = WORK_DIR / "depresion_valpo_30m.tif"
SUELO_GPKG = WORK_DIR / "suelos_ciren_rv_32719.gpkg"
CIREN_SERIES = WORK_DIR / "ciren_series_retencion.csv"
RIOS_GPKG = WORK_DIR / "rios_rv_32719.gpkg"
SUSC_CSV = WORK_DIR / "humedales_susceptibilidad.csv"
HWSD_DB = WORK_DIR / "HWSD2.sqlite"
FAO_TIF = ("zip://C:/Users/cfran/Downloads/"
           "Raster - Suelos FAO-20260719T181705Z-1-001.zip!"
           "Raster - Suelos FAO/Suelos_FAO.tif")

TEXT = {"GRUESA": 0.0, "MODERADAMENTE GRUESA": 0.25, "MEDIA": 0.5,
        "MODERADAMENTE FINA": 0.75, "FINA": 1.0}
PERM = {"MUY RAPIDA": 0.0, "RAPIDA": 0.15, "MODERADAMENTE RAPIDA": 0.3, "MODERADA": 0.5,
        "MODERADAMENTE LENTA": 0.7, "LENTA": 0.85, "MUY LENTA": 1.0}
DREN = {"EXCESIVO": 0.0, "BUENO": 0.2, "MODERADO": 0.45, "IMPERFECTO": 0.7,
        "POBRE": 0.9, "MUY POBRE": 1.0}
TEX_RET = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.80, 5: 0.75, 6: 0.65, 7: 0.60, 8: 0.60,
           9: 0.50, 10: 0.40, 11: 0.30, 12: 0.15, 13: 0.0}
DREN_RET = {"E": 0.0, "SE": 0.1, "W": 0.2, "MW": 0.4, "I": 0.7, "P": 0.9, "VP": 1.0}


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def sample_with_fallback(arr, r, c):
    v = arr[r, c]
    if np.isfinite(v):
        return v
    for rad in range(1, 9):
        r0, r1 = max(r - rad, 0), min(r + rad + 1, arr.shape[0])
        c0, c1 = max(c - rad, 0), min(c + rad + 1, arr.shape[1])
        win = arr[r0:r1, c0:c1]
        fin = win[np.isfinite(win)]
        if fin.size:
            return float(fin.mean())
    return np.nan


def confianza(pct_solape, fuente):
    if fuente == "muestreo_directo":
        return "media (muestreo directo, sin promedio espacial)"
    if pct_solape >= 80:
        return "alta"
    if pct_solape >= 30:
        return "media (solape parcial)"
    return "baja (solape < 30%, revisar manualmente)"


def main():
    urb = gpd.read_file(URB_GEOM).to_crs(UTM)
    urb_d = urb.dissolve("id_solicitud", aggfunc={"nombre": "first"}).reset_index()
    urb_d["area_ha"] = urb_d.geometry.area / 10000

    csv = pd.read_csv(URB_CSV, encoding="utf-8")
    csv["id_solicitud"] = csv["id_solicitud"].astype(int)
    urb_d = urb_d.merge(
        csv[["id_solicitud", "comuna", "tipo_final", "superficie_ha", "clasificacion"]],
        on="id_solicitud", how="left")

    inv = gpd.read_file(BASE_POLY).to_crs(UTM)
    susc_full = pd.read_csv(SUSC_CSV, encoding="utf-8")
    qs = np.nanquantile(susc_full["amenaza_inundacion"].to_numpy(), [0.2, 0.4, 0.6, 0.8])
    clases_lbl = np.array(["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"])

    def clasifica(a):
        if a is None or not np.isfinite(a):
            return None
        return clases_lbl[np.digitize([a], qs)[0]]

    rows = []
    for _, u in urb_d.iterrows():
        geom = u.geometry
        inter = inv[inv.intersects(geom)]
        pct_solape, n_solape = 0.0, 0
        p = a = s = su = cl = None
        fuente = "muestreo_directo"
        if len(inter):
            iareas = inter.geometry.intersection(geom).area
            solape_ha = iareas.sum() / 10000
            pct_solape = round(min(solape_ha / u.area_ha * 100, 100), 1) if u.area_ha > 0 else 0.0
            n_solape = len(inter)
            if iareas.sum() > 0:
                w = iareas.values / iareas.sum()
                p = float(np.average(inter["p"].astype(float), weights=w))
                a = float(np.average(inter["a"].astype(float), weights=w))
                s = float(np.average(inter["s"].astype(float), weights=w))
                su = float(np.average(inter["su"].astype(float), weights=w))
                cl = clasifica(a)
                fuente = "heredado_solape"
        rows.append(dict(
            id_solicitud=int(u.id_solicitud), nombre=u.nombre, comuna=u.comuna,
            tipo_final=u.tipo_final, area_ha=round(float(u.area_ha), 2),
            pct_solape_2013=pct_solape, n_poligonos_2013=n_solape,
            pctl_empirico=p, amenaza_inundacion=a, susc_inundacion=s,
            expo_suelo=su, clase_amenaza=cl, fuente=fuente))
    df = pd.DataFrame(rows)

    falta = df["fuente"].eq("muestreo_directo")
    print(f"Con solape (heredado): {(~falta).sum()} | Muestreo directo: {falta.sum()}")

    if falta.any():
        sub = urb_d[urb_d.id_solicitud.isin(df.loc[falta, "id_solicitud"])].reset_index(drop=True)
        pts = sub.geometry.representative_point()

        grid = pd.read_csv(GRID_CSV, encoding="utf-8")
        npz = np.load(GRID_NPZ)
        transform = Affine(*npz["transform"][:6])
        polys = []
        for r, c in zip(grid.row, grid.col):
            x0, y0 = transform * (c, r)
            x1, y1 = transform * (c + 1, r + 1)
            polys.append(box(min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
        g = gpd.GeoDataFrame(grid[["pctl_empirico"]].copy(), geometry=polys, crs=UTM)
        pts_gdf = gpd.GeoDataFrame({"id_solicitud": sub.id_solicitud.values}, geometry=pts, crs=UTM)
        j = gpd.sjoin(pts_gdf, g, how="left", predicate="within")
        j = j[~j.index.duplicated(keep="first")]
        miss = j["pctl_empirico"].isna()
        if miss.any():
            jn = gpd.sjoin_nearest(pts_gdf[miss], g, how="left")
            jn = jn[~jn.index.duplicated(keep="first")]
            j.loc[miss, "pctl_empirico"] = jn["pctl_empirico"].values
        pctl = j["pctl_empirico"].to_numpy()
        expo_met = np.clip((pctl - 50.0) / 50.0, 0, 1)

        with rasterio.open(TWI_TIF) as sr:
            twi = sr.read(1).astype("float64"); twi[twi == sr.nodata] = np.nan
            tr = sr.transform
        finite = twi[np.isfinite(twi)]
        lo, hi = np.nanpercentile(finite, 2), np.nanpercentile(finite, 98)
        twin = np.clip((twi - lo) / (hi - lo), 0, 1)
        inv_tr = ~tr
        cols, rowsidx = inv_tr * (pts.x.values, pts.y.values)
        rowsidx = np.clip(np.asarray(rowsidx, int), 0, twi.shape[0] - 1)
        cols = np.clip(np.asarray(cols, int), 0, twi.shape[1] - 1)
        twi_topo = np.array([sample_with_fallback(twin, r, c) for r, c in zip(rowsidx, cols)])

        with rasterio.open(CONCAV_TIF) as sr:
            concav = sr.read(1).astype("float64"); concav[concav == sr.nodata] = np.nan
            crtr = sr.transform
        with rasterio.open(DEPRES_TIF) as sr:
            dep = sr.read(1).astype("float64"); dep[dep == sr.nodata] = np.nan
        c_ = concav[np.isfinite(concav)]
        cn_full = np.clip((concav - np.nanpercentile(c_, 50)) /
                           (np.nanpercentile(c_, 98) - np.nanpercentile(c_, 50)), 0, 1)
        depn_full = np.clip(dep / (np.nanpercentile(dep[dep > 0], 95) if (dep > 0).any() else 1), 0, 1)
        acc_full = np.nanmax(np.dstack([cn_full, depn_full]), axis=2)
        inv_crtr = ~crtr
        ccols, crows = inv_crtr * (pts.x.values, pts.y.values)
        crows = np.clip(np.asarray(crows, int), 0, concav.shape[0] - 1)
        ccols = np.clip(np.asarray(ccols, int), 0, concav.shape[1] - 1)
        acc_topo = np.array([sample_with_fallback(acc_full, r, c) for r, c in zip(crows, ccols)])

        suelo_poly = gpd.read_file(SUELO_GPKG)
        pts_gdf2 = gpd.GeoDataFrame({"id_solicitud": sub.id_solicitud.values}, geometry=pts, crs=UTM)
        js = gpd.sjoin(pts_gdf2, suelo_poly[["NOMBSERI", "DESCTEXT", "DESCPERM", "DESCDREN", "geometry"]],
                        how="left", predicate="within")
        js = js[~js.index.duplicated(keep="first")]
        ciren_ser = pd.read_csv(CIREN_SERIES, encoding="utf-8")
        smap = ciren_ser.set_index(ciren_ser["serie"].str.upper().str.strip())
        key = js["NOMBSERI"].fillna("").str.upper().str.strip()
        fc = key.map(smap["fc"]); clay = key.map(smap["clay"])
        t = js["DESCTEXT"].map(TEXT); p_ = js["DESCPERM"].map(PERM); d_ = js["DESCDREN"].map(DREN)
        fcn = np.clip((fc - 15) / (40 - 15), 0, 1); clayn = np.clip(clay / 45.0, 0, 1)
        comp = pd.concat([t, p_, d_, fcn, clayn], axis=1)
        expo_suelo = comp.mean(axis=1, skipna=True).to_numpy().copy()
        fuente_suelo = np.where(~np.isnan(expo_suelo), "CIREN", "none")

        falta_suelo = np.isnan(expo_suelo)
        if falta_suelo.any():
            pts_ll = sub.geometry.to_crs(4326).representative_point()
            with rasterio.open(FAO_TIF) as sr:
                smu = np.array([v[0] for v in sr.sample([(p.x, p.y) for p in pts_ll])], dtype="float64")
                smu[smu == sr.nodata] = np.nan
            con = sqlite3.connect(HWSD_DB)
            need = sorted({int(x) for x in smu[falta_suelo] if np.isfinite(x)})
            if need:
                q = ("SELECT HWSD2_SMU_ID,SHARE,TEXTURE_USDA,DRAINAGE,AWC FROM HWSD2_SMU "
                     "WHERE HWSD2_SMU_ID IN (%s)" % ",".join(map(str, need)))
                db = (pd.read_sql(q, con).sort_values("SHARE", ascending=False)
                      .drop_duplicates("HWSD2_SMU_ID").set_index("HWSD2_SMU_ID"))
                for i in np.where(falta_suelo)[0]:
                    if np.isfinite(smu[i]) and int(smu[i]) in db.index:
                        r = db.loc[int(smu[i])]
                        tt = TEX_RET.get(int(r.TEXTURE_USDA)) if pd.notna(r.TEXTURE_USDA) else np.nan
                        dd = DREN_RET.get(str(r.DRAINAGE)) if pd.notna(r.DRAINAGE) else np.nan
                        aa = np.clip(r.AWC / 170.0, 0, 1) if pd.notna(r.AWC) and r.AWC >= 0 else np.nan
                        vals = [v for v in (tt, dd, aa) if pd.notna(v)]
                        if vals:
                            expo_suelo[i] = float(np.mean(vals)); fuente_suelo[i] = "FAO"

        rios = gpd.read_file(RIOS_GPKG).to_crs(UTM)
        pts_gdf3 = gpd.GeoDataFrame({"id_solicitud": sub.id_solicitud.values}, geometry=pts, crs=UTM)
        dn = gpd.sjoin_nearest(pts_gdf3, rios[["geometry"]], how="left", distance_col="d")
        dn = dn[~dn.index.duplicated(keep="first")]
        dist_rio = dn["d"].to_numpy()
        prox_rio = np.clip(1 - (dist_rio - 60) / (1500 - 60), 0, 1)

        susc = np.nanmean(np.vstack([twi_topo, acc_topo, expo_suelo, prox_rio]), axis=0)
        amenaza = expo_met * susc
        cl_new = [clasifica(x) for x in amenaza]

        df["twi_norm"] = np.nan; df["acc_topo"] = np.nan; df["prox_rio"] = np.nan
        df["fuente_suelo"] = None
        for k in range(len(sub)):
            id_ = int(sub.loc[k, "id_solicitud"])
            m = df["id_solicitud"] == id_
            df.loc[m, "pctl_empirico"] = round(float(pctl[k]), 1)
            df.loc[m, "amenaza_inundacion"] = round(float(amenaza[k]), 3)
            df.loc[m, "susc_inundacion"] = round(float(susc[k]), 3)
            df.loc[m, "expo_suelo"] = round(float(expo_suelo[k]), 3) if np.isfinite(expo_suelo[k]) else None
            df.loc[m, "clase_amenaza"] = cl_new[k]
            df.loc[m, "twi_norm"] = round(float(twi_topo[k]), 3)
            df.loc[m, "acc_topo"] = round(float(acc_topo[k]), 3)
            df.loc[m, "prox_rio"] = round(float(prox_rio[k]), 3)
            df.loc[m, "fuente_suelo"] = fuente_suelo[k]

    df["confianza"] = [confianza(p, f) for p, f in zip(df["pct_solape_2013"], df["fuente"])]

    dmc = pd.read_csv(DMC, encoding="utf-8")
    # dmc_observado_valpo.csv trae "estacion" con doble codificacion UTF-8
    # (ej. "AgrÃ­cola" en vez de "Agrícola") - bug de origen en dmc_extract.py,
    # no de este script; se repara aqui solo para esta salida.
    def _fix_mojibake(s):
        try:
            return s.encode("latin1").decode("utf-8")
        except (UnicodeDecodeError, UnicodeEncodeError):
            return s
    dmc["estacion"] = dmc["estacion"].map(_fix_mojibake)
    urb_ll = urb_d.to_crs(4326).set_index("id_solicitud").geometry.apply(lambda g: g.representative_point())
    nearest_est, nearest_dist, nearest_mm = [], [], []
    for id_ in df.id_solicitud:
        pt = urb_ll.loc[id_]
        d = dmc.apply(lambda r: haversine_km(pt.y, pt.x, r.lat, r.lon), axis=1)
        i = d.idxmin()
        nearest_est.append(dmc.loc[i, "estacion"])
        nearest_dist.append(round(float(d.loc[i]), 1))
        nearest_mm.append(dmc.loc[i, "agua24h_mm"])
    df["estacion_dmc_cercana"] = nearest_est
    df["dist_estacion_km"] = nearest_dist
    df["estacion_agua24h_mm"] = nearest_mm

    df = df.sort_values("amenaza_inundacion", ascending=False).reset_index(drop=True)
    OUT = ROOT / "data" / "humedales_urbanos_amenaza.csv"
    df.to_csv(OUT, index=False, encoding="utf-8")

    resumen = {
        "n_total": len(df),
        "con_solape_2013": int((~falta).sum()),
        "muestreo_directo": int(falta.sum()),
        "clases_amenaza": df["clase_amenaza"].value_counts(dropna=False).to_dict(),
        "confianza": df["confianza"].value_counts(dropna=False).to_dict(),
        "comunas": df["comuna"].value_counts().to_dict(),
        "amenaza_media": round(float(df["amenaza_inundacion"].mean()), 3),
        "quintiles_poblacion_completa_2916": [round(float(x), 3) for x in qs],
    }
    (ROOT / "data" / "humedales_urbanos_amenaza_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")

    print(df[["nombre", "comuna", "tipo_final", "pct_solape_2013", "fuente", "clase_amenaza",
              "amenaza_inundacion", "confianza", "estacion_dmc_cercana", "estacion_agua24h_mm"]]
          .to_string(index=False))
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    print(f"\n-> {OUT}")


if __name__ == "__main__":
    main()
