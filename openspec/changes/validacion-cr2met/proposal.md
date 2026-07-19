# Validación con CR2MET (producto observacional) y arreglo de la Figura 5

## Problem

La climatología y el evento se apoyaban en un reanálisis (era5_seamless), que
la propia validación con estaciones mostró sesgado sobre Chile. Faltaba un
contraste contra un producto observacional independiente. Además, la Figura 5
(relieve 3D) no cargaba completa en el navegador.

## Proposed Solution

1. **Validación CR2MET** (`cr2met_clim.py`, opción B — validación, no reemplazo):
   se procesó CR2MET v2.0 (precipitación diaria observacional para Chile, ~5 km,
   1979&ndash;2020; NetCDF de 10,6 GB, leído con xarray/dask, recortado a la V
   Región). Se extrajo el acumulado 1&ndash;19 jul por año en las 157 celdas y se
   comparó el normal, la correlación espacial y el percentil del evento contra
   era5. CR2MET no cubre 2026, por lo que es validación independiente, no
   climatología principal (se mantiene era5 1995&ndash;2025).
2. **Figura 5**: se regeneró el relieve 3D más liviano (218 KB frente a 657 KB;
   dpi 115, figura menor) y con estilo responsivo (`max-width:100%`), para que
   el data-URI cargue completo.

## Decisions

- Opción B (validación, no reemplazo de baseline): la robustez cruzada
  observacional/reanálisis es más valiosa que otro cambio de referencia, y
  CR2MET no llega a los años recientes (2021&ndash;2025).
- El NetCDF de CR2MET (10,6 GB) no se versiona; sí el resultado derivado
  (`clim_cr2met_years.npz`, `resumen_cr2met.json`) y el script.

## Non-goals

- No se adopta CR2MET como climatología principal (termina en 2020).

## Results

- Convergencia: normal CR2MET 1991&ndash;2020 (WMO) = 38,8 mm ≈ era5
  1995&ndash;2025 = 43,0 mm; percentil del evento P90 (CR2MET) vs P88 (era5).
  La conclusión «muy inusual, no un récord» se sostiene con datos
  observacionales (1984, 1987 y 2001 fueron julios mayores).
- La correlación espacial celda a celda es baja (0,19 global; 0,52 costa/valle,
  ~0 cordillera): el reanálisis no reproduce el patrón fino sobre los Andes,
  motivo de fondo de la corrección con estaciones.
- Sección nueva en el informe + referencia CR2MET (Alvarez-Garreton et al.,
  2018). Figura 5 corregida (carga completa).
