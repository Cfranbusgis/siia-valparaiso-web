# -*- coding: utf-8 -*-
"""Genera el informe HTML autocontenido (Sistema Regional de Inteligencia Ambiental).

Dirección editorial de tipo publicación científica: identidad de sistema
operacional (no dashboard), jerarquía de indicadores, figura conceptual de la
arquitectura, figuras numeradas, tarjeta de nivel de confianza, secciones de
implicancias y limitaciones. Estructura de datos, mapas y cifras se conservan.
Salida: informe_anomalia_valpo_julio2026.html (tema claro/oscuro).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

import config
HERE = config.WORK_DIR
R = json.loads((HERE / "resumen_valpo.json").read_text(encoding="utf-8"))
T = json.loads((HERE / "resumen_topo.json").read_text(encoding="utf-8"))

TOPO_COM = list(T["top_comunas_expo_comp"].items())

# Escala de rios atmosfericos (Ralph et al., 2019, BAMS): categoria, nombre,
# umbral de IVT maximo (kg m-1 s-1) e impacto predominante.
AR_SCALE = [
    ("AR1", "Débil", "250–500", "Beneficios predominantes"),
    ("AR2", "Moderado", "500–750", "Mayormente beneficioso"),
    ("AR3", "Fuerte", "750–1000", "Equilibrio beneficio/riesgo"),
    ("AR4", "Extremo", "1000–1250", "Mayormente peligroso"),
    ("AR5", "Excepcional", "&gt; 1250", "Peligros predominantes"),
]
ar_rows = "".join(
    f'<tr class="{ "hit" if c in ("AR4","AR5") else "" }"><td><strong>{c}</strong></td>'
    f'<td>{n}</td><td class="num">{ivt}</td><td>{imp}</td></tr>'
    for c, n, ivt, imp in AR_SCALE)


def img64(name: str) -> str:
    b = (HERE / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode()


def es(x: float, d: int = 1) -> str:
    s = f"{x:,.{d}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


# ---- serie diaria (el 18 es parcial: 00:00-09:00) ----
TL = R["serie_diaria_mm_media"]
TL_MAX = max(TL.values())
tl_rows = "".join(
    f'<tr class="{ "hit" if v>20 else "" }">'
    f'<td>{int(d[8:10])}{"*" if d == "2026-07-18" else ""}</td>'
    f'<td class="num">{es(v,1)}</td>'
    f'<td class="bar"><span style="width:{min(100, v/TL_MAX*100):.0f}%"></span></td></tr>'
    for d, v in TL.items())

# ---- observaciones DMC/DGAC ----
DMC_OBS = [("Llanos de Caleu / La Dormida", 120.1, 227), ("Quillota", 84.9, 214),
           ("Panquehue", 71.8, 145), ("Rodelillo, Valparaíso", 67.1, 155),
           ("Llay Llay", 65.0, 131), ("Viña del Mar (Torquemada)", 64.7, 159),
           ("Jardín Botánico, Viña del Mar", 64.2, 158)]
dmc_rows = "".join(
    f'<tr class="{ "hit" if v>=60 else "" }"><td>{n}</td>'
    f'<td class="num strong">{es(v,1)}</td>'
    f'<td class="num">{p} %</td>'
    f'<td class="bar"><span style="width:{v/120.1*100:.0f}%"></span></td></tr>'
    for n, v, p in DMC_OBS)

# ---- consistencia entre modelos ----
MODELS = [("ECMWF-IFS (Europa)", 31.7, 95.0, 140.7),
          ("NCEP-GFS (Estados Unidos)", 63.3, 96.6, 163.1),
          ("DWD-ICON (Alemania)", 66.7, 74.3, 143.3),
          ("JMA (Japón)", 18.9, 143.1, 166.5),
          ("Open-Meteo (best_match)", 42.1, 101.3, 157.0)]
model_rows = "".join(
    f'<tr><td>{m}</td><td class="num">{es(a,1)}</td><td class="num">{es(b,1)}</td>'
    f'<td class="num strong">{es(s,1)}</td></tr>' for m, a, b, s in MODELS)

# ---- comunas ----
COMUNAS = [(n, int(p)) for n, p in R["top_comunas"].items()]
COM_MAX = max(p for _, p in COMUNAS)
comuna_rows = "".join(
    f'<tr><td>{n}</td><td class="num">+{p} %</td>'
    f'<td class="bar"><span style="width:{p/COM_MAX*100:.0f}%"></span></td></tr>'
    for n, p in COMUNAS)

topo_com_rows = "".join(
    f'<tr><td>{n}</td><td class="num strong">{es(v,2)}</td>'
    f'<td class="bar"><span style="width:{v/0.9*100:.0f}%"></span></td></tr>'
    for n, v in TOPO_COM)

METAR = [
    ("SCVM · Viña del Mar / Concón",
     "Lluvia intensa (+RA) el 17 de julio, visibilidad reducida a 500 m, cielo "
     "cubierto a baja altura y viento del norte con rachas de hasta 48 nudos."),
    ("SCRD · Rodelillo, Valparaíso",
     "Lluvia continua (RA) el 17 de julio, visibilidad reducida a 300 m y cielo "
     "cubierto a baja altura (30 m)."),
    ("SCEL · Santiago",
     "Lluvias frecuentes entre el 16 y el 18 de julio (35 de 61 reportes con "
     "lluvia) y presión atmosférica baja (1004–1007 hPa)."),
]
metar_cards = "".join(
    f'<div class="metar"><h4>{s}</h4><p>{t}</p></div>' for s, t in METAR)

# ---- figura conceptual (flujo metodológico) ----
FLOW = ["IVT / río atmosférico (motor)", "ERA5-Land (2003–2023)", "Climatología regional",
        "Open-Meteo (ventana reciente)", "Anomalía porcentual y estandarizada",
        "Inventario de humedales", "Integración espacial",
        "Modelo digital de elevación (TWI)", "Exposición compuesta",
        "Contraste con estaciones DMC/DGAC", "Diagnóstico territorial"]
flow_html = '<span class="fl-arrow">→</span>'.join(
    f'<span class="fl-node">{t}</span>' for t in FLOW)

CSS = """
:root{
  --paper:#f5f7fa; --card:#ffffff; --ink:#0f1922; --muted:#586a78;
  --line:#dae3ec; --accent:#1f6f8b; --deep:#0b3d66; --rain:#2b8cbe;
  --crit:#b5341f; --good:#0f766e; --hi:#0b3d66;
  --shadow:0 1px 2px rgba(15,25,34,.05),0 8px 24px rgba(15,25,34,.06);
}
@media (prefers-color-scheme:dark){:root{
  --paper:#0a0f15; --card:#111a23; --ink:#e6eef5; --muted:#93a6b6;
  --line:#213039; --accent:#57b6d6; --deep:#8ecae6; --rain:#4aa8d8;
  --crit:#f0785c; --good:#5eead4; --hi:#8ecae6;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 10px 30px rgba(0,0,0,.35);
}}
:root[data-theme="light"]{--paper:#f5f7fa;--card:#fff;--ink:#0f1922;--muted:#586a78;--line:#dae3ec;--accent:#1f6f8b;--deep:#0b3d66;--rain:#2b8cbe;--crit:#b5341f;--good:#0f766e;--hi:#0b3d66;}
:root[data-theme="dark"]{--paper:#0a0f15;--card:#111a23;--ink:#e6eef5;--muted:#93a6b6;--line:#213039;--accent:#57b6d6;--deep:#8ecae6;--rain:#4aa8d8;--crit:#f0785c;--good:#5eead4;--hi:#8ecae6;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.wrap{max-width:940px;margin:0 auto;padding:clamp(20px,4vw,54px)}
h1,h2,h3,h4{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;
  text-wrap:balance;line-height:1.22;letter-spacing:-.01em}
h1{font-size:clamp(1.7rem,3.8vw,2.4rem);margin:.1em 0}
h2{font-size:1.4rem;margin:2.6em 0 .6em;padding-bottom:.3em;border-bottom:1px solid var(--line)}
h3{font-size:1.1rem;margin:1.8em 0 .4em}
.eyebrow{font-family:-apple-system,"Segoe UI",sans-serif;text-transform:uppercase;
  letter-spacing:.16em;font-size:.72rem;font-weight:700;color:var(--accent)}
.kicker{font-family:-apple-system,"Segoe UI",sans-serif;font-size:.82rem;
  text-transform:uppercase;letter-spacing:.1em;color:var(--muted);font-weight:600;margin-top:.5em}
.lead{font-size:1.08rem}
.muted{color:var(--muted)}
p{max-width:none;text-align:justify;hyphens:auto}
.masthead{border-top:3px solid var(--deep);padding-top:16px}
/* --- jerarquia de indicadores --- */
.stats{display:grid;gap:14px;margin:24px 0;
  grid-template-columns:repeat(2,1fr)}
@media(min-width:720px){.stats{grid-template-columns:repeat(4,1fr)}}
.stat{background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px;box-shadow:var(--shadow)}
.stat .k{font-size:.74rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.stat .v{font-family:Georgia,serif;font-weight:700;color:var(--deep);
  font-variant-numeric:tabular-nums;margin:.08em 0;font-size:1.7rem}
.stat .s{font-size:.8rem;color:var(--muted)}
.stat.lead-stat{grid-column:1/-1;background:
  linear-gradient(135deg,color-mix(in srgb,var(--deep) 14%,var(--card)),var(--card));
  border-color:color-mix(in srgb,var(--deep) 25%,var(--line))}
@media(min-width:720px){.stat.lead-stat{grid-column:span 2;grid-row:span 1}}
.stat.lead-stat .v{font-size:3.1rem;color:var(--hi)}
.stat.lead-stat .k{color:var(--accent);font-weight:700}
/* --- figura conceptual --- */
.flow{display:flex;flex-wrap:wrap;gap:8px;align-items:center;
  background:var(--card);border:1px solid var(--line);border-radius:14px;
  padding:18px;box-shadow:var(--shadow);margin:16px 0}
.fl-node{background:color-mix(in srgb,var(--accent) 10%,var(--card));
  border:1px solid color-mix(in srgb,var(--accent) 30%,var(--line));
  color:var(--ink);border-radius:8px;padding:7px 12px;font-size:.86rem;font-weight:600}
.fl-arrow{color:var(--accent);font-weight:700}
.flow-out{margin-top:12px;text-align:center;font-weight:700;color:var(--deep);
  font-family:Georgia,serif;font-size:1.05rem}
figure{margin:20px 0;background:var(--card);border:1px solid var(--line);
  border-radius:14px;padding:12px;box-shadow:var(--shadow)}
figure img{width:100%;height:auto;border-radius:8px;display:block}
figcaption{font-size:.86rem;color:var(--muted);padding:12px 6px 2px;max-width:none;
  text-align:justify;hyphens:auto}
figcaption b{color:var(--ink)}
.cols{display:grid;gap:20px;grid-template-columns:1fr}
@media(min-width:700px){.cols.two{grid-template-columns:1fr 1fr}}
table{width:100%;border-collapse:collapse;font-size:.9rem;margin:.4em 0}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line)}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);font-weight:700}
td.num{text-align:right;font-variant-numeric:tabular-nums}
td.strong{font-weight:700;color:var(--deep)}
.tablewrap{overflow-x:auto}
td.bar{width:30%;padding-right:14px}
td.bar span{display:block;height:8px;border-radius:6px;background:linear-gradient(90deg,var(--rain),var(--deep))}
tr.hit td{background:color-mix(in srgb,var(--crit) 12%,transparent)}
tr.hit td:first-child{font-weight:700;color:var(--crit)}
.metar{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--accent);
  border-radius:10px;padding:12px 16px;margin:10px 0;box-shadow:var(--shadow)}
