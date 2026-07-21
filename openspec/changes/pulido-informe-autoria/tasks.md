# Tasks — pulido-informe-autoria

## 1. Autoría y título
- [x] 1.1 Byline `Nombre | correo` en masthead y footer.
- [x] 1.2 CSS del `h1`: `text-align:justify` → `text-align:center`
      (`text-wrap:auto` → `text-wrap:balance`). Verificado en 1920×1000 y
      1280×800: centro del `h1` coincide con el centro de `.wrap`.

## 2. Versionado
- [x] 2.1 Eliminado "corregido/corregida" de: 2 títulos de tarjeta de
      estadística, 1 pie de figura, 1 encabezado de tabla, 1 badge de
      confianza, 2 alt de imagen, y ~10 ocurrencias en texto corrido fuera
      de la sección de métodos.
- [x] 2.2 Eliminadas las referencias explícitas "v1"/"v2"/"(v2)" del cuerpo
      narrativo (7 ocurrencias) y renombrada la sección "Auditoría del
      análisis y trazabilidad de versiones" → "Auditoría del análisis".
- [x] 2.3 Verificado: la sección de métodos ("Validación observacional y
      corrección de sesgo") y el apéndice de reproducibilidad conservan
      "corrección"/"corregido" donde describen el método real, incluida la
      referencia técnica a la especificación OpenSpec
      `auditoria-validacion-anomalia-v2`.

## 3. Enlace a GitHub
- [x] 3.1 Ícono SVG inline en la barra de navegación, enlace a
      `https://github.com/Cfranbusgis/siia-valparaiso-web`, `target="_blank"`.
- [x] 3.2 Verificado: presente, apunta al repo correcto, abre en pestaña
      nueva.

## 4. Entrega
- [x] 4.1 Revisión por Camila; commit + push (aprobado).

## 5. Enlace a LinkedIn (21-jul-2026, pedido posterior)
- [x] 5.1 Ícono SVG inline junto al de GitHub (mismo estilo, `margin-left`
      fijo en vez de `auto` ya que el GitHub conserva el empuje a la
      derecha del nav), enlace a `https://www.linkedin.com/in/cfranbusgis`,
      `target="_blank"`. Editado directamente en `public/index.html` (no se
      usó `build_report.py`, ver advertencia agregada en ese script tras el
      incidente documentado en `humedales-urbanos-amenaza` tarea 8).
- [x] 5.2 Verificado con Playwright local (`href` correcto) y en el sitio
      en vivo tras el despliegue (commit `6d25a7b`).
- [ ] 5.3 Pendiente: confirmación visual de Camila.
