# -*- coding: utf-8 -*-
"""Regenera Figura 2 (serie diaria) para la ventana 1-19 jul (dia 19 parcial 00-03h)."""
import json, urllib.request
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import WORK_DIR as HERE
pts = [(-33.05,-71.40),(-33.05,-71.20),(-32.80,-71.20),(-33.20,-71.30),(-32.95,-71.05),(-33.40,-71.40)]
lats=",".join(str(a) for a,_ in pts); lons=",".join(str(b) for _,b in pts)

u=("https://api.open-meteo.com/v1/forecast?latitude="+lats+"&longitude="+lons+
   "&daily=precipitation_sum&past_days=25&forecast_days=1&timezone=America/Santiago")
d=json.loads(urllib.request.urlopen(u,timeout=60).read()); L=d if isinstance(d,list) else [d]
days=L[0]["daily"]["time"]; mat=np.array([l["daily"]["precipitation_sum"] for l in L],dtype=float)
mean=np.nanmean(mat,axis=0)
keep=[(a,m) for a,m in zip(days,mean) if "2026-07-01"<=a<="2026-07-18"]
# dia 19 parcial 00-03h
u3=("https://api.open-meteo.com/v1/forecast?latitude="+lats+"&longitude="+lons+
    "&hourly=precipitation&start_hour=2026-07-19T00:00&end_hour=2026-07-19T03:00&timezone=America/Santiago")
d3=json.loads(urllib.request.urlopen(u3,timeout=60).read()); L3=d3 if isinstance(d3,list) else [d3]
p19=np.mean([sum(b for a,b in zip(l["hourly"]["time"],l["hourly"]["precipitation"]) if a>"2026-07-19T00:00" and b) for l in L3])
keep.append(("2026-07-19", float(p19)))

days_lbl=[str(int(a[8:10])) for a,_ in keep]; vals=[m for _,m in keep]
days_lbl[-1]="19*"
fig,ax=plt.subplots(figsize=(10,4))
ax.bar(days_lbl, vals, color=["#b5341f" if v>20 else "#3a7ca5" for v in vals])
ax.set_ylabel("Precipitación media regional (mm/día)")
ax.set_xlabel("Día (julio de 2026) — *19: acumulado parcial hasta las 03:00")
ax.grid(axis="y", color="#e6e6e6", linewidth=0.7); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig(HERE/"evento_rio_atmosferico.png", dpi=150); plt.close(fig)
print("dias 16-19:", [(a[5:],round(m,1)) for a,m in keep if a>="2026-07-16"])
print("16+17+18 =", round(sum(m for a,m in keep if a in("2026-07-16","2026-07-17","2026-07-18")),1))
print("-> evento_rio_atmosferico.png")
