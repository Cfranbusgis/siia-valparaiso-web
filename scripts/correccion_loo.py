"""FASE 4b - Validacion leave-one-out (LOO) de tres correcciones del sesgo.

El modelo (Open-Meteo, base del "reciente") sobreestima el peak-24h ~2x
respecto de las 14 estaciones robustas. Antes de corregir la grilla hay que
elegir COMO corregir, y la eleccion debe ganarse fuera de muestra:

  A) factor_regional : corregido = modelo * mediana(obs/modelo)   [robusto]
  B) residuos_idw    : corregido = modelo * exp(IDW de log(obs/modelo))
  C) altitud         : corregido = modelo * exp(a + b*altitud)    [OLS en log]

LOO: se retira una estacion, se ajusta la correccion con las 13 restantes,
se predice la retirada. MAE / RMSE / sesgo sobre las 14 predicciones.
Baseline: modelo sin corregir. Base = model_win24_mm (ventana temporal exacta).

Salida: resultados_loo.csv (metricas) + loo_predicciones.csv (por estacion)
        + eleccion impresa.
"""
from __future__ import annotations

from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import numpy as np
import pandas as pd

from config import WORK_DIR as HERE
IDW_POWER = 2.0


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def idw_logratio(lat, lon, tr):
    """IDW del log-ratio de las estaciones de entrenamiento hacia (lat, lon)."""
    d = np.array([haversine_km(lat, lon, la, lo) for la, lo in zip(tr.lat, tr.lon)])
    d = np.maximum(d, 1.0)
    w = 1.0 / d ** IDW_POWER
    return float(np.sum(w * tr.logratio.values) / np.sum(w))


def fit_altitud(tr):
    b, a = np.polyfit(tr.alt_m.values, tr.logratio.values, 1)
    return a, b


def main():
    aud = pd.read_csv(HERE / "auditoria_estaciones.csv", encoding="utf-8")
    v = aud[aud.flag.str.startswith("OK")].reset_index(drop=True)
    v["logratio"] = np.log(v.agua24h_mm / v.model_win24_mm)   # log(obs/modelo)
    n = len(v)
    print(f"estaciones robustas: n={n}")

    # correlaciones diagnosticas del log-ratio
    for var in ["alt_m", "dist_nucleo_km"]:
        r = np.corrcoef(v[var], v.logratio)[0, 1]
        print(f"  corr(log obs/mod, {var}): {r:+.2f}")

    preds = {m: np.zeros(n) for m in
             ["sin_correccion", "factor_regional", "residuos_idw", "altitud"]}
    for i in range(n):
        te, tr = v.iloc[i], v.drop(index=i)
        m = te.model_win24_mm
        preds["sin_correccion"][i] = m
        preds["factor_regional"][i] = m * np.exp(np.median(tr.logratio))
        preds["residuos_idw"][i] = m * np.exp(idw_logratio(te.lat, te.lon, tr))
        a, b = fit_altitud(tr)
        preds["altitud"][i] = m * np.exp(a + b * te.alt_m)

    obs = v.agua24h_mm.values
    rows = []
    for met, p in preds.items():
        rows.append({
            "metodo": met,
            "MAE_mm": round(np.mean(np.abs(p - obs)), 1),
            "RMSE_mm": round(np.sqrt(np.mean((p - obs) ** 2)), 1),
            "sesgo_mm": round(np.mean(p - obs), 1),
            "ratio_medio": round(np.mean(p / obs), 2),
        })
    res = pd.DataFrame(rows)
    res.to_csv(HERE / "resultados_loo.csv", index=False, encoding="utf-8")
    print("\n=== LOO (n=14, prediccion fuera de muestra) ===")
    print(res.to_string(index=False))

    det = v[["estacion", "alt_m", "dist_nucleo_km", "agua24h_mm"]].copy()
    for met, p in preds.items():
        det[met] = np.round(p, 1)
    det.to_csv(HERE / "loo_predicciones.csv", index=False, encoding="utf-8")

    corr_methods = res[res.metodo != "sin_correccion"]
    best = corr_methods.sort_values(["RMSE_mm", "MAE_mm"]).iloc[0]
    base = res[res.metodo == "sin_correccion"].iloc[0]
    print(f"\nGANADOR fuera de muestra: {best.metodo} "
          f"(RMSE {best.RMSE_mm} vs {base.RMSE_mm} sin corregir; "
          f"sesgo {best.sesgo_mm} vs {base.sesgo_mm})")

    # factor final (ajustado con TODAS las estaciones) para aplicar a la grilla
    print(f"factor regional (mediana obs/mod, n=14): "
          f"{np.exp(np.median(v.logratio)):.3f}")
    print(f"regresion altitud: log(obs/mod) = {fit_altitud(v)[0]:+.3f} "
          f"{fit_altitud(v)[1]:+.5f}*alt_m")
    print("-> resultados_loo.csv, loo_predicciones.csv")


if __name__ == "__main__":
    main()
