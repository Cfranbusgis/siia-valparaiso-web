"""Humedales Urbanos reconocidos (Ley 21.202) para la Region de Valparaiso.

Fuente: Portal de Humedales del MMA (sistemahumedales.mma.gob.cl), listado
publico de solicitudes + ficha de detalle por solicitud. Ambos endpoints son
HTML/JSON servidos por el servidor (sin JavaScript), verificado con curl.

Alcance (decidido con Camila, 20-jul-2026):
- Solo Estado == "Humedal Urbano Reconocido" (categoria legal consolidada
  por decreto bajo la Ley 21.202; se excluyen solicitudes en tramite o
  archivadas).
- Sin geometria: el portal no expone un servicio de poligonos/puntos
  consultable para estas fichas. El cruce con las capas existentes del
  proyecto se hace a nivel de comuna.
- Criterio "natural" vs "artificial": el campo "Clasificacion del humedal
  acorde al inventario nacional de humedales" es texto libre (no un
  vocabulario controlado), llenado de forma distinta por cada municipio.
  Regla aplicada, revisada caso a caso sobre los 21 registros reales:
    * vacio o "No señala"      -> tipo_final = "sin dato"   (SE INCLUYE,
      marcado; no se asume natural ni artificial sin evidencia)
    * menciona "artificial" Y "natural" a la vez -> tipo_final =
      "mixto (excluido)" (registro describe mas de un poligono con tipos
      distintos en el mismo tramite -- ej. "Laguna El Criquet, humedal
      artificial...; Quebrada Honda, humedal natural..."; sin geometria no
      hay forma confiable de aislar solo la parte natural, se excluye el
      registro completo)
    * menciona "artificial" (y no "natural")    -> tipo_final = "artificial"
      (SE EXCLUYE)
    * cualquier otro texto no vacio             -> tipo_final = "natural"
      (los terminos ribereño/palustre/estuarino/marino costero/continental
      son categorias exclusivamente naturales en la nomenclatura CONAMA
      2006/MMA; lo artificial se declara explicito con tranque/embalse/
      estanque/canal -- por eso la ausencia de "artificial" en un texto no
      vacio se interpreta como natural, no por omision sino por convencion
      de nomenclatura)

Salida: data/humedales_urbanos_valpo.csv (las 21 filas reconocidas, con
tipo_final e incluir_capa) y data/humedales_urbanos_valpo_natural.csv (solo
incluir_capa=True: el insumo para el cruce con la capa de humedales 2013).
"""
from __future__ import annotations
import json, re, time
from pathlib import Path
import requests
from bs4 import BeautifulSoup

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "data" / "humedales_urbanos_valpo.csv"
BASE = "https://sistemahumedales.mma.gob.cl/HumedalesUrbanos"
HEADERS = {"User-Agent": "Mozilla/5.0 (tesis-humedales-valparaiso; contacto academico)"}

def listar_valparaiso() -> list[dict]:
    r = requests.post(f"{BASE}/ListarSolicitudesPublicas",
                       data={"Region": "REGIÓN DE VALPARAÍSO", "Provincia": "", "Comuna": "",
                             "Expediente": "", "NumeroSolicitud": "", "Estado": ""},
                       headers=HEADERS, timeout=30)
    r.raise_for_status()
    r.encoding = "utf-8"  # el JSON no declara charset; requests adivina mal el acentuado
    return r.json()["resultados"]

def detalle(id_solicitud: int) -> dict:
    r = requests.get(f"{BASE}/DetailsPublico/{id_solicitud}", headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")

    def val(field_id):
        el = soup.find(id=field_id)
        return el.get("value", "").strip() if el else None

    fila = soup.select_one("#comunas-table tbody tr")
    comuna = provincia = region = None
    if fila:
        tds = [td.get_text(strip=True) for td in fila.find_all("td")]
        if len(tds) >= 3:
            comuna, provincia, region = tds[0], tds[1], tds[2]

    return {
        "comuna": comuna, "provincia": provincia, "region": region,
        "superficie_ha": val("Superficie"),
        "clasificacion": val("Clasificacion"),
    }

def main():
    registros = listar_valparaiso()
    reconocidos = [r for r in registros if r["Estado"] == "Humedal Urbano Reconocido"]
    print(f"Valparaíso: {len(registros)} solicitudes totales, "
          f"{len(reconocidos)} con estado 'Humedal Urbano Reconocido'")

    filas = []
    for r in reconocidos:
        d = detalle(r["IDSolicitud"])
        filas.append({
            "id_solicitud": r["IDSolicitud"], "nombre": r["Nombre"], "expediente": r["Expediente"],
            "fecha_ingreso_ms": re.search(r"\d+", r["FechaIngreso"]).group(),
            "estado": r["Estado"], "vigente": r["Vigente"], **d,
        })
        print(f"  #{r['IDSolicitud']:>3} {r['Nombre'][:45]:45} {d['comuna']:15} {d['clasificacion']}")
        time.sleep(0.4)  # no saturar el servidor público

    import pandas as pd
    df = pd.DataFrame(filas)

    c = df["clasificacion"].fillna("")
    vacio = (c.str.strip() == "") | (c.str.strip().str.lower() == "no señala")
    tiene_artificial = c.str.contains("artificial", case=False, na=False)
    tiene_natural = c.str.contains("natural", case=False, na=False)
    mixto = tiene_artificial & tiene_natural

    df["tipo_final"] = "natural"
    df.loc[vacio, "tipo_final"] = "sin dato"
    df.loc[tiene_artificial & ~mixto & ~vacio, "tipo_final"] = "artificial"
    df.loc[mixto, "tipo_final"] = "mixto (excluido)"
    df["incluir_capa"] = df["tipo_final"].isin(["natural", "sin dato"])

    OUT.parent.mkdir(exist_ok=True)
    df.to_csv(OUT, index=False, encoding="utf-8-sig")
    df[df["incluir_capa"]].drop(columns=["incluir_capa"]).to_csv(
        OUT.parent / "humedales_urbanos_valpo_natural.csv", index=False, encoding="utf-8-sig")

    print("\nResumen tipo_final:")
    print(df["tipo_final"].value_counts().to_string())
    print(f"\n-> {OUT} ({len(df)} filas, todos los estados 'Reconocido')")
    print(f"-> {OUT.parent / 'humedales_urbanos_valpo_natural.csv'} "
          f"({df['incluir_capa'].sum()} filas incluidas en la capa)")

if __name__ == "__main__":
    main()
