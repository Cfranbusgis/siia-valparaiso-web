# Tasks — mapa-interactivo-humedales (retroactiva)

## 1. Implementación (consolidación retroactiva; evidencia: commits)
- [x] 1.1 Página MapLibre con los 2.916 humedales coloreables (4 variables),
      leyenda dinámica y popup-ficha; `build_geojson_web.py`; enlaces en nav e
      informe (`cbe2dcc`).
- [x] 1.2 Fondo Claro (CARTO) / Satélite (Esri); cuencas BNA como polígonos
      coloreados; `build_cuencas_web.py` (`14fe0b9`).
- [x] 1.3 Capas independientes y superponibles (checkboxes); polígonos de
      humedales con ficha; borde regional (`20628e8`).
- [x] 1.4 Solo polígonos («Humedales»); panel y leyenda minimizables
      (`24a9cc2`).
- [x] 1.5 Transparencia por capa (sliders); sección «Datos y metadatos» con
      descargas CSV/GeoJSON (`3555eb0`).
- [x] 1.6 Ficha con tipo de humedal y serie de suelo; nombre de cuenca al
      pasar el cursor (`69cbc31`).

## 2. Transparencia del mapa base (working tree, sin commit)
- [x] 2.1 Slider `#baseop` que aplica `raster-opacity` a los fondos Claro y
      Satélite; etiqueta «Base» → «Mapa base».
- [x] 2.2 Verificado en navegador (Chromium/Playwright, 19-jul-2026, servidor
      local): opacidad 0, 50 y 100 aplican `raster-opacity` 0/0,5/1 en ambos
      fondos (Claro y Satélite).
- [x] 2.3 Verificado: la opacidad se conserva al alternar Claro ↔ Satélite en
      ambos sentidos (slider 50 → sat-op 0,5; slider 0 en Satélite → claro-op
      0 al volver).
- [x] 2.4 Verificado: mover `#baseop` no altera `fill-opacity` de los
      humedales (0,88 sin cambio) y mover el slider temático de Humedales
      (0→100) no altera valor ni opacidad del mapa base.
- [x] 2.5 Verificado en 375×667: panel dentro del viewport, minimizar/restaurar
      panel y leyenda operativos, slider funcional (0/50/100). Observación:
      con panel y leyenda expandidos a la vez, la leyenda se superpone a la
      sección de descargas del panel (ambas tarjetas son minimizables).

## 3. Entrega
- [x] 3.1 Commit + push del cambio pendiente tras la verificación
      (este commit).
