# Delta: monitoreo-ambiental — usabilidad del mapa interactivo

## MODIFIED Requirements

### Requirement: Mapa interactivo de humedales

El sistema SHALL publicar una página de mapa interactivo que permita explorar
los 2.916 humedales del inventario con sus atributos derivados, superponer
capas de contexto y descargar los datos mostrados, manteniendo todo el
contenido interactivo accesible en viewports de escritorio y móviles.

#### Scenario: Exploración por variable temática

- **WHEN** el usuario selecciona una variable (percentil, amenaza de
  inundación, susceptibilidad o retención de suelo)
- **THEN** los polígonos de humedales SHALL colorearse según esa variable con
  leyenda dinámica
- **AND** el clic sobre un humedal SHALL mostrar una ficha con sus atributos,
  sin exponer códigos internos de ausencia de dato (p. ej. `NO SUELOS`)

#### Scenario: Capas superponibles y control del peso visual del fondo

- **WHEN** el usuario activa capas de contexto (borde regional, cuencas BNA,
  humedales)
- **THEN** SHALL poder combinarlas libremente y regular la transparencia de
  cada una
- **AND** SHALL poder alternar el mapa base (claro/satélite) y regular su
  transparencia, conservándose la opacidad elegida al cambiar de fondo, para
  facilitar la lectura de los humedales y las capas temáticas
- **AND** los nombres de cuenca SHALL presentarse con ortografía corregida en
  leyenda, ficha y rótulos, sin alterar los identificadores usados en los
  cruces internos

#### Scenario: Descarga de datos desde el sitio

- **WHEN** el usuario abre la sección de datos y metadatos del panel
- **THEN** SHALL poder descargar la tabla de humedales (CSV) y las capas de
  humedales y cuencas (GeoJSON)

#### Scenario: Contenido interactivo accesible en viewports pequeños

- **WHEN** la página se muestra en un viewport móvil (retrato u horizontal)
- **THEN** todos los controles y enlaces de descarga SHALL ser alcanzables
  (mediante scroll interno de las tarjetas o su minimización), sin quedar
  tapados por otras tarjetas ni fuera de pantalla
- **AND** el scroll interno de las tarjetas SHALL NOT desplazar ni hacer zoom
  al mapa

#### Scenario: Controles con nombre y estado accesibles

- **WHEN** un lector de pantalla u otra tecnología de asistencia recorre los
  controles
- **THEN** cada botón y slider SHALL exponer un nombre accesible descriptivo
- **AND** los botones de alternancia (variable, mapa base, minimizar) SHALL
  exponer su estado (`aria-pressed` o `aria-expanded`)
