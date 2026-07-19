"""Mapa de susceptibilidad de acumulación y prioridad de inundación por humedal."""
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
AOI = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\AOI\RV.shp")
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"

def main():
    s = pd.read_csv(HERE / "humedales_susceptibilidad.csv", encoding="utf-8")
    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True)
    assert len(hu) == len(s)
    hu = hu.to_crs(4326)
    for c in ["susc_inundacion", "amenaza_inundacion", "pctl_empirico", "clase_amenaza"]:
        hu[c] = s[c].values
    aoi = gpd.read_file(AOI).to_crs(4326)
    huc = gpd.clip(hu, aoi)

    fig, ax = plt.subplots(1, 2, figsize=(15, 9))
    aoi.boundary.plot(ax=ax[0], color="#111", linewidth=1.0)
    huc.plot(ax=ax[0], column="susc_inundacion", cmap="YlGnBu", vmin=0, vmax=0.7,
             markersize=5, legend=True,
             legend_kwds={"label": "Susceptibilidad de inundación (TWI + concavidad + suelo + ríos)",
                          "shrink": 0.55})
    ax[0].set_title("Susceptibilidad de inundación\n(dónde el agua converge, se estanca y no drena)", fontsize=10)
    ax[0].set_xlabel("Longitud"); ax[0].set_ylabel("Latitud"); ax[0].set_aspect(1.18)

    aoi.boundary.plot(ax=ax[1], color="#111", linewidth=1.0)
    huc.plot(ax=ax[1], color="#eee", markersize=3)
    import matplotlib.patches as mpatches
    orden=["Muy Baja","Baja","Moderada","Alta","Muy Alta"]
    cols={"Muy Baja":"#2c7bb6","Baja":"#abd9e9","Moderada":"#ffffbf","Alta":"#fdae61","Muy Alta":"#d7191c"}
    pri = huc[huc.pctl_empirico >= 90]
    for k in orden:
        sub=pri[pri.clase_amenaza==k]
        if len(sub): sub.plot(ax=ax[1], color=cols[k], markersize=10)
    ax[1].legend(handles=[mpatches.Patch(color=cols[k], label=k) for k in orden],
                 title="Amenaza de inundacion", loc="lower left", fontsize=8, title_fontsize=8)
    ax[1].set_title("Amenaza de inundacion en 5 clases (humedales >=P90)", fontsize=10)
    ax[1].set_xlabel("Longitud"); ax[1].set_ylabel("Latitud"); ax[1].set_aspect(1.18)

    fig.suptitle("Río atmosférico jul-2026, Valparaíso — susceptibilidad y amenaza de inundación de humedales",
                 fontsize=12, y=0.98)
    fig.tight_layout()
    fig.savefig(HERE / "mapa_susceptibilidad.png", dpi=170)
    plt.close(fig)
    print("-> mapa_susceptibilidad.png")

if __name__ == "__main__":
    main()
