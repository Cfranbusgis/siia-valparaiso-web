"""Climatología observacional CR2MET v2.0 (pr diaria, 1979-2020) para la V Región.

CR2MET es el producto grillado de precipitación restringido con observaciones
para Chile (~5 km). Se usa como climatología independiente (NO cubre el evento
2026, termina en 2020) para: (a) validar el normal era5_seamless que usamos, y
(b) situar el evento corregido contra una referencia observacional.

Extrae, en las 157 celdas de nuestra grilla, el acumulado 1-19 jul por año
(1979-2020), y compara con la climatología era5 y con el evento corregido.

Salida: clim_cr2met_years.npz, resumen_cr2met.json
"""
from __future__ import annotations
import json, zipfile
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
ZIP = Path(r"C:\Users\cfran\Downloads\CR2MET_v2.0_pr_day_1979_2020.zip")
NC = HERE / "CR2MET_pr_v2.0_day_1979_2020_005deg.nc"

def main():
    if not NC.exists():
        print("extrayendo NetCDF (10,6 GB)...", flush=True)
        with zipfile.ZipFile(ZIP) as z:
            z.extract(NC.name, HERE)
    import xarray as xr
    grid = pd.read_csv(HERE / "anomaly_grid_valpo_v2.csv")
    lons = xr.DataArray(grid.lon.values, dims="cell")
    lats = xr.DataArray(grid.lat.values, dims="cell")

    print("abriendo CR2MET...", flush=True)
    ds = xr.open_dataset(NC, chunks={"time": 400})
    # nombre de variable/coords robusto
    pv = "pr" if "pr" in ds else [v for v in ds.data_vars][0]
    latn = "lat" if "lat" in ds.coords else ("latitude" if "latitude" in ds.coords else "y")
    lonn = "lon" if "lon" in ds.coords else ("longitude" if "longitude" in ds.coords else "x")
    da = ds[pv]
    # recortar a la ventana 1-19 jul de cada año
    t = pd.to_datetime(da["time"].values)
    mask = (t.month == 7) & (t.day <= 19)
    da = da.isel(time=np.where(mask)[0])
    years = np.arange(1979, 2021)
    n = len(grid)
    sums = np.full((len(years), n), np.nan)
    tt = pd.to_datetime(da["time"].values)
    for yi, y in enumerate(years):
        sel = da.isel(time=np.where(tt.year == y)[0]).sum("time")
        # muestreo en las 157 celdas por vecino más cercano
        v = sel.sel({latn: lats, lonn: lons}, method="nearest").values
        sums[yi] = v
        if yi % 10 == 0: print(f"  {y}: media {np.nanmean(v):.1f} mm", flush=True)

    np.savez_compressed(HERE / "clim_cr2met_years.npz", sums=sums,
                        years=years, lon=grid.lon.values, lat=grid.lat.values)

    # --- comparaciones ---
    era = np.load(HERE / "clim_om_years.npz")["sums"]           # 1995-2025 era5
    era_mean = np.nanmean(era, axis=0)
    cr_mean = np.nanmean(sums, axis=0)
    # normal WMO 1991-2020 de CR2MET
    m9120 = (years >= 1991) & (years <= 2020)
    cr_9120 = np.nanmean(sums[m9120], axis=0)
    rec = grid["recent_v2_mm"].values
    def pctl(clim):
        ny = np.sum(~np.isnan(clim), axis=0)
        rank = np.sum(clim <= rec[None, :], axis=0)
        return 100.0 * rank / (ny + 1)
    res = {
        "cr2met_media_1979_2020_mm": round(float(np.nanmean(cr_mean)), 1),
        "cr2met_media_1991_2020_mm": round(float(np.nanmean(cr_9120)), 1),
        "era5_media_1995_2025_mm": round(float(np.nanmean(era_mean)), 1),
        "corr_por_celda_cr2met_vs_era5": round(float(np.corrcoef(
            cr_mean[np.isfinite(cr_mean)&np.isfinite(era_mean)],
            era_mean[np.isfinite(cr_mean)&np.isfinite(era_mean)])[0,1]), 3),
        "evento_pctl_mediano_vs_cr2met_9120": round(float(np.nanmedian(pctl(sums[m9120]))), 1),
        "evento_anom_pct_vs_cr2met_9120": round(float(np.nanmean(
            (rec - cr_9120) / cr_9120 * 100)), 1),
        "reciente_v2_media_mm": round(float(np.nanmean(rec)), 1),
    }
    (HERE / "resumen_cr2met.json").write_text(json.dumps(res, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False, indent=2))
    print("-> clim_cr2met_years.npz, resumen_cr2met.json")

if __name__ == "__main__":
    main()
