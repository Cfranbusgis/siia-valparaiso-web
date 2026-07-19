# Tasks — climatologia-30-anos-hidro

## 1. Baseline de 30 años
- [x] 1.1 `clim_1995_2025.py`: descarga 1995-2002 + 2024-2025, fusiona a 30 años.
- [x] 1.2 Re-corrida v2: normal 43,0 mm; anomalía +145 %; P88; 0 celdas sobre máx.
- [x] 1.3 Comparación de baselines preservada (clim_om_years_2003_2023.npz).

## 2. Corrección del récord
- [x] 2.1 Titular, lead, distribución espacial, interpretación, Figura 3 y
      limitaciones: el evento es muy inusual (P88) pero no un récord; julio de
      2001 fue más lluvioso. Contexto de megasequía declarado.

## 3. Capas hídricas
- [x] 3.1 `dist_rios.py`: distancia a ríos oficiales (DGA, Strahler); 57 % de
      humedales a ≤150 m. Reemplaza el cauce sintético del DEM.
- [x] 3.2 Cuenca (BNA) y acuífero (SHAC) por humedal: 68 % en cuenca del
      Aconcagua; 100 % sobre acuífero (contexto, no discriminante).

## 4. Entrega
- [x] 4.1 Figuras 3, 4 y 7 regeneradas; números actualizados (núcleo 211,
      395/468 en Alta/Muy Alta).
- [x] 4.2 Scripts y datos al repo; commit + push + deploy.
