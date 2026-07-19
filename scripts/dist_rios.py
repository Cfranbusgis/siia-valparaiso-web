"""Distancia a la red hidrográfica REAL (ríos de Chile, DGA/BCN) por humedal.

Complementa la distancia a drenaje derivada del DEM (dist_drenaje.py) con la
cartografía oficial de cauces (Hidrografia_V2), que trae orden de Strahler y
tipo. Se calcula, por humedal:
  - distancia al cauce mapeado más cercano (cualquier orden);
  - distancia a un cauce mayor (Strahler >= 4);
y una cercanía normalizada 0..1 para el índice de acumulación.

Salida: rios_rv_32719.gpkg, humedales_distrios.csv
"""
from __future__ import annotations
import zipfile, glob
from pathlib import Path
import numpy as np, geopandas as gpd, pandas as pd
import warnings; warnings.filterwarnings("ignore")

HERE = Path(__file__).resolve().parent
ZIP = Path(r"C:\Users\cfran\Downloads\Hidrografia_V2.zip")
AOI = Path(r"C:\Users\cfran\Desktop\MOD_EToPM-HS\03_inputs\AOI\RV.shp")
HU = HERE.parent / "humedales_inventario_rm_rv_cont.shp"
UTM = 32719

def main():
    tmp = HERE / "_hidro"
    if not list(tmp.glob("**/*.shp")):
        zipfile.ZipFile(ZIP).extractall(tmp)
    shp = glob.glob(str(tmp / "**" / "*.shp"), recursive=True)[0]

    aoi = gpd.read_file(AOI).to_crs(UTM)
    aoi_ll = aoi.to_crs(9155)
    b = aoi_ll.total_bounds
    print("cargando ríos dentro del bbox de la V Región...", flush=True)
    rios = gpd.read_file(shp, bbox=tuple(b)).to_crs(UTM)
    rios = gpd.clip(rios, aoi)
    rios = rios[~rios.geometry.is_empty & rios.geometry.notna()].reset_index(drop=True)
    print(f"segmentos de cauce en RV: {len(rios)}")
    if "STRAHLER_N" in rios:
        print("orden Strahler:", rios["STRAHLER_N"].value_counts().sort_index().to_dict())
    rios.to_file(HERE / "rios_rv_32719.gpkg", driver="GPKG")

    mayores = rios[pd.to_numeric(rios.get("STRAHLER_N"), errors="coerce") >= 4]
    print(f"cauces mayores (Strahler>=4): {len(mayores)}")

    hu = gpd.read_file(HU)
    hu = hu[hu["region"].astype(str).str.contains("Valpara", na=False)].reset_index(drop=True).to_crs(UTM)
    rp = gpd.GeoDataFrame(geometry=hu.representative_point(), crs=UTM)

    # distancia al cauce más cercano (sjoin_nearest)
    dn = gpd.sjoin_nearest(rp, rios[["geometry"]], how="left", distance_col="d")
    dn = dn[~dn.index.duplicated(keep="first")]
    dist_rio = dn["d"].values
    dm = gpd.sjoin_nearest(rp, mayores[["geometry"]], how="left", distance_col="d")
    dm = dm[~dm.index.duplicated(keep="first")]
    dist_mayor = dm["d"].values

    prox = np.clip(1 - (dist_rio - 60) / (1500 - 60), 0, 1)          # cerca de cualquier cauce
    prox_may = np.clip(1 - (dist_mayor - 60) / (3000 - 60), 0, 1)    # cerca de río mayor
    out = pd.DataFrame({
        "nom_humed": hu["nom_humed"].values, "comuna": hu["comuna"].values,
        "dist_rio_m": np.round(dist_rio, 0), "dist_rio_mayor_m": np.round(dist_mayor, 0),
        "prox_rio": np.round(prox, 3), "prox_rio_mayor": np.round(prox_may, 3),
    })
    out.to_csv(HERE / "humedales_distrios.csv", index=False, encoding="utf-8")
    print(f"dist. a río (m) mediana: {np.nanmedian(dist_rio):.0f} | "
          f"humedales a <=150 m de un cauce: {(dist_rio<=150).sum()} "
          f"({100*np.mean(dist_rio<=150):.0f}%)")
    print("-> rios_rv_32719.gpkg, humedales_distrios.csv")

if __name__ == "__main__":
    main()
