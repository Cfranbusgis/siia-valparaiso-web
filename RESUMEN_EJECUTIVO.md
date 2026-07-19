# Resumen ejecutivo — Sistema Regional de Inteligencia Ambiental (SIIA), Región de Valparaíso

**Caso de aplicación:** anomalía de precipitación del río atmosférico del 14–18
de julio de 2026 y exposición del inventario regional de humedales.
**Versión:** v2 (corregida y validada con observaciones; sustituye a la v1).

---

## 1. Objeto y alcance

El SIIA caracteriza, con datos abiertos y un pipeline reproducible, la expresión
territorial de eventos hidrometeorológicos sobre la Región de Valparaíso. En
este caso de aplicación cuantifica cuánto se apartó la precipitación acumulada
del 1 al 18 de julio de 2026 respecto de su climatología (2003–2023), celda a
celda, y traslada esa señal a los 2.916 humedales del inventario regional. El
análisis describe **exposición meteorológica**; no estima inundación, respuesta
hidrológica ni daño ecológico, que requieren modelación específica.

## 2. Síntesis del evento

Un sistema frontal asociado a un río atmosférico de categoría **AR4 (extremo)**
—transporte integrado de vapor máximo de 819 kg m⁻¹ s⁻¹ el 16 de julio, 82 horas
sobre el umbral AR, flujo del NNO— descargó sobre la región un pulso de
precipitación concentrado en 48–60 horas.

| Indicador | v1 (sin corregir) | **v2 (corregido y validado)** |
|---|---|---|
| Acumulado regional medio, 1–18 jul | 192 mm | **96 mm** (climatología: 47 mm) |
| Anomalía regional media | +313 % | **+111 %** |
| Rareza (mediana regional) | z = 3,74 | **percentil empírico 86 del registro de 21 años** |
| Humedales en condición inusual | 1.364 con z > 3 (47 %) | **379 ≥ P90 (13 %); 214 sobre el máximo del registro** |
| Prioridad territorial (exposición compuesta) | 671 de los z > 3, índice sin calibrar | **núcleo robusto de 202 humedales, invariante a la ponderación** |
| Máximo observado en 24 h | 120,1 mm (La Dormida, red DMC/DGAC) | ídem (dato observacional) |

Lectura: un evento **notable, pero no excepcional a escala regional** —más del
doble de una quincena normal de julio—, con **récord local del registro
2003–2023 en su núcleo**, la cordillera de la Costa entre el estero Marga-Marga
y La Dormida. El máximo de rareza coincide espacialmente con el máximo
observado en superficie.

## 3. Por qué existe una versión v2

La comparación *like-for-like* contra la red de estaciones DMC/DGAC —misma
cantidad física, misma ventana de 24 horas, misma ubicación— mostró que el
producto de modelo casi en tiempo real que alimenta la ventana reciente
**sobreestimaba el evento en un factor cercano a 2** y aplanaba su gradiente
espacial. Dos verificaciones acotaron el diagnóstico: el desajuste de ventana
temporal quedó descartado como causa (alinear las ventanas empeora el sesgo) y
la climatología quedó exonerada (la referencia homogénea coincide con el modelo
propio, correlación por celda 0,93).

La corrección no se eligió por plausibilidad a priori sino por **desempeño
fuera de muestra**: tres candidatas se evaluaron por validación *leave-one-out*
sobre las 14 estaciones robustas.

| Corrección | MAE (mm) | RMSE (mm) | Sesgo (mm) |
|---|---|---|---|
| Sin corrección | 50,0 | 54,2 | +49,6 |
| Factor regional robusto | 23,1 | 26,6 | −3,7 |
| Condicionada por altitud | 20,3 | 26,0 | −5,1 |
| **Espacial de residuos (IDW) — aplicada** | **17,0** | **22,0** | **−2,0** |

Adicionalmente, la rareza se reporta con **percentiles empíricos** del registro
año a año (2003–2023) en lugar de umbrales gaussianos (z > k), inadecuados para
la precipitación quincenal, variable sesgada y con años secos frecuentes. El
cambio corrige un artefacto verificable de la v1: el 47 % de los humedales
superaba z > 3, proporción imposible bajo el supuesto de normalidad.

## 4. Método (cadena v2)

1. **Climatología homogénea:** acumulados 1–18 de julio por año (2003–2023) por
   celda, del mismo producto que la ventana reciente (ERA5 seamless); el modelo
   propio MOD_EToPM-HS (ERA5-Land, 10 km) actúa como verificación cruzada.
2. **Ventana reciente:** producto operacional casi en tiempo real (Open-Meteo),
   por el rezago de publicación del reanálisis consolidado.
3. **Auditoría observacional:** las 32 estaciones del snapshot DMC/DGAC con uso
   o descarte documentado (17 en la región; 3 excluidas por dato dudoso, falla
   atribuible al snapshot y replicada en regiones vecinas).
