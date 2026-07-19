# Delta: monitoreo-ambiental — recalibración de la exposición compuesta

## MODIFIED Requirements

### Requirement: Exposición topográfica combinada

El sistema SHALL derivar un índice de exposición que combine la rareza
meteorológica corregida (percentil empírico) con la posición topográfica, y
SHALL reportar la sensibilidad del índice a su ponderación cuando esta no pueda
calibrarse contra observaciones de terreno.

#### Scenario: Índice de humedad topográfica y exposición compuesta

- **WHEN** se procesa el modelo digital de elevación (250 m)
- **THEN** el sistema SHALL calcular pendiente, acumulación de flujo (D8) e
  índice topográfico de humedad (TWI)
- **AND** SHALL combinar la componente meteorológica (percentil empírico
  corregido, reescalado a [0, 1]) y la topográfica (TWI normalizado) en un
  índice compuesto sobre el conjunto de exposición vigente (≥ P90)

#### Scenario: Ponderación sin calibración de terreno

- **WHEN** no existen registros de anegamiento que permitan calibrar la
  ponderación meteorológica/topográfica
- **THEN** el sistema SHALL evaluar el índice bajo al menos tres ponderaciones
  alternativas y reportar la estabilidad del ordenamiento (correlación de
  rangos) y de la clasificación (intersección/unión de conjuntos «alta»)
- **AND** el conjunto de prioridad comunicado SHALL ser el núcleo robusto:
  los humedales clasificados «alta» bajo todas las ponderaciones evaluadas
- **AND** la calibración contra terreno SHALL quedar declarada como extensión
  pendiente, sin simularse
