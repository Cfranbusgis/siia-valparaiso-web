# Tasks — recalibracion-exposicion-compuesta

## 1. Índice v2

- [x] 1.1 `exposicion_v2.py`: expo_met = (percentil − 50)/50 en [0, 1];
      expo_topo = TWI normalizado (2–98); compuesto para w ∈ {0,3; 0,5; 0,7};
      componentes para los 2.916 humedales, evaluación sobre los 379 ≥ P90.
- [x] 1.2 Sensibilidad: Spearman 0,94–0,99; Jaccard «alta» 0,54–0,82; núcleo
      robusto 202 humedales (54 % de la unión); comunas líderes Casablanca /
      Quillota / Quilpué / Limache / Valparaíso.
- [x] 1.3 Productos: `humedales_exposicion_v2.csv`,
      `humedales_p90_exposicion_v2.geojson`, `resumen_exposicion_v2.json`.

## 2. Informe y documentos

- [x] 2.1 Sección «Exposición topográfica combinada» reescrita con el índice
      v2 y la lógica de sensibilidad/núcleo robusto (sitio + informe local).
- [x] 2.2 Tabla comunal compuesta v2 (conjunto ≥ P90, w = 0,5) con recuento de
      humedales por comuna.
- [x] 2.3 Limitación (v) y línea de profundización actualizadas (calibración
      contra anegamiento = extensión pendiente).
- [x] 2.4 README y RESUMEN_EJECUTIVO actualizados (paso 7 del método, fila de
      prioridad territorial en la tabla v1→v2, decisión D8, limitación 5).

## 3. Entrega

- [x] 3.1 Script portado a `scripts/` (rutas vía `config.py`) e integrado a
      `run_pipeline.py`; datos copiados a `data/`.
- [x] 3.2 Commit + push + redespliegue Railway verificado.
