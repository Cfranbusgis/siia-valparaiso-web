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

    from map_deco import add_grid, add_north, add_scalebar
    import matplotlib.patches as mpatches
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import Normalize
    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    def deco7(a, lab):
        add_grid(a); add_scalebar(a, 50, pos="center"); add_north(a, y=0.86)
        a.text(0.97, 0.985, lab, transform=a.transAxes, ha="right", va="top",
               fontsize=15, fontweight="bold", zorder=25,
               bbox=dict(boxstyle="round,pad=0.28", fc="white", ec="#333", lw=1.1))

    fig, ax = plt.subplots(1, 2, figsize=(15, 8.6))

    # --- Panel A: susceptibilidad (colorbar inset, no encoge el eje) ---
    aoi.boundary.plot(ax=ax[0], color="#111", linewidth=1.0)
    huc.plot(ax=ax[0], column="susc_inundacion", cmap="YlGnBu", vmin=0, vmax=0.7, markersize=6)
    cax = inset_axes(ax[0], width="3.4%", height="34%", loc="lower right", borderpad=1.6)
    cb = fig.colorbar(ScalarMappable(norm=Normalize(0, 0.7), cmap="YlGnBu"), cax=cax)
    cb.set_label("Susceptibilidad de inundación", fontsize=8); cb.ax.tick_params(labelsize=7)
    ax[0].set_title("Susceptibilidad de inundación",
                    fontsize=11.5, fontweight="bold")
    ax[0].set_xlabel("Longitud"); ax[0].set_ylabel("Latitud"); ax[0].set_aspect(1.18)
    deco7(ax[0], "A")

    # --- Panel B: amenaza en 5 clases (leyenda abajo-derecha) ---
    aoi.boundary.plot(ax=ax[1], color="#111", linewidth=1.0)
    huc.plot(ax=ax[1], color="#eee", markersize=3)
    orden=["Muy Baja","Baja","Moderada","Alta","Muy Alta"]
    cols={"Muy Baja":"#2c7bb6","Baja":"#abd9e9","Moderada":"#ffffbf","Alta":"#fdae61","Muy Alta":"#d7191c"}
    pri = huc[huc.pctl_empirico >= 90]
    for k in orden:
        sub=pri[pri.clase_amenaza==k]
        if len(sub): sub.plot(ax=ax[1], color=cols[k], markersize=10)
    ax[1].legend(handles=[mpatches.Patch(color=cols[k], label=k) for k in orden],
                 title="Amenaza de inundación", loc="lower right", fontsize=8, title_fontsize=8,
                 framealpha=0.95)
    ax[1].set_title("Amenaza de inundación en 5 clases",
                    fontsize=11.5, fontweight="bold")
    ax[1].set_xlabel("Longitud"); ax[1].set_ylabel("Latitud"); ax[1].set_aspect(1.18)
    deco7(ax[1], "B")

    fig.suptitle("Río atmosférico jul-2026, Valparaíso — susceptibilidad y amenaza de inundación de humedales",
                 fontsize=12.5, fontweight="bold", y=0.99)
    fig.tight_layout()
    fig.savefig(HERE / "mapa_susceptibilidad.png", dpi=170)
    plt.close(fig)
    print("-> mapa_susceptibilidad.png")

if __name__ == "__main__":
    main()
