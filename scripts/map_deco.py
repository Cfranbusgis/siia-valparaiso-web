"""Decoración cartográfica común para las figuras de mapa (lon/lat, EPSG:4326):
brújula de norte elegante (arriba-izquierda), grilla fina y barra de escala en km.
"""
from __future__ import annotations
import numpy as np


def add_north(ax, x=0.055, y=0.93):
    """Brújula de norte minimalista en coordenadas de ejes."""
    ax.annotate("", xy=(x, y), xytext=(x, y - 0.075), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="#2b2b2b", lw=1.5),
                zorder=20)
    ax.text(x, y + 0.012, "N", transform=ax.transAxes, ha="center", va="bottom",
            fontsize=9.5, fontweight="bold", color="#2b2b2b", zorder=20)


def add_grid(ax):
    """Grilla fina (graticule) tenue."""
    ax.grid(True, which="major", color="#9fb0bb", linewidth=0.4,
            linestyle=(0, (1, 3)), alpha=0.65, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(labelsize=8)


def add_scalebar(ax, km=50, pos="right"):
    """Barra de escala en km. pos: 'right' (inferior derecha), 'left' o 'center'."""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    latmid = (y0 + y1) / 2.0
    deg = km / (111.32 * np.cos(np.radians(latmid)))
    if pos == "left":
        xa = x0 + (x1 - x0) * 0.06
    elif pos == "center":
        xa = (x0 + x1) / 2.0 - deg / 2.0
    else:                               # right
        xa = x1 - (x1 - x0) * 0.06 - deg
    xb = xa + deg
    ya = y0 + (y1 - y0) * 0.05
    ax.plot([xa, xb], [ya, ya], color="#2b2b2b", lw=2.6,
            solid_capstyle="butt", zorder=20)
    for xt in (xa, xb):
        ax.plot([xt, xt], [ya, ya + (y1 - y0) * 0.012], color="#2b2b2b",
                lw=1.2, zorder=20)
    ax.text((xa + xb) / 2, ya + (y1 - y0) * 0.02, f"{km} km", ha="center",
            va="bottom", fontsize=8, color="#2b2b2b", zorder=20)


def decorate(ax, km=50):
    add_grid(ax); add_north(ax); add_scalebar(ax, km)
