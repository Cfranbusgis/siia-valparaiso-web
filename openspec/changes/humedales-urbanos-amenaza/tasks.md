# Tasks — humedales-urbanos-amenaza

## 1. Script y ejecución
- [x] 1.1 `scripts/humedales_urbanos_amenaza.py`: replica
      `susceptibilidad.py`/`exposicion_v2.py`/`concavidad_30m.py`/
      `suelo_retencion.py`/`suelo_fao_fill.py`/`dist_rios.py` sobre los 21
      humedales urbanos, usando los rasters/gpkg/csv intermedios ya
      calculados (`config.WORK_DIR`), sin recalcular el DEM ni descargar
      nada nuevo.
- [x] 1.2 Corrida completa sin errores: 16 con solape (herencia ponderada
      por área) + 5 con muestreo directo (Kan Kan, Tranque Cerro La Huinca,
      El Bato, Entre Cerros, Canal Waddington). Bug real encontrado y
      corregido en el camino: `comp.mean(...).to_numpy()` devolvía un array
      de solo lectura al asignar el relleno FAO — se agregó `.copy()`.
- [x] 1.3 Verificado: `clase_amenaza` usa los mismos quintiles
      (`[0.229, 0.286, 0.331, 0.398]`) de `amenaza_inundacion` sobre los
      2.916 del inventario base, no recalculados sobre n=21 — confirmado
      leyendo `humedales_susceptibilidad.csv` directamente en el script.
- [x] 1.4 Verificado por consistencia cruzada: los 4 "sin ningún solape" ya
      documentados en `humedales-urbanos-mma` (Kan Kan, Entre Cerros, Canal
      Waddington, y en ese documento también El Bato antes de tener
      geometría propia) coinciden exactamente con el resultado de este
      script; el 5º caso (Tranque Cerro La Huinca) es nuevo porque ese
      documento cubría solo los 18 del mapa web (excluye artificiales).

## 2. Validación de resultados
- [x] 2.1 El Bato (#1237): área calculada 2,38 ha == superficie declarada
      2,38 ha (ratio 1,00) — consistente con la corrección de archivo ya
      documentada en `humedales-urbanos-mma` (bug `Diferencia.shp`).
- [x] 2.2 Casos de confianza baja (#162 Estero Reñaca, #163 Laguna El
      Criquet y Quebrada Honda) quedan marcados `confianza=baja` en la
      salida, consistente con las re-auditorías ya pendientes en
      `humedales-urbanos-mma` (tareas 5.4 y 9.2) — no se intenta resolver
      aquí, solo se hereda la advertencia.
- [x] 2.3 Bug de codificación real encontrado en `dmc_observado_valpo.csv`
      (columna `estacion` con doble UTF-8, ej. "AgrÃ­cola"/"Agrícola") —
      confirmado a nivel de bytes (no artefacto de terminal), reparado solo
      en la salida de este script, archivo fuente NO modificado (fuera de
      alcance, alimenta otras salidas del informe).
- [ ] 2.4 Pendiente: revisión manual de #162 Estero Reñaca (ya era tarea
      abierta) y decisión sobre si corregir `dmc_extract.py` en el origen.

## 3. Salidas
- [x] 3.1 `data/humedales_urbanos_amenaza.csv` (21 filas: id, nombre,
      comuna, tipo, área, % solape, fuente, todos los componentes,
      confianza, estación DMC más cercana + su acumulado 24h observado).
- [x] 3.2 `data/humedales_urbanos_amenaza_resumen.json` (conteos por clase,
      por confianza, por comuna, medias, quintiles usados).

## 4. Entrega
- [ ] 4.1 Revisión por Camila.
- [ ] 4.2 Commit/push — pendiente, no realizado todavía (junto con los
      cambios ya comprometidos localmente de la sección 5 de
      `mejoras-usabilidad-mapa-interactivo`, aún sin `railway up`).

## 5. Integración en el mapa interactivo (activar los mismos íconos de
      variable para humedales urbanos)
