# Tasks — suelo-concavidad-inundacion

## 1. Suelo CIREN
- [x] 1.1 Parseo del KMZ (atributos HTML) y reproyección a EPSG:32719.
- [x] 1.2 Retención edáfica: textura + permeabilidad + drenaje (KMZ) +
      capacidad de campo + arcilla (PDF por serie). Densidad aparente no
      disponible en CIREN → sustituida por curva de retención.
- [x] 1.3 Cobertura 32 % (70 % en ≥ P90); validación corr(cap. campo, textura) = +0,61.

## 2. Concavidad / depresiones
- [x] 2.1 Curvatura y profundidad de depresión del DEM AW3D30 (30 m).
- [x] 2.2 24 % cóncavos; 376 en depresiones > 0,5 m.

## 3. Integración y entrega
- [x] 3.1 Susceptibilidad de acumulación + prioridad de inundación por humedal.
- [x] 3.2 Sección nueva + Figura 7 en el informe; refs CIREN (2016) y HWSD2.
- [x] 3.3 Datos y scripts al repo; commit + push + deploy.

## Pendiente (alcance de mejora)
- [ ] Complemento edáfico global HWSD2 (decodificar SMU→WRB) para el ~30 % de
      ≥ P90 altoandino sin CIREN.
