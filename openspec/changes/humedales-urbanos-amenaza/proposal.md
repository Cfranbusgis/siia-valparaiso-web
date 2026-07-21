# Propuesta: amenaza y susceptibilidad de inundación en los 21 humedales urbanos de Valparaíso

## Contexto

El SIIA ya calculó amenaza de inundación/saturación (`amenaza_inundacion`,
`clase_amenaza`, `susc_inundacion`) para los 2.916 humedales del inventario
base de la Región de Valparaíso (`scripts/susceptibilidad.py`), a partir de
exposición meteorológica (percentil empírico del evento, `exposicion_v2.py`),
TWI, concavidad/depresiones, retención edáfica y cercanía a cauces oficiales.

Esta propuesta aplica esa misma metodología — sin recalibrar nada — a los
**21 humedales urbanos reconocidos (Ley 21.202) de la Región de Valparaíso**
(`data/humedales_urbanos_geom.geojson` + `data/humedales_urbanos_valpo.csv`,
ver `humedales-urbanos-mma`), cruzándolos además con comuna y con la estación
DMC/DGAC observada más cercana. **Alcance explícitamente limitado a
Valparaíso** — no se toca el inventario nacional de humedales urbanos
(proyecto aparte, sin versionar, en `Inventario_Humedales_Urbanos_Chile`).

## Metodología

**Con solape con el inventario base 2013** (`public/humedales_poly.geojson`,
16 de 21): los valores de `pctl_empirico`, `amenaza_inundacion`,
`susc_inundacion` y `expo_suelo` se heredan como **promedio ponderado por
área de intersección** de todos los polígonos base que solapan (mismo cálculo
de `pct2013` que `build_humedales_urbanos_web.py`). `clase_amenaza` se
reclasifica sobre ese promedio usando los **mismos quintiles de
`amenaza_inundacion` de la población completa de 2.916** — nunca se
re-quintiliza sobre n=21, para mantener comparabilidad con el resto del
informe.

**Sin solape** (5 de 21: Kan Kan #170, Tranque Cerro La Huinca #44, El Bato
#1237, Entre Cerros #177, Canal Waddington #47 — 4 de estos 5 ya estaban
documentados como "sin ningún solape" en `humedales-urbanos-mma`; Tranque
Cerro La Huinca se suma aquí porque ese documento cubría solo los 18 del
mapa web, que excluyen los artificiales): se muestrea directamente sobre el
punto representativo del polígono, replicando cada componente exactamente
como en el script original:
- `expo_met`: percentil empírico de la celda de `anomaly_grid_valpo_v2.csv`
  que contiene el punto (mismo sjoin + respaldo `sjoin_nearest` de
  `anomalia_v2.py`).
- TWI: `twi_valpo_30m.tif`, normalización percentil 2–98 regional
  (`exposicion_v2.py`), con respaldo de vecindad hasta 8 px si el punto cae
  en nodata.
- Concavidad/depresión: `concavidad_valpo_30m.tif` + `depresion_valpo_30m.tif`,
  misma normalización que `concavidad_30m.py`.
- Suelo: `suelos_ciren_rv_32719.gpkg` (unión espacial) con relleno FAO/HWSD2
  (`suelo_retencion.py` + `suelo_fao_fill.py`) cuando no hay serie CIREN en
  el punto.
- Cercanía a río oficial: `rios_rv_32719.gpkg`, `sjoin_nearest`
  (`dist_rios.py`).

**Estación DMC/DGAC más cercana**: para los 21, distancia Haversine contra las
33 estaciones de `dmc_observado_valpo.csv`, reportando el acumulado 24h
observado de la más próxima (no es un valor "del humedal", es el dato de la
estación más representativa de su entorno).

**Comuna**: ya disponible como atributo del CSV de origen (verificado, no
recalculado).

## Nivel de confianza por registro

Se agrega una columna `confianza`, explícita por fila:
- **alta**: solape ≥ 80 % con el inventario base (2 casos).
- **media (solape parcial)**: solape 30–80 % (11 casos) — los valores
  heredados representan bien la porción solapada, pero no necesariamente el
  100 % del polígono si el resto no coincide con ningún polígono base.
