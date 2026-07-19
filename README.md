# SIIA · Valparaíso — Anomalía de precipitación del río atmosférico de julio de 2026

Informe técnico y sistema de análisis reproducible del **Sistema Regional de
Inteligencia Ambiental (SIIA)**: caracterización del evento hidrometeorológico
del 14–18 de julio de 2026 (río atmosférico categoría AR4) y de su expresión
territorial sobre la Región de Valparaíso y sus 2.916 humedales inventariados.

**Productos publicados** (sitio estático, desplegado en Railway):

- **`/`** — informe científico completo, autocontenido (figuras embebidas).
- **`/modelo-3d.html`** — modelo interactivo del relieve regional con la
  anomalía proyectada sobre la superficie.

---

## Resumen del análisis (versión v2, corregida)

El evento se cuantifica comparando el acumulado de precipitación del 1 al 18 de
julio de 2026 contra una climatología homogénea de 21 años (2003–2023, misma
familia de reanálisis que el dato reciente), celda a celda, y trasladando el
resultado al inventario regional de humedales.

Resultados principales tras la corrección observacional:

| Indicador | v1 (sin corregir) | **v2 (corregido y validado)** |
|---|---|---|
| Acumulado regional medio (1–18 jul) | 192 mm | **96 mm** |
| Anomalía regional media | +313 % | **+111 %** |
| Rareza (mediana regional) | z = 3,74 | **percentil empírico 86** |
| Humedales en condición inusual | 1.364 con z > 3 (47 %) | **379 ≥ P90 (13 %); 214 sobre el máximo de 21 años** |

Lectura: un evento **notable, pero no excepcional a escala regional** — más del
doble de una quincena normal — con **récord local del registro de 21 años en su
núcleo** (cordillera de la Costa, eje Marga-Marga–La Dormida).

## Método

La cadena metodológica, documentada por especificación en
[`openspec/`](openspec/), es:

1. **Climatología homogénea** (`clim_valpo.py`, `anomalia_v2.py`): acumulados
   1–18 de julio por año (2003–2023) por celda, del mismo producto que el dato
   reciente (ERA5 seamless); se conserva el registro año a año para habilitar
   percentiles empíricos. La climatología del modelo propio MOD_EToPM-HS
   (ERA5-Land, 10 km) coincide con esta referencia (correlación por celda 0,93)
   y actúa como verificación cruzada.
2. **Ventana reciente** (`fetch_recent.py`): producto operacional casi en
   tiempo real (Open-Meteo), dado el rezago de publicación de ERA5-Land.
3. **Validación observacional** (`auditoria_estaciones.py`): auditoría de las
   32 estaciones DMC/DGAC disponibles — uso o descarte documentado por
   estación — y comparación *like-for-like* del máximo de 24 h sobre la ventana
   exacta de cada estación. Resultado: el producto reciente sobreestima el
   evento en un factor ~2; el desajuste temporal quedó descartado como causa.
4. **Corrección de sesgo** (`correccion_loo.py`): tres candidatas (factor
   regional robusto, corrección espacial de residuos, corrección por altitud)
   evaluadas por validación *leave-one-out*; se aplica la ganadora fuera de
   muestra — corrección espacial de residuos IDW (RMSE 22,0 mm frente a
   54,2 mm sin corrección; sesgo residual −2,0 mm).
5. **Anomalía y rareza v2** (`anomalia_v2.py`, `mapa_v2.py`,
   `mapa_humedales_v2.py`): anomalía porcentual corregida, percentil empírico
   del acumulado (posición de Weibull, 21 años) y puntuación estandarizada como
   indicador complementario; traspaso a humedales por celda.
6. **Motor del evento** (`ivt_evento.py`): transporte integrado de vapor (IVT)
   propio — máximo 819 kg m⁻¹ s⁻¹ el 16 de julio, 82 h sobre umbral AR —
   consistente con la clasificación operacional AR4.
7. **Exposición compuesta recalibrada** (`exposicion_v2.py`): componente
   meteorológica desde el percentil empírico corregido y topográfica desde el
   TWI, sobre el conjunto ≥ P90; la ponderación se somete a análisis de
   sensibilidad (30/70–70/30) y se reporta el núcleo robusto de 202 humedales
   invariante a ella.

Las limitaciones vigentes (densidad de la red de estaciones, transferencia de la
corrección de 24 h al acumulado, resolución de percentiles con 21 años,
pseudo-réplica humedal–celda) están declaradas en el propio informe.

## Estructura del repositorio

```
siia-valparaiso-web/
├── public/            # informe (index.html) y modelo 3D — lo que se sirve
├── data/              # productos del análisis: grillas v1/v2, auditoría de
│                      #   estaciones, métricas LOO, resúmenes JSON, GeoJSON
├── scripts/           # pipeline Python (config.py + run_pipeline.py)
├── sources/           # insumos livianos incluidos (DEM 250 m, AOI RV.shp)
├── openspec/          # especificación y trazabilidad de cambios (OpenSpec)
├── server.js          # servidor estático Node sin dependencias (PORT)
└── CONTRIBUTING.md    # reproducción y extensión del análisis
```

## Reproducibilidad

El pipeline es ejecutable en otro equipo sin editar código: las rutas se
resuelven con las variables de entorno `SIIA_MODEL_DIR`, `SIIA_HUMEDALES_DIR` y
`SIIA_WORK_DIR` (véase `scripts/config.py`), con insumos livianos incluidos en
`sources/` como alternativa.

```bash
pip install -r requirements.txt
python scripts/run_pipeline.py            # cadena completa (v1 + validación + v2)
python scripts/run_pipeline.py --lista    # enumera los pasos
python scripts/run_pipeline.py --sin-dmc  # omite pasos que requieren token DMC
```

Detalle de requisitos, datos externos y extensión a otras regiones o eventos:
[`CONTRIBUTING.md`](CONTRIBUTING.md).

## Publicación

Sitio estático servido por `server.js` (Node ≥ 18, sin dependencias):

```bash
npm start          # http://localhost:3000
```

El despliegue está conectado a Railway: cada *push* a `main` redepliega
automáticamente. Para un despliegue nuevo: **New Project → Deploy from GitHub
repo** en railway.app (Railway detecta Node e inyecta `PORT`).

## Trazabilidad

Los cambios metodológicos se gestionan con [OpenSpec](openspec/): cada cambio
registra problema, decisión, validación y deltas de especificación. El cambio
`auditoria-validacion-anomalia-v2` documenta la auditoría de estaciones, la
selección de la corrección por validación cruzada y el recálculo v2 que
sustituye al titular original.

## Fuentes

ERA5 / ERA5-Land · Open-Meteo (ECMWF-IFS, NCEP-GFS, DWD-ICON, JMA) · Dirección
Meteorológica de Chile y DGAC (Red EMA y reportes METAR SCVM, SCRD, SCEL) ·
Inventario de humedales de la Región de Valparaíso continental · Modelo propio
MOD_EToPM-HS (climatología ERA5-Land 2003–2023) · Escala de ríos atmosféricos
de Ralph et al. (2019).

> La ventana reciente incorpora información operacional corregida con
> observaciones; los valores se revisarán cuando ERA5-Land consolide el
> periodo analizado.
