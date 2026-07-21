"""Geometria real de los 18 humedales urbanos reconocidos (natural + sin dato)
de data/humedales_urbanos_valpo_natural.csv, descargada desde el expediente
publico de cada solicitud en el Portal de Humedales del MMA.

Mecanismo (verificado, sin JavaScript, sin login):
  POST /HumedalesUrbanos/DescargarExpediente  {Documentos:[ids], IDSolicitud:id}
  -> ZIP con los documentos seleccionados (blob, sin auth).
  Encontrado leyendo /Scripts/HumedalesUrbanos/TablasDocumentosExpediente.js.

Cada expediente trae MUCHAS versiones de la cartografia (borradores y
revisiones de todo el tramite). SELECCION_ARCHIVO abajo fue construida a
mano, revisando el listado completo de documentos de cada uno de los 18
expedientes (20-jul-2026), priorizando archivos marcados "VF"
(version final), "rectificada" u "Oficial" en su nombre, o -- cuando no
existe esa marca -- el ultimo documento cartografico antes de la resolucion
que reconoce el humedal. Nivel de confianza declarado por caso:
  alta  = nombre de archivo marca explicitamente que es la version final
  media = sin marca explicita, pero es el ultimo cartografico antes de la
          resolucion de reconocimiento (Estero El Totoral, id 169)
  baja  = expediente con multiples cartografias en distintas rondas de
          correccion, SIN ninguna marcada como final/rectificada
          (Estero Reñaca, id 162) -- requiere revision manual, ver
          openspec/changes/humedales-urbanos-mma/tasks.md tarea 5.4.

Salida: data/humedales_urbanos_geom.geojson (WGS84 / EPSG:4326).
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
BASE = "https://sistemahumedales.mma.gob.cl/HumedalesUrbanos"
HEADERS = {"User-Agent": "Mozilla/5.0 (tesis-humedales-valparaiso)"}
SEVENZIP = r"C:\Program Files\7-Zip\7z.exe"

# id_solicitud -> (patron de nombre de archivo objetivo, tipo, confianza)
# tipo: "shp" (shapefile suelto, se piden todos los sidecars del mismo nombre
#        base) | "archive" (un unico .rar/.zip a extraer con 7z)
SELECCION_ARCHIVO = {
    5:    ("Hu_Quirilluca_VF.shp", "shp", "alta"),
    6:    ("Hu_LosMaitenesCampiche_VF.shp", "shp", "alta"),
    7:    ("Hu_ReservaNaturalMunicipalPiedrasBlancas_VF.shp", "shp", "alta"),
    15:   ("Hu_EsteroQuilpue_VF.shp", "shp", "alta"),
    20:   ("Hu_ElLitre_VF.shp", "shp", "alta"),
    28:   ("HU_LosMolles_VF.zip", "archive", "alta"),
    32:   ("Hu_EsteroQuilpueSectorQuilpueVF.shp", "shp", "alta"),
    43:   ("Hu_Mayaca_VF.shp", "shp", "alta"),
    47:   ("Hu_CanalWaddington_VF.shp", "shp", "alta"),
    48:   ("Hu_EsteroAguaSalada_VF.shp", "shp", "alta"),
    67:   ("Hu_Mantagua_VF.shp", "shp", "alta"),
    # Estos 6 traen boundary "rectificada" respecto de la superficie ORIGINAL
    # solicitada (el campo del formulario dice explicitamente "originales"):
    # el area de la geometria NO deberia coincidir con superficie_ha del CSV,
    # eso es lo esperado tras la correccion tecnica del limite, no un error.
    164:  ("Cartografía Oficial HU Estero El Jote.rar", "archive", "alta (rectificada)"),
    169:  ("Archivos cartograficos.rar", "archive", "alta (rectificada)"),
    170:  ("Cartografía rectificada HU Kan Kan.rar", "archive", "alta (rectificada)"),
    177:  ("Cartografía Rectificada HU Entre Cerros.zip", "archive", "alta (rectificada)"),
    1222: ("Cartografia_HU_SistemadeLagunasDeLllolleo_OjosdeMar_VF.zip", "archive", "alta (rectificada)"),
    # El_Bato: "Diferencia.shp" (producto de analisis GIS, no el limite) fue
    # descartado tras validar area; "Polígono_El_Bato_VF.shp" da ratio 1.00
    # contra la superficie declarada -- validado.
    1237: ("Polígono_El_Bato_VF.shp", "shp_directo", "alta (validada por área)"),
    # Reñaca: ninguno de los 2 candidatos ("...ART8.shp" 15,1 ha,
    # "Final CMS/..._VF.shp" 16,9 ha) coincide con las 233,4 ha declaradas.
    # Sin archivo adicional que lo resuelva -- ver tasks.md, requiere
    # revisión manual de la resolución oficial (Res Ex 5196).
    162:  ("Final CMS/HU_EsteroReñaca_VF.shp", "shp_directo", "baja (superficie no coincide, ver tasks.md)"),
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

def resolver_geometria(id_solicitud, patron, tipo, dest):
    if tipo == "shp_directo":
        # ya extraído en una corrida previa (archive); apunta directo al
        # .shp correcto dentro de data/_geom_tmp/{id}, sin volver a bajar.
        cands = [p for p in dest.rglob("*.shp") if p.name == Path(patron).name
                 or norm(str(p)).endswith(norm(patron))]
        return (cands[0], None) if cands else (None, f"no se encontró '{patron}' ya extraído en {dest}")
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
        shp = [p for p in dest.rglob("*.shp") if "vertic" not in norm(p.name)]
        if shp:
            return shp[0], None
        kmz = list(dest.rglob("*.kmz")) + list(dest.rglob("*.kml"))
        if kmz:
            return kmz[0], None
        return None, f"'{nombre_real}' extraído pero sin .shp/.kmz de polígono dentro"

def main():
    WORK.mkdir(parents=True, exist_ok=True)
    natural = pd.read_csv(HERE.parent / "data" / "humedales_urbanos_valpo_natural.csv")
    gdfs, fallos = [], []

    for _, row in natural.iterrows():
        iid = int(row.id_solicitud)
        if iid not in SELECCION_ARCHIVO:
            fallos.append((iid, row.nombre, "sin entrada en SELECCION_ARCHIVO")); continue
        patron, tipo, confianza = SELECCION_ARCHIVO[iid]
        dest = WORK / str(iid)
        dest.mkdir(parents=True, exist_ok=True)
        print(f"#{iid} {row.nombre} -> {patron} ({tipo}, confianza {confianza})")
        try:
            geo_file, err = resolver_geometria(iid, patron, tipo, dest)
        except Exception as e:
            geo_file, err = None, str(e)
        if err:
            print(f"    FALLO: {err}")
            fallos.append((iid, row.nombre, err)); continue

        g = gpd.read_file(geo_file)
        if g.crs is None:
            g = g.set_crs(32719)  # UTM 19S, WGS84 -- verificado en .prj de casos con shp suelto
        g = g.to_crs(4326)
        g["id_solicitud"] = iid
        g["nombre"] = row.nombre
        g["comuna"] = row.comuna
        g["tipo_clasificacion"] = row.tipo_final
        g["archivo_fuente"] = geo_file.name
        g["confianza_geometria"] = confianza
        gdfs.append(g[["id_solicitud", "nombre", "comuna", "tipo_clasificacion",
                        "archivo_fuente", "confianza_geometria", "geometry"]])
        print(f"    OK: {len(g)} geometría(s) desde {geo_file.name}")
        time.sleep(0.4)

    if gdfs:
        final = pd.concat(gdfs, ignore_index=True)
        final = gpd.GeoDataFrame(final, geometry="geometry", crs=4326)
        final.to_file(OUT, driver="GeoJSON")
        print(f"\n-> {OUT} ({len(final)} geometrías de {final['id_solicitud'].nunique()} humedales)")
    if fallos:
        print(f"\n{len(fallos)} fallos:")
        for iid, nombre, err in fallos:
            print(f"  #{iid} {nombre}: {err}")

if __name__ == "__main__":
    main()
