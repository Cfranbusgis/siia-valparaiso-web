# Resumen ejecutivo — Sistema Regional de Inteligencia Ambiental (SIIA)

Estado del **Sistema Regional de Inteligencia Ambiental** aplicado al río
atmosférico de julio de 2026 en Valparaíso: decisiones tomadas, estructura de
trabajo y elementos de mejora.

---

## 1. Visión general

Se construyó, de principio a fin, un **sistema de monitoreo ambiental
reproducible** que caracteriza el río atmosférico que afectó a Chile central el
14–18 de julio de 2026 y su expresión en la Región de Valparaíso y sus humedales.
El producto quedó publicado como sitio web y como repositorio en GitHub, listo
para desplegarse en Railway.

---

## 2. Sistema Regional de Inteligencia Ambiental (Valparaíso)

### 2.1 Objetivo

Detectar y comprender la **anomalía de precipitación** del evento en curso, con
foco en un piloto territorial (Región de Valparaíso), y contrastarla con el
inventario regional de humedales para identificar territorios de mayor exposición.

### 2.2 Resultados principales

| Indicador | Valor |
|---|---|
| Categoría del río atmosférico | **AR4 (extremo)** — escala de Ralph et al. (2019) |
| IVT máximo (estimación propia) | **819 kg m⁻¹ s⁻¹** (16 de julio), flujo NNO (341°), 82 h > 250 |
| Anomalía media regional | **+313 %** (z = 3,74 vs. climatología 2003–2023) |
| Precipitación acumulada 1 jul – 18 jul 09:00 | **192 mm** vs. 48,2 mm normales |
| Máximo diario regional | 106,8 mm (17 de julio); madrugada del 18 (00–09 h) sumó 21,8 mm |
| Máximo observado en 24 h | **120,1 mm** — estación La Dormida (DMC/DGAC, al 17 jul 21:00) |
| Humedales analizados | **2.916** (Región de Valparaíso) |
| Humedales con anomalía fuerte (z > 2) | **2.620 (90 %)**; 1.364 con z > 3 |
| Exposición topográfica combinada alta | **671 (49 %)** de los z > 3 |
| Humedales bajo el nivel de congelación (2.300 m) | **72 %** → recibieron lluvia líquida |

### 2.3 Decisiones clave (con fundamento)

1. **Climatología desde el modelo propio, no de una fuente externa.** Se usó
   `MOD_EToPM-HS` (rásteres diarios ERA5-Land, 10 km, EPSG:32719) para calcular la
   precipitación acumulada 1–18 de julio de cada año 2003–2023, por celda. La
   ventana reciente combina totales diarios (1–17) con el acumulado horario del 18
   hasta las 09:00 (hora local).
   *Motivo:* aprovechar el modelo ya validado de la usuaria y mantener coherencia
   metodológica.
2. **Ventana reciente vía Open-Meteo (tiempo casi real), no ERA5 archivo.**
   *Motivo:* el reanálisis ERA5 tiene rezago (~9 de julio) y **no cubría los días
   del evento (16–18)**; además, el modelo `era5_land` puro devuelve nulos de
   precipitación en Open-Meteo, por lo que se recurrió al producto operacional que
   sí captura el evento.
3. **Solo Valparaíso (no RM).** Se acotó el piloto a la Región de Valparaíso a
   pedido, recortando todas las capas al AOI regional.
4. **Distinguir motor y expresión.** El sistema mide la *expresión* (anomalía de
   precipitación); el *motor* (río atmosférico / IVT) se incorporó después con
   estimación propia, coherente con la clasificación operacional AR4–AR5.
5. **Exposición compuesta 50/50.** Se combinó exposición meteorológica (anomalía
   estandarizada) y topográfica (índice TWI derivado del DEM) en partes iguales.
   *Decisión de diseño explícita y ajustable.*
6. **Enmarque científico, no de dashboard.** Se reescribió el informe con lenguaje
   académico, numeración de figuras, formato numérico en español y advertencias de
   alcance (el evento afectó una franja amplia de Chile central y centro-sur; el
   análisis solo caracteriza su expresión regional).

### 2.4 Validación del evento (tres vías independientes)

- **Observación DMC/DGAC** (principal): API oficial, Red EMA, agua caída 24 h.
  Máximo 120,1 mm (La Dormida); 65–67 mm en Rodelillo y Viña del Mar.
- **Consistencia entre modelos**: ECMWF-IFS, NCEP-GFS, DWD-ICON, JMA — todos
  reproducen el pulso del 16–17 (74–143 mm/día).
