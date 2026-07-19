# Climatología de 30 años (1995-2025) y capas hídricas (ríos, cuencas, acuíferos)

## Problem

La climatología de referencia era de 21 años (2003-2023). Esa ventana, corta y
reciente, (a) no constituye un normal climatológico estándar y (b) excluía
julios húmedos previos (notablemente 2001), lo que producía un sesgo: el evento
2026 aparecía superando "el máximo de los 21 años" en el núcleo, sugiriendo un
récord local que no resiste una referencia más larga. Además, el índice de
inundación usaba cauces sintéticos del DEM y no incorporaba la red hidrográfica
oficial ni el contexto de cuencas y acuíferos.

## Proposed Solution

1. **Baseline de 30 años (1995-2025)** (`clim_1995_2025.py`): se descargan los
   años faltantes (1995-2002 y 2024-2025) desde Open-Meteo Archive
   (era5_seamless) y se fusionan con 2003-2023, formando un normal de 30 años
   que **capta la megasequía de Chile central**. Se recalcula toda la cadena v2
   (anomalía, percentiles, humedales, exposición, susceptibilidad).
2. **Corrección del récord**: con 30 años, **ninguna celda supera el máximo**
   del registro (julio de 2001 fue más lluvioso). Se corrige el titular y las
   secciones: el evento es muy inusual (P88, +145 %) pero **no un récord**.
3. **Red hidrográfica oficial** (`dist_rios.py`): distancia a los ríos mapeados
   (DGA, con orden de Strahler) reemplaza a los cauces sintéticos del DEM como
   predictor de inundación (57 % de humedales a ≤150 m de un cauce).
4. **Contexto de cuencas y acuíferos**: cada humedal recibe su cuenca (BNA) y su
   sector acuífero (SHAC). El 68 % pertenece a la cuenca del río Aconcagua y el
   100 % se ubica sobre sectores acuíferos, subrayando el vínculo con el agua
   subterránea.

## Decisions

- El porcentaje de anomalía (+145 %) sube respecto de la ventana de 21 años
  (+121 %) porque el normal de 30 años es menor (43,0 vs 47,6 mm): incluye los
  años de megasequía 2024-2025 (0,1 y 1,3 mm). Se declara ese contexto.
- El acuífero (SHAC) no discrimina (100 % de cobertura); se usa como contexto,
  no como componente de susceptibilidad.
- Se conserva el respaldo de la climatología de 21 años (`clim_om_years_2003_
  2023.npz`) para trazabilidad de la comparación.

## Non-goals

- No se reponderan los componentes de la susceptibilidad (la red oficial
  reemplaza al cauce sintético, misma estructura).

## Results

- Baseline 1995-2025: normal 43,0 mm; anomalía +145 %; percentil mediano P88;
  **0 celdas y 0 humedales sobre el máximo** del registro (récord descartado).
- Núcleo robusto de exposición: 211 humedales. Prioridad de inundación: 395 de
  468 ≥ P90 en clase Alta/Muy Alta.
- Ríos oficiales, cuencas y acuíferos incorporados; informe corregido (récord),
  Figuras 3, 4 y 7 regeneradas; contexto de megasequía documentado.
