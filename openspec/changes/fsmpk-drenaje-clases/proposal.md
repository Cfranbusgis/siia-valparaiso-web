# Distancia a drenaje y clases de prioridad (elementos de fsm-pk)

## Problem

El índice de susceptibilidad de acumulación (TWI + concavidad + suelo) no
incorporaba la **cercanía a la red de drenaje**, un predictor estándar de
inundación (proximidad a cauces = mayor riesgo de desborde), y reportaba la
prioridad como un valor continuo poco accionable para gestión. El repositorio
`waleedgeo/fsm-pk` (flood susceptibility mapping por ML) usa ambos elementos.

## Proposed Solution

Adoptar dos elementos de fsm-pk, sin copiar su código (licencia CC BY-NC-SA):

1. **Distancia a la red de drenaje** (`dist_drenaje.py`): se extraen los cauces
   del flujo D8 (acumulación ≥ 1.000 celdas) del DEM AW3D30 (30 m) y se calcula
   la distancia euclidiana al cauce más cercano; se normaliza a una cercanía
   0..1 y se suma como cuarto componente de la susceptibilidad de acumulación.
2. **Esquema de 5 clases** (`susceptibilidad.py`): la prioridad de inundación se
   clasifica en Muy Baja / Baja / Moderada / Alta / Muy Alta por quintiles, como
   en los mapas de susceptibilidad a inundación.

## Decisions

- Se documenta también el resultado de investigar la **API de la DGA**: el
  instructivo aportado (Res. 2.170/2025) regula el **envío** de datos de
  extracciones por parte de los usuarios de agua, **no** es una fuente para
  obtener un inventario de inundaciones. El camino a un modelo supervisado
  (fsm-pk completo) requiere etiquetas de crecidas/anegamiento de SENAPRED o
  caudales del Sistema Nacional de Información del Agua; se deja como alcance de
  mejora.

## Non-goals

- No se entrena aún el modelo supervisado (falta inventario de inundaciones).
- No se calcula HAND (Height Above Nearest Drainage); la distancia horizontal
  a drenaje es el proxy adoptado, como en fsm-pk.

## Results

- Susceptibilidad de acumulación con 4 componentes (TWI + concavidad + suelo +
  cercanía a drenaje). El 50 % de los humedales está a ≤ 120 m de un cauce.
- Prioridad de inundación en 5 clases: de los 468 humedales ≥ P90, **417 quedan
  en clase Alta o Muy Alta**. Figura 7 actualizada con la leyenda de 5 clases.
- Referencia fsm-pk (Ahmad et al., 2024) y alcance de mejora del modelo
  supervisado con su fuente de etiquetas aclarada.
