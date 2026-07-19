"""Índice de susceptibilidad de acumulación y prioridad de inundación/saturación.

Marco:
  Exposición meteorológica (percentil del acumulado corregido)
    ×  Susceptibilidad de acumulación (dónde el agua converge, se estanca y no drena):
         - TWI normalizado           (convergencia potencial, 30 m)
         - concavidad / depresiones  (hoyas donde se estanca, 30 m)
         - retención edáfica         (suelo que retiene: CIREN + [FAO fill])
  = prioridad de inundación/saturación por humedal.

Toma los productos ya calculados por humedal (orden idéntico de los 2916):
  humedales_exposicion_v2.csv  -> expo_met, expo_topo (TWI)
  humedales_concavidad.csv     -> acc_topo
  humedales_suelo.csv          -> expo_suelo
  humedales_valpo_anomalia_v2.csv -> pctl_empirico

Salida: humedales_susceptibilidad.csv, resumen_susceptibilidad.json
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent

def main():
    exp = pd.read_csv(HERE / "humedales_exposicion_v2.csv", encoding="utf-8")
    con = pd.read_csv(HERE / "humedales_concavidad.csv", encoding="utf-8")
    sue = pd.read_csv(HERE / "humedales_suelo.csv", encoding="utf-8")
    ddr = pd.read_csv(HERE / "humedales_distrios.csv", encoding="utf-8")  # rios oficiales
    ano = pd.read_csv(HERE / "humedales_valpo_anomalia_v2.csv", encoding="utf-8")
    n = len(exp); assert len(con) == n == len(sue) == len(ano) == len(ddr)

    twi = exp["expo_topo"].to_numpy()
    acc = con["acc_topo"].to_numpy()
    suelo = sue["expo_suelo"].to_numpy()             # puede tener NaN
    prox = ddr["prox_rio"].to_numpy()                # cercania a rio oficial (fsm-pk)
    met = exp["expo_met"].to_numpy()

    # susceptibilidad de acumulacion = media de componentes disponibles
    # (TWI + concavidad/depresiones + retencion de suelo + cercania a drenaje)
    S = np.vstack([twi, acc, suelo, prox])
    susc = np.nanmean(S, axis=0)
    cobertura_suelo = ~np.isnan(suelo)

    # prioridad de inundación/saturación = exposición meteo × susceptibilidad
    prioridad = met * susc

    # 5 clases (Muy Baja->Muy Alta) por quintiles de la prioridad (fsm-pk)
    qs = np.nanquantile(prioridad, [0.2, 0.4, 0.6, 0.8])
    clases = np.array(["Muy Baja", "Baja", "Moderada", "Alta", "Muy Alta"])
    clase = clases[np.digitize(prioridad, qs)]

    out = pd.DataFrame({
        "nom_humed": exp["nom_humed"] if "nom_humed" in exp else ano.get("nom_humed"),
        "comuna": sue["comuna"], "pctl_empirico": ano["pctl_empirico"],
        "expo_met": np.round(met, 3), "twi": np.round(twi, 3),
        "acc_topo": np.round(acc, 3), "expo_suelo": np.round(suelo, 3),
        "prox_drenaje": np.round(prox, 3),
        "susc_acumulacion": np.round(susc, 3),
        "prioridad_inundacion": np.round(prioridad, 3),
        "clase_prioridad": clase,
        "suelo_fuente": sue["fuente_suelo"],
        "cuenca": pd.read_csv(HERE / "humedales_hidro.csv", encoding="utf-8")["cuenca"],
    })
    out.to_csv(HERE / "humedales_susceptibilidad.csv", index=False, encoding="utf-8")

    # umbral de prioridad alta: P90 de la prioridad, dentro de los ≥P90 meteo
    p90 = ano["pctl_empirico"] >= 90
    thr = np.nanpercentile(prioridad[p90], 66)
    alta = p90 & (prioridad >= thr)
    res = {
        "cobertura_suelo_pct": round(100*cobertura_suelo.mean(), 1),
        "susc_media": round(float(np.nanmean(susc)), 3),
        "prioridad_media": round(float(np.nanmean(prioridad)), 3),
        "humedales_ge_P90": int(p90.sum()),
        "prioridad_alta (>=P90 y susc alta)": int(alta.sum()),
        "clases_prioridad": {k:int(v) for k,v in pd.Series(clase).value_counts().to_dict().items()},
        "clases_prioridad_ge_P90": {k:int(v) for k,v in pd.Series(clase[p90.values]).value_counts().to_dict().items()},
        "top_comunas_prioridad": (out[alta].groupby("comuna").size()
                                  .sort_values(ascending=False).head(8).to_dict()),
    }
    (HERE / "resumen_susceptibilidad.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("-> humedales_susceptibilidad.csv, resumen_susceptibilidad.json")

if __name__ == "__main__":
    main()