.metar h4{margin:.1em 0 .3em;font-size:.98rem;color:var(--deep)}
.metar p{margin:0;font-size:.9rem;color:var(--muted)}
.panel{border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin:18px 0;
  background:var(--card);box-shadow:var(--shadow)}
.panel.confidence{border-left:4px solid var(--good);
  background:color-mix(in srgb,var(--good) 7%,var(--card))}
.panel.limits{border-left:4px solid var(--crit);
  background:color-mix(in srgb,var(--crit) 7%,var(--card))}
.panel h3{margin-top:0}
.conf-badge{display:inline-block;background:var(--good);color:#fff;font-weight:700;
  padding:.2em .7em;border-radius:999px;font-size:.85rem;margin-left:.4em}
ul.tight{margin:.3em 0;padding-left:1.2em}
ul.tight li{margin:.35em 0;text-align:justify;hyphens:auto}
.sourcebar{margin-top:44px;border-top:2px solid var(--deep);padding-top:14px;
  font-size:.82rem;color:var(--muted)}
.sourcebar .lbl{text-transform:uppercase;letter-spacing:.1em;font-weight:700;
  color:var(--ink);font-size:.72rem}
a{color:var(--accent)}
"""

HTML = f"""<div class="wrap">
<header class="masthead">
  <div class="eyebrow">Sistema Regional de Inteligencia Ambiental &middot; Región de Valparaíso</div>
  <h1>Anomalía de precipitación durante un sistema frontal asociado a un río atmosférico</h1>
  <p class="kicker">Análisis científico del evento hidrometeorológico del 1 al 18 de julio de
  2026 (corte 09:00) &middot; Evaluación de 2.916 humedales del inventario regional</p>
