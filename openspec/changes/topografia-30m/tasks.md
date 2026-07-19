# Tasks — topografia-30m

## 1. DEM 30 m

- [x] 1.1 `prep_dem30.py`: verificación de CRS del export GEE (EPSG:4326),
      mosaico de las 2/16 teselas que intersectan el AOI, reproyección a
      EPSG:32719 @ 30 m (bilineal) y máscara RV.shp →
      `DEM_AW3D30_30m_UTM19S_RV.tif` (73 MB, no versionado).
- [x] 1.2 Sanidad contra DEM 250 m: media 1.234 vs 1.233 m; máx 5.945 vs
      5.828 m.

## 2. Cadena topográfica y exposición

- [x] 2.1 `topo_30m.py`: pendiente, D8, TWI a 30 m (17,8 M celdas, 73 s);
      `twi_valpo_30m.tif`, `slope_valpo_30m.tif`, `resumen_topo_30m.json`.
- [x] 2.2 `exposicion_v2.py`: TWI 30 m con respaldo automático a 250 m;
      muestreo con vecino válido más cercano (11 humedales costeros).
- [x] 2.3 Resultado: núcleo robusto 202 → **172** (46 % de la unión);
      Spearman 0,95–0,99; comparación 250↔30 m preservada
      (`resumen_exposicion_v2_twi250.json`).

## 3. Documentos y entrega

- [x] 3.1 Informe (sitio + local): sección topográfica con fuente AW3D30
      30 m, caveat DSM, cifras 172 y tabla comunal actualizada.
- [x] 3.2 README y RESUMEN_EJECUTIVO actualizados.
- [x] 3.3 Scripts portados al repo con omisión limpia si faltan insumos
      externos; integrados a `run_pipeline.py`; datos a `data/`.
- [x] 3.4 Commit + push + redespliegue verificado.
