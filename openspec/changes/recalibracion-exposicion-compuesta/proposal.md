# Recalibración del índice de exposición compuesta (v2)

## Problem

Tras la corrección observacional de la anomalía (change
`auditoria-validacion-anomalia-v2`), el índice de exposición compuesta quedó
como el único producto anclado a la cadena v1: su componente meteorológica era
el z gaussiano sin corregir (z/6), su conjunto de evaluación eran los 1.364
humedales con z > 3 (selección auto-falsada por la auditoría) y su ponderación
meteorológica/topográfica 50/50 era una decisión de diseño sin calibrar ni
análisis de robustez.

## Proposed Solution

Recalcular el índice sobre la cadena v2 (`exposicion_v2.py`):

1. **Componente meteorológica** desde el percentil empírico corregido:
   expo_met = (percentil − 50)/50, acotada a [0, 1]; 0 equivale a una quincena
   normal o seca y el techo alcanzable con 21 años de registro es 0,91 (P95,5).
2. **Componente topográfica** sin cambios: TWI normalizado (percentiles 2–98
   del ráster regional, DEM 250 m) — la topografía no depende de la corrección.
3. **Conjunto de exposición**: los 379 humedales ≥ P90 (los componentes se
   calculan igualmente para los 2.916).
4. **Ponderación por análisis de sensibilidad, no por calibración**: al no
   existir registros sistemáticos de anegamiento en la región para validar
   contra terreno, la ponderación w ∈ {0,3; 0,5; 0,7} se evalúa por
   sensibilidad (correlación de rangos de Spearman entre ponderaciones,
   Jaccard entre conjuntos «alta» ≥ 0,6) y se reporta el **núcleo robusto**:
   humedales clasificados «alta» bajo las tres ponderaciones.

## Decisions

- El umbral «alta» ≥ 0,6 se conserva de v1 por comparabilidad.
- El núcleo robusto (intersección) es el conjunto de prioridad territorial que
  se comunica; la unión y los conteos por ponderación quedan en los datos.
- La calibración contra terreno (registros de anegamiento) queda declarada
  como extensión pendiente, no se simula.
- Dentro de un conjunto ya seleccionado por percentil, el componente
  discriminante es el topográfico; esto se declara explícitamente en el
  informe para evitar sobreinterpretar la ponderación.

## Non-goals

- No se valida el TWI contra eventos de anegamiento observados (sin datos).
- No se modifica la cadena de anomalía v2 ni sus productos.

## Results

- Conjunto ≥ P90: 379 humedales; expo_met media 0,87; expo_topo media 0,55.
- «Alta» por ponderación: w=0,3 → 202; w=0,5 → 308; w=0,7 → 377.
- Sensibilidad: Spearman 0,94–0,99 entre ponderaciones (ordenamiento
  invariante); Jaccard de conjuntos «alta» 0,54–0,82 (el conteo sí depende de
  la ponderación, por eso se reporta el núcleo).
- **Núcleo robusto: 202 humedales** (54 % de la unión), en la práctica los
  ≥ P90 con TWI normalizado ≳ 0,5. Comunas líderes: Casablanca (61),
  Quillota (25), Quilpué (22), Limache (19), Valparaíso (17).
- Informe (sitio e informe local): sección de exposición compuesta reescrita
  con el índice v2, tabla comunal 50/50 sobre el conjunto ≥ P90 y nota de
  sensibilidad; limitación (v) y línea de profundización actualizadas.
- Productos: `humedales_exposicion_v2.csv` (2.916),
  `humedales_p90_exposicion_v2.geojson` (379), `resumen_exposicion_v2.json`.