- [x] 5.1 `scripts/build_humedales_urbanos_web.py`: ahora filtra
      explícitamente por `incluir_capa==True` (antes el filtro a 18 era
      implícito porque el script no se había vuelto a correr desde que
      `data/humedales_urbanos_geom.geojson` pasó a 21 — al día de hoy
      correrlo sin el filtro habría producido 21, rompiendo el criterio ya
      aprobado); agrega columnas `p/cl/s/su/cf` desde
      `humedales_urbanos_amenaza.csv`. Regenerado
      `public/humedales_urbanos.geojson`: 18 humedales, distribución de
      `cl` = 9 Muy Alta, 5 Alta, 2 Muy Baja, 2 Baja (dentro del subconjunto
      de 18; los 3 excluidos — 2 artificiales + el mixto — no entran a esta
      capa web, ver justificación ya documentada en `humedales-urbanos-mma`).
- [x] 5.2 `public/mapa-interactivo.html`: `hurb-fill` ahora usa
      `colorExpr(cvar)` (la misma expresión de color que `hpoly`) en vez de
      un esquema fijo sin_solape/con_solape; `setColor()` actualiza ambas
      capas a la vez. El sin_solape/con_solape se conserva como color de
      **borde** (`hurb-line`), no compite con el relleno.
- [x] 5.3 Ficha (popup) de cada humedal urbano ampliada con Percentil,
      Amenaza de inundación, Susceptibilidad y Retención de suelo, más una
      advertencia visible cuando `cf` (confianza) es "baja".
- [x] 5.4 Grupo "variable" de la leyenda: el encabezado ahora usa el nombre
      corto de la variable (ej. "Amenaza") en vez de la descripción larga,
      igual que los grupos "Cuencas" y "Humedales urbanos" — la descripción
      larga se movió al cuerpo (oculto si el grupo está colapsado).
- [x] 5.5 Verificado con Playwright (`test-urbanos-amenaza.mjs`): al cargar,
      `hurb-fill` ya usa la misma expresión de color que `hpoly`; al elegir
      "Amenaza" o "Suelo" ambas capas cambian de color juntas; el header del
      grupo "variable" es el nombre corto; la ficha de un humedal urbano
      real (Humedales de Quirilluca) muestra Percentil, Amenaza y
      Susceptibilidad. Regresión verificada: `test-legend.mjs` (grupos
      colapsables) sigue pasando sin cambios.
- [ ] 5.6 Pendiente: commit/push + `railway up` (no realizado, junto con el
      resto de cambios locales pendientes de despliegue).

## 6. Sección propia en el informe (analogía con las tablas de ranking por
      comuna que ya existían para el inventario de 2.916)
- [x] 6.1 `scripts/build_report.py`: nueva sección "Humedales urbanos
      reconocidos (Ley 21.202)" después de "Exposición topográfica
      combinada" — mismo formato que las secciones existentes (tarjetas de
      indicador + tabla de ranking de comunas con barra), usando los 21
      registros completos de `humedales_urbanos_amenaza.csv` (no solo los
      18 de la capa web del mapa, ya que el informe escrito puede presentar
      el inventario declarado completo).
- [x] 6.2 Ranking de comunas por **amenaza media** (no por conteo), mismo
      criterio que las tablas "Comunas con mayor anomalía/exposición media"
      ya existentes; 14 comunas, 21 humedales urbanos en total, conteo por
      comuna verificado (suma = 21).
- [x] 6.3 Bug evitado: `.title()` de Python rompe "Viña del Mar" ->
      "Viña Del Mar" (ya documentado como error real en este proyecto, ver
      feedback de sesión) — se usa `com_case()`, una función propia que
      respeta conectores (de/del/la/las/los) en minúscula.
- [x] 6.4 Corrida sin errores: `build_report.py` + `assemble_web.py`
      regeneraron `public/index.html` (1.408 KB). Verificado a nivel de
      bytes (no por impresión en consola, que distorsiona tildes) que el
      texto nuevo y la tabla de comunas están en UTF-8 simple y correcto
      (Puchuncaví, Valparaíso, Quilpué, Viña del Mar todos con tilde
      correcta, sin doble codificación).
- [x] 6.5 Verificado visualmente con Playwright (captura de pantalla,
      `informe-humedales-urbanos.png`): la sección se ve con el mismo
      estilo que el resto del informe (tarjetas + tabla con barras), en el
      lugar correcto del documento.
- [ ] 6.6 Pendiente: revisión por Camila; commit/push + `railway up`.
