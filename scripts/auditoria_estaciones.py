"""FASE 4a - Auditoria de estaciones: descartes, correspondencia temporal y
tabla completa por estacion.

Tres preguntas de la auditoria:
1. Estaciones descartadas: cuales, por que, y si el descarte fue correcto.
   (dmc_observado_valpo.csv trae 32 estaciones; el AOI RV.shp retiene 17.)
2. Correspondencia temporal: el obs es aguaCaida24Horas en un snapshot
   ~01:00 UTC del 18-jul = ventana movil 16-jul ~21:00 -> 17-jul ~21:00 LOCAL.
   El modelo v1 usaba el dia CALENDARIO (00-24h). Aqui se suma el modelo
   horario sobre la MISMA ventana de 24 h que cada estacion -> se cuantifica
   cuanto del "2x" era desajuste de ventana y cuanto es sesgo real.
3. Tabla por estacion: obs, modelo (calendario y ventana exacta), error,
   ratio, altitud (DEM 250 m) y distancia al nucleo del evento (La Dormida,
   maximo observado).

Salida: auditoria_estaciones.csv (todas las 32, con flag de descarte)
        + resumen por consola.
"""
from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timedelta
from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import Point

from config import WORK_DIR as HERE, AOI_SHP as AOI, DEM_TIF as DEM
FORECAST = "https://api.open-meteo.com/v1/forecast"
EVENT_DAYS = ["2026-07-15", "2026-07-16", "2026-07-17", "2026-07-18"]
UTC_OFFSET = timedelta(hours=-4)          # Chile continental, julio (sin DST)
NUCLEO = (-33.04944, -71.00139)           # La Dormida: maximo observado (120.1 mm)


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return s


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def fetch_hourly(lats, lons):
    url = (f"{FORECAST}?latitude={lats}&longitude={lons}"
           "&hourly=precipitation&past_days=7&forecast_days=1"
           "&timezone=America/Santiago")
    d = json.loads(urllib.request.urlopen(url, timeout=120).read())
    return d if isinstance(d, list) else [d]


