"""Actualiza recent_mm y last_day de anomaly_grid_valpo.csv desde recent_valpo.csv
(nueva ventana 1-18 completo + 19 parcial 00-03h) sin re-descargar la parte v1.

anomalia_v2.py lee de anomaly_grid_valpo.csv solo recent_mm y row/col/lon/lat;
la climatologia v2 viene de clim_om_years.npz. Recalcula tambien las columnas
v1 (anomaly_pct, z_score) por coherencia interna del archivo, aunque no se
publican.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

from config import WORK_DIR as HERE


def main():
    grid = pd.read_csv(HERE / "anomaly_grid_valpo.csv")
    rec = pd.read_csv(HERE / "recent_valpo.csv")
    m = rec.set_index(["row", "col"])[["recent_mm", "cover_days", "last_day"]]
    grid = grid.set_index(["row", "col"])
    grid["recent_mm"] = m["recent_mm"]
    grid["cover_days"] = m["cover_days"]
    grid["last_day"] = m["last_day"]
    grid["anomaly_pct"] = ((grid.recent_mm - grid.clim_mean_mm) /
                           grid.clim_mean_mm * 100).round(1)
    grid["z_score"] = ((grid.recent_mm - grid.clim_mean_mm) /
                       grid.clim_std_mm).round(2)
    grid.reset_index().to_csv(HERE / "anomaly_grid_valpo.csv",
                              index=False, encoding="utf-8")
    print(f"recent_mm media {grid.recent_mm.mean():.1f} mm, "
          f"last_day {grid.last_day.iloc[0]} -> anomaly_grid_valpo.csv")


if __name__ == "__main__":
    main()
