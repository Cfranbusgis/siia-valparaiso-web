# monitoreo-ambiental Specification

## Purpose

Caracterizar la anomalía de precipitación de un evento hidrometeorológico (río
atmosférico) sobre la Región de Valparaíso, contrastarla con el inventario de
humedales y validarla con observaciones independientes, produciendo un informe
científico reproducible y un sitio web desplegable.

## Requirements

### Requirement: Cálculo de anomalía de precipitación

El sistema SHALL calcular la anomalía de precipitación de una ventana reciente
respecto de una climatología de referencia, por celda de la grilla del área de
estudio.

#### Scenario: Anomalía por celda

- **WHEN** se dispone de la climatología (ERA5-Land del modelo, 2003–2020) y de la
  precipitación reciente (Open-Meteo)
- **THEN** el sistema SHALL producir, por celda, la anomalía porcentual y la
  puntuación estandarizada (z) recortadas al límite regional (AOI)

#### Scenario: Ventana reciente cuando el reanálisis tiene rezago

- **WHEN** el reanálisis ERA5 aún no publica los días del evento
- **THEN** el sistema SHALL usar la fuente operacional casi-tiempo-real (Open-Meteo
  forecast/past_days) para la ventana reciente

### Requirement: Contraste con humedales

El sistema SHALL asignar a cada humedal del inventario regional la anomalía de la
celda correspondiente.

#### Scenario: Exposición meteorológica de humedales

- **WHEN** se cruzan los 2.916 humedales de Valparaíso con la grilla de anomalía
- **THEN** cada humedal SHALL recibir su anomalía porcentual y su valor z
- **AND** el sistema SHALL identificar los humedales con z > 2 y z > 3

### Requirement: Exposición topográfica combinada

El sistema SHALL derivar un índice de exposición que combine la anomalía
meteorológica con la posición topográfica.

#### Scenario: Índice de humedad topográfica y exposición compuesta

- **WHEN** se procesa el modelo digital de elevación (250 m)
- **THEN** el sistema SHALL calcular pendiente, acumulación de flujo (D8) e índice
  topográfico de humedad (TWI)
- **AND** SHALL combinar exposición meteorológica y topográfica en un índice
  compuesto por humedal

### Requirement: Caracterización del río atmosférico (IVT)

El sistema SHALL estimar el transporte integrado de vapor (IVT) del evento y su
categoría en la escala de ríos atmosféricos.

#### Scenario: IVT y categoría AR

- **WHEN** se dispone de humedad y viento en niveles de presión (1000–300 hPa)
- **THEN** el sistema SHALL calcular el IVT horario y su máximo
- **AND** SHALL clasificar el evento según magnitud y duración (escala de Ralph et al., 2019)

### Requirement: Validación con fuentes independientes

El sistema SHALL contrastar el evento con al menos una fuente observacional oficial.

#### Scenario: Observación DMC/DGAC

- **WHEN** se consulta la API oficial de la Dirección Meteorológica de Chile
- **THEN** el sistema SHALL obtener la precipitación acumulada en 24 h de las
  estaciones de la región
- **AND** SHALL contrastarla con la anomalía modelada

### Requirement: Reproducibilidad del pipeline

El sistema SHALL ser ejecutable en otro equipo sin editar el código fuente.

#### Scenario: Rutas configurables

- **WHEN** se definen las variables de entorno SIIA_MODEL_DIR, SIIA_HUMEDALES_DIR y
  SIIA_WORK_DIR
- **THEN** el pipeline SHALL resolver todas las rutas desde ellas
- **AND** SHALL usar los insumos livianos incluidos en sources/ si la fuente externa
  no está disponible

### Requirement: Publicación como sitio web

El sistema SHALL publicar el informe y el modelo 3D como un sitio estático
desplegable.

#### Scenario: Servidor y despliegue

- **WHEN** se ejecuta el servidor Node
- **THEN** SHALL servir el informe en `/` y el modelo 3D en `/modelo-3d.html`
- **AND** SHALL usar el puerto de la variable de entorno PORT (compatible con Railway)
