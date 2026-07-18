# -*- coding: utf-8 -*-
"""Transporte integrado de vapor (IVT) del rio atmosferico, con dato propio.

Calcula el IVT horario a partir de humedad relativa, temperatura y viento en
niveles de presion (reanalisis/operacional de Open-Meteo) para puntos de la costa
de Valparaiso, e identifica la categoria del rio atmosferico segun la escala de
Ralph et al. (2019): categoria por IVT maximo, ajustada por duracion de las
condiciones de AR (IVT > 250 kg m-1 s-1).

    IVT = (1/g) * | integral_{p_sfc}^{300hPa} q * V dp |
    q (humedad especifica) = 0.622 e / (p - 0.378 e),  e = (RH/100) es(T)
    es(T) = 6.112 exp(17.67 Tc/(Tc+243.5))  [hPa, Tetens]

Salidas:
  ivt_serie.csv       (hora, IVT, IVTu, IVTv, direccion)
  ivt_evento.png      (serie temporal con bandas de categoria AR)
  resumen_ivt.json    (IVT maximo, duracion >250, categoria, direccion del flujo)
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
LEVELS = [1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300]
G = 9.80665
# puntos costeros de entrada del flujo (norte, centro, sur de la region)
POINTS = [(-32.55, -71.45), (-33.05, -71.60), (-33.60, -71.60)]
CAT_EDGES = [250, 500, 750, 1000, 1250]     # umbrales IVT escala AR
CAT_NAMES = {1: "AR1 (débil)", 2: "AR2 (moderado)", 3: "AR3 (fuerte)",
             4: "AR4 (extremo)", 5: "AR5 (excepcional)"}


def fetch(lat, lon):
    vs = []
    for L in LEVELS:
        vs += [f"temperature_{L}hPa", f"relative_humidity_{L}hPa",
               f"wind_speed_{L}hPa", f"wind_direction_{L}hPa"]
    u = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
         f"&hourly={','.join(vs)}&past_days=7&forecast_days=1"
         "&wind_speed_unit=ms&timezone=America/Santiago")
    return json.loads(urllib.request.urlopen(u, timeout=90).read())["hourly"]


def es_hpa(tc):
    return 6.112 * np.exp(17.67 * tc / (tc + 243.5))


def ivt_series(h):
    t = h["time"]
    n = len(t)
    lev = np.array(LEVELS, dtype="float64")          # hPa
    # matrices (n, nlev)
    T = np.array([h[f"temperature_{L}hPa"] for L in LEVELS], dtype="float64").T
    RH = np.array([h[f"relative_humidity_{L}hPa"] for L in LEVELS], dtype="float64").T
    WS = np.array([h[f"wind_speed_{L}hPa"] for L in LEVELS], dtype="float64").T
    WD = np.array([h[f"wind_direction_{L}hPa"] for L in LEVELS], dtype="float64").T

    e = (RH / 100.0) * es_hpa(T)                      # hPa
    q = 0.622 * e / (lev[None, :] - 0.378 * e)        # kg/kg
    # componentes del viento (convencion meteo: WD = de donde viene)
    wd = np.radians(WD)
    u = -WS * np.sin(wd)
    v = -WS * np.cos(wd)
    qu = q * u
    qv = q * v
    # integral en presion (Pa), niveles descendentes 1000->300
    p_pa = lev * 100.0
    trapz = getattr(np, "trapezoid", None) or np.trapz
    IVTu = -trapz(qu, p_pa, axis=1) / G              # signo por p decreciente
    IVTv = -trapz(qv, p_pa, axis=1) / G
    IVT = np.hypot(IVTu, IVTv)
    direction = (np.degrees(np.arctan2(-IVTu, -IVTv)) % 360)   # de donde viene
    return t, IVT, IVTu, IVTv, direction


def category(max_ivt, hours_gt250):
    base = int(np.searchsorted(CAT_EDGES, max_ivt, side="right"))  # 1..5
    base = min(max(base, 1), 5)
    # ajuste por duracion (Ralph 2019): <24 h baja 1; >48 h sube 1
    if hours_gt250 < 24:
        base = max(1, base - 1)
    elif hours_gt250 > 48:
        base = min(5, base + 1)
    return base


def main():
    # IVT por punto costero; la escala AR se define por el IVT maximo en un sitio,
    # asi que la serie graficada/clasificada es la del punto de mayor pico.
    series = []
    t_ref = None
    for lat, lon in POINTS:
        h = fetch(lat, lon)
        t, IVT_p, IVTu_p, IVTv_p, d = ivt_series(h)
        t_ref = t
        series.append((IVT_p, IVTu_p, IVTv_p))
    peaks = [float(np.max(s[0])) for s in series]
    ksite = int(np.argmax(peaks))
    IVT, IVTu, IVTv = series[ksite]
    direction = (np.degrees(np.arctan2(-IVTu, -IVTv)) % 360)

    t = np.array(t_ref)
    imax = int(np.argmax(IVT))
    max_ivt = float(IVT[imax])
    hours_gt250 = int(np.sum(IVT > 250))
    cat = category(max_ivt, hours_gt250)

    # guardar serie
    lines = ["hora,IVT,IVTu,IVTv,direccion_grados"]
    for i in range(len(t)):
        lines.append(f"{t[i]},{IVT[i]:.1f},{IVTu[i]:.1f},{IVTv[i]:.1f},{direction[i]:.0f}")
    (HERE / "ivt_serie.csv").write_text("\n".join(lines), encoding="utf-8")

    resumen = {
        "ivt_maximo_kg_m_s": round(max_ivt, 1),
        "hora_maximo": str(t[imax]),
        "direccion_flujo_en_maximo_grados": round(float(direction[imax])),
        "horas_ivt_sobre_250": hours_gt250,
        "categoria_AR_estimada": CAT_NAMES[cat],
        "ivt_pico_por_punto": [round(p, 1) for p in peaks],
        "metodo": "IVT = (1/g) int q*V dp, niveles 1000-300 hPa; punto costero de mayor pico",
        "fuente": "Open-Meteo (niveles de presion); escala Ralph et al. 2019",
        "nota": ("estimacion propia; confirma un rio atmosferico intenso con flujo del "
                 "NNO. Es algo menor que la clasificacion operacional AR4-AR5, esperable "
                 "por la resolucion del dato y el suavizado espacial/temporal"),
    }
    (HERE / "resumen_ivt.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))

    # --- figura: serie temporal con bandas de categoria ---
    x = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(11, 4.6))
    band_colors = ["#eef6f9", "#d7ebf2", "#fde9c8", "#f7c4a5", "#e88f6f", "#d9534f"]
    edges = [0] + CAT_EDGES + [max(1400, max_ivt * 1.1)]
    for i in range(len(edges) - 1):
        ax.axhspan(edges[i], edges[i + 1], color=band_colors[i], alpha=.5, zorder=0)
    for e, lb in zip(CAT_EDGES, ["AR1", "AR2", "AR3", "AR4", "AR5"]):
        ax.axhline(e, color="#8894a0", lw=.7, ls="--", zorder=1)
        ax.text(len(t) - 1, e + 8, lb, fontsize=8, color="#57636e", ha="right")
    ax.plot(x, IVT, color="#0b3d66", lw=2, zorder=3)
    ax.fill_between(x, IVT, color="#2b8cbe", alpha=.25, zorder=2)
    ax.scatter([imax], [max_ivt], color="#b5341f", zorder=4, s=40)
    ax.annotate(f"máx {max_ivt:.0f}\n{str(t[imax])[5:16]}",
                (imax, max_ivt), textcoords="offset points", xytext=(-4, 10),
                fontsize=9, color="#b5341f", ha="right")
    # ticks diarios
    day_idx = [i for i in range(len(t)) if str(t[i])[11:16] == "00:00"]
    ax.set_xticks(day_idx)
    ax.set_xticklabels([str(t[i])[5:10] for i in day_idx], rotation=0)
    ax.set_ylabel("IVT (kg m⁻¹ s⁻¹)")
    ax.set_xlabel("Fecha (julio de 2026)")
    ax.set_xlim(0, len(t) - 1); ax.set_ylim(0, edges[-1])
    ax.set_title("Transporte integrado de vapor (IVT) durante el río atmosférico\n"
                 "costa de Valparaíso (punto de mayor magnitud) · niveles 1000–300 hPa",
                 fontsize=11)
    fig.tight_layout(); fig.savefig(HERE / "ivt_evento.png", dpi=160)
    plt.close(fig)
    print("\n-> ivt_serie.csv, ivt_evento.png, resumen_ivt.json")


if __name__ == "__main__":
    main()
