# Topografía a 30 m (ALOS AW3D30) para la exposición de humedales

## Problem

Una auditoría externa del sistema (hallazgos H1–H21, con recomendación de
publicación FAIR) observó que la resolución topográfica de 250 m es gruesa
respecto del tamaño de los humedales del inventario: un píxel de 250 m
(6,25 ha) excede la superficie de muchos humedales, de modo que el TWI —y con
él la componente topográfica del índice de exposición compuesta— promediaba
laderas y fondos de valle dentro de una misma celda.

## Proposed Solution

Incorporar el modelo ALOS AW3D30 (~30 m) y recalcular la cadena topográfica:

1. **Preparación del DEM** (`prep_dem30.py`): del export GEE de todo Chile
   (16 teselas, EPSG:4326, 0,000269°) se mosaican solo las 2 teselas que
   intersectan el AOI, se reproyecta a EPSG:32719 a 30 m exactos (bilineal,
   nodata −9999) y se enmascara al límite regional (RV.shp) →
   `DEM_AW3D30_30m_UTM19S_RV.tif` (5.718 × 7.220 px; 16.007 km²).
2. **Cadena topográfica** (`topo_30m.py`): pendiente, acumulación de flujo D8
   (pysheds: fill_pits → fill_depressions → resolve_flats) y TWI, mismo método
   que a 250 m.
3. **Exposición compuesta** (`exposicion_v2.py`): usa el TWI de 30 m si
   existe (respaldo automático al de 250 m); el muestreo por humedal incorpora
   búsqueda del vecino válido más cercano (anillos hasta 240 m) para los
   puntos costeros que caen en nodata del DEM enmascarado.

## Decisions

- AW3D30 es un **DSM** (superficie: incluye dosel y edificaciones); se declara
  como fuente de incertidumbre en el informe en lugar de pretender que es un
  DTM.
- Sanidad del DEM verificada contra el de 250 m: elevación media 1.234 vs
  1.233 m; el máximo sube de 5.828 a 5.945 m (el 30 m resuelve cumbres).
- Los rásteres (DEM 73 MB, TWI/pendiente) **no se versionan** en el
  repositorio por tamaño; los scripts que los regeneran sí, con salida
  in situ y omisión limpia si el insumo externo no está disponible.
- La definición del índice y el protocolo de sensibilidad no cambian; solo la
  fuente topográfica.

## Non-goals

- No se re-deriva la exposición topográfica del análisis v1 (z > 3, histórico).
- No se convierte el DSM a DTM (sin datos de dosel regionales).

## Results

- Cadena topográfica a 30 m sobre 17,8 M de celdas en 73 s; pendiente media
  regional 18,6° (el 250 m la suavizaba).
- Exposición compuesta con TWI 30 m: **núcleo robusto 172 humedales** (46 % de
  la unión; antes 202 con 250 m). El refinamiento depura falsas zonas de
  convergencia del píxel grueso; 11 humedales costeros requirieron el
  respaldo de vecindad. Sensibilidad estable: Spearman 0,95–0,99.
- Comunas líderes del núcleo: Casablanca (50), Limache (24), Algarrobo (22),
  Quilpué (15), Valparaíso (15).
- Informe, README y resumen ejecutivo actualizados (fuente topográfica, caveat
  DSM y cifras); comparación 250 m ↔ 30 m preservada en
  `data/resumen_exposicion_v2_twi250.json`.
