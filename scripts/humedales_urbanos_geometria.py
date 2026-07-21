"""Geometria real de los 21 humedales urbanos reconocidos de Valparaiso
(data/humedales_urbanos_valpo.csv, TODOS los tipos: natural, artificial,
mixto y sin_dato -- el inventario ya no excluye ninguno), descargada desde
el expediente publico de cada solicitud en el Portal de Humedales del MMA.

Mecanismo (verificado, sin JavaScript, sin login):
  POST /HumedalesUrbanos/DescargarExpediente  {Documentos:[ids], IDSolicitud:id}
  -> ZIP con los documentos seleccionados (blob, sin auth).
  Encontrado leyendo /Scripts/HumedalesUrbanos/TablasDocumentosExpediente.js.

Cada expediente trae MUCHAS versiones de la cartografia (borradores y
revisiones de todo el tramite). SELECCION_ARCHIVO abajo fue construida a
mano, revisando el listado completo de documentos de cada expediente
(20/21-jul-2026), priorizando archivos marcados "VF" (version final),
"rectificada" u "Oficial" en su nombre, y validando por area contra la
superficie ORIGINAL solicitada cuando hay mas de un candidato -- ver casos
#1237 (bug real corregido: se descarto "Diferencia.shp", un subproducto de
analisis GIS) y #167 (3 versiones con reduccion progresiva 33.8->5.6->2.3
ha; la que coincide con la superficie original es la mas vieja, NO la
final -- coincidir con el numero original es señal de borrador, no de
version definitiva). Nivel de confianza declarado por caso:
  alta               = nombre de archivo marca explicitamente version final,
                        y/o area coincide con la superficie original
  alta (rectificada) = version final con boundary corregido respecto de la
                        superficie ORIGINAL solicitada (mismatch esperado)
  media               = sin marca explicita, pero es el ultimo cartografico
                        antes de la resolucion de reconocimiento
  baja                = ningun candidato disponible reconcilia con la
                        superficie declarada -- requiere revision manual,
                        ver openspec/changes/humedales-urbanos-mma/tasks.md

Caso especial #163 (Laguna El Criquet y Quebrada Honda, mixto): la unica
cartografia oficial disponible es UN solo poligono combinado (2,57 ha,
atributo Nombre="El Criquet y Quebrada Honda"), no dos poligonos separables
por tipo. No se puede aislar la parte artificial de la natural con los
datos publicos disponibles -- se mantiene como un unico registro tipo_final
"mixto", documentado.

Salida:
  data/humedales_urbanos_geom.geojson       (WGS84 / EPSG:4326, para el mapa web)
  data/humedales_urbanos_valpo.shp (+sidecars) (CRS nativo UTM 19S / EPSG:32719,
                                                 entregable del inventario)
"""
from __future__ import annotations
import io, json, subprocess, time, unicodedata, zipfile
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import geopandas as gpd
import pandas as pd

HERE = Path(__file__).resolve().parent
WORK = HERE.parent / "data" / "_geom_tmp"
OUT = HERE.parent / "data" / "humedales_urbanos_geom.geojson"
OUT_SHP = HERE.parent / "data" / "humedales_urbanos_valpo.shp"
CRS_NATIVO = 32719  # UTM 19S / WGS84 -- verificado en los .prj de los shapefiles del expediente
BASE = "https://sistemahumedales.mma.gob.cl/HumedalesUrbanos"
HEADERS = {"User-Agent": "Mozilla/5.0 (tesis-humedales-valparaiso)"}
SEVENZIP = r"C:\Program Files\7-Zip\7z.exe"

