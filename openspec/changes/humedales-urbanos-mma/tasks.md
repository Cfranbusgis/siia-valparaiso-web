# Tasks — humedales-urbanos-mma

## 1. Extracción
- [x] 1.1 Confirmar que el portal MMA sirve los datos en HTML/JSON del
      servidor, sin JavaScript (verificado con `curl` directo, sin
      navegador).
- [x] 1.2 `scripts/humedales_urbanos_mma.py`: listado de solicitudes de
      Valparaíso (`ListarSolicitudesPublicas`) + ficha por solicitud
      (`DetailsPublico/{id}`) para comuna, provincia, región, superficie y
      clasificación.
- [x] 1.3 Filtrar a estado "Humedal Urbano Reconocido" (21 de 47 registros).
- [x] 1.4 Corregir encoding (mojibake por detección automática de `requests`
      en respuestas sin charset declarado); verificado en el CSV de salida
      (no en la consola de Windows, que sigue mostrando mal por su propio
      codepage).

## 2. Clasificación natural / artificial
- [x] 2.1 Revisar las 21 clasificaciones (texto libre) una por una; no se
      asumió un vocabulario controlado.
- [x] 2.2 Reglas decididas con Camila caso por caso (ver proposal.md):
      vacío/"No señala" → sin dato (incluido); artificial+natural a la vez →
      mixto (excluido); solo artificial → excluido; resto → natural
      (incluido por convención de nomenclatura CONAMA 2006/MMA).
- [x] 2.3 Verificado: 15 natural + 3 sin dato + 2 artificial + 1 mixto = 21
      (cuadra con el total extraído).

## 3. Cruce exploratorio por comuna
- [x] 3.1 Conteo de humedales 2013 por comuna desde
      `public/humedales_poly.geojson`, con normalización de mayúsculas/acentos
      para el join (bug detectado y corregido: `.title()` capitalizaba
      "Del" en "Viña del Mar" y rompía el cruce con "Viña Del Mar").
- [x] 3.2 Verificado: las 12 comunas de los 18 humedales nuevos ya tienen
      presencia en el inventario 2013 (rango 5–163 humedales por comuna).

## 4. Entrega (atributos)
- [x] 4.1 `data/humedales_urbanos_valpo.csv` (21 filas) y
      `data/humedales_urbanos_valpo_natural.csv` (18 filas) generados y
      verificados.
- [x] 4.2 `beautifulsoup4==4.12.3` agregado a `requirements.txt`.

## 5. Geometría real desde el expediente público
- [x] 5.1 Mecanismo de descarga encontrado y verificado: `POST
      /HumedalesUrbanos/DescargarExpediente` (sin auth), leyendo
      `TablasDocumentosExpediente.js`. Instalado 7-Zip (`winget`) para
      extraer `.rar`/`.zip` anidados.
- [x] 5.2 `scripts/humedales_urbanos_geometria.py`: descarga, extrae y
      reproyecta a WGS84 los 18 polígonos. 18/18 resueltos.
- [x] 5.3 Validación por área: se contrastó el área calculada de cada
      polígono contra `superficie_ha` (superficie *original* solicitada).
      11 casos sin ambigüedad (ratio 0,95–1,16). Se detectó y corrigió un
      bug real de selección en #1237 El Bato (`Diferencia.shp`, un
      subproducto de análisis GIS, en vez de `Polígono_El_Bato_VF.shp`;
      corregido y confirmado con ratio 1,00). 5 casos con boundary
      "rectificada" documentada, donde el desajuste de área es esperado
      (no error): #164, #169, #170, #177, #1222.
- [ ] **5.4 RE-AUDITORÍA PENDIENTE — #162 Estero Reñaca**: ningún polígono
      disponible en el expediente público coincide con la superficie
      declarada (233,4 ha original vs. 15,1–16,9 ha en los 2 candidatos
      encontrados). Se usó `Final CMS/HU_EsteroReñaca_VF.shp` (16,9 ha) como
      mejor esfuerzo, con `confianza_geometria = "baja"` explícito en el
      GeoJSON. **No usar este polígono en ningún análisis o figura de la
      tesis sin antes revisar la Resolución Exenta 5196 (reconoce HU Estero
      Reñaca) u otra fuente oficial** que aclare la superficie real
      reconocida.
- [ ] 5.5 (opcional, menor prioridad) Verificar por muestreo 2–3 de los 5
      casos "rectificada" (164, 169, 170, 177, 1222) contra su
      "Mapa Oficial"/Resolución en PDF, para confirmar que el polígono
      elegido corresponde a la versión efectivamente reconocida y no a un
      borrador intermedio.

## 6. Cruce espacial con el inventario 2013
- [x] 6.1 `scripts/build_humedales_urbanos_web.py`: intersección de los 18
      polígonos disueltos contra los 2.916 del inventario 2013; `pct2013`
      (% de área cubierta), `n2013` (n° de polígonos 2013 intersectados),
      `nom2013` (nombres relacionados) y `clase` (sin_solape/con_solape).
      Resultado: 4 sin solape, 5 con solape muy alto (79–94%), 9 en zona
      intermedia (21–68%) — no se forzó un umbral binario de "nuevo"; el %
      queda expuesto para que se juzgue caso a caso (ver proposal.md).

## 7. Capa en el mapa interactivo
- [x] 7.1 `public/mapa-interactivo.html`: capa "Humedales urbanos (Ley
      21.202)" superponible, visible por defecto, color por `clase`,
      leyenda propia, ficha con % de solape y nombres 2013 relacionados,
      advertencia visible para geometría de confianza baja, descarga desde
      el panel.
- [x] 7.2 **Bug encontrado y corregido**: simplificación automática de la
      fuente GeoJSON según zoom borraba los 4 polígonos más chicos (<2 ha)
      al zoom inicial — exactamente los 4 "sin solape", el hallazgo más
      importante de la capa. Corregido con `tolerance:0` en la fuente.
- [x] 7.3 Verificado con Playwright (escritorio): capa carga los 18
      humedales, toggle on/off, opacidad independiente de las demás capas,
      leyenda, ficha de un humedal "sin solape" (Canal Waddington) y de
      #162 "confianza baja" (Estero Reñaca) con su advertencia visible,
      descarga del GeoJSON (200, 18 features), sin errores de consola.
- [x] 7.4 Verificado: panel sigue dentro del viewport en 375×667 con la
      capa nueva agregada (sin romper el trabajo de
      mejoras-usabilidad-mapa-interactivo).

## 8. Entrega final
- [x] 8.1 Revisión por Camila; commit + push (aprobado).
