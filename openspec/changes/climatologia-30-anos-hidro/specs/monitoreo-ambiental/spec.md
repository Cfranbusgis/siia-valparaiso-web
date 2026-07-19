# Delta: monitoreo-ambiental — normal de 30 años y capas hídricas

## MODIFIED Requirements

### Requirement: Cálculo de anomalía de precipitación

El sistema SHALL calcular la anomalía respecto de una climatología de referencia
homogénea de al menos 30 años cuando el registro lo permita, y SHALL declarar el
contexto climático del período de referencia (p. ej. inclusión de sequías
persistentes) cuando afecte la lectura de la anomalía.

#### Scenario: Normal de 30 años

- **WHEN** se dispone de ≥30 años del mismo producto que el reciente
- **THEN** el sistema SHALL usar el período de 30 años como referencia
- **AND** SHALL declarar si el período incluye anomalías climáticas persistentes
  (megasequía) que depriman o inflen el normal

#### Scenario: Afirmaciones de récord robustas al período

- **WHEN** se afirme que el evento supera el máximo del registro
- **THEN** la afirmación SHALL evaluarse contra el registro de 30 años, y SHALL
  descartarse si un período de referencia más largo contiene un valor mayor
- **AND** el informe SHALL preferir "muy inusual (percentil)" a "récord" cuando
  la condición de récord dependa de la longitud de la ventana

### Requirement: Susceptibilidad de acumulación hídrica

El sistema SHALL usar la red hidrográfica oficial (cuando esté disponible) en
lugar de cauces sintéticos para la distancia a drenaje, y SHALL reportar el
contexto de cuenca y de sector acuífero de cada humedal.

#### Scenario: Red hidrográfica oficial y contexto hídrico

- **WHEN** se dispone de la cartografía oficial de ríos, cuencas y acuíferos
- **THEN** la distancia a drenaje SHALL derivarse de la red oficial (con orden
  de Strahler si existe)
- **AND** cada humedal SHALL recibir su cuenca y su sector acuífero como
  contexto, distinguiendo lo que discrimina de lo que no
