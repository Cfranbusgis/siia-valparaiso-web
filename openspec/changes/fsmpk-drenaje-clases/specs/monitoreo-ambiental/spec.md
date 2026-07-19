# Delta: monitoreo-ambiental — distancia a drenaje y clases de prioridad

## MODIFIED Requirements

### Requirement: Susceptibilidad de acumulación hídrica

El sistema SHALL estimar, por humedal, una susceptibilidad de acumulación que
integre convergencia topográfica, morfología de depresiones, retención del
suelo y cercanía a la red de drenaje, y SHALL combinarla con la exposición
meteorológica en una prioridad de inundación/saturación expresada también en
clases ordinales.

#### Scenario: Componentes de acumulación

- **WHEN** se dispone del DEM (30 m) y de la cartografía de suelos
- **THEN** el sistema SHALL derivar TWI, concavidad/profundidad de depresión,
  retención edáfica y distancia a la red de drenaje (extraída del flujo D8)
- **AND** SHALL combinarlos en una susceptibilidad de acumulación que degrade
  de forma elegante donde falte alguna componente

#### Scenario: Clases de prioridad

- **WHEN** se reporta la prioridad de inundación/saturación
- **THEN** el sistema SHALL expresarla también en clases ordinales
  (Muy Baja a Muy Alta) además del valor continuo
- **AND** SHALL declarar la prioridad como indicador, no como modelo hidrológico

#### Scenario: Fuente de etiquetas para un modelo supervisado

- **WHEN** se plantee entrenar un modelo supervisado de inundación
- **THEN** las etiquetas SHALL provenir de un inventario de crecidas/anegamiento
  observado (p. ej. SENAPRED o caudales fluviométricos), y NO de la resolución
  de reporte de extracciones de la DGA, que no es una fuente de datos de
  inundación
