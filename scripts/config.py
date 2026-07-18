# -*- coding: utf-8 -*-
"""Configuración central de rutas del pipeline SIIA-Valparaíso.

Todas las rutas se resuelven desde variables de entorno, con valores por defecto
que apuntan a la máquina donde se construyó el proyecto. Para ejecutar el
pipeline en otro equipo, define estas variables antes de correr los scripts:

    SIIA_MODEL_DIR      Carpeta del modelo ETo (fuente de DEM, ERA5 y AOI).
    SIIA_HUMEDALES_DIR  Carpeta con los shapefiles de humedales y área de estudio.
    SIIA_WORK_DIR       Carpeta de trabajo/salidas (intermedios y figuras).

Ejemplo (PowerShell):
    $env:SIIA_MODEL_DIR = "D:/datos/MOD_EToPM-HS"
    $env:SIIA_WORK_DIR  = "D:/salidas/valpo"

Ejemplo (bash):
    export SIIA_MODEL_DIR=/datos/MOD_EToPM-HS
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def _dir(env: str, default: str) -> Path:
    return Path(os.environ.get(env, default))


# Directorios base (configurables)
MODEL_DIR = _dir("SIIA_MODEL_DIR", r"C:\Users\cfran\Desktop\MOD_EToPM-HS")
HUMEDALES_DIR = _dir(
    "SIIA_HUMEDALES_DIR", r"C:\Users\cfran\Desktop\Taller RRNN\Mapa_Humedales")
WORK_DIR = _dir(
    "SIIA_WORK_DIR",
    r"C:\Users\cfran\Desktop\Taller RRNN\Mapa_Humedales\anomalia_valpo_julio2026")

# Fuentes geoespaciales derivadas
DEM_TIF = MODEL_DIR / "03_inputs" / "DEM" / "DEM_250m_UTM19S_AOI.tif"
AOI_SHP = MODEL_DIR / "03_inputs" / "AOI" / "RV.shp"
ERA5_DIR = MODEL_DIR / "03_inputs" / "ERA5"
HUMEDALES_SHP = HUMEDALES_DIR / "humedales_inventario_rm_rv_cont.shp"

# Alternativa incluida en el repositorio (insumos livianos), por si el modelo
# externo no está disponible: se usa si existe y la fuente principal no.
_REPO_DEM = REPO / "sources" / "DEM_250m_UTM19S_AOI.tif"
_REPO_AOI = REPO / "sources" / "RV.shp"
if not DEM_TIF.exists() and _REPO_DEM.exists():
    DEM_TIF = _REPO_DEM
if not AOI_SHP.exists() and _REPO_AOI.exists():
    AOI_SHP = _REPO_AOI

WORK_DIR.mkdir(parents=True, exist_ok=True)
