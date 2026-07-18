# -*- coding: utf-8 -*-
"""Ensambla el sitio estatico (public/) a partir de los productos del analisis.

- Envuelve el informe (fragmento HTML) en una pagina completa con <head>, charset
  UTF-8 y una barra de navegacion.
- Copia el modelo 3D interactivo e inserta un enlace de regreso al informe.
- Copia los datos y scripts del analisis al repositorio.

Uso:  python scripts/assemble_web.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

import config
REPO = config.REPO
SRC = config.WORK_DIR
PUBLIC = REPO / "public"
DATA = REPO / "data"
SCRIPTS = REPO / "scripts"

REPORT = SRC / "informe_anomalia_valpo_julio2026.html"
MODEL3D = SRC / "modelo_3d_anomalia_valpo.html"

TITLE = ("Sistema Regional de Inteligencia Ambiental — Anomalía de precipitación, "
         "Región de Valparaíso, julio 2026")

NAV = """
<nav style="position:sticky;top:0;z-index:1000;display:flex;gap:18px;align-items:center;
  padding:10px 20px;background:#0b3d66;color:#fff;font-family:-apple-system,Segoe UI,sans-serif;
  font-size:.9rem;box-shadow:0 2px 8px rgba(0,0,0,.15)">
  <strong style="letter-spacing:.04em">SIIA · Valparaíso</strong>
  <a href="/" style="color:#cfe6f2;text-decoration:none">Informe</a>
  <a href="/modelo-3d.html" style="color:#cfe6f2;text-decoration:none">Modelo 3D interactivo</a>
</nav>
"""

BACKLINK = """
<div style="position:fixed;top:12px;left:12px;z-index:9999;font-family:Arial,sans-serif">
  <a href="/" style="display:inline-block;padding:8px 14px;background:rgba(11,61,102,0.9);
    color:#fff;border-radius:8px;text-decoration:none;font-size:13px;box-shadow:0 4px 12px rgba(0,0,0,.2)">
    ← Volver al informe</a>
</div>
"""


def build_index() -> None:
    fragment = REPORT.read_text(encoding="utf-8")
    # el informe referencia el modelo 3D por nombre de archivo: convertir en enlace
    fragment = fragment.replace(
        "<code>modelo_3d_anomalia_valpo.html</code>",
        '<a href="/modelo-3d.html"><code>modelo 3D interactivo</code></a>')
    page = (
        "<!doctype html>\n"
        '<html lang="es">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"<title>{TITLE}</title>\n"
        '<meta name="description" content="Analisis del rio atmosferico de julio 2026 '
        'y su expresion en la Region de Valparaiso y sus humedales.">\n'
        "</head>\n<body>\n"
        + NAV + fragment + "\n</body>\n</html>\n"
    )
    (PUBLIC / "index.html").write_text(page, encoding="utf-8")
    print(f"public/index.html  ({len(page)//1024} KB)")


def build_model() -> None:
    html = MODEL3D.read_text(encoding="utf-8")
    if "</body>" in html:
        html = html.replace("</body>", BACKLINK + "\n</body>", 1)
    else:
        html += BACKLINK
    (PUBLIC / "modelo-3d.html").write_text(html, encoding="utf-8")
    print(f"public/modelo-3d.html  ({len(html)//1024} KB)")


def copy_assets() -> None:
    data_files = [
        "anomaly_grid_valpo.csv", "humedales_valpo_anomalia.csv",
        "humedales_z_gt3_valpo.geojson", "humedales_z_gt3_topo.geojson",
        "humedales_z_gt3_topo.csv", "estaciones_modelo_vs_obs.csv",
        "dmc_observado_valpo.csv", "ivt_serie.csv",
        "resumen_valpo.json", "resumen_topo.json", "resumen_ivt.json",
        "clim_valpo.csv", "recent_valpo.csv",
    ]
    for f in data_files:
        p = SRC / f
        if p.exists():
            shutil.copy2(p, DATA / f)
    print(f"data/  ({sum(1 for f in data_files if (SRC/f).exists())} archivos)")
    # NOTA: no se copian los scripts. Los scripts del repositorio (scripts/) son
    # la fuente de verdad (versionada y con rutas configurables via config.py);
    # copiarlos desde WORK_DIR los sobrescribiria con versiones no portables.


def main() -> None:
    build_index()
    build_model()
    copy_assets()
    print("\nSitio ensamblado en:", PUBLIC)


if __name__ == "__main__":
    main()
