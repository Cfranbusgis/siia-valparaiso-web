"""FASE 5 - Recalibracion del indice de exposicion compuesta (v2).

La auditoria dejo dos objeciones sobre el indice v1 (0.5*z/6 + 0.5*TWI_norm,
umbral alta >= 0.6, sobre los 1364 humedales z>3):
  a) la componente meteorologica usaba el z gaussiano sin corregir (invalido), y
  b) la ponderacion 50/50 era una decision de diseno sin calibrar.

v2:
  - Conjunto de exposicion: humedales >= P90 del registro 2003-2023 (acumulado
    corregido), n=379. Los componentes se calculan para los 2916.
  - expo_met = (pctl_empirico - 50) / 50, recortado a [0, 1]: 0 = quincena
    normal o seca, 1 = percentil 100. Con 21 anhos el maximo alcanzable es
    P95.5 -> expo_met tope 0.91 (resolucion del registro, documentado).
  - expo_topo = TWI normalizado (percentiles 2-98 del raster regional), igual
    que v1 (la topografia no cambio).
  - SIN registros de anegamiento no hay calibracion posible contra terreno.
    Sustituto honesto: analisis de sensibilidad de la ponderacion
    w in {0.3, 0.5, 0.7} (peso meteorologico) + NUCLEO ROBUSTO = humedales
    clasificados "alta" (>= 0.6) bajo LAS TRES ponderaciones, con Spearman
    entre rankings y Jaccard entre conjuntos "alta".

Salidas: humedales_exposicion_v2.csv (2916), humedales_p90_exposicion_v2.geojson
         (379), resumen_exposicion_v2.json, filas HTML tabla comunal (consola).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from scipy.stats import spearmanr

from config import WORK_DIR as HERE, HUMEDALES_SHP as HU
TWI_TIF = HERE / "twi_valpo.tif"
PESOS = [0.3, 0.5, 0.7]          # peso de la componente meteorologica
UMBRAL_ALTA = 0.6                # igual que v1, por comparabilidad


def main():
    hv = pd.read_csv(HERE / "humedales_valpo_anomalia_v2.csv", encoding="utf-8")
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    assert len(hu) == len(hv), (len(hu), len(hv))

    with rasterio.open(TWI_TIF) as s:
        twi = s.read(1).astype("float64")
        twi[twi == s.nodata] = np.nan
        transform = s.transform
        crs = s.crs
    finite = twi[np.isfinite(twi)]
    lo, hi = np.nanpercentile(finite, 2), np.nanpercentile(finite, 98)
    twi_n = np.clip((twi - lo) / (hi - lo), 0, 1)

    pts = hu.to_crs(crs).representative_point()
    inv = ~transform
    cols, rows = inv * (pts.x.values, pts.y.values)
    rows = np.clip(np.asarray(rows, dtype=int), 0, twi.shape[0] - 1)
    cols = np.clip(np.asarray(cols, dtype=int), 0, twi.shape[1] - 1)

    df = hv.copy()
    df["twi"] = np.round(twi[rows, cols], 2)
    df["expo_topo"] = np.round(twi_n[rows, cols], 3)
    df["expo_met"] = np.round(np.clip((df.pctl_empirico - 50.0) / 50.0, 0, 1), 3)

    for w in PESOS:
        df[f"expo_comp_w{int(w*100)}"] = np.round(
            w * df.expo_met + (1 - w) * df.expo_topo, 3)

    df["en_p90"] = df.pctl_empirico >= 90
    sub = df[df.en_p90].copy()
    n = len(sub)
    print(f"conjunto de exposicion >= P90: n={n} (de {len(df)})")

    # sensibilidad de la ponderacion en el conjunto >= P90
    comps = {w: sub[f"expo_comp_w{int(w*100)}"] for w in PESOS}
    altas = {w: set(sub.index[comps[w] >= UMBRAL_ALTA]) for w in PESOS}
    rho = {f"spearman_w{int(a*100)}_w{int(b*100)}":
           round(float(spearmanr(comps[a], comps[b]).statistic), 3)
           for a, b in [(0.3, 0.5), (0.5, 0.7), (0.3, 0.7)]}
    jac = {f"jaccard_alta_w{int(a*100)}_w{int(b*100)}":
           round(len(altas[a] & altas[b]) / max(len(altas[a] | altas[b]), 1), 3)
           for a, b in [(0.3, 0.5), (0.5, 0.7), (0.3, 0.7)]}
    nucleo = altas[0.3] & altas[0.5] & altas[0.7]
    union = altas[0.3] | altas[0.5] | altas[0.7]
    df["alta_robusta"] = df.index.isin(nucleo)

    df.to_csv(HERE / "humedales_exposicion_v2.csv", index=False, encoding="utf-8")
    out = hu.loc[sub.index].copy()
    for c in ["pctl_empirico", "anomaly_v2_pct", "twi", "expo_topo", "expo_met",
              "expo_comp_w50", "alta_robusta"]:
        out[c] = df.loc[sub.index, c].values
    out.to_crs(4326).to_file(HERE / "humedales_p90_exposicion_v2.geojson",
                             driver="GeoJSON")

    resumen = {
        "definicion": ("expo_met=(pctl-50)/50 en [0,1]; expo_topo=TWI norm 2-98; "
                       "compuesto w*met+(1-w)*topo; alta >= 0.6; conjunto >= P90"),
        "n_conjunto_p90": n,
        "expo_met_media_p90": round(float(sub.expo_met.mean()), 3),
        "expo_topo_media_p90": round(float(sub.expo_topo.mean()), 3),
        "alta_por_peso": {f"w{int(w*100)}": len(altas[w]) for w in PESOS},
        "sensibilidad_spearman": rho,
        "sensibilidad_jaccard_alta": jac,
        "nucleo_robusto_alta": len(nucleo),
        "union_alta": len(union),
        "pct_nucleo_de_union": round(100 * len(nucleo) / max(len(union), 1), 1),
        "top_comunas_nucleo": (df[df.alta_robusta].groupby("comuna").size()
                               .sort_values(ascending=False).head(8).to_dict()),
    }
    (HERE / "resumen_exposicion_v2.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))

    # tabla comunal para el informe: comunas por expo compuesta media (w50, P90)
    top = (sub.assign(c=comps[0.5]).groupby(hv.loc[sub.index, "comuna"])
             .agg(comp=("c", "mean"), n=("c", "size"))
             .sort_values("comp", ascending=False).head(8))
    wmax = top.comp.max()
    filas = ["  <tbody>"]
    for com, r in top.iterrows():
        pw = int(round(100 * r.comp / wmax))
        filas.append(f'<tr><td>{com}</td><td class="num">{r.comp:.2f}</td>'
                     f'<td class="num">{int(r.n)}</td>'
                     f'<td class="bar"><span style="width:{pw}%"></span></td></tr>')
    filas.append("</tbody>")
    (HERE / "tabla_comunal_expo_v2.html").write_text("".join(filas),
                                                     encoding="utf-8")
    print("\n-> humedales_exposicion_v2.csv, humedales_p90_exposicion_v2.geojson,"
          " resumen_exposicion_v2.json, tabla_comunal_expo_v2.html")


if __name__ == "__main__":
    main()