# id_solicitud -> (patron de nombre de archivo objetivo, tipo, confianza,
#                   archivo_interno opcional)
# tipo: "shp" (shapefile suelto, se piden todos los sidecars del mismo nombre
#        base) | "archive" (un unico .rar/.zip a extraer con 7z; si el
#        archivo trae mas de un .shp no-vertices, archivo_interno indica
#        cual usar por nombre, en vez de tomar el primero encontrado --
#        asi se evita repetir el bug de #1237)
SELECCION_ARCHIVO = {
    5:    ("Hu_Quirilluca_VF.shp", "shp", "alta", None),
    6:    ("Hu_LosMaitenesCampiche_VF.shp", "shp", "alta", None),
    7:    ("Hu_ReservaNaturalMunicipalPiedrasBlancas_VF.shp", "shp", "alta", None),
    15:   ("Hu_EsteroQuilpue_VF.shp", "shp", "alta", None),
    20:   ("Hu_ElLitre_VF.shp", "shp", "alta", None),
    28:   ("HU_LosMolles_VF.zip", "archive", "alta", None),
    32:   ("Hu_EsteroQuilpueSectorQuilpueVF.shp", "shp", "alta", None),
    43:   ("Hu_Mayaca_VF.shp", "shp", "alta", None),
    47:   ("Hu_CanalWaddington_VF.shp", "shp", "alta", None),
    48:   ("Hu_EsteroAguaSalada_VF.shp", "shp", "alta", None),
    67:   ("Hu_Mantagua_VF.shp", "shp", "alta", None),
    # Estos 6 traen boundary "rectificada" respecto de la superficie ORIGINAL
    # solicitada (el campo del formulario dice explicitamente "originales"):
    # el area de la geometria NO deberia coincidir con superficie_ha del CSV,
    # eso es lo esperado tras la correccion tecnica del limite, no un error.
    164:  ("Cartografía Oficial HU Estero El Jote.rar", "archive", "alta (rectificada)", None),
    169:  ("Archivos cartograficos.rar", "archive", "alta (rectificada)", None),
    170:  ("Cartografía rectificada HU Kan Kan.rar", "archive", "alta (rectificada)", None),
    177:  ("Cartografía Rectificada HU Entre Cerros.zip", "archive", "alta (rectificada)", None),
    1222: ("Cartografia_HU_SistemadeLagunasDeLllolleo_OjosdeMar_VF.zip", "archive", "alta (rectificada)", None),
    # El_Bato: dentro del zip "Cartografía rectificada" hay 5 .shp no-vertices
    # candidatos ("Diferencia.shp", "El_Bato_Art8.shp", "El_Bato_CMS.shp",
    # "El_Bato_VF.shp", "Polígono_El_Bato_VF.shp"). La seleccion automatica
    # original tomaba el primero encontrado ("Diferencia.shp", un subproducto
    # de analisis GIS, NO el limite del humedal) -- bug real. Validado por
    # area contra la superficie declarada: "Polígono_El_Bato_VF.shp" da
    # ratio 1.00; ahora se fija explicitamente via archivo_interno.
    1237: ("Cartografía rectificada.zip", "archive", "alta (validada por área)", "Polígono_El_Bato_VF.shp"),
    # Reñaca: ninguno de los 2 candidatos ("...ART8.shp" 15,1 ha,
    # "Final CMS/..._VF.shp" 16,9 ha) coincide con las 233,4 ha declaradas.
    # Sin archivo adicional que lo resuelva -- ver tasks.md, requiere
    # revisión manual de la resolución oficial (Res Ex 5196).
    162:  ("848 archivos cartograficos.zip", "archive", "baja (superficie no coincide, ver tasks.md)",
           "HU_EsteroReñaca_VF.shp"),
    # Tranque Cerro La Huinca (artificial): archivo suelto limpio, área 0,127
    # ha = declarada exacta.
    44:   ("Hu_TranqueCerroLaHuinca_VF.shp", "shp", "alta", None),
    # El Batro (artificial): 3 versiones en el expediente (33,84 -> 5,64 ->
    # 2,26 ha). La que coincide con la superficie ORIGINAL (33,84) es la más
    # vieja (folio 049); la "VF" al final del expediente (folio 486, 2,26 ha)
    # es la reducción final tras la revisión -- mismo patrón que los demás
    # "rectificada", no un error.
    167:  ("486 Archivos Cartograficos.zip", "archive", "alta (rectificada)", "HU_ElBatro_VF.shp"),
    # Laguna El Criquet y Quebrada Honda (mixto): único polígono combinado
    # disponible (2,57 ha, atributo Nombre="El Criquet y Quebrada Honda");
    # no se puede separar la parte artificial de la natural con la
    # cartografía pública disponible -- documentado, no forzado.
    163:  ("175 Cartografía Oficial HU Laguna El Criquet y Quebrada Honda.zip", "archive",
           "alta (mixto no separable, ver proposal.md)", None),
}

def norm(s):
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()

def listar_documentos(id_solicitud):
    r = requests.get(f"{BASE}/DetailsPublico/{id_solicitud}", headers=HEADERS, timeout=30)
    r.encoding = "utf-8"
    soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")
    table = soup.find(id="doc-publicos-table")
    docs = []
    if table and table.find("tbody"):
        for tr in table.find("tbody").find_all("tr"):
            cb = tr.find("input", class_="documento-publico")
            tds = tr.find_all("td")
            if cb and len(tds) >= 2:
                docs.append((cb["value"], tds[1].get_text(strip=True)))
    return docs

