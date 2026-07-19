# Delta: monitoreo-ambiental — validación observacional cruzada (CR2MET)

## MODIFIED Requirements

### Requirement: Validación con fuentes independientes

El sistema SHALL contrastar el evento y su climatología contra al menos un
producto observacional independiente del reanálisis cuando esté disponible, y
SHALL reportar la convergencia (o divergencia) en magnitud, rareza y patrón
espacial.

#### Scenario: Contraste contra un producto observacional grillado

- **WHEN** existe un producto grillado restringido con observaciones (p. ej.
  CR2MET) que cubra el período climatológico
- **THEN** el sistema SHALL comparar el normal, el percentil del evento y la
  correlación espacial celda a celda contra el producto de reanálisis
- **AND** SHALL declarar si la conclusión de rareza es robusta a la fuente
- **AND** SHALL indicar las limitaciones de cobertura temporal del producto
  observacional (p. ej. que no alcance los años del evento)
