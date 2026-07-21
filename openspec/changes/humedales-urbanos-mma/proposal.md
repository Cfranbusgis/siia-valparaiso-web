# Capa de humedales urbanos reconocidos (Ley 21.202) — Valparaíso

## Problem

El inventario base del proyecto (2.916 humedales, capa MMA vía geoportal.cl,
2013) no refleja los humedales reconocidos legalmente como **Humedal Urbano**
bajo la Ley 21.202 con posterioridad a esa fecha, un dato relevante como
insumo de tesis (incorporación de nuevos humedales urbanos, excluyendo
artificiales).

## Proposed Solution

`scripts/humedales_urbanos_mma.py` extrae del Portal de Humedales del MMA
(`sistemahumedales.mma.gob.cl/HumedalesUrbanos`) las solicitudes de la Región
de Valparaíso con estado **"Humedal Urbano Reconocido"**, vía dos endpoints
servidos por el servidor (verificado con `curl`, sin JavaScript):
`ListarSolicitudesPublicas` (listado) y `DetailsPublico/{id}` (ficha con
comuna, provincia, región, superficie y clasificación).

Resultado: **21 humedales urbanos reconocidos** en la región (de 47
solicitudes totales, todos los demás estados en trámite/archivados).

### Clasificación natural / artificial

El campo "Clasificación del humedal acorde al inventario nacional de
humedales" es **texto libre**, no un vocabulario controlado — cada municipio
lo redactó de forma distinta. Regla aplicada (decidida con Camila,
20-jul-2026, tras revisar los 21 casos reales uno por uno):

