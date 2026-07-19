# Delta: monitoreo-ambiental — topografía a resolución acorde al objeto

## MODIFIED Requirements

### Requirement: Exposición topográfica combinada

El sistema SHALL derivar un índice de exposición que combine la rareza
meteorológica corregida (percentil empírico) con la posición topográfica
calculada a una resolución acorde al tamaño de los objetos analizados, y SHALL
reportar la sensibilidad del índice a su ponderación cuando esta no pueda
calibrarse contra observaciones de terreno.

#### Scenario: Resolución topográfica acorde al objeto

- **WHEN** el tamaño característico de los objetos analizados (humedales) es
  menor que el píxel del modelo de elevación disponible
- **THEN** el sistema SHALL derivar la cadena topográfica (pendiente, flujo D8,
  TWI) desde un modelo de elevación de resolución igual o mejor a ~30 m,
  reproyectado al CRS de trabajo y enmascarado al área de estudio
- **AND** si el modelo es de superficie (DSM), esa condición SHALL declararse
  como fuente de incertidumbre

#### Scenario: Muestreo robusto en bordes del ráster

- **WHEN** el punto representativo de un humedal cae en nodata del ráster
  topográfico enmascarado (borde costero o regional)
- **THEN** el sistema SHALL muestrear el vecino válido más cercano dentro de un
  radio acotado y reportar cuántos puntos requirieron ese respaldo

#### Scenario: Ponderación sin calibración de terreno

- **WHEN** no existen registros de anegamiento que permitan calibrar la
  ponderación meteorológica/topográfica
- **THEN** el sistema SHALL evaluar el índice bajo al menos tres ponderaciones
  alternativas y reportar la estabilidad del ordenamiento y de la
  clasificación
- **AND** el conjunto de prioridad comunicado SHALL ser el núcleo robusto
  (clasificación «alta» bajo todas las ponderaciones evaluadas)
