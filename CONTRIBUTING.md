# Cómo iterar y extender el modelo

Esta guía explica cómo reproducir el análisis y cómo ampliarlo (otra región,
otra variable, otro evento). El sitio web (`public/`) es el producto final; el
pipeline en `scripts/` es lo que lo genera.

## 1. Preparar el entorno

```bash
# Python 3.10+ y Node 18+
pip install -r requirements.txt
```

Dependencias geoespaciales principales: geopandas, rasterio, shapely, pyproj,
pysheds (hidrología), plotly y tifffile (modelo 3D), scipy.

## 2. Configurar las rutas de datos

Las rutas se definen en `scripts/config.py` y se pueden sobrescribir con
variables de entorno, sin tocar el código:

| Variable | Qué apunta | Por defecto |
|---|---|---|
| `SIIA_MODEL_DIR` | Modelo ETo (DEM, rásteres ERA5, AOI) | ruta de la máquina original |
| `SIIA_HUMEDALES_DIR` | Shapefiles de humedales y área de estudio | ídem |
| `SIIA_WORK_DIR` | Carpeta de trabajo y salidas | ídem |

```bash
export SIIA_MODEL_DIR=/datos/MOD_EToPM-HS
export SIIA_WORK_DIR=/salidas/valpo
```

### Qué datos vienen incluidos y cuáles no

- **Incluidos** (`sources/`): el modelo digital de elevación (DEM 250 m) y el área
  de estudio (`RV.shp`). `config.py` los usa automáticamente si el modelo externo
  no está disponible. Con esto, los pasos de **topografía** y **modelo 3D** son
  reproducibles sin nada más.
- **Externos** (por tamaño): los **rásteres ERA5** de la climatología
  (`PM_daily_YYYY.tif`, ~140 MB) y el **inventario completo de humedales**
  (shapefile ~39 MB). Se obtienen del proyecto `MOD_EToPM-HS` y de la carpeta
  `Mapa_Humedales`. Los resultados ya derivados de ellos están en `data/`, de modo
  que se puede iterar sobre el análisis sin reprocesarlos.

## 3. Ejecutar el pipeline

```bash
python scripts/run_pipeline.py            # todo, en orden
python scripts/run_pipeline.py --lista    # ver los pasos
python scripts/run_pipeline.py --sin-dmc  # omitir pasos que requieren token DMC
python scripts/run_pipeline.py --desde topo_analysis   # reanudar desde un paso
```

Orden del pipeline:

1. `clim_valpo.py` — climatología 1-17 jul (ERA5 del modelo) → `clim_valpo.csv/.npz`
2. `fetch_recent.py` — precipitación reciente (Open-Meteo) → `recent_valpo.csv`
3. `analyze_valpo.py` — anomalía por celda + contraste con humedales + mapas
4. `build_extras.py` — mapa modelo-vs-observado + GeoJSON de humedales z>3
5. `topo_analysis.py` — pendiente, acumulación de flujo (D8) y TWI → exposición compuesta
6. `modelo_3d_anomalia.py` — relieve 3D con la anomalía drapeada (HTML + PNG)
7. `dmc_query.py` / `dmc_extract.py` — observaciones DMC/DGAC *(requiere token)*
8. `ivt_evento.py` — transporte de vapor (IVT) y categoría del río atmosférico
9. `build_report.py` — ensambla el informe HTML
10. `assemble_web.py` — construye el sitio en `public/`

### Token DMC/DGAC (opcional)

Los pasos DMC consultan la API de la Dirección Meteorológica de Chile. Requieren
una cuenta y un token gratuito (https://climatologia.meteochile.gob.cl):

```bash
export DMC_USER=tu_correo@ejemplo.cl
export DMC_TOKEN=xxxxxxxxxxxx
```

El token **nunca** debe escribirse en el código ni subirse al repositorio.

## 4. Extender el modelo

- **Otro evento / otras fechas**: ajusta la ventana en `clim_valpo.py`
  (`DAY_MIN`, `DAY_MAX`) y `fetch_recent.py` (`D0`, `D1`), y el rango en
  `ivt_evento.py` (`past_days`). Vuelve a correr el pipeline.
- **Otra región**: cambia el AOI (`SIIA_MODEL_DIR/03_inputs/AOI`) y el inventario
  de humedales (`SIIA_HUMEDALES_DIR`). La grilla se recorta automáticamente al AOI.
- **Otra variable**: la climatología se arma desde las bandas de los rásteres del
  modelo; para otra variable (p. ej. temperatura), adapta el filtro de bandas en
  `clim_valpo.py` y el cálculo de anomalía en `analyze_valpo.py`.
- **Ponderación de la exposición compuesta**: en `topo_analysis.py`, el índice
  combina 50 % anomalía meteorológica + 50 % topográfica (`expo_comp`). Ajusta esos
  pesos según el criterio de priorización.
- **Textos y diseño del informe**: todo el contenido se genera en
  `build_report.py`; edita ahí y vuelve a correr `assemble_web.py`.

## 5. Publicar los cambios

```bash
python scripts/assemble_web.py            # reconstruye public/
git add . && git commit -m "..." && git push
```

Railway redepliega automáticamente con cada `push` a `main`.