| Caso | Regla | Resultado |
|---|---|---|
| Campo vacío o "No señala" (3 casos) | `tipo_final = "sin dato"` | **incluido**, marcado explícitamente |
| Menciona "artificial" y "natural" a la vez (1 caso: #163, dos polígonos en un mismo trámite) | `tipo_final = "mixto (excluido)"` | **excluido** — sin geometría no hay forma confiable de aislar solo la parte natural |
| Menciona "artificial" sin "natural" (2 casos) | `tipo_final = "artificial"` | **excluido** |
| Cualquier otro texto no vacío (15 casos, p. ej. "ribereño", "palustre", "estuarino", "continental") | `tipo_final = "natural"` | **incluido** — estos términos son categorías exclusivamente naturales en la nomenclatura CONAMA 2006/MMA; lo artificial se declara explícito con tranque/embalse/estanque/canal |

Resultado final: **18 de 21 incluidos** en la capa (15 natural + 3 sin dato),
3 excluidos (2 artificiales + 1 mixto).

### Geometría real (corrección: sí existe, no está en un servicio, está en el expediente)

La evaluación inicial de esta propuesta asumió que no había geometría
descargable (el mapa de cada ficha es solo un widget ArcGIS de
visualización). Eso era incorrecto: cada expediente público trae shapefiles
y/o KMZ oficiales como documentos adjuntos, descargables sin autenticación
vía `POST /HumedalesUrbanos/DescargarExpediente` (mecanismo encontrado
leyendo `TablasDocumentosExpediente.js`). `scripts/humedales_urbanos_geometria.py`
descarga, extrae (7-Zip para `.rar`/`.zip` anidados) y reproyecta a WGS84 el
polígono de cada uno de los 18 humedales.

**Selección de versión**: cada expediente trae múltiples revisiones de la
cartografía (borradores + versión final, a veces con subproductos de
análisis GIS como capas "Diferencia" o "vértices"). La selección se validó
contrastando el área calculada del polígono contra `superficie_ha` (el campo
"superficie total... **originales**..." del formulario — es decir, la
superficie *solicitada*, no necesariamente la final):

- **11 humedales**: archivo único sin ambigüedad, área calculada coincide con
  la superficie original solicitada (ratio 0,95–1,16) — confianza alta.
- **6 humedales** (164, 169, 170, 177, 1222, 1237): el trámite incluyó una
  corrección de límite ("rectificada"); el área no coincide con la
  superficie *original* solicitada, lo cual es el resultado esperado de la
  rectificación, no un error de selección. Para **El Bato (#1237)** se
  detectó y corrigió un bug real: la extracción automática había tomado
  `Diferencia.shp` (un subproducto de análisis GIS) en vez de
  `Polígono_El_Bato_VF.shp`; el archivo correcto se confirmó porque su área
  coincide exactamente (ratio 1,00) con la superficie declarada.
- **1 humedal (#162, Estero Reñaca)**: **sin resolver**. Los dos candidatos
  de polígono disponibles en el expediente (`..._ART8.shp`, 15,1 ha, y
  `Final CMS/..._VF.shp`, 16,9 ha) están ambos muy por debajo de las 233,4 ha
  declaradas como superficie original solicitada. No hay, en los documentos
  públicos revisados, ningún archivo adicional que reconcilie esa diferencia.
  Se usa el de la carpeta "Final CMS" como mejor esfuerzo, marcado
  explícitamente de **baja confianza** — **pendiente de re-auditoría**
  (ver tasks.md tarea 5.4: requiere revisar la Resolución Exenta 5196 que
  reconoce el humedal, u otra fuente oficial, antes de usar este polígono en
  cualquier análisis o figura de la tesis).

### Cruce espacial con el inventario 2013 (resuelto)

`scripts/build_humedales_urbanos_web.py` intersecta cada humedal urbano
(polígonos disueltos por `id_solicitud`) contra los 2.916 polígonos de
`public/humedales_poly.geojson`, y calcula el % del área del humedal urbano
cubierta por polígonos 2013 preexistentes (`pct2013`).

No se colapsó esto en un único umbral binario de "nuevo" — el resultado no
es binario:

- **4 humedales sin ningún solape** (Entre Cerros, Kan Kan, Canal
  Waddington, El Bato): el polígono 2013 más cercano está a 680 m–1,6 km.
  Estos sí son "nuevos" en el sentido estricto: no hay nada del inventario
  2013 en esa ubicación.
- **5 con solape muy alto (79–94%)** (Mayaca, El Totoral, Mantagua, El
  Litre, Agua Salada): es el mismo humedal ya mapeado en 2013, solo
  redigitalizado con un límite ligeramente distinto.
- **9 en zona intermedia (21–68%)**: el inventario 2013 tenía el área
  fragmentada en varios polígonos pequeños (hasta 12, en Los Maitenes-
  Campiche) que el trámite de humedal urbano unificó en un límite mayor. No
  es "nuevo" en el sentido de ubicación desconocida, sino consolidación de
  algo ya presente — el % exacto y los nombres 2013 relacionados quedan
  expuestos en el dato, no resumidos en una etiqueta.

Se expone `pct2013` (variable continua) y `clase` (`sin_solape`/`con_solape`,
solo para el color del mapa) en vez de forzar "nuevo sí/no" — así el criterio
de "nuevo" queda resuelto con evidencia trazable en vez de con un corte
arbitrario que Camila no había pedido.

### Nueva capa en el mapa interactivo

`public/mapa-interactivo.html`: capa "Humedales urbanos (Ley 21.202)"
(fuente `/humedales_urbanos.geojson`, 18 humedales), superponible e
independiente de la capa de 2.916 humedales, visible por defecto, con:
- Color por `clase` (sin/con solape), leyenda propia.
- Ficha por humedal: nombre, comuna, superficie, clasificación
  natural/sin dato, % de solape con nombres 2013 relacionados, y advertencia
  visible en rojo para geometría de confianza baja (hoy solo #162).
- Descarga directa del GeoJSON desde "Datos y metadatos".
- **Bug encontrado y corregido durante la prueba**: la fuente GeoJSON se
  simplifica por defecto según el zoom; a zoom inicial (7.4) eso borraba por
  completo los polígonos más chicos (<2 ha) — exactamente 4 de los 4
  humedales "sin solape", el hallazgo más importante de la capa. Corregido
  con `tolerance:0` en la fuente (sin costo de rendimiento: son 18
  features).

## Decisions

- Solo estado "Humedal Urbano Reconocido" (categoría legal consolidada por
  decreto); se excluyen solicitudes en trámite o archivadas.
- La regla de clasificación natural/artificial es case-by-case documentada,
  no una heurística genérica de confianza ciega — los 3 casos "sin dato" y el
  caso mixto quedan visibles en el CSV completo para auditoría.
- Nueva dependencia: `beautifulsoup4==4.12.3` (parseo de HTML del portal
  MMA), agregada a `requirements.txt`.

## Non-goals

- No se intenta scraping del dashboard Power BI complementario (API interna
  frágil, no documentada); se descartó como fuente de extracción y quedó solo
  como referencia de verificación visual cruzada.
- No se resuelve la discrepancia de superficie del humedal #162 (Estero
  Reñaca) dentro de esta propuesta — queda como tarea de re-auditoría
  explícita (tasks.md 5.4).

## Results

- `data/humedales_urbanos_valpo.csv` — 21 filas (todas las "Reconocido"),
  con `tipo_final` e `incluir_capa`.
- `data/humedales_urbanos_valpo_natural.csv` — 18 filas (`incluir_capa=True`).
- `data/humedales_urbanos_geom.geojson` — 22 geometrías (18 humedales, 4 con
  más de un polígono) en WGS84, con `confianza_geometria` por registro.
- `public/humedales_urbanos.geojson` — capa web con el cruce espacial
  (`pct2013`, `n2013`, `nom2013`, `clase`) lista para el mapa.
- `scripts/humedales_urbanos_mma.py`, `scripts/humedales_urbanos_geometria.py`
  y `scripts/build_humedales_urbanos_web.py` — reproducibles, con toda la
  regla de clasificación, selección de archivo y cruce espacial documentada
  en el docstring.
- Mapa interactivo (`public/mapa-interactivo.html`) con la nueva capa,
  validado con Playwright: toggle, opacidad independiente, leyenda, ficha
  (incl. advertencia de confianza baja), descarga, y layout móvil intacto.
