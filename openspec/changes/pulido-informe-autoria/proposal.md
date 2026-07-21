# Pulido del informe: autoría, título, versionado y enlace al repositorio

## Problem

Cuatro problemas de presentación en `public/index.html`, señalados por
Camila el 20-jul-2026:

1. El byline mostraba nombre y correo en líneas separadas; se pidió el
   formato `Nombre | correo`.
2. El título (`h1`) no quedaba centrado en navegadores con la ventana
   maximizada/pantalla completa.
3. El texto usaba "corregido/corregida" como calificador repetido en
   tarjetas de estadísticas, pies de figura, encabezados de tabla y una
   sección completa enmarcada en "v1 → v2", exponiendo el versionado
   interno del análisis en el informe público.
4. No había enlace visible al repositorio de GitHub.

## Proposed Solution

1. **Byline**: `<strong>Camila Bustamante-Álvarez</strong> | <a
   href="mailto:...">camibustamante@ug.uchile.cl</a>` en el masthead y en el
   pie de página (`.sourcebar`).
2. **Título centrado**: `h1{text-align:justify}` (línea 42 del CSS)
   sobrescribía siempre el `text-align:center` heredado de `.masthead`,
   porque una propiedad declarada directamente sobre un elemento gana sobre
   la heredada de un ancestro, sin importar la especificidad de este último.
   Cambiado a `text-align:center` (con `text-wrap:balance` para un
   quiebre de línea parejo). Verificado en 1920×1000 y 1280×800: el centro
   del `h1` coincide con el centro de `.wrap` en ambos casos.
3. **Versionado**: se distinguió entre (a) etiquetas repetidas de
   "corregido/corregida" en títulos de tarjetas, pies de figura,
   encabezados de tabla, badge de confianza y texto alt de imágenes — todas
   eliminadas, ya que el dato mostrado es simplemente la anomalía calculada,
   sin una versión rival "sin corregir" presentada al lado; y (b) la sección
   dedicada "Validación observacional y corrección de sesgo" y el apéndice
   de reproducibilidad, donde "corrección"/"corregido" describe el método
   real (no una etiqueta de versión) — esos se mantuvieron intactos. Se
   eliminó también la sección "Auditoría del análisis y trazabilidad de
   versiones" como marco de v1/v2 explícito, dejando la referencia técnica
   (especificación OpenSpec `auditoria-validacion-anomalia-v2`) como el
   puntero al detalle completo en GitHub.
4. **Ícono de GitHub**: SVG inline (sin dependencia externa) en la barra de
   navegación, enlazando a `https://github.com/Cfranbusgis/siia-valparaiso-web`
   con `target="_blank"`.

## Decisions

- No se tocó la sección "Validación observacional y corrección de sesgo"
  (h2, cerca de la mitad del documento) ni el apéndice de reproducibilidad:
  ahí "corrección" es la explicación legítima y única del método, el lugar
  correcto para ese detalle según el propio criterio de Camila ("lo demás
  se detalla en el github" no significa que el informe no pueda tener una
  sección de métodos).
- Se mantuvo la referencia literal `auditoria-validacion-anomalia-v2` (el
  nombre real de la especificación OpenSpec en el repositorio) porque es
  un puntero técnico, no una etiqueta de versión narrada en el cuerpo del
  informe.

## Results

- `public/index.html`: byline (masthead + footer), CSS del `h1`, ~15
  ocurrencias de "corregido/corregida" simplificadas o eliminadas, sección
  de auditoría renombrada y sin marco v1/v2, ícono + enlace de GitHub.
- Verificado con Playwright en dos anchos de viewport: centrado del título,
  formato del byline, presencia y destino del enlace de GitHub, ausencia de
  "corregido" fuera de la sección de métodos.
