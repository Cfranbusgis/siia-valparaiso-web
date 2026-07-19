# Terminología de riesgo: amenaza de inundación (no "prioridad")

## Problem

El índice se rotulaba como «prioridad de inundación/saturación» y la componente
del terreno como «susceptibilidad de acumulación». «Prioridad» es un término de
gestión, no de la ciencia del riesgo, e inducía imprecisión: el producto de la
susceptibilidad del terreno por la anomalía meteorológica del evento (el
detonante) es, en rigor, una **amenaza** (peligro), no una «prioridad».

## Proposed Solution

Renombrar según el marco estándar de riesgo (amenaza × exposición ×
vulnerabilidad = riesgo):

- **«susceptibilidad de acumulación» → «susceptibilidad de inundación»**: la
  predisposición estática del terreno y el suelo (TWI + concavidad + retención
  edáfica + cercanía a ríos).
- **«prioridad de inundación» → «amenaza de inundación»**: el producto de esa
  susceptibilidad por la exposición meteorológica del evento (el detonante).
- Se declara explícitamente que **no es «riesgo»** (falta la vulnerabilidad de
  cada humedal) ni un modelo hidráulico.
- Se conserva «prioridad territorial» donde designa gestión de monitoreo del
  núcleo de exposición (uso legítimo, no referido a inundación).

## Non-goals

- No cambia el cálculo ni los valores; es un renombre conceptual con una
  aclaración de marco.

## Results

- Informe, Figura 7, columnas de datos (`susc_inundacion`, `amenaza_inundacion`,
  `clase_amenaza`) y scripts renombrados. Nota conceptual (amenaza vs
  susceptibilidad vs riesgo) añadida al informe.
