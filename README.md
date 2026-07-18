# SIIA · Valparaíso — Informe del río atmosférico de julio 2026

Sitio web estático que publica el informe del **Sistema Regional de Inteligencia
Ambiental**: el análisis del río atmosférico (categoría AR4) del 14 al 18 de julio
de 2026 y su expresión territorial en la Región de Valparaíso y sus humedales.

Incluye:

- **`/`** — el informe científico completo (autocontenido, con todas las figuras
  embebidas).
- **`/modelo-3d.html`** — el modelo 3D interactivo del relieve regional con la
  anomalía de precipitación proyectada sobre la superficie.

El sitio es **estático**: un servidor mínimo en Node (sin dependencias) entrega los
archivos de `public/`. Está listo para desplegarse en **Railway**.

El análisis que genera el informe es **reproducible**: ver
[`CONTRIBUTING.md`](CONTRIBUTING.md) para instalar el entorno
(`requirements.txt`), configurar las rutas de datos y ejecutar el pipeline
(`python scripts/run_pipeline.py`).

---

## Estructura

```
siia-valparaiso-web/
├── server.js          # servidor estático (sin dependencias), usa process.env.PORT
├── package.json       # define "npm start"
├── railway.json       # configuración de Railway (Nixpacks)
├── public/            # lo que se sirve
│   ├── index.html         # informe
│   └── modelo-3d.html     # modelo 3D interactivo
├── data/              # datos del análisis (CSV, GeoJSON, resúmenes JSON)
├── sources/           # insumos livianos incluidos (DEM 250 m, AOI RV.shp)
├── scripts/           # pipeline Python + config.py (rutas) + run_pipeline.py
├── requirements.txt   # dependencias Python
├── Makefile           # atajos (make pipeline / site / serve)
└── CONTRIBUTING.md    # cómo reproducir y extender el modelo
```

---

## Probar localmente

Requiere Node 18 o superior.

```bash
npm start
# abre http://localhost:3000
```

(No hay `npm install`: el servidor no tiene dependencias.)

---

## Desplegar en Railway

### Opción A — desde GitHub (recomendada)

1. Sube este repositorio a GitHub (ver más abajo).
2. En [railway.app](https://railway.app), entra con tu cuenta.
3. **New Project → Deploy from GitHub repo** y elige este repositorio.
4. Railway detecta Node automáticamente, ejecuta `npm start` y asigna un puerto
   mediante la variable `PORT` (el servidor ya la respeta). No hay que configurar
   nada más.
5. En **Settings → Networking → Generate Domain** para obtener la URL pública.

### Opción B — con la CLI de Railway

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

No se requieren variables de entorno. Railway inyecta `PORT` automáticamente.

---

## Subir a GitHub

```bash
# dentro de la carpeta del repositorio
git init                      # ya viene inicializado; omitir si corresponde
git add .
git commit -m "Sitio SIIA Valparaíso"

# crea un repo vacío en github.com y luego:
git remote add origin https://github.com/USUARIO/siia-valparaiso-web.git
git branch -M main
git push -u origin main
```

---

## Actualizar el contenido

El informe y el modelo 3D se generan desde el análisis (carpeta `Taller RRNN`).
Para regenerar el sitio tras un cambio:

```bash
python scripts/assemble_web.py   # reconstruye public/index.html y public/modelo-3d.html
git add . && git commit -m "Actualiza informe" && git push
```

Railway redepliega automáticamente con cada `push` a `main`.

---

## Fuentes de datos

ERA5-Land · Open-Meteo (ECMWF-IFS, NCEP-GFS, DWD-ICON, JMA) · Dirección
Meteorológica de Chile y Dirección General de Aeronáutica Civil (Red EMA y
reportes METAR) · Inventario de humedales de la Región de Valparaíso · Modelo
propio MOD_EToPM-HS (climatología ERA5-Land 2003–2023) · escala de ríos
atmosféricos de Ralph et al. (2019).

> Los datos de la ventana reciente incorporan información operacional sujeta a
> revisión cuando ERA5-Land consolide el periodo analizado.
