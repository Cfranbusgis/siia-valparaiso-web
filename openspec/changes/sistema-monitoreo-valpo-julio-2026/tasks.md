# Tareas

## 1. Análisis de la anomalía
- [x] 1.1 Climatología 1–17 jul desde el modelo (ERA5-Land 2003–2020)
- [x] 1.2 Ventana reciente (Open-Meteo, tiempo casi real)
- [x] 1.3 Anomalía por celda (% y z) recortada al AOI

## 2. Humedales
- [x] 2.1 Cruce con el inventario regional (2.916 humedales)
- [x] 2.2 Identificación de z > 2 (1.848) y z > 3 (1.026)
- [x] 2.3 Exportación a GeoJSON para QGIS

## 3. Topografía
- [x] 3.1 Pendiente y acumulación de flujo D8 (DEM 250 m)
- [x] 3.2 Índice topográfico de humedad (TWI)
- [x] 3.3 Exposición compuesta (483 humedales de alta exposición)

## 4. Río atmosférico (motor)
- [x] 4.1 Cálculo propio del IVT (niveles 1000–300 hPa)
- [x] 4.2 Clasificación en la escala AR (AR4)
- [x] 4.3 Nivel de congelación vs. tipo de precipitación

## 5. Validación
- [x] 5.1 Observación DMC/DGAC (API oficial, agua caída 24 h)
- [x] 5.2 Consenso multi-modelo (ECMWF, GFS, ICON, JMA)
- [x] 5.3 Reportes METAR (SCVM, SCRD, SCEL)

## 6. Entregables
- [x] 6.1 Informe HTML científico (6 figuras)
- [x] 6.2 Modelo 3D interactivo del relieve
- [x] 6.3 Repositorio GitHub + servidor Node + config Railway

## 7. Reproducibilidad
- [x] 7.1 config.py con rutas por variables de entorno
- [x] 7.2 requirements.txt con versiones verificadas
- [x] 7.3 run_pipeline.py + Makefile
- [x] 7.4 Insumos livianos en sources/ (DEM + AOI)
- [x] 7.5 CONTRIBUTING.md

## 8. Pendiente
- [x] 8.1 Empujar a GitHub las mejoras de reproducibilidad (verificado
      19-jul-2026: `main` sincronizado con `origin/main`, sin commits locales
      pendientes)
- [ ] 8.2 Nowcasting: acoplar IVT pronosticado (anticipación)
- [ ] 8.3 Integrar NDVI/LST (condición de humedales)