4. **Corrección de sesgo** validada por *leave-one-out* (sección 3).
5. **Anomalía y rareza:** anomalía porcentual corregida, percentil empírico
   (posición de Weibull, 21 años) y puntuación estandarizada solo como
   indicador complementario; cada humedal hereda el valor de su celda.
6. **Motor del evento:** IVT propio (integración 1000–300 hPa) y clasificación
   en la escala de Ralph et al. (2019), coherente con la clasificación
   operacional.
7. **Exposición compuesta (recalibrada):** componente meteorológica desde el
   percentil empírico corregido, componente topográfica desde el TWI (DEM
   250 m), evaluadas sobre el conjunto ≥ P90. Sin registros de anegamiento que
   permitan calibrar la ponderación, esta se somete a análisis de sensibilidad
   (30/70–70/30): el ordenamiento es invariante (Spearman ≥ 0,94) y 202
   humedales mantienen la categoría alta bajo cualquier ponderación (núcleo
   robusto; encabezan Casablanca, Quillota, Quilpué y Limache).

## 5. Decisiones metodológicas

| # | Decisión | Fundamento |
|---|---|---|
| D1 | Climatología homogénea con la fuente del dato reciente | El sesgo entre productos se cancela en la anomalía; el modelo propio queda como verificación cruzada |
| D2 | Ventana reciente operacional (Open-Meteo) | El reanálisis consolidado no cubría los días del evento |
| D3 | Alcance acotado a la Región de Valparaíso | Piloto territorial; el evento excede la región y así se declara |
| D4 | Validación *like-for-like* contra estaciones oficiales | Misma cantidad, ventana y ubicación; requisito para atribuir sesgo |
| D5 | Corrección elegida solo por desempeño fuera de muestra | Evita ajustar a la muestra con n = 14 |
| D6 | Rareza por percentil empírico, no por umbral gaussiano | Distribución sesgada y cero-inflada; el z se conserva como complemento |
| D7 | Distinción motor (IVT/AR) / expresión (anomalía) | Cadenas de evidencia independientes |
| D8 | Ponderación del índice compuesto por análisis de sensibilidad + núcleo robusto | Sin registros de anegamiento no hay calibración contra terreno; se reporta lo invariante a la ponderación |
| D9 | Trazabilidad v1 → v2 visible en el propio informe | La corrección es parte del resultado, no una fe de erratas |

## 6. Entregables

- **Sitio web** (Railway): informe científico (`/`) y modelo 3D interactivo
  (`/modelo-3d.html`).
- **Repositorio** (GitHub): pipeline Python completo (`scripts/`), productos de
  datos v1 y v2 (`data/`: grillas, humedales, auditoría de estaciones, métricas
  de validación cruzada, clima año a año), insumos livianos (`sources/`) y
  especificación OpenSpec (`openspec/`).
- **Figuras:** IVT y escala AR, serie diaria del evento, anomalía corregida y
  percentil empírico (mapa v2), exposición de humedales por percentil, relieve
  3D, contraste modelo–observación.

## 7. Limitaciones vigentes

1. La corrección de sesgo se apoya en 14 estaciones robustas; su detalle
   espacial está limitado por esa densidad.
2. La corrección se deriva del máximo de 24 horas y se transfiere al acumulado
   del periodo (supuesto verificado: el evento concentra >95 % del acumulado).
3. Con 21 años de registro, de un acumulado que supera el máximo histórico solo
   puede afirmarse que excede el percentil ≈95.
4. Los 2.916 humedales heredan el valor de ≤157 celdas (pseudo-réplica); los
   recuentos describen superficie expuesta, no unidades independientes.
5. La ponderación del índice de exposición compuesta no está calibrada contra
   registros de anegamiento; en su lugar se reporta su sensibilidad
   (30/70–70/30) y un núcleo robusto de 202 humedales invariante a ella.

## 8. Líneas de trabajo

- Validar las zonas de convergencia del índice compuesto (recalculado sobre el
  conjunto ≥ P90) contra registros de anegamiento observados, para calibrar la
  ponderación contra terreno.
- Acoplar IVT pronosticado (anticipación, no solo caracterización).
- Integrar condición ecológica (NDVI, LST) de los humedales.
- Consolidar la ventana reciente con ERA5-Land cuando publique el periodo y
  re-estimar la anomalía sin corrección operacional.

## 9. Trazabilidad

Los cambios metodológicos se gestionan por especificación
([`openspec/`](openspec/)). El cambio `auditoria-validacion-anomalia-v2`
documenta el problema, la auditoría de estaciones, la selección de la
corrección por validación cruzada, el recálculo v2 y sus deltas de
especificación. Las tablas de auditoría por estación y las métricas
*leave-one-out* están versionadas en `data/`.

---

*Documento actualizado el 18 de julio de 2026 (datos hasta las 09:00, hora
local; corrección observacional v2 aplicada). La ventana reciente incorpora
información operacional sujeta a revisión cuando ERA5-Land consolide el
periodo analizado.*