- **media (muestreo directo)**: sin solape, muestreo directo de la misma
  metodología en un único punto representativo, sin promediado espacial
  (5 casos).
- **baja (solape < 30 %, revisar manualmente)**: 3 casos — incluye #162
  Estero Reñaca, ya marcado como re-auditoría pendiente en
  `humedales-urbanos-mma` (tarea 5.4) por una discrepancia de superficie no
  resuelta; y #163 Laguna El Criquet y Quebrada Honda, el caso mixto ya
  documentado (polígono único combinado natural+artificial, área menor a la
  declarada por esa razón conocida).

## Hallazgo de datos: bug de codificación en `dmc_observado_valpo.csv`

La columna `estacion` de `dmc_observado_valpo.csv` está **doblemente
codificada en UTF-8** (ej. bytes que decodifican a `"AgrÃ­cola"` en vez de
`"Agrícola"` — confirmado a nivel de bytes, no es un artefacto de terminal).
Afecta solo el nombre legible de la estación, no sus coordenadas ni
`agua24h_mm`. Se repara únicamente en la salida de este script
(`_fix_mojibake` en `humedales_urbanos_amenaza.py`); **no se modifica el
archivo fuente** `dmc_observado_valpo.csv`, porque ya alimenta otras salidas
del informe y una corrección retroactiva ahí queda fuera del alcance de esta
propuesta. Pendiente: decidir si vale la pena corregir `dmc_extract.py` en el
origen.

## Resultados (resumen)

- 21 humedales urbanos, `amenaza_inundacion` media 0,375 (vs. 0,318 en la
  población completa de 2.916 — los humedales urbanos, en conjunto, están
  algo más expuestos que el promedio regional).
- Clases: 9 Muy Alta, 7 Alta, 1 Moderada, 2 Baja, 2 Muy Baja.
- Comunas con más humedales urbanos en la muestra: Limache (3), Viña del Mar
  (3), Puchuncaví (2), Quintero (2), Papudo (2).

## Ampliación posterior: integración en el mapa y en el informe

Tras la primera entrega (solo `data/humedales_urbanos_amenaza.csv`), Camila
pidió activar en el mapa interactivo los mismos íconos de variable
(Percentil/Amenaza/Susceptibilidad/Suelo) para la capa de humedales urbanos,
que hasta entonces se coloreaba con un esquema fijo sin_solape/con_solape
ajeno a estos resultados. Esto amplió el alcance original (ver tareas 5 y 6):

- `scripts/build_humedales_urbanos_web.py` ahora agrega `p/cl/s/su/cf` a
  `public/humedales_urbanos.geojson` (18 registros, filtro `incluir_capa`
  ahora explícito) y `mapa-interactivo.html` colorea `hurb-fill` con la misma
  expresión que la capa base; el sin_solape/con_solape pasó a ser el color
  del borde, no del relleno.
- De paso se pidió que los grupos de la leyenda mostraran solo un nombre
  corto al colapsarse (el grupo "variable" mostraba la descripción larga
  como título) — corregido en el mismo cambio, aunque el mecanismo de
  colapso en sí pertenece a `mejoras-usabilidad-mapa-interactivo`.
- Se agregó una sección nueva al informe (`build_report.py`), "Humedales
  urbanos reconocidos (Ley 21.202)", con el mismo formato de tarjetas +
  ranking de comunas que ya existía para el inventario de 2.916, pero para
  los 21 humedales urbanos declarados.

Esta ampliación **sí** modifica `public/humedales_urbanos.geojson` y
`public/index.html` — a diferencia de lo indicado originalmente más abajo,
que quedó desactualizado por este cambio de alcance pedido explícitamente.

## Fuera de alcance

- Inventario nacional de humedales urbanos (proyecto aparte).
- Resolver la discrepancia de superficie de #162 Estero Reñaca (ya es tarea
  pendiente en `humedales-urbanos-mma`).
- Corregir el bug de codificación en el archivo fuente `dmc_observado_valpo.csv`.
