# Integración de la auditoría multicomité y ventana de datos al 19-jul

## Problem

Una auditoría multicomité externa (constructiva, priorizada) revisó la versión
v2 del informe. Clasificó la solidez científica en nivel 4/5 y detectó, entre
otros, cinco hallazgos accionables sobre el propio texto/datos (no solo sobre
reproducibilidad, que depende de publicar el pipeline): (1) la fuente del
inventario de humedales debía explicitarse con su tipología; (2) el porcentaje
de humedales bajo el nivel de congelación carecía de documentación
metodológica; (3) faltaba la definición de humedal (Ramsar) y literatura de
Chile central; (4) el índice compuesto debía declararse no calibrado con su
análisis de sensibilidad; (5) faltaba declarar licencia y naturaleza operativa
del sistema. En paralelo, el usuario pidió extender la ventana de datos hasta
las 03:00 del 19 de julio y aclarar que el sistema corre localmente, sin
ingesta en vivo.

## Proposed Solution

Aplicar las mejoras **necesarias y verificables** (no un rediseño), y dejar
documentadas las demás como hoja de ruta:

1. **Ventana de datos al 19-jul 03:00.** `fetch_recent.py` pasa a 1&ndash;18
   completos + 19 parcial (00&ndash;03h); `extend_clim_19.py` extiende la
   climatología homogénea a 1&ndash;19 por año (era5_seamless) para no
   reintroducir el desajuste de ventanas; `patch_grid_recent.py` propaga el
   nuevo reciente y se re-corre la cadena v2 completa.
2. **Corrección del % bajo la cota de nieve.** Recalculado desde el DEM
   AW3D30 (30 m) por punto representativo: 50,3 % (no ~85 %), con nota
   metodológica. El inventario está dominado por vegas/bofedales altoandinos.
3. **Fuente y tipología del inventario.** Se mantiene la procedencia ya
   resuelta (capa MMA vía IDE Chile / geoportal 34955, 2013), se añade la
   definición Ramsar, la tipología de seis tipos (Figueroa et al., 2014) y la
   precisión de que el atributo de la capa es la relación con el límite urbano,
   no la clasificación hidro-geomorfológica.
4. **Justificación cuantitativa del DEM 30 m.** 81 % de los humedales < 5 ha
   (mediana 1,2 ha), por lo que la grilla de 250 m era inadecuada.
5. **Naturaleza del sistema, licencia y alcances de mejora.** Se declara que el
   pipeline corre local/manual (sin ingesta en vivo), la licencia (CC BY 4.0 /
   MIT) y una sección «Alcances de mejora» con el backlog priorizado de la
   auditoría (reproducibilidad FAIR, densidad de red, calibración de terreno,
   incertidumbre explícita, etiquetado visual, factores hidrológicos, operación
   continua).

## Decisions

- **No** se adopta la etiqueta «MMA 2015» de la auditoría: la capa efectivamente
  usada es la de 2013 (geoportal 34955), verificada con el usuario. Se conserva.
- Se aplican solo las recomendaciones necesarias y verificables con los datos
  disponibles; el resto se documenta como trabajo futuro, no se simula.
- La ventana reciente (día 19 parcial 00&ndash;03h) frente a la climatología
  (día 19 completo) mantiene la anomalía levemente conservadora, igual que antes.

## Non-goals

- No se contenedoriza ni se publica el pipeline completo (reproducibilidad plena
  queda como pendiente priorizado).
- No se cruza la tipología hidro-geomorfológica de seis tipos (no es atributo de
  la capa; requiere fuente adicional).
- No se calibra el índice compuesto contra registros de anegamiento (sin datos).

## Results

- Ventana 1&ndash;19 jul 03:00: reciente 205 mm (día 19 sin lluvia; el evento
  terminó). Anomalía +111 % &rarr; **+121 %**; acumulado corregido 96 &rarr;
  **102 mm**; climatología 47,0 &rarr; 47,6 mm.
- Humedales &ge; P90: 379/13 % &rarr; **468/16 %**; sobre el máximo de 21 años
  214 &rarr; **280**; núcleo robusto 172 &rarr; **218**.
- % bajo 2.300 m corregido: ~85 % &rarr; **50,3 %** (verificado con ambos DEM).
- Figuras 2, 3, 4 y 5 regeneradas; tablas comunales (rareza y compuesta)
  actualizadas; referencias Ramsar (2013), Figueroa et al. (2014) y Wilkinson
  et al. (2016) incorporadas; sección «Alcances de mejora» y licencia añadidas.
