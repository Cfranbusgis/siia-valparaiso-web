# -*- coding: utf-8 -*-
"""Consulta la API oficial de la Direccion Meteorologica de Chile (DMC / DGAC).

La DMC pertenece a la DGAC. Su API de Servicios Climaticos requiere un usuario
(correo) y un token gratuito. Registro:
    https://climatologia.meteochile.gob.cl/  ->  crear cuenta  ->  el token
    llega por correo (no se puede automatizar: requiere confirmacion por email).

Uso (una vez tengas el token):
    set DMC_USER=tu_correo@ejemplo.cl        (PowerShell:  $env:DMC_USER=...)
    set DMC_TOKEN=xxxxxxxx
    python dmc_query.py

Consulta los datos recientes de precipitacion de estaciones DMC de la Region de
Valparaiso y guarda dmc_valpo_reciente.json / .csv.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "https://climatologia.meteochile.gob.cl/application/servicios"
USER = os.getenv("DMC_USER", "")
TOKEN = os.getenv("DMC_TOKEN", "")

# Codigo nacional DMC -> nombre (estaciones Region de Valparaiso y cercanas)
ESTACIONES = {
    "320041": "Rodelillo, Valparaiso Ad.",
    "320051": "Torquemada, Concon Ad.",
    "321030": "San Felipe",
    "330007": "Los Libertadores",
    "330030": "Quillota",
    "330020": "Quinta Normal, Santiago",
}


def api(path: str) -> dict:
    url = f"{BASE}/{path}?usuario={USER}&token={TOKEN}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def main() -> None:
    if not USER or not TOKEN:
        print("Falta DMC_USER / DMC_TOKEN en el entorno. Registrate en "
              "https://climatologia.meteochile.gob.cl/ y exporta las variables.")
        return
    out = {}
    for cod, name in ESTACIONES.items():
        try:
            d = api(f"getDatosRecientesRedEma/{cod}")
            out[cod] = {"nombre": name, "data": d}
            msg = d.get("mensaje")
            print(f"{cod} {name}: {'OK' if not msg else msg}")
        except Exception as e:                          # noqa: BLE001
            print(f"{cod} {name}: ERR {e}")
    (HERE / "dmc_valpo_reciente.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("-> dmc_valpo_reciente.json")


if __name__ == "__main__":
    main()
