# Mejoras de usabilidad del mapa interactivo (P1 + P5 + P6)

## Problem

La auditoría visual/funcional del 19-jul-2026 (Playwright/Chromium, escritorio
1280×800, móvil 375×667 y paisaje 667×375) encontró tres problemas
verificables de presentación en `public/mapa-interactivo.html`:

1. **P1 — Superposición móvil**: en 375×667 la leyenda tapa 246×46 px del
   panel y cubre el último enlace de descarga; ambas tarjetas ocupan ~88 % de
   la altura. En paisaje 667×375 el panel mide 448 px en un viewport de 375
   (desborda sin scroll: `.card` no tiene `max-height` ni `overflow`) y el
   solape llega a 165 px.
2. **P5 — Datos crudos visibles**: la ficha muestra el código CIREN
   `NO SUELOS` (261 humedales) como si fuera una serie de suelo; los nombres
   de cuenca del BNA se muestran con sus errores tipográficos
   (`Rio QuiLimari`, `Costeras entre  Maipo y Rapel` con doble espacio, todos
   sin tilde en «Río»).
3. **P6 — Accesibilidad**: los botones de minimizar `#pmin`/`#lmin` tienen
   como único nombre accesible «–»/«+»; los 4 sliders dependen solo de
   `title`; los botones de variable y de fondo no exponen estado
   (`aria-pressed`).

## Proposed Solution

Todo en `public/mapa-interactivo.html` (CSS + JS), sin tocar datos ni servidor.

1. **P1**: `max-height` con `overflow-y:auto` en el cuerpo del panel para que
   nunca desborde el viewport; en pantallas angostas o bajas
   (`max-width: 480px` o `max-height: 520px`) la leyenda arranca minimizada,
   eliminando la superposición inicial.
2. **P5**: diccionario de presentación para las 12 cuencas (solo display: el
   cruce interno de coloreo sigue usando `NOM_CUEN` crudo; los valores `cu`
   de los humedales usan las mismas grafías crudas, verificado en los datos).
   `NO SUELOS` deja de mostrarse como serie: la línea se omite, igual que en
   los 1.729 humedales sin dato de serie.
3. **P6**: `aria-label` en botones de minimizar (con `aria-expanded`
   sincronizado) y en los 4 sliders; `aria-pressed` en los botones de
   variable y de mapa base.

## Decisions

- Los nombres corregidos de cuenca son únicamente ortográficos/tipográficos
  (tildes, espacio duplicado, mayúscula interna); no se renombra ninguna
  cuenca. Si `cuencas.geojson` se regenerara con nombres corregidos, el
  diccionario devolvería el nombre tal cual (fallback identidad), sin romper.
- Las series de suelo legítimas (LO VASQUEZ, POCURO, …) se muestran tal como
  vienen de CIREN: son nombres de series, no códigos; normalizar su
  capitalización/acentuación excede esta propuesta y arriesga inventar
  grafías.
- La leyenda parte minimizada solo en viewports pequeños; en escritorio no
  cambia nada.

## Non-goals

- P2 (tolerancia espacial de clic): propuesta separada — cambia la lógica de
  selección y exige diseñar la resolución de ambigüedad entre humedales
  próximos y el popup de cuencas.
- P3 (compresión/caché en `server.js`), P4 (metadatos y licencia — no se
  publica ninguna licencia del MMA sin verificarla en fuente oficial) y
  P7 (CDN): cambios independientes.
