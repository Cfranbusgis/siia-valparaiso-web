# -*- coding: utf-8 -*-
"""Extrae precipitacion observada (24h/6h) de la red DMC/DGAC desde el JSON.

Lee dmc_valpo_reciente.json (respuesta de la API oficial) y escribe
dmc_observado_valpo.csv con el acumulado de agua caida mas reciente por estacion
de la Region de Valparaiso y zona central.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import config
HERE = config.WORK_DIR
d = json.loads((HERE / "dmc_valpo_reciente.json").read_text(encoding="utf-8"))
est = next(iter(d.values()))["data"]["datosEstaciones"]


def num(x):
    if not x:
        return None
    m = re.search(r"[-\d.]+", x)
    return float(m.group()) if m else None


def latest(datos, field):
    for rec in datos:
        v = num(rec.get(field))
        if v is not None:
            return v, rec.get("momento")
    return None, None


rows = []
for e in est:
    s = e["estacion"]
    datos = e.get("datos") or []
    try:
        la, lo = float(s["latitud"]), float(s["longitud"])
    except (TypeError, ValueError):
        continue
    if not (-34.3 <= la <= -32.0 and -72.0 <= lo <= -70.0):
        continue
    a24, m24 = latest(datos, "aguaCaida24Horas")
    a6, _ = latest(datos, "aguaCaida6Horas")
    if a24 is None:
        continue
    rows.append((s["nombreEstacion"], la, lo, a24, a6 if a6 is not None else "",
                 m24, s["codigoNacional"]))

rows.sort(key=lambda r: r[3], reverse=True)
out = ["estacion,lat,lon,agua24h_mm,agua6h_mm,momento_utc,codigo"]
for n, la, lo, a24, a6, m24, cod in rows:
    n2 = n.replace(",", " ")
    out.append(f"{n2},{la},{lo},{a24},{a6},{m24},{cod}")
(HERE / "dmc_observado_valpo.csv").write_text("\n".join(out), encoding="utf-8")

vals = [r[3] for r in rows]
print(f"estaciones: {len(rows)} | 24h mm rango {min(vals)}-{max(vals)} | "
      f"media {sum(vals)/len(vals):.1f}")
print("top5:", [(r[0], r[3]) for r in rows[:5]])
