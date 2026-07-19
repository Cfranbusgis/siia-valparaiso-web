# Tasks — auditoria-multicomite-v3

## 1. Ventana de datos al 19-jul 03:00
- [x] 1.1 `fetch_recent.py`: 1–18 completos + 19 parcial (00–03h).
- [x] 1.2 `extend_clim_19.py`: climatología homogénea a 1–19 (era5_seamless).
- [x] 1.3 `patch_grid_recent.py` + re-corrida v2 (anomalía, exposición, mapas, 3D).
- [x] 1.4 Cifras: +121 %, 102 mm, 47,6 mm; 468/16 %, 280, núcleo 218.
- [x] 1.5 Serie diaria y Figura 2 regeneradas (día 18 completo, día 19 parcial 0,0).

## 2. Correcciones y adiciones de la auditoría
- [x] 2.1 % bajo cota de nieve: 85 % → 50,3 % (DEM AW3D30 + nota metodológica).
- [x] 2.2 Definición Ramsar + tipología (Figueroa et al., 2014) + aclaración del
      atributo de la capa (relación con límite urbano, no hidro-geomorfológico).
- [x] 2.3 Distribución de tamaños (81 % < 5 ha) justificando el DEM 30 m.
- [x] 2.4 Naturaleza local/manual del sistema + licencia (CC BY 4.0 / MIT).
- [x] 2.5 Sección «Alcances de mejora» con el backlog priorizado.
- [x] 2.6 Referencias: Ramsar (2013), Figueroa et al. (2014), Wilkinson et al. (2016).

## 3. Entrega
- [x] 3.1 Scripts y datos portados al repo; pipeline extendido.
- [x] 3.2 Change OpenSpec (proposal + spec + tasks).
- [x] 3.3 Commit + push + redespliegue verificado.

## Notas
- Se conserva la fuente MMA 2013 (geoportal 34955), verificada con el usuario;
  no se adopta la etiqueta «2015» de la auditoría.