- **Reportes METAR** (aeródromos DGAC SCVM, SCRD, SCEL): lluvia intensa, viento
  del norte con rachas de 48 nudos, presión baja.

### 2.5 Análisis derivados

- **Topografía (DEM 250 m):** pendiente, acumulación de flujo D8 (pysheds) e índice
  topográfico de humedad (TWI) → índice de exposición compuesta por humedal.
- **Transporte de vapor (IVT):** cálculo propio `IVT = g⁻¹ ∫ q·V dp` (niveles
  1000–300 hPa) → categoría AR4, coincidente con la clasificación operacional.
- **Nivel de congelación:** 2.300–2.500 m → distinción lluvia (aporte inmediato)
  vs. nieve (aporte diferido) en los humedales.

### 2.6 Entregables

- **Repositorio GitHub**: https://github.com/Cfranbusgis/siia-valparaiso-web
- **Sitio web**: informe científico (`/`) y modelo 3D interactivo
  (`/modelo-3d.html`), listos para Railway.
- **6 figuras** (IVT, serie diaria, anomalía, exposición de humedales, relieve 3D,
  contraste modelo-observación), CSV/GeoJSON de resultados, raster TWI.

### 2.7 Estructura de trabajo (pipeline)

```
IVT / río atmosférico (motor)
        │
ERA5-Land (2003–2023) ─► Climatología regional
Open-Meteo (reciente) ─► Anomalía (% y z)
                              │
Inventario de humedales ─► Integración espacial
Modelo digital de elevación ─► TWI ─► Exposición compuesta
Estaciones DMC/DGAC ─► Contraste observación-modelo
        │
Diagnóstico territorial ─► Informe + sitio web
```

Orden de scripts: `clim_valpo → fetch_recent → analyze_valpo → build_extras →
topo_analysis → modelo_3d_anomalia → dmc_query/extract → ivt_evento →
build_report → assemble_web`.

### 2.8 Reproducibilidad

- `config.py` — rutas por variables de entorno (`SIIA_MODEL_DIR`,
  `SIIA_HUMEDALES_DIR`, `SIIA_WORK_DIR`), sin rutas absolutas en el código.
- `requirements.txt` — dependencias con versiones verificadas.
- `run_pipeline.py` + `Makefile` — ejecución del análisis en orden.
- `sources/` — DEM y AOI incluidos: la topografía y el 3D se reproducen **sin** el
  modelo externo. Probado en limpio con éxito.
- `CONTRIBUTING.md` — cómo reproducir y extender (otra región, variable o evento).

---

## 3. Elementos de mejora

- **Nowcasting:** acoplar el IVT **pronosticado** (no solo el observado) para
  anticipar la exposición antes del evento.
- **Condición ecológica:** integrar NDVI (estado de la vegetación) y LST (contexto
  térmico) de los humedales — insumos ya disponibles en el modelo.
- **Calibración:** ajustar la ponderación de la exposición compuesta y validar las
  zonas de convergencia (TWI alto) contra registros de anegamiento.
- **Consolidación:** reemplazar la ventana reciente por ERA5-Land cuando publique el
  periodo, para homogeneizar la comparación climatológica.

---

## 4. Bitácora de decisiones

| # | Decisión | Fundamento |
|---|---|---|
| D1 | Climatología desde el modelo propio (ERA5-Land 2003–2023) | Coherencia con el trabajo de la usuaria |
| D2 | Ventana reciente vía Open-Meteo, no ERA5 archivo | ERA5 no cubre el evento (rezago); `era5_land` da nulos |
| D3 | Acotar a la Región de Valparaíso | Alcance del piloto |
| D4 | Validación observada con DMC/DGAC vía API oficial | Dato de estación en mm, autoritativo |
| D5 | Cálculo propio del IVT + escala AR | Caracterizar el motor con dato propio |
| D6 | Exposición compuesta 50 % meteo / 50 % topo | Integrar dos dimensiones; ponderación ajustable |
| D7 | Enmarque científico (no dashboard/piloto) | Imagen de sistema operacional reproducible |
| D8 | Repo con servidor Node sin dependencias + Railway | Despliegue simple para terceros |
| D9 | Rutas configurables + insumos livianos incluidos | Reproducibilidad en cualquier equipo |

---

*Documento actualizado el 18 de julio de 2026 (datos hasta las 09:00 hora local).
La ventana reciente incorpora información operacional sujeta a revisión cuando
ERA5-Land consolide el periodo analizado.*
