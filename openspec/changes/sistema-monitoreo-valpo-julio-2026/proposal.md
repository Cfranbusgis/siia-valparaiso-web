# Sistema de monitoreo del río atmosférico de julio 2026 (Valparaíso)

## Problem

El 14–18 de julio de 2026 un río atmosférico (categoría AR4) afectó Chile central.
Se necesitaba comprender su expresión territorial en la Región de Valparaíso y su
efecto potencial sobre los humedales, con datos reales y de forma reproducible y
presentable ante instituciones.

## Proposed Solution

Construir un sistema de análisis reproducible que:

1. Calcule la anomalía de precipitación (climatología del modelo propio ERA5-Land +
   ventana reciente de Open-Meteo).
2. Contraste la anomalía con el inventario de humedales de Valparaíso.
3. Derive exposición topográfica combinada desde el DEM (pendiente, flujo D8, TWI).
4. Caracterice el motor del evento con IVT propio y la escala AR.
5. Valide con observaciones DMC/DGAC, consenso multi-modelo y METAR.
6. Publique un informe científico y un modelo 3D como sitio web (Railway).

## Decisions

- Climatología desde el modelo propio (MOD_EToPM-HS), no de fuente externa.
- Ventana reciente vía Open-Meteo porque ERA5 archivo no cubre el evento.
- Alcance acotado a la Región de Valparaíso.
- Distinción explícita entre motor (IVT/AR) y expresión (anomalía).
- Exposición compuesta 50/50 (meteorológica/topográfica), ajustable.
- Enmarque científico, no de dashboard.
- Rutas configurables + insumos livianos incluidos para reproducibilidad.

## Non-goals

- No se estima directamente inundación, daño ecológico ni respuesta hidrológica
  (requieren modelación adicional; documentado como línea de profundización).
- No se recalcula la clasificación operacional oficial del evento.

## Results

- Anomalía media +264 % (z = 3,15); acumulado 168 mm vs. 48 mm normales.
- IVT máximo propio 819 kg m⁻¹ s⁻¹ (16 jul) → AR4, coherente con lo operacional.
- 2.916 humedales; 1.848 (63 %) con z > 2; 1.026 con z > 3; 483 (47 %) con
  exposición compuesta alta.
- Máximo observado DMC/DGAC: 120,1 mm/24 h (La Dormida).
- Entregables: informe HTML, modelo 3D, repositorio GitHub (Railway-ready).