</header>

<p class="lead">Entre el 16 y el 18 de julio de 2026, un sistema frontal asociado a un
río atmosférico afectó una extensa franja de Chile central y centro-sur. El
fenómeno transportó una elevada cantidad de humedad desde el océano Pacífico y
generó precipitaciones intensas en distintas zonas del país.</p>
<p>Este sistema no evalúa la extensión nacional completa del evento, sino su expresión
territorial en la Región de Valparaíso. En esta región, la precipitación se concentró
principalmente durante los días 16 y 17 de julio &mdash; con un remanente activo la
madrugada del 18 &mdash; después de una primera quincena relativamente seca. Como
resultado, el acumulado entre el 1 de julio y las 09:00 del 18 de julio superó
ampliamente el promedio climatológico estimado para el mismo periodo.</p>

<section class="stats">
  <div class="stat lead-stat"><div class="k">Humedales con anomalía fuerte (z &gt; 2)</div>
    <div class="v">90 %</div>
    <div class="s">2.620 de los 2.916 humedales analizados; 1.364 alcanzan una anomalía de
    elevada magnitud (z &gt; 3).</div></div>
  <div class="stat"><div class="k">Anomalía regional</div>
    <div class="v">+313 %</div>
    <div class="s">Equivalente a z = 3,74 respecto de la climatología 2003&ndash;2023.</div></div>
  <div class="stat"><div class="k">Precipitación acumulada</div>
    <div class="v">192 mm</div>
    <div class="s">Frente a una media climatológica de 48,2 mm (1&ndash;18 de julio).</div></div>
  <div class="stat"><div class="k">Máximo observado (24 h)</div>
    <div class="v">120 mm</div>
    <div class="s">Estación Llanos de Caleu/La Dormida, red DMC/DGAC (al 17 de julio,
    21:00).</div></div>
  <div class="stat"><div class="k">Máximo diario regional estimado</div>
    <div class="v">106,8 mm</div>
    <div class="s">Precipitación media de las celdas analizadas, 17 de julio.</div></div>
  <div class="stat"><div class="k">Categoría del río atmosférico</div>
    <div class="v">AR4&ndash;AR5</div>
    <div class="s">Clasificación operacional (escala de Ralph et al., 2019) para el
    evento del 14&ndash;18 de julio en Chile central.</div></div>
