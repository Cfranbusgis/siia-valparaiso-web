# Delta: monitoreo-ambiental — susceptibilidad de acumulación (suelo + concavidad)

## ADDED Requirements

### Requirement: Susceptibilidad de acumulación hídrica

El sistema SHALL estimar, por humedal, una susceptibilidad de acumulación que
integre convergencia topográfica, morfología de depresiones y retención del
suelo, y SHALL combinarla con la exposición meteorológica en una prioridad de
inundación/saturación.

#### Scenario: Componentes de acumulación

- **WHEN** se dispone del DEM (30 m) y de la cartografía de suelos
- **THEN** el sistema SHALL derivar TWI, concavidad/profundidad de depresión y
  una retención edáfica (textura, permeabilidad, drenaje; y capacidad de campo
  y arcilla donde la serie esté descrita)
- **AND** SHALL combinarlos en una susceptibilidad de acumulación que degrade
  de forma elegante donde falte alguna componente

#### Scenario: Prioridad de inundación como indicador, no modelo

- **WHEN** se reporta la prioridad de inundación/saturación
- **THEN** el sistema SHALL declararla como indicador de prioridad, no como
  modelo hidrológico (no resuelve caudal, lámina ni conectividad)
- **AND** SHALL declarar la cobertura de la componente edáfica y el complemento
  pendiente para las áreas sin catastro de suelo