def main():
    dmc = pd.read_csv(HERE / "dmc_observado_valpo.csv", encoding="utf-8")
    dmc["estacion"] = dmc["estacion"].map(fix_mojibake).str.strip()

    aoi = gpd.read_file(AOI).to_crs(4326).union_all()
    dmc["en_aoi"] = [Point(lo, la).within(aoi) for la, lo in zip(dmc.lat, dmc.lon)]

    # --- altitud desde el DEM (EPSG:32719) ---
    pts = gpd.GeoSeries([Point(lo, la) for la, lo in zip(dmc.lat, dmc.lon)],
                        crs=4326).to_crs(32719)
    with rasterio.open(DEM) as src:
        alts = [next(src.sample([(p.x, p.y)]))[0] for p in pts]
    nod = rasterio.open(DEM).nodata
    dmc["alt_m"] = [np.nan if (a is None or (nod is not None and a == nod) or a < -100)
                    else float(a) for a in alts]

    dmc["dist_nucleo_km"] = [haversine_km(la, lo, *NUCLEO)
                             for la, lo in zip(dmc.lat, dmc.lon)]

    # --- modelo horario Open-Meteo en TODAS las estaciones ---
    lats = ",".join(f"{v:.5f}" for v in dmc.lat)
    lons = ",".join(f"{v:.5f}" for v in dmc.lon)
    locs = fetch_hourly(lats, lons)

    win24, cal24, elev_om = [], [], []
    for (_, st), one in zip(dmc.iterrows(), locs):
        times = [datetime.fromisoformat(t) for t in one["hourly"]["time"]]
        prec = [p if p is not None else 0.0 for p in one["hourly"]["precipitation"]]
        elev_om.append(one.get("elevation", np.nan))

        # ventana exacta del snapshot: [momento_local - 24h, momento_local)
        mom_local = (datetime.fromisoformat(str(st["momento_utc"])) + UTC_OFFSET)
        w0, w1 = mom_local - timedelta(hours=24), mom_local
        win24.append(sum(p for t, p in zip(times, prec) if w0 < t <= w1))

        # dia calendario (metodo v1): max suma diaria 15-18 jul
        daily = {}
        for t, p in zip(times, prec):
            daily[t.date().isoformat()] = daily.get(t.date().isoformat(), 0.0) + p
        cal24.append(max(daily.get(d, 0.0) for d in EVENT_DAYS))

    dmc["model_win24_mm"] = np.round(win24, 1)
    dmc["model_cal24_mm"] = np.round(cal24, 1)
    dmc["elev_openmeteo_m"] = elev_om

    obs = dmc["agua24h_mm"]
    dmc["error_mm"] = np.round(dmc.model_win24_mm - obs, 1)
    dmc["ratio_model_obs"] = np.where(obs > 0,
                                      np.round(dmc.model_win24_mm / obs, 2), np.nan)

    # --- flags de auditoria ---
    def flag(row):
        if not row.en_aoi:
            return "DESCARTADA: fuera de la V Region (AOI RV.shp)"
        if row.agua24h_mm < 5:
            return "SOSPECHOSA: obs ~0 en pleno evento (dato DMC dudoso)"
        return "OK: usada en validacion"
    dmc["flag"] = dmc.apply(flag, axis=1)

    cols = ["estacion", "codigo", "lat", "lon", "alt_m", "elev_openmeteo_m",
            "dist_nucleo_km", "agua24h_mm", "model_win24_mm", "model_cal24_mm",
            "error_mm", "ratio_model_obs", "momento_utc", "en_aoi", "flag"]
    out = dmc[cols].copy()
    out["dist_nucleo_km"] = out["dist_nucleo_km"].round(1)
    out["alt_m"] = out["alt_m"].round(0)
    out = out.sort_values(["en_aoi", "agua24h_mm"], ascending=[False, False])
    out.to_csv(HERE / "auditoria_estaciones.csv", index=False, encoding="utf-8")

    # --- resumen ---
    print("=== 1) ESTACIONES DESCARTADAS (fuera de AOI) ===")
    for _, r in out[~out.en_aoi].iterrows():
        print(f"  {r.estacion:45s} obs={r.agua24h_mm:6.1f} mm  "
              f"dist_nucleo={r.dist_nucleo_km:5.0f} km")
    n_zero_out = ((~out.en_aoi) & (out.agua24h_mm < 5)).sum()
    print(f"  -> {(~out.en_aoi).sum()} descartadas; {n_zero_out} de ellas tambien "
          "marcan ~0 mm (el problema de ceros es del snapshot DMC, no del AOI)")

    v = out[out.en_aoi].copy()
    rob = v[v.agua24h_mm >= 10]
    o, w, c = rob.agua24h_mm.values, rob.model_win24_mm.values, rob.model_cal24_mm.values
    print(f"\n=== 2) CORRESPONDENCIA TEMPORAL (n={len(rob)} robustas) ===")
    print(f"  modelo DIA CALENDARIO vs obs : sesgo {np.mean(c-o):+6.1f} mm | "
          f"RMSE {np.sqrt(np.mean((c-o)**2)):5.1f} | ratio medio {np.mean(c/o):.2f}")
    print(f"  modelo VENTANA EXACTA vs obs : sesgo {np.mean(w-o):+6.1f} mm | "
          f"RMSE {np.sqrt(np.mean((w-o)**2)):5.1f} | ratio medio {np.mean(w/o):.2f}")
    print(f"  corr ventana exacta: {np.corrcoef(o, w)[0,1]:.2f}")

    print("\n=== 3) TABLA V REGION (obs desc) ===")
    print(v[["estacion", "alt_m", "dist_nucleo_km", "agua24h_mm",
             "model_win24_mm", "error_mm", "ratio_model_obs", "flag"]]
          .to_string(index=False))
    print("\n-> auditoria_estaciones.csv")


if __name__ == "__main__":
    main()