def descargar(id_solicitud, doc_ids):
    r = requests.post(f"{BASE}/DescargarExpediente",
                       data={"Documentos": doc_ids, "IDSolicitud": str(id_solicitud)},
                       headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.content

def resolver_geometria(id_solicitud, patron, tipo, dest, archivo_interno=None):
    docs = listar_documentos(id_solicitud)
    if tipo == "shp":
        base = norm(patron.rsplit(".", 1)[0])
        elegidos = [(v, n) for v, n in docs if norm(n).startswith(base)]
        if not elegidos:
            return None, f"no se encontró ningún sidecar para '{patron}'"
        zbytes = descargar(id_solicitud, [v for v, _ in elegidos])
        zipfile.ZipFile(io.BytesIO(zbytes)).extractall(dest)
        shp = list(dest.glob("*.shp"))
        if not shp:
            return None, "el ZIP no contenía .shp"
        return shp[0], None
    else:  # archive
        match = [(v, n) for v, n in docs if norm(patron) in norm(n) or norm(n) in norm(patron)]
        if not match:
            return None, f"no se encontró el archivo '{patron}'"
        v, nombre_real = match[0]
        zbytes = descargar(id_solicitud, [v])
        outer = dest / "outer"; outer.mkdir(exist_ok=True)
        zipfile.ZipFile(io.BytesIO(zbytes)).extractall(outer)
        inner = list(outer.glob("*.rar")) + list(outer.glob("*.zip"))
        if not inner:
            return None, f"'{nombre_real}' no era un .rar/.zip anidado"
        subprocess.run([SEVENZIP, "x", str(inner[0]), f"-o{dest}", "-y"],
                        check=True, capture_output=True)
        if archivo_interno:
            cands = [p for p in dest.rglob("*.shp") if norm(p.name) == norm(archivo_interno)]
            if cands:
                return cands[0], None
            return None, f"archivo_interno '{archivo_interno}' no encontrado tras extraer '{nombre_real}'"
        shp = [p for p in dest.rglob("*.shp") if "vertic" not in norm(p.name)]
        if len(shp) > 1:
            return None, (f"{len(shp)} candidatos .shp sin desambiguar "
                           f"({[p.name for p in shp]}) -- especificar archivo_interno")
        if shp:
            return shp[0], None
        kmz = list(dest.rglob("*.kmz")) + list(dest.rglob("*.kml"))
        if kmz:
            return kmz[0], None
        return None, f"'{nombre_real}' extraído pero sin .shp/.kmz de polígono dentro"

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    todos = pd.read_csv(HERE.parent / "data" / "humedales_urbanos_valpo.csv")
    gdfs, fallos, sin_geometria = [], [], []

    for _, row in todos.iterrows():
        iid = int(row.id_solicitud)
        if iid not in SELECCION_ARCHIVO:
            sin_geometria.append((iid, row.nombre, row.tipo_final)); continue
        patron, tipo, confianza, archivo_interno = SELECCION_ARCHIVO[iid]
        dest = WORK / str(iid)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"#{iid} {row.nombre} -> {patron} ({tipo}, confianza {confianza})")
        try:
            geo_file, err = resolver_geometria(iid, patron, tipo, dest, archivo_interno)
        except Exception as e:
            geo_file, err = None, str(e)
        if err:
            print(f"    FALLO: {err}")
            fallos.append((iid, row.nombre, err)); continue

        g = gpd.read_file(geo_file)
        if g.crs is None:
            g = g.set_crs(CRS_NATIVO)
        g["id_solicitud"] = iid
        g["nombre"] = row.nombre
        g["comuna"] = row.comuna
        g["tipo_clasificacion"] = row.tipo_final
        g["archivo_fuente"] = geo_file.name
        g["confianza_geometria"] = confianza
        gdfs.append(g[["id_solicitud", "nombre", "comuna", "tipo_clasificacion",
                        "archivo_fuente", "confianza_geometria", "geometry"]].to_crs(CRS_NATIVO))
        print(f"    OK: {len(g)} geometría(s) desde {geo_file.name}")
        time.sleep(0.4)

    if gdfs:
        final = pd.concat(gdfs, ignore_index=True)
        final = gpd.GeoDataFrame(final, geometry="geometry", crs=CRS_NATIVO)

        final.to_crs(4326).to_file(OUT, driver="GeoJSON")  # GeoJSON exige WGS84 (RFC 7946)
        print(f"\n-> {OUT} ({len(final)} geometrías de {final['id_solicitud'].nunique()} humedales, WGS84)")

        # nombres de columna <=10 caracteres para el formato .shp (dbf)
        shp_cols = final.rename(columns={
            "id_solicitud": "id", "tipo_clasificacion": "tipo",
            "archivo_fuente": "archivo", "confianza_geometria": "confianza",
        })
        shp_cols.to_file(OUT_SHP, driver="ESRI Shapefile")
        print(f"-> {OUT_SHP} ({len(shp_cols)} geometrías, CRS nativo EPSG:{CRS_NATIVO})")

    if sin_geometria:
        print(f"\n{len(sin_geometria)} sin geometría en el expediente público (sin cartografía disponible):")
        for iid, nombre, tipo in sin_geometria:
            print(f"  #{iid} {nombre} ({tipo})")
    if fallos:
        print(f"\n{len(fallos)} fallos:")
        for iid, nombre, err in fallos:
            print(f"  #{iid} {nombre}: {err}")

if __name__ == "__main__":
    main()
