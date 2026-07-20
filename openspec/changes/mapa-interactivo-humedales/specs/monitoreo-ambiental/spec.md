# Delta: monitoreo-ambiental — mapa interactivo de humedales

## ADDED Requirements

### Requirement: Mapa interactivo de humedales

El sistema SHALL publicar una página de mapa interactivo que permita explorar
los 2.916 humedales del inventario con sus atributos derivados, superponer
capas de contexto y descargar los datos mostrados.

#### Scenario: Exploración por variable temática

- **WHEN** el usuario selecciona una variable (percentil, amenaza de
  inundación, susceptibilidad o retención de suelo)
- **THEN** los polígonos de humedales SHALL colorearse según esa variable con
  leyenda dinámica
- **AND** el clic sobre un humedal SHALL mostrar una ficha con sus atributos
  (nombre, comuna, cuenca, tipo, percentil, acumulado, amenaza,
  susceptibilidad, retención y serie de suelo)

#### Scenario: Capas superponibles y control del peso visual del fondo

- **WHEN** el usuario activa capas de contexto (borde regional, cuencas BNA,
  humedales)
- **THEN** SHALL poder combinarlas libremente y regular la transparencia de
  cada una
- **AND** SHALL poder alternar el mapa base (claro/satélite) y regular su
  transparencia, conservándose la opacidad elegida al cambiar de fondo, para
  facilitar la lectura de los humedales y las capas temáticas

#### Scenario: Descarga de datos desde el sitio

- **WHEN** el usuario abre la sección de datos y metadatos del panel
- **THEN** SHALL poder descargar la tabla de humedales (CSV) y las capas de
  humedales y cuencas (GeoJSON)
