# Susceptibilidad de acumulación: suelo (CIREN) + concavidad → áreas de inundación

## Problem

El índice de exposición v2 combinaba exposición meteorológica (percentil) con
convergencia topográfica (TWI). No consideraba (a) la morfología de depresiones
donde el agua efectivamente se estanca, ni (b) las propiedades del suelo que
determinan si el agua se retiene o drena en el perfil. Sin esas dos dimensiones
no es posible aproximar dónde el evento produce acumulación o inundación.

## Proposed Solution

Añadir dos capas físicas y combinarlas en un índice de susceptibilidad de
acumulación y una prioridad de inundación/saturación por humedal:

1. **Suelo (CIREN)** (`suelos_ciren.py`, `suelo_retencion.py`): se parsea el KMZ
   del Estudio Agrológico de la V Región (atributos edáficos embebidos en HTML),
   se reproyecta a EPSG:32719 y se extraen textura, permeabilidad, drenaje.
   Del informe agroecológico (PDF) se añaden, por serie, la capacidad de campo
   (humedad a 1/3 atm) y el contenido de arcilla. La densidad aparente no está
   poblada en CIREN; se sustituye por la curva de retención real (capacidad de
   campo + arcilla), físicamente más directa. Retención edáfica 0..1
   (1 = retiene). Validación cruzada: corr(capacidad de campo, textura) = +0,61.
2. **Concavidad / depresiones** (`concavidad_30m.py`): curvatura general y
   profundidad de depresión del DEM AW3D30 (30 m). 24 % de los humedales en
   posición cóncava; 376 en depresiones > 0,5 m.
3. **Combinación** (`susceptibilidad.py`): susceptibilidad de acumulación =
   media de TWI + concavidad + retención edáfica (degradación elegante donde
   falta suelo); prioridad = exposición meteorológica × susceptibilidad.

## Decisions

- La retención de suelo se apoya en la física de la superficie específica: a
  textura más fina, mayor adsorción y retención; la arcilla es el driver primario.
- Cobertura edáfica CIREN: 32 % del inventario, pero 70 % de los humedales
  ≥ P90 (los relevantes para el evento). El resto (altoandinos) queda para el
  complemento HWSD2.
- El índice de acumulación se declara como indicador de prioridad, no como un
  modelo hidrológico de inundación.

## Non-goals

- No se modela caudal, lámina de agua ni conectividad hidrológica.
- No se decodifica aún la HWSD2 (requiere su base de atributos WRB; se enumera
  como alcance de mejora).

## Results

- Índice de prioridad de inundación/saturación por humedal (Figura 7 nueva).
- 159 humedales ≥ P90 con susceptibilidad de acumulación alta; encabezan
  Casablanca (43), Limache (17), Algarrobo (16), Quilpué (14), Valparaíso (12).
- Sección nueva en el informe; referencias CIREN (2016) y HWSD2 (FAO/IIASA, 2023);
  alcance de mejora del complemento edáfico global.
