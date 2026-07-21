# Delta: monitoreo-ambiental — humedales urbanos reconocidos (Ley 21.202)

## ADDED Requirements

### Requirement: Capa de humedales urbanos reconocidos

El sistema SHALL extraer del Portal de Humedales del MMA los humedales
urbanos con estado "Humedal Urbano Reconocido" de la Región de Valparaíso,
como insumo complementario al inventario regional (2013) usado por el resto
del sistema.

#### Scenario: Extracción y filtrado por estado

- **WHEN** se consulta el listado público de solicitudes de la Región de
  Valparaíso
- **THEN** el sistema SHALL retener solo las de estado
  "Humedal Urbano Reconocido"
- **AND** SHALL obtener, por cada una, comuna, provincia, región, superficie
  y clasificación desde su ficha de detalle

#### Scenario: Exclusión de humedales artificiales con clasificación en texto libre

- **WHEN** el campo de clasificación no sigue un vocabulario controlado
- **THEN** el sistema SHALL excluir los registros cuya clasificación indique
  explícitamente un tipo artificial
- **AND** SHALL excluir los registros cuya clasificación mezcle tipos
  natural y artificial en un mismo trámite, por no poder aislarlos sin
  geometría
- **AND** SHALL incluir, marcados explícitamente, los registros sin dato de
  clasificación, sin asumir que son naturales ni artificiales

#### Scenario: Geometría desde el expediente público

- **WHEN** el humedal urbano reconocido tiene documentos cartográficos en su
  expediente público
- **THEN** el sistema SHALL descargar y reproyectar a WGS84 el polígono de
  la versión final (o rectificada) del límite
- **AND** SHALL validar el área calculada contra la superficie declarada en
  la solicitud, para detectar selecciones de archivo incorrectas
- **AND** SHALL marcar explícitamente con confianza baja, y como tarea
  pendiente de re-auditoría en OpenSpec, cualquier geometría cuya área no
  se pueda reconciliar con ninguna fuente disponible

#### Scenario: Cruce espacial con el inventario existente

- **WHEN** hay geometría disponible para un humedal urbano reconocido
- **THEN** el sistema SHALL calcular el porcentaje de su área cubierto por
  polígonos del inventario 2013 mediante intersección espacial
- **AND** SHALL exponer ese porcentaje como variable continua en vez de
  forzarlo a una clasificación binaria de "nuevo"
- **AND** SHALL publicar el resultado como capa superponible en el mapa
  interactivo, con ficha por humedal que incluya el porcentaje de solape y
  los polígonos 2013 relacionados
