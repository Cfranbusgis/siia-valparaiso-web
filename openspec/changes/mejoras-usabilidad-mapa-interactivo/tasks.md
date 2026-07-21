# Tasks — mejoras-usabilidad-mapa-interactivo

Evidencia «antes» (auditoría 19-jul-2026, Playwright/Chromium local):
375×667 → solape leyenda/panel 246×46 px, último enlace de descarga tapado,
~88 % del alto ocupado; 667×375 → panel de 448 px desborda el viewport de
375 px, solape 165 px; ficha real mostrando «Serie de suelo: NO SUELOS»;
nombres BNA crudos en leyenda/ficha/hover; a11y: `#pmin`/`#lmin` con nombre
«–», sliders solo con `title`, toggles sin estado.

## 1. P1 — Tarjetas en viewports pequeños
- [x] 1.1 `max-height:calc(100vh - 132px)` + `overflow-y:auto` en `.panel .body`.
- [x] 1.2 Leyenda arranca minimizada vía `matchMedia("(max-width:480px),
      (max-height:520px)")`; escritorio (1280×800) no se ve afectado
      (verificado: leyenda expandida por defecto).
- [x] 1.3 Verificado (Playwright) en 375×667: panel dentro del viewport,
      solape panel/leyenda = 0 px (leyenda colapsada), las 3 descargas
      alcanzables y no tapadas. En 667×375: panel ya no desborda (antes 448 px
      en 375 px de alto; ahora `bottom=361` ≤ 375), leyenda colapsada, 3
      descargas y todos los controles del panel alcanzables mediante scroll
      interno.
- [x] 1.4 Verificado: rueda del mouse sobre el cuerpo del panel no cambia
      centro ni zoom del mapa, en ambos viewports. En 375×667 el contenido
      cabe dentro del `max-height` sin necesitar scroll (no hay overflow que
      probar ahí); en 667×375 sí hay overflow real
      (`scrollHeight=408 > clientHeight=255`) y se confirmó que la rueda
      mueve `scrollTop` del panel (153px) sin mover el mapa.

## 2. P5 — Presentación de datos
- [x] 2.1 Diccionario `CUENCA_LBL`/`cuLbl()` para las 12 cuencas (solo
      display); fallback identidad si un nombre no está en el diccionario.
      Aplicado en leyenda, ficha y popup de hover.
- [x] 2.2 `NO SUELOS` omitido en la ficha (misma rama que "sin dato").
- [x] 2.3 Verificado: la expresión `fill-color` de cuencas sigue usando las
      12 claves crudas de `CUENCAS` (`NOM_CUEN` sin modificar) y 0 features
      cayeron al color de fallback — el coloreo por cuenca es idéntico al de
      antes del cambio.
- [x] 2.4 Verificado con dos fichas reales: una con `se="NO SUELOS"` no
      muestra la línea de serie de suelo; otra con serie legítima (p. ej.
      `COLUNQUEN`) sí la muestra, y su cuenca aparece como «Río Aconcagua» en
      vez de «Rio Aconcagua». Hover de cuenca también corregido
      (`Rio Choapa` → «Río Choapa»).

## 3. P6 — Accesibilidad
- [x] 3.1 `aria-label`/`aria-expanded` en botones de minimizar (con texto
      dinámico «Minimizar/Expandir el panel de controles» y «...la leyenda»);
      `aria-label` en los 4 sliders (base + 3 por capa); `aria-pressed` en
      botones de variable de coloreo y de mapa base.
- [x] 3.2 Verificado con barrido automatizado: 0 controles sin nombre
      accesible (antes: 2, `#pmin`/`#lmin`). `aria-pressed` cambia
      correctamente al elegir variable y al alternar mapa base;
      `aria-expanded` cambia correctamente al minimizar/restaurar panel.

## 4. Orden de capas
- [x] 4.1 "Cuencas (BNA)" reordenada antes que "Región de Valparaíso" en la
      lista de capas y en el z-order del mapa (cuencas-fill/cuencas-line se
      agregan antes que region-line), para que el borde de la región quede
      siempre visible sobre el relleno de cuencas y cada capa más chica no
      quede tapada por una más grande debajo. Verificado con Playwright:
      orden del checkbox, z-order real de las capas, y que ambos toggles
      siguen funcionando tras el reordenamiento.

## 5. Ajustes menores de texto y leyenda
- [x] 5.1 Etiqueta "Colorear humedales por" → "Identificación de humedales".
- [x] 5.2 Leyenda con grupos colapsables independientes (variable activa,
      Cuencas, Humedales urbanos): cada uno con su propio botón "–"/"+",
      estado preservado al cambiar de variable o al redibujar. Verificado
      con Playwright: 3 grupos presentes, colapsar uno no afecta a los
      demás, el estado persiste entre redibujados, se puede reexpandir.

## 6. Entrega
- [x] 6.1 Revisión del diff por Camila; commit + push (aprobado).
- [ ] 6.2 Ajustes de la sección 5: revisión y commit pendiente (no
      pusheado — desde ahora el despliegue a Railway se hace con
      `railway up` manual, ver README/CONTRIBUTING actualizar).