</section>

<h2>Caracterización del río atmosférico</h2>
<p>Conviene distinguir el <strong>motor</strong> del fenómeno de su <strong>expresión
territorial</strong>. Un río atmosférico es una banda estrecha y alargada de
transporte concentrado de vapor de agua; su intensidad se cuantifica mediante el
transporte integrado de vapor (IVT, en kg m⁻¹ s⁻¹) y su duración. El presente
sistema no calcula el IVT, sino que mide la <strong>expresión</strong> de ese motor
en la superficie: la anomalía de precipitación sobre la Región de Valparaíso.</p>
<p>Según los sistemas de pronóstico operacional, el evento del 14 al 18 de julio de
2026 se clasificó entre las categorías <strong>AR4 (extremo) y AR5 (excepcional)</strong>
en la escala de ríos atmosféricos, con una duración aproximada de 72 horas y un nivel
de congelación estimado entre 2.300 y 2.500 m. La escala combina la magnitud del IVT
y su persistencia:</p>
<div class="tablewrap"><table>
  <thead><tr><th>Categoría</th><th>Denominación</th>
    <th class="num">IVT máximo (kg m⁻¹ s⁻¹)</th><th>Impacto predominante</th></tr></thead>
  <tbody>{ar_rows}</tbody>
</table></div>
<p class="muted">Escala según Ralph et al. (2019). La clasificación operacional del evento
proviene de fuentes chilenas (Dirección Meteorológica de Chile, Centro CR2,
Universidad de O'Higgins, Universidad de Talca, MINAGRI-UGRA y SENAPRED).</p>

<h3>Estimación propia del transporte de vapor</h3>
<p>Para caracterizar el motor con dato propio, se calculó el IVT horario a partir de la
humedad y el viento en niveles de presión (1000&ndash;300 hPa), integrando el flujo de
vapor sobre la vertical en la franja costera de la región. El resultado es coherente con
la clasificación operacional: el IVT alcanzó un <strong>máximo de 819 kg m⁻¹ s⁻¹ el 16 de
julio</strong>, con <strong>82 horas de condiciones de río atmosférico</strong> (IVT &gt; 250)
y flujo procedente del <strong>nor-noroeste (341°)</strong>, la dirección característica de
estos sistemas sobre Chile central. La combinación de magnitud y persistencia corresponde a
una categoría <strong>AR4 (extremo)</strong>.</p>
<figure>
  <img alt="Serie temporal del IVT durante el evento, con bandas de categoria AR" src="{img64('ivt_evento.png')}">
  <figcaption><b>Figura 1.</b> Transporte integrado de vapor (IVT) en la costa de Valparaíso
  durante el evento, con las bandas de la escala de ríos atmosféricos. El transporte de
  humedad presenta dos pulsos (16 y 17 de julio) que anteceden y acompañan la precipitación
  observada en superficie.</figcaption>
</figure>
<p class="muted">Estimación propia (IVT = g⁻¹∫ q·V dp, niveles 1000&ndash;300 hPa; datos de
Open-Meteo). Su magnitud es levemente inferior a la clasificación operacional
AR4&ndash;AR5, diferencia esperable por la resolución del dato y el suavizado espacial y
temporal; confirma, no obstante, un río atmosférico extremo. El máximo del IVT (16 de julio)
antecede al máximo de precipitación en superficie (16&ndash;17 de julio), consistente con la
secuencia física del fenómeno.</p>
<div class="panel">
  <h3 style="margin-top:0">Nivel de congelación y tipo de precipitación</h3>
  <p style="margin-bottom:0">El nivel de congelación (2.300&ndash;2.500 m) determina si la
  precipitación cae como lluvia o como nieve, lo que condiciona el aporte hídrico
  inmediato a los humedales. De los 1.364 humedales con z &gt; 3, el
  <strong>72 % se sitúa bajo los 2.300 m</strong> y, por lo tanto, recibió
  precipitación líquida con aporte directo; los 383 humedales altoandinos restantes,
  sobre esa cota, habrían recibido nieve, cuyo aporte es diferido.</p>
</div>

<h2>Arquitectura del sistema</h2>
<p>El diagnóstico integra múltiples fuentes de información en un flujo reproducible, desde
la climatología de referencia hasta la interpretación territorial sobre el inventario de
humedales.</p>
<div class="flow">{flow_html}</div>
<p class="flow-out">→ Sistema Regional de Inteligencia Ambiental</p>

<h2>Concentración temporal de la precipitación</h2>
<p>La serie representa la precipitación diaria media estimada sobre las celdas analizadas de la
Región de Valparaíso. El evento presentó una marcada concentración temporal: el 16 y el
17 de julio acumularon 152,3 mm y la madrugada del 18 (00:00&ndash;09:00) sumó otros
21,8 mm; en conjunto, cerca del 92 % de la precipitación registrada durante todo el
periodo analizado. Este comportamiento evidencia que la anomalía estuvo determinada
principalmente por un pulso breve de precipitación de alta intensidad y no por una
distribución persistente de las lluvias durante la primera mitad del mes.</p>
<figure>
  <img alt="Evolucion diaria de la precipitacion media regional" src="{img64('evento_rio_atmosferico.png')}">
  <figcaption><b>Figura 2.</b> Evolución diaria de la precipitación media regional durante el
  evento hidrometeorológico (1 de julio &ndash; 18 de julio de 2026; el día 18 corresponde
  al acumulado parcial hasta las 09:00, hora local).</figcaption>
</figure>
<div class="tablewrap"><table>
  <thead><tr><th>Día (julio de 2026)</th><th class="num">mm/día</th><th>Intensidad relativa</th></tr></thead>
  <tbody>{tl_rows}</tbody>
</table></div>
<p class="muted">*El día 18 corresponde al acumulado parcial entre las 00:00 y las 09:00,
hora local.</p>

<h2>Distribución espacial de la anomalía</h2>
<p>Las anomalías de mayor magnitud se localizaron principalmente en el litoral y la cordillera de
la Costa. Este resultado describe la expresión regional del evento y no debe interpretarse como
una representación de toda su extensión en Chile central y centro-sur.</p>
<div class="cols two">
  <figure><img alt="Anomalia porcentual de la precipitacion acumulada" src="{img64('mapa_anomalia_valpo.png')}">
    <figcaption><b>Figura 3.</b> Anomalía porcentual de la precipitación acumulada
    (1 de julio &ndash; 18 de julio 09:00, 2026) respecto de la climatología 2003&ndash;2023
    estimada mediante ERA5-Land.</figcaption></figure>
  <figure><img alt="Exposicion meteorologica de los humedales" src="{img64('mapa_humedales_valpo.png')}">
    <figcaption><b>Figura 4.</b> Exposición meteorológica de los humedales según la anomalía
    estandarizada de precipitación (puntuación estandarizada, z). El mapa representa
    exposición meteorológica, no respuesta ecológica.</figcaption></figure>
</div>

<h3>Exposición meteorológica de los humedales</h3>
<p>Los 2.916 humedales del inventario regional fueron asociados con la anomalía de la celda
correspondiente y representados según su puntuación estandarizada (<em>z-score</em>). Del total
analizado, 2.620 humedales presentaron una anomalía fuerte, con z &gt; 2, mientras que 1.364
alcanzaron una anomalía de elevada magnitud, con z &gt; 3. Estos resultados caracterizan
exclusivamente la exposición meteorológica de los humedales frente al evento; su
respuesta hidrológica o ecológica depende de factores adicionales descritos en las
limitaciones.</p>
<h4 style="font-size:1rem;margin:1.2em 0 .3em">Comunas con mayor anomalía media en sus humedales</h4>
<div class="tablewrap"><table>
  <thead><tr><th>Comuna</th><th class="num">Anomalía media</th><th>Intensidad relativa</th></tr></thead>
  <tbody>{comuna_rows}</tbody>
</table></div>

<h2>Exposición topográfica combinada</h2>
<p>La exposición meteorológica describe cuánto se apartó la precipitación de su
climatología, pero no dónde tiende a acumularse el agua sobre el terreno. Para
avanzar en esa dirección se procesó el modelo digital de elevación regional (250 m):
se derivaron la pendiente y la acumulación de flujo (algoritmo D8, previo relleno de
depresiones) y, a partir de ambas, el índice topográfico de humedad
(<em>TWI</em>), que identifica las posiciones de convergencia hídrica &mdash; fondos
de valle y vegas &mdash; con mayor propensión a la saturación.</p>
<p>Combinando en partes iguales la exposición meteorológica (anomalía estandarizada)
y la exposición topográfica (TWI normalizado) se obtiene un <strong>índice de
exposición compuesta</strong> para los {T['humedales_z_gt3']:,} humedales con z &gt; 3. De ellos,
<strong>{T['humedales_expo_comp_alta']:,} ({es(T['pct_expo_comp_alta'],1)} %) presentan
exposición compuesta alta</strong>: reciben una anomalía marcada y, además, ocupan
posiciones topográficas donde el agua tiende a concentrarse. Estos humedales
constituyen un primer conjunto de prioridad territorial para seguimiento.</p>
<figure>
  <img alt="Relieve 3D de Valparaiso con la anomalia de precipitacion drapeada" src="{img64('modelo_3d_anomalia_valpo.png')}">
  <figcaption><b>Figura 5.</b> Modelo de relieve de la Región de Valparaíso con la
  anomalía de precipitación de julio de 2026 proyectada sobre la superficie
  (exageración vertical ×8). Las anomalías de mayor magnitud se concentran en el
  litoral y la cordillera de la Costa; los valles interiores y el sector andino
  presentan valores menores. Existe además una versión interactiva
  (<code>modelo_3d_anomalia_valpo.html</code>).</figcaption>
</figure>
<h4 style="font-size:1rem;margin:1.2em 0 .3em">Comunas con mayor exposición compuesta media (humedales z &gt; 3)</h4>
<div class="tablewrap"><table>
  <thead><tr><th>Comuna</th><th class="num">Exposición compuesta (0&ndash;1)</th><th>Intensidad relativa</th></tr></thead>
  <tbody>{topo_com_rows}</tbody>
</table></div>
<p class="muted">El índice combina anomalía meteorológica y posición topográfica; no
constituye una estimación de inundación, sino un indicador de prioridad que integra
dos dimensiones de la exposición. Valores derivados del modelo digital de elevación
ASTER GDEM (250 m) y del análisis de precipitación descrito.</p>

<h2>Contraste entre observaciones y modelos</h2>
<p>Debido al desfase temporal en la publicación de ERA5-Land, la precipitación
correspondiente a los días más recientes se contrastó mediante tres fuentes independientes:
observaciones de estaciones meteorológicas, resultados de modelos operacionales y reportes
aeronáuticos METAR. La convergencia de estas fuentes respalda la ocurrencia de un evento de
precipitación intenso en la Región de Valparaíso. Cada fuente representa una escala y un
tipo de información diferentes: las estaciones entregan observaciones puntuales; los modelos
representan valores medios por celda; y los reportes METAR describen las condiciones
meteorológicas observadas en aeródromos específicos.</p>

<div class="panel confidence">
  <h3>Nivel de confianza del diagnóstico <span class="conf-badge">Alta</span></h3>
  <p style="margin-bottom:0">La confianza se sustenta cualitativamente en la consistencia
  espacial de la anomalía, el contraste con las estaciones de la red DMC/DGAC y la
  comparación entre múltiples fuentes independientes (modelos operacionales y reportes
  aeronáuticos). No corresponde a una métrica estadística única, sino a la convergencia de
  evidencia de origen distinto.</p>
</div>

<h3>Observaciones de la red DMC/DGAC</h3>
<p class="muted">Precipitación acumulada en 24 horas de la Red de Estaciones Meteorológicas
Automáticas de la Dirección Meteorológica de Chile, consultada mediante su API oficial el 17
de julio de 2026, alrededor de las 21:00 hora local.</p>
<div class="tablewrap"><table>
  <thead><tr><th>Estación (Región de Valparaíso)</th><th class="num">Agua caída en 24 h (mm)</th>
    <th class="num">% de la quincena climatológica</th><th>Intensidad relativa</th></tr></thead>
  <tbody>{dmc_rows}</tbody>
</table></div>
<p>El mayor registro correspondió a la estación Llanos de Caleu/La Dormida, con 120,1 mm en
24 horas. Las estaciones de Rodelillo y Viña del Mar registraron valores cercanos a 65&ndash;67
mm durante el mismo periodo. Estas observaciones confirman la elevada magnitud de la
precipitación. No obstante, su comparación con los modelos debe realizarse con cautela, porque
una estación representa una medición puntual, mientras que el valor modelado corresponde al
promedio de una celda espacial.</p>
<figure>
  <img alt="Contraste espacial entre la anomalia modelada y las observaciones" src="{img64('mapa_modelo_vs_obs.png')}">
  <figcaption><b>Figura 6.</b> Contraste espacial entre la anomalía modelada y las
  observaciones de precipitación registradas por estaciones DMC/DGAC. Las estaciones con
  mayores registros coinciden con las celdas de mayor anomalía.</figcaption>
</figure>

<h3>Consistencia entre modelos meteorológicos</h3>
<p>Los cinco modelos y sistemas operacionales consultados reprodujeron un incremento considerable de
la precipitación durante los días 16 y 17 de julio. Para el 17 de julio, las estimaciones
variaron entre 74,3 y 143,1 mm/día, mientras que el acumulado entre el 1 y el 17 de julio
fluctuó entre 140,7 y 166,5 mm (valores previos a la lluvia de la madrugada del 18). La
dispersión entre los resultados representa la
incertidumbre asociada a las diferencias de resolución, parametrización y condiciones
iniciales de cada modelo. Pese a ello, todos identificaron un pulso intenso de precipitación,
lo que aporta consistencia al diagnóstico general del evento.</p>
<div class="tablewrap"><table>
  <thead><tr><th>Modelo</th><th class="num">16 de julio</th><th class="num">17 de julio</th>
    <th class="num">Acumulado 1&ndash;17 (mm)</th></tr></thead>
  <tbody>{model_rows}</tbody>
</table></div>

<h3>Reportes METAR</h3>
{metar_cards}
<p>Los reportes METAR de Viña del Mar/Concón y Rodelillo registraron lluvia intensa o
continua, visibilidad reducida, cielo cubierto a baja altura y vientos procedentes del norte. En
Santiago también se observaron lluvias frecuentes y una disminución de la presión
atmosférica, condiciones compatibles con el paso del sistema frontal. En conjunto, estos
antecedentes confirman la intensidad de las condiciones meteorológicas durante el evento. La
identificación del río atmosférico se sustenta en las fuentes meteorológicas que documentan
el transporte concentrado de humedad, mientras que los METAR aportan evidencia local sobre sus
condiciones asociadas.</p>

<h2>Interpretación territorial</h2>
<p>Los resultados muestran que el sistema frontal asociado al río atmosférico produjo una
anomalía de precipitación excepcional en la Región de Valparaíso. La señal regional
forma parte de un evento de mayor extensión que también afectó otras zonas de Chile central
y centro-sur. Por lo tanto, este análisis debe interpretarse como una evaluación territorial de
la expresión del evento en Valparaíso y no como una delimitación completa de sus efectos a
escala nacional.</p>

<h2>Implicancias para el monitoreo ambiental</h2>
<div class="panel">
  <p style="margin-top:0">El sistema aporta a la gestión y el monitoreo ambiental regional en los
  siguientes términos:</p>
  <ul class="tight">
    <li>Caracteriza la <strong>exposición meteorológica</strong> del territorio y de sus
      humedales frente a eventos de precipitación intensa.</li>
    <li>Identifica <strong>territorios prioritarios</strong> según la magnitud de la anomalía,
      orientando la atención hacia los sectores más expuestos.</li>
    <li>Aporta información oportuna que puede <strong>apoyar sistemas de alerta</strong> y la
      toma de decisiones territoriales.</li>
    <li><strong>No reemplaza modelos hidrológicos</strong> ni evaluaciones de impacto: constituye
      una herramienta de apoyo para el monitoreo ambiental, integrable a plataformas de mayor
      alcance.</li>
  </ul>
</div>

<h2>Limitaciones del análisis</h2>
<div class="panel limits">
  <p style="margin-top:0"><strong>En su etapa actual, el sistema caracteriza la exposición
  meteorológica y no estima directamente:</strong></p>
  <ul class="tight">
    <li>inundación;</li>
    <li>daño ecológico;</li>
    <li>respuesta hidrológica;</li>
    <li>impacto ambiental.</li>
  </ul>
  <p style="margin-bottom:0">Estos procesos dependen de factores adicionales &mdash; topografía,
  red de drenaje, conectividad, humedad antecedente y características particulares de cada
  humedal &mdash; y de modelación específica. Se trata de una delimitación del alcance vigente,
  no de una restricción permanente: varios de estos factores pueden incorporarse en etapas
  posteriores con insumos ya disponibles en el sistema (véanse las líneas de profundización).
  Adicionalmente, la climatología de referencia y la información reciente proceden de productos
  distintos: la magnitud del evento permite reconocer una señal regional robusta, pero los
  valores absolutos deberán revisarse cuando ERA5-Land incorpore y consolide el periodo
  completo.</p>
</div>

<h2>Líneas de profundización</h2>
<p>El sistema está diseñado para escalar desde la exposición meteorológica hacia un análisis
territorial más completo. Las siguientes líneas son viables con insumos que ya integran el
modelo MOD_EToPM-HS, a resolución de 250 m y en el mismo sistema de referencia (EPSG:32719)
que el área de estudio:</p>
<div class="panel">
  <ul class="tight">
    <li><strong>Susceptibilidad topográfica (modelo digital de elevación) &mdash; incorporada.</strong>
      A partir del DEM regional (ASTER GDEM, 250 m) se derivaron la pendiente, la acumulación de
      flujo y el índice topográfico de humedad, y se integraron con la anomalía en un índice de
      exposición compuesta (véase la sección correspondiente). Una extensión posible es calibrar la
      ponderación y validar las zonas de convergencia con eventos de anegamiento observados.</li>
    <li><strong>Condición de la vegetación (NDVI).</strong> La serie MODIS de NDVI
      (250 m, 2003&ndash;2023) permite caracterizar el estado y la estacionalidad de la
      cobertura vegetal de los humedales, y contrastar la respuesta posterior al evento.</li>
    <li><strong>Contexto térmico (temperatura superficial, LST).</strong> Las series MODIS de
      temperatura superficial aportan información complementaria sobre las condiciones de cada
      sistema.</li>
    <li><strong>Transporte de vapor (IVT) &mdash; incorporado; nowcasting como extensión.</strong>
      El sistema ya calcula el IVT del evento con dato propio (véase la caracterización del río
      atmosférico). El paso siguiente es acoplar el IVT pronosticado, en línea con los sistemas
      operacionales de ríos atmosféricos para Chile, de modo de anticipar la exposición antes del
      evento y no solo caracterizarla una vez ocurrido.</li>
    <li><strong>Consolidación de la línea reciente.</strong> Reemplazar la ventana operacional por
      ERA5-Land una vez publicado el periodo, para homogeneizar la comparación climatológica.</li>
  </ul>
</div>

<h2>Método y trazabilidad</h2>
<div class="panel">
  <ul class="tight">
    <li><strong>Línea base climatológica:</strong> resultados del modelo MOD_EToPM-HS,
      construido a partir de rásteres diarios de ERA5-Land (resolución aproximada de 10 km,
      EPSG:32719). Para cada celda se calculó la precipitación acumulada entre el 1 y el 18 de
      julio de cada año del periodo 2003&ndash;2023; la media regional fue de 48,2 mm. Dado que
      la ventana reciente corta a las 09:00 del 18, la comparación con la climatología del día
      18 completo hace que la anomalía estimada sea levemente conservadora.</li>
    <li><strong>Ventana reciente:</strong> datos operacionales de Open-Meteo (totales diarios
      del 1 al 17 de julio y acumulado horario del 18 de julio entre las 00:00 y las 09:00,
      hora local), dado que al momento del análisis ERA5-Land aún no incorporaba los días
      16 a 18 de julio de 2026.</li>
    <li><strong>Cálculo de la anomalía:</strong> por celda se calcularon la anomalía porcentual
      y la puntuación estandarizada respecto de la distribución climatológica; cada humedal se
      asoció al valor de la celda en la que se localiza. Los 1.364 humedales con z &gt; 3 se
      exportaron a formato GeoJSON (<code>humedales_z_gt3_valpo.geojson</code>) para su uso en
      QGIS.</li>
  </ul>
</div>

<div class="sourcebar">
  <div class="lbl">Fuentes</div>
  <p style="max-width:none;margin:.3em 0 0">ERA5-Land &middot; Open-Meteo (ECMWF-IFS, NCEP-GFS,
  DWD-ICON, JMA) &middot; Dirección Meteorológica de Chile y Dirección General de
  Aeronáutica Civil (Red EMA y reportes METAR SCVM, SCRD, SCEL) &middot; Inventario de
  humedales de la Región de Valparaíso continental &middot; Elaboración propia
  (modelo MOD_EToPM-HS). Datos procesados entre el 17 y el 18 de julio de 2026; actualización
  con la precipitación acumulada hasta las 09:00 del 18 de julio. La ventana reciente incorpora
  información operacional sujeta a revisión cuando ERA5-Land consolide el periodo
  analizado.</p>
</div>
</div>"""

TITLE = ("Sistema Regional de Inteligencia Ambiental — Anomalía de precipitación, "
         "Región de Valparaíso, julio 2026")
DOC = ("<style>" + CSS + "</style>\n" + HTML +
       f'<script>document.title={json.dumps(TITLE)};</script>')
(HERE / "informe_anomalia_valpo_julio2026.html").write_text(DOC, encoding="utf-8")
print("informe escrito:",
      (HERE / "informe_anomalia_valpo_julio2026.html").stat().st_size, "bytes")
