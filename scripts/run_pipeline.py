# -*- coding: utf-8 -*-
"""Ejecuta el pipeline completo del análisis SIIA-Valparaíso en orden.

Cada paso es un script independiente que lee y escribe en la carpeta de trabajo
(config.WORK_DIR). Uso:

    python scripts/run_pipeline.py            # pipeline completo
    python scripts/run_pipeline.py --desde analyze_valpo   # reanuda desde un paso
    python scripts/run_pipeline.py --lista    # muestra los pasos y termina

Requisitos:
  - Dependencias:  pip install -r requirements.txt
  - Fuentes: DEM y AOI vienen en sources/; la climatología (rásteres ERA5) y el
    inventario de humedales son externos (ver CONTRIBUTING.md). Define
    SIIA_MODEL_DIR / SIIA_HUMEDALES_DIR si no están en la ruta por defecto.
  - Pasos de red: fetch_recent, ivt_evento y dmc_* consultan APIs.
  - Los pasos DMC requieren las variables DMC_USER y DMC_TOKEN (opcionales).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

# (script, descripción, ¿requiere token DMC?)
STEPS = [
    ("clim_valpo.py", "Climatología 1-18 jul (ERA5 del modelo)", False),
    ("fetch_recent.py", "Precipitación reciente 1 jul-18 jul 09:00 (Open-Meteo)", False),
    ("analyze_valpo.py", "Anomalía + contraste con humedales", False),
    ("build_extras.py", "Mapa modelo-vs-obs + GeoJSON z>3", False),
    ("topo_analysis.py", "Pendiente + flujo + TWI (DEM)", False),
    ("modelo_3d_anomalia.py", "Modelo 3D del relieve", False),
    ("dmc_query.py", "Consulta API DMC/DGAC (opcional)", True),
    ("dmc_extract.py", "Extrae precipitación observada DMC", True),
    ("ivt_evento.py", "Transporte de vapor (IVT) + categoría AR", False),
    ("auditoria_estaciones.py", "Auditoría de estaciones + ventana exacta 24 h", False),
    ("correccion_loo.py", "Corrección de sesgo: validación leave-one-out", False),
    ("anomalia_v2.py", "Anomalía v2: clima homogéneo + percentiles empíricos", False),
    ("mapa_v2.py", "Mapa v2 (anomalía corregida + percentil empírico)", False),
    ("mapa_humedales_v2.py", "Figura humedales v2 (percentil empírico)", False),
    ("build_report.py", "Ensambla el informe HTML", False),
    ("assemble_web.py", "Construye el sitio (public/)", False),
]


def run(step: str) -> int:
    print(f"\n{'='*66}\n▶ {step}\n{'='*66}", flush=True)
    t0 = time.time()
    r = subprocess.run([sys.executable, str(SCRIPTS / step)])
    print(f"  ({time.time()-t0:.1f} s, código {r.returncode})")
    return r.returncode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="reanuda desde este script (p. ej. analyze_valpo)")
    ap.add_argument("--lista", action="store_true", help="muestra los pasos y termina")
    ap.add_argument("--sin-dmc", action="store_true",
                    help="omite los pasos DMC (requieren token)")
    args = ap.parse_args()

    if args.lista:
        for i, (s, d, dmc) in enumerate(STEPS, 1):
            print(f"  {i:2d}. {s:22s} {d}{'  [DMC]' if dmc else ''}")
        return

    started = args.desde is None
    for step, desc, needs_dmc in STEPS:
        if not started:
            if step.startswith(args.desde):
                started = True
            else:
                continue
        if needs_dmc and args.sin_dmc:
            print(f"\n⏭  {step} omitido (--sin-dmc)")
            continue
        code = run(step)
        if code != 0:
            if needs_dmc:
                print(f"⚠  {step} falló (¿faltan DMC_USER/DMC_TOKEN?). Continúo.")
                continue
            print(f"\n✖ Pipeline detenido en {step} (código {code}).")
            sys.exit(code)
    print("\n✔ Pipeline completo. Sitio en public/. Ejecuta 'npm start' para verlo.")


if __name__ == "__main__":
    main()
