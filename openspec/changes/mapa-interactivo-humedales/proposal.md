# Mapa interactivo de humedales (MapLibre)

> Propuesta **retroactiva**: consolida una línea de trabajo ya implementada en
> seis commits del 19-jul-2026 (`cbe2dcc` → `69cbc31`) que se desarrolló sin
> propuesta OpenSpec, e incorpora una última mejora aún sin commit (slider de
> transparencia del mapa base). La evidencia citada proviene de los mensajes de
> commit y del código de `public/mapa-interactivo.html`.

## Problem

El informe presenta figuras estáticas: los 2.916 humedales del inventario y sus
atributos derivados (percentil del acumulado, clase de amenaza de inundación,
susceptibilidad, retención de suelo, cuenca) no podían explorarse
individualmente, ni superponerse con el contexto (cuencas BNA, límite regional,
imagen satelital), ni descargarse desde el sitio.

## Proposed Solution

Página estática `public/mapa-interactivo.html`, autónoma y enlazada en la
navegación del sitio y en el cuerpo del informe.

### Arquitectura

- **MapLibre GL JS 4.7.1** desde CDN (unpkg); open source. Reutiliza el
  concepto de `dgeoiacl/urban-wetlandMS-cl`, no su código (commit `cbe2dcc`).
- **Sin backend adicional**: el mismo servidor Node estático (`server.js`)
  sirve la página y los datos. Sin paso de build para el frontend.
- **Datos como GeoJSON/CSV estáticos** en `public/`, generados por scripts
  Python: `build_geojson_web.py` (humedales) y `build_cuencas_web.py`
  (cuencas BNA simplificadas, 73 KB). Archivos: `humedales_poly.geojson`
  (polígonos con atributos), `cuencas.geojson`, `region_rv.geojson` (borde
  regional), `humedales_tabla.csv` (2.916 filas).
- **Fondos raster por tiles remotos**: CARTO light («Claro») y Esri World
  Imagery («Satélite»).

### Capas (superponibles, con checkbox y slider de transparencia cada una)

1. **Región de Valparaíso** — borde político-administrativo (visible por defecto).
2. **Cuencas (BNA)** — 12 cuencas como polígonos coloreados con borde; el
   nombre aparece al pasar el cursor (`69cbc31`).
3. **Humedales** — polígonos del inventario (visible por defecto), coloreados
   por la variable seleccionada.

### Controles

- **Variable de coloreo** (4 botones): Percentil empírico (1995–2025), Amenaza
  de inundación (5 clases), Susceptibilidad, Retención de suelo
  (CIREN + HWSD2). Leyenda dinámica que agrega las cuencas al activar esa capa.
- **Ficha por humedal** (popup al clic): nombre, comuna, cuenca, tipo de
  humedal, percentil, acumulado (mm), amenaza, susceptibilidad, retención y
  serie de suelo (`69cbc31`).
- **Mapa base**: alternador Claro/Satélite (`14fe0b9`) y — **mejora pendiente
  de commit** — slider de transparencia (`#baseop`) que aplica
  `raster-opacity` a ambos fondos a la vez, de modo que la opacidad elegida se
  conserva al alternar entre ellos.
- **Panel de controles y leyenda minimizables** (tarjetas flotantes, `24a9cc2`).
- Controles de navegación y escala métrica (esquinas del mapa).

### Descargas («Datos y metadatos», `3555eb0`)

Tabla CSV de los 2.916 humedales, humedales en GeoJSON y cuencas en GeoJSON,
con descarga directa desde el panel.

## Decisions

- **Solo polígonos**: la capa de puntos inicial se eliminó; queda una única
  capa «Humedales» de polígonos — un objeto por humedal y una sola ficha
  (`24a9cc2`).
- **«Cuenca» dejó de ser variable de coloreo** y pasó a ser capa propia de
  polígonos coloreados con hover; los humedales mantienen sus 4 variables
  temáticas (`14fe0b9`, `20628e8`).
- **Transparencia como control de lectura**: primero por capa (`3555eb0`) y
  ahora también del mapa base (cambio pendiente). El slider del fondo permite
  reducir el peso visual del mapa base — en particular el satelital — para
  facilitar la lectura de los polígonos de humedales y de las capas temáticas.
- **Datos simplificados y servidos como archivos**: geometrías simplificadas a
  tamaños aptos para la web (p. ej. cuencas 73 KB) en lugar de tiles
  vectoriales o un servidor de mapas.

## Non-goals

- Tiles vectoriales propios o servidor de mapas dedicado.
- Edición de datos, autenticación o estado por usuario (solo lectura/descarga).
- Reemplazar las figuras estáticas del informe (el mapa las complementa).

## Estado

- **Implementado y committeado** (y en `origin/main`): todo lo anterior salvo
  el slider del mapa base — commits `cbe2dcc`, `14fe0b9`, `20628e8`, `24a9cc2`,
  `3555eb0`, `69cbc31`.
- **Pendiente de commit**: slider de transparencia del mapa base y etiqueta
  «Mapa base» (+4/−1 líneas en `public/mapa-interactivo.html`); su verificación
  en navegador se registra en `tasks.md`.
