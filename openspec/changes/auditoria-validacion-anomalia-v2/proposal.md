# Auditoría de estaciones, corrección de sesgo validada y anomalía v2

## Problem

La auditoría multiagente del 2026-07-18 (paneles meteo/estadística/atribución/
scicomm) detectó que el titular del informe («anomalía +313 %, z = 3,74»)
descansaba en dos debilidades críticas no resueltas:

1. **Sesgo del reciente**: la validación like-for-like (peak-24h modelo vs.
   17 estaciones DMC de la V Región) mostró que Open-Meteo sobreestima el
   evento ~2× e «inunda» la región con ~100 mm casi uniformes cuando lo
   observado tuvo gradiente 30–120 mm. El sesgo estaba diagnosticado pero la
   corrección no estaba elegida ni validada.
2. **z gaussiano sobre precipitación sesgada/cero-inflada**: el 47 % de los
   humedales superaba z > 3, imposible bajo normalidad → los umbrales z
   sobreestiman la rareza. Faltaba una métrica empírica.

Además, la comparación obs–modelo tenía dudas de auditoría abiertas: qué
estaciones se descartaron y por qué, y si la ventana temporal del observado
(24 h móviles del snapshot DMC) correspondía a la del modelo (día calendario).

## Proposed Solution

Cadena de auditoría → corrección → validación → recálculo, en este orden:

1. **Auditoría de estaciones** (`auditoria_estaciones.py`): tabla completa de
   las 32 estaciones DMC con obs, modelo, error, ratio, altitud (DEM 250 m),
   distancia al núcleo del evento (La Dormida) y motivo de descarte; y
   comparación del modelo sobre la **ventana exacta de 24 h** de cada snapshot
   (no el día calendario) para descartar que el «2×» fuera desajuste temporal.
2. **Elección de corrección por leave-one-out** (`correccion_loo.py`): tres
   candidatas — factor regional robusto (mediana obs/modelo), corrección
   espacial de residuos (IDW de log-ratios) y corrección condicionada por
   altitud (OLS en log) — evaluadas fuera de muestra (LOO, n = 14 estaciones
   robustas) con MAE/RMSE/sesgo contra la línea base sin corrección.
3. **Anomalía v2** (`anomalia_v2.py`): climatología homogénea por año
   (Open-Meteo Archive era5_seamless 2003–2023, misma familia que el
   reciente), reciente corregido con la corrección ganadora, percentil
   empírico (posición de Weibull, 21 años) y z homogéneo como indicador
   complementario; traspaso a los 2.916 humedales.
4. **Mapa v2 y titular**: regenerar el mapa de anomalía con los valores
   corregidos y reescribir el titular del informe con percentiles empíricos.

## Decisions

- El descarte de estaciones se limita al criterio espacial (fuera del AOI
  V Región) y de calidad (obs < 5 mm en pleno evento). Los «ceros» se
  atribuyen al snapshot DMC, no a las estaciones: 6 estaciones descartadas de
  RM/O'Higgins también marcan ~0 mm el mismo día.
- La corrección se elige **solo** por desempeño fuera de muestra (LOO), no por
  plausibilidad física a priori.
- La corrección del peak-24h se aplica al acumulado 1–18 jul porque el evento
  15–18 jul aporta >95 % del acumulado (días 1–14 ≈ 0 mm).
- La rareza se reporta con percentil empírico (r/(n+1), 21 años); el z se
  mantiene solo como indicador complementario, nunca como umbral de rareza.
- El titular v1 (+313 %, z = 3,74) se reemplaza, no se elimina: el informe
  documenta la corrección y conserva la trazabilidad v1 → v2.

## Non-goals

- No se recalibra el índice de exposición compuesta 50/50 (pendiente de otra
  iteración; la auditoría lo marcó como moderado, no crítico).
- No se corrige la pseudo-réplica humedal↔celda (los 2.916 humedales siguen
  heredando el valor de ≤157 celdas; documentado).
- No se re-valida la cadena IVT/AR (la auditoría la dio por bien fundamentada).

## Results

- Correspondencia temporal: con la ventana exacta de 24 h el sesgo del modelo
  **empeora** levemente (+49,6 mm, ratio 2,11 vs. 1,97 con día calendario) →
  el «2×» es sesgo real del modelo, no artefacto de ventana.
- Descartes auditados: 16 estaciones fuera de AOI (correcto); 3 en AOI con
  obs ~0 excluidas con respaldo (6 estaciones de RM también marcan ~0 → falla
  del snapshot DMC, no del filtro espacial).
- LOO (n = 14): sin corrección RMSE 54,2 mm / sesgo +49,6; factor regional
  RMSE 26,6; altitud RMSE 26,0; **residuos IDW RMSE 22,0 / sesgo −2,0 mm →
  ganadora**. Diagnóstico coherente: corr(log-ratio, distancia al núcleo)
  = −0,63 vs. corr(log-ratio, altitud) = +0,33.
- Anomalía v2 (157 celdas, clima homogéneo 47,0 mm): reciente medio corregido
  **95,7 mm** (v1: 192,3), anomalía media **+110,7 %** (v1: +313 %), z medio
  **1,29** (v1: 3,74), percentil empírico mediano **P86**; 28 celdas ≥ P90 y
  14 sobre el máximo de 21 años (núcleo: cordillera de la Costa,
  Marga-Marga–La Dormida, coincide con el máximo observado).
- Humedales (2.916): **379 (13 %) ≥ P90**, 214 sobre el máximo del registro;
  z > 3 cae de 1.364 (47 %, auto-falsado) a 54 (1,9 %). El titular del
  informe y el mapa (mapa_anomalia_valpo_v2.png) quedaron actualizados.
- Conclusión de la auditoría: evento real y notable (~2× lo normal, récord
  local de 21 años en su núcleo), pero no el extremo del titular v1.
