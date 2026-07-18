## ADDED Requirements

### Requirement: Anomalía de precipitación del evento

El sistema SHALL calcular la anomalía de precipitación de la ventana del evento
respecto de la climatología del modelo, por celda del área de estudio.

#### Scenario: Anomalía por celda recortada al AOI

- **WHEN** se dispone de la climatología (ERA5-Land 2003–2020) y la precipitación
  reciente (Open-Meteo)
- **THEN** el sistema SHALL producir la anomalía porcentual y la puntuación
  estandarizada (z) por celda, recortadas al límite regional

### Requirement: Exposición combinada de humedales

El sistema SHALL asignar a cada humedal una exposición que integre la anomalía
meteorológica y la posición topográfica.

#### Scenario: Índice de exposición compuesta

- **WHEN** se cruzan los humedales con la grilla de anomalía y con el índice
  topográfico de humedad (TWI) derivado del DEM
- **THEN** cada humedal SHALL recibir su anomalía (z) y su exposición compuesta
- **AND** el sistema SHALL identificar los humedales de mayor prioridad territorial

### Requirement: Caracterización y validación del evento

El sistema SHALL caracterizar el motor del evento (IVT / escala AR) y validarlo con
al menos una fuente observacional oficial.

#### Scenario: IVT propio y observación DMC/DGAC

- **WHEN** se calcula el IVT desde niveles de presión y se consulta la API DMC/DGAC
- **THEN** el sistema SHALL estimar la categoría del río atmosférico
- **AND** SHALL contrastar la anomalía modelada con la precipitación observada en 24 h
