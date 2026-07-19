# Delta: monitoreo-ambiental — auditoría multicomité y ventana al 19-jul

## ADDED Requirements

### Requirement: Explicitación de la fuente oficial del inventario

El sistema SHALL identificar la fuente oficial del inventario de humedales con
su organismo, versión/fecha y condiciones de uso, y SHALL declarar qué
clasificación tipológica está efectivamente disponible como atributo.

#### Scenario: Fuente y tipología declaradas

- **WHEN** se emplea una capa de humedales de un organismo oficial
- **THEN** el informe SHALL citar el organismo, la vía de distribución, la fecha
  y la condición de uso, adoptar la definición de humedal de referencia (Ramsar)
  y precisar si la tipología del atributo es la disponible o requiere cruce
  posterior

### Requirement: Documentación de indicadores derivados del DEM

El sistema SHALL documentar el método de cálculo de cualquier indicador derivado
del modelo de elevación (por ejemplo, fracción bajo una cota), incluyendo DEM,
método de muestreo y verificación.

#### Scenario: Fracción bajo la cota de nieve

- **WHEN** se reporta el porcentaje de humedales bajo el nivel de congelación
- **THEN** el sistema SHALL indicar el DEM, el método (punto representativo),
  el n válido y una verificación cruzada, y SHALL declarar el sentido del sesgo
  del DSM sobre la estimación

### Requirement: Declaración de naturaleza operativa y licencia

El sistema SHALL declarar su naturaleza de ejecución (tiempo real frente a
corrida manual) y la licencia de texto, datos y código.

#### Scenario: Naturaleza y licencia

- **WHEN** se publica una versión del informe
- **THEN** el informe SHALL indicar si los datos provienen de ingesta en vivo o
  de una corrida manual con fecha de corte, y SHALL declarar la licencia
  aplicable y las condiciones de la capa base

### Requirement: Hoja de ruta de mejora trazable

El sistema SHALL registrar, como sección del informe, los alcances de mejora
pendientes identificados por auditoría, priorizados y distinguidos de los ya
incorporados.

#### Scenario: Alcances de mejora

- **WHEN** una auditoría identifica mejoras no implementadas en la versión actual
- **THEN** el informe SHALL listarlas como trabajo futuro priorizado, sin
  simular su implementación, y SHALL separar lo ya incorporado de lo pendiente

## MODIFIED Requirements

### Requirement: Cálculo de anomalía de precipitación

El sistema SHALL calcular la anomalía de precipitación de una ventana reciente
respecto de una climatología de referencia homogénea (mismo producto y misma
ventana temporal), por celda de la grilla del área de estudio.

#### Scenario: Ventana reciente y climatología homogéneas

- **WHEN** se amplía o modifica la ventana temporal del dato reciente
- **THEN** la climatología de referencia SHALL extenderse a la misma ventana
  antes de recalcular la anomalía, de modo que el denominador no mezcle ventanas
- **AND** cualquier asimetría residual (día parcial reciente frente a día
  completo climatológico) SHALL declararse y su efecto acotarse
