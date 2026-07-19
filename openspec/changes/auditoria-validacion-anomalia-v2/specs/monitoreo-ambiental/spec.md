# Delta: monitoreo-ambiental — auditoría, corrección de sesgo y anomalía v2

## ADDED Requirements

### Requirement: Auditoría de estaciones observacionales

El sistema SHALL documentar, para cada estación observacional disponible, su
uso o descarte con motivo explícito, y SHALL comparar el modelo sobre la misma
ventana temporal que el observado.

#### Scenario: Trazabilidad de descartes

- **WHEN** se filtran las estaciones DMC para la validación
- **THEN** el sistema SHALL emitir una tabla con todas las estaciones (usadas y
  descartadas) incluyendo obs, modelo, error, ratio, altitud, distancia al
  núcleo del evento y flag con el motivo (fuera de AOI / dato dudoso / OK)

#### Scenario: Correspondencia temporal obs–modelo

- **WHEN** el observado es un acumulado móvil de 24 h con hora de snapshot
- **THEN** el modelo SHALL evaluarse también sobre esa ventana exacta de 24 h
  (horario, misma zona horaria), además del día calendario, y la diferencia
  entre ambas métricas SHALL reportarse antes de atribuir sesgo al modelo

### Requirement: Corrección de sesgo validada fuera de muestra

El sistema SHALL corregir el sesgo del producto reciente contra observaciones
solo con una corrección que haya demostrado mejorar la predicción fuera de
muestra.

#### Scenario: Selección por leave-one-out

- **WHEN** existen ≥3 correcciones candidatas (factor regional robusto,
  interpolación espacial de residuos, corrección condicionada por covariable)
- **THEN** cada candidata SHALL evaluarse por leave-one-out sobre las
  estaciones robustas reportando MAE, RMSE y sesgo contra la línea base sin
  corrección
- **AND** SHALL aplicarse a la grilla únicamente la candidata con mejor
  desempeño fuera de muestra

### Requirement: Rareza por percentil empírico

El sistema SHALL cuantificar la rareza del evento con percentiles empíricos
sobre una climatología homogénea (mismo producto que el reciente), y SHALL NOT
usar umbrales gaussianos (z > k) como métrica principal de rareza en
precipitación.

#### Scenario: Percentil empírico por celda

- **WHEN** se dispone de los acumulados de la ventana por año (≥20 años) del
  mismo producto que el reciente
- **THEN** cada celda SHALL recibir su percentil empírico (posición de
  plotting r/(n+1)) y el número de años del registro que el evento supera
- **AND** el z homogéneo MAY reportarse solo como indicador complementario

## MODIFIED Requirements

### Requirement: Validación con fuentes independientes

El sistema SHALL contrastar el evento con al menos una fuente observacional
oficial, sobre la misma cantidad física, la misma ventana temporal y la misma
ubicación (like-for-like), y SHALL propagar el resultado de esa validación a
los productos finales (corrección de sesgo o advertencia explícita).

#### Scenario: Observación DMC/DGAC

- **WHEN** se consulta la API oficial de la Dirección Meteorológica de Chile
- **THEN** el sistema SHALL obtener la precipitación acumulada en 24 h de las
  estaciones de la región
- **AND** SHALL contrastarla con el modelo en la misma ventana de 24 h y
  ubicación
- **AND** si el contraste revela sesgo sistemático, el sistema SHALL corregir
  el producto de anomalía o etiquetarlo como no corregido

### Requirement: Contraste con humedales

El sistema SHALL asignar a cada humedal del inventario regional la anomalía
corregida y el percentil empírico de la celda correspondiente.

#### Scenario: Exposición meteorológica de humedales

- **WHEN** se cruzan los 2.916 humedales de Valparaíso con la grilla de
  anomalía v2
- **THEN** cada humedal SHALL recibir su anomalía porcentual corregida, su
  percentil empírico y su z homogéneo
- **AND** los recuentos de exposición SHALL reportarse por percentil
  (≥P90, sobre el máximo del registro), no por z > k
