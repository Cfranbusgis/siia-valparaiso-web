# Tasks — auditoria-validacion-anomalia-v2

## 1. Auditoría de estaciones y correspondencia temporal

- [x] 1.1 Tabla completa de 32 estaciones DMC (`auditoria_estaciones.csv`):
      obs, modelo (ventana exacta y día calendario), error, ratio, altitud
      (DEM 250 m), distancia al núcleo (La Dormida), flag de descarte.
- [x] 1.2 Auditar descartes: 16 fuera de AOI (RM/O'Higgins; correcto), 3 en
      AOI con obs ~0 en pleno evento (Zapallar Catapilco, Catemu, Los
      Libertadores) marcadas SOSPECHOSAS; 6 estaciones fuera de AOI también
      marcan ~0 → el problema de ceros es del snapshot DMC, no del filtro.
- [x] 1.3 Correspondencia temporal: modelo horario sumado sobre la ventana
      móvil exacta de cada snapshot (UTC−4). Resultado: sesgo +49,6 mm /
      ratio 2,11 (peor que día calendario: +44,2 / 1,97) → el 2× NO es
      artefacto de ventana; es sesgo real del modelo.

## 2. Corrección de sesgo elegida por validación fuera de muestra

- [x] 2.1 LOO n=14 estaciones robustas (`correccion_loo.py`,
      `resultados_loo.csv`, `loo_predicciones.csv`).
- [x] 2.2 Resultados (MAE / RMSE / sesgo, mm): sin corrección 50,0 / 54,2 /
      +49,6; factor regional 23,1 / 26,6 / −3,7; altitud 20,3 / 26,0 / −5,1;
      **residuos IDW 17,0 / 22,0 / −2,0 → ganadora**.
- [x] 2.3 Diagnóstico: corr(log obs/mod, dist. núcleo) = −0,63 domina sobre
      altitud (+0,33) → coherente con que gane la corrección espacial.

## 3. Anomalía v2 sobre climatología homogénea

- [x] 3.1 Descarga por año 2003–2023 (1–18 jul) por celda, era5_seamless
      (`clim_om_years.npz`; la Fase 1 solo guardó media/std).
- [x] 3.2 Reciente corregido: `recent_v2 = recent × exp(IDW log-ratio)`
      (14 estaciones, potencia 2).
- [x] 3.3 Percentil empírico (Weibull r/(n+1), 21 años) + z homogéneo por
      celda (`anomaly_grid_valpo_v2.csv`).
- [x] 3.4 Traspaso a humedales (`humedales_valpo_anomalia_v2.csv`) y resumen
      (`resumen_valpo_v2.json`).

## 4. Productos v2

- [x] 4.1 Mapa v2 (`mapa_anomalia_valpo_v2.png`): anomalía corregida +
      percentil empírico.
- [x] 4.2 Titular del informe reescrito con cifras v2 y nota de corrección
      (trazabilidad v1 → v2 documentada en el propio informe).
- [x] 4.3 Figura de humedales v2 (`mapa_humedales_valpo_v2.png`, percentil
      empírico en lugar de z) y tabla comunal reordenada por percentil
      (corrige el artefacto de base seca: Papudo/La Ligua/Petorca →
      Limache/Villa Alemana/Concón/Valparaíso/Quillota).
- [x] 4.5 Figura 5 / modelo 3D regenerados con la anomalía corregida (drape
      v2, escala de la Figura 3; puntos = humedales ≥ P90 por exposición
      compuesta) — cerrado el último producto anclado a v1.
- [x] 4.6 Sección «Auditoría del análisis y trazabilidad de versiones»
      incorporada al informe: panel de cuatro especialidades, contrauditoría
      empírica (1 hallazgo refutado, 2 confirmados y corregidos), auditoría
      externa → topografía 30 m.
- [x] 4.4 Reescritura de las secciones profundas del informe en tono técnico:
      validación observacional y corrección de sesgo (con tabla LOO),
      distribución espacial, exposición de humedales por percentil,
      exposición compuesta marcada como referencia v1, interpretación
      territorial, limitaciones metodológicas v2 y método/trazabilidad.
      Aplicada al sitio (`public/index.html`) y al informe local.

## 5. Documentación y entrega

- [x] 5.1 Este change de OpenSpec (proposal + deltas de spec + tasks).
- [x] 5.2 Actualizar memoria de auditoría del proyecto.
- [x] 5.3 Scripts v2 portados al repo (`scripts/`, rutas vía `config.py`) e
      integrados a `run_pipeline.py`; productos v2 copiados a `data/`
      (auditoría, métricas LOO, grilla y humedales v2, clima por año).
- [x] 5.4 README reescrito como informe técnico de entrega (resumen v1→v2,
      método, reproducibilidad, trazabilidad).
- [x] 5.5 Commit y push a `main` (auto-despliegue en Railway).
