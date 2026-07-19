# -*- coding: utf-8 -*-
"""
Generate layered assets for 4 memory worlds:
  Portal I, San Marco, Muqarnas, Mandala.

Each world produces:
  - Base image (static background without moving elements) at 512 and 1024 px as WebP
  - JSON atlas describing the moving elements' positions/properties

Uses helpers from make_domes.py.
Run: python make_memory_layers.py [tag...]
"""
import os, sys, json, math
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PolyCollection, LineCollection
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_domes as M
hx = M.hx; clip = M.clip; base = M.base; frame = M.frame; newdome = M.newdome; rng = M.rng

OUT_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "fulldome", "web")
OUT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "fulldome")
os.makedirs(OUT_WEB, exist_ok=True)
os.makedirs(OUT_DATA, exist_ok=True)

GA = np.pi * (3 - np.sqrt(5))


def _save_base(fig, tag):
    """Save base figure at 512 and 1024 as WebP, then close."""
    for size in [512, 1024]:
        dpi = size / 8  # fig is 8x8 inches
        fn_png = os.path.join(OUT_WEB, f"{tag}_base_{size}.png")
        fig.savefig(fn_png, transparent=False, dpi=dpi,
                    facecolor=fig.get_facecolor())
        fn_webp = os.path.join(OUT_WEB, f"{tag}_base_{size}.webp")
        img = Image.open(fn_png)
        img.save(fn_webp, "WEBP", quality=88)
        print(f"ok {fn_webp}")
        os.remove(fn_png)
    plt.close(fig)


# ═══════════════════════════════════════════════════════════════════════════════
# PORTAL I
# ═══════════════════════════════════════════════════════════════════════════════

PORTAL1_TAG = "portal_1"
PORTAL1_BASE_COL = "#0a1430"
PORTAL1_WARM = "#fff2c8"
PORTAL1_RING = "#caa24c"
PORTAL1_CLO_H = "#22335e"
PORTAL1_CHI_H = "#c99a3a"
PORTAL1_NBEINGS = 84
PORTAL1_BW_H = "#f2dca0"
PORTAL1_BD_H = "#2a3a6a"
PORTAL1_SPIN = 0.0


def portal_1_base():
    """Generate portal_1 base: cassons + oculus glow, WITHOUT the 84 beings."""
    fig, ax = newdome()
    base(ax, PORTAL1_BASE_COL)

    # Casson grid
    ringr = [0.985, 0.86, 0.73, 0.60, 0.47, 0.35, 0.24, 0.15]
    ribs = [36, 30, 24, 20, 16, 12, 8]
    clo = hx(PORTAL1_CLO_H)
    chi = hx(PORTAL1_CHI_H)
    for ti in range(len(ringr) - 1):
        r0 = ringr[ti]; r1 = ringr[ti + 1]; n = ribs[ti]
        off = (ti % 2) * (np.pi / n)
        for kk in range(n):
            a = 2 * np.pi * kk / n + off
            da = np.pi / n * 0.92
            th = np.linspace(a - da, a + da, 6)
            us = np.concatenate([r0 * np.cos(th), r1 * np.cos(th[::-1])])
            vs = np.concatenate([r0 * np.sin(th), r1 * np.sin(th[::-1])])
            shade = 0.4 + 0.6 * (ti / len(ringr))
            clip(ax, ax.add_collection(
                PolyCollection([list(zip(us, vs))],
                               facecolors=[np.clip(clo * shade + chi * 0.12, 0, 1)],
                               edgecolors=[chi * 0.5], linewidths=0.5, zorder=3)
            ) or ax.collections[-1])

    # Oculus glow
    for rr, al in [(0.19, 0.14), (0.13, 0.22), (0.08, 0.34), (0.045, 0.6)]:
        ax.add_patch(Circle((0, 0), rr, fc=hx(PORTAL1_WARM), ec="none", alpha=al, zorder=5))

    # Sparkle dots
    for _ in range(60):
        a = rng.random() * 2 * np.pi
        r = rng.random() * 0.13
        ax.add_patch(Circle((r * np.cos(a), r * np.sin(a)), 0.006,
                            fc=hx("#fff2cf"), ec="none", zorder=8))

    frame(ax, oculus=(0.0, 0.0), warm=PORTAL1_WARM, ring=PORTAL1_RING, glow=0.7, rib=False)
    _save_base(fig, PORTAL1_TAG)


def portal_1_atlas():
    """Generate JSON atlas with 84 beings."""
    beings = []
    bw = hx(PORTAL1_BW_H)
    bd = hx(PORTAL1_BD_H)
    for i in range(1, PORTAL1_NBEINGS + 1):
        plane = i / PORTAL1_NBEINGS
        r = 0.90 * np.sqrt(plane)
        a = i * GA + PORTAL1_SPIN
        u = float(r * np.cos(a))
        v = float(r * np.sin(a))
        sz = 0.026 + 0.026 * plane
        body_color = np.clip(bw * plane + bd * (1 - plane), 0, 1)
        wing_color = np.clip(body_color * 0.82, 0, 1)
        has_halo = plane > 0.55

        beings.append({
            "index": i,
            "r": float(r),
            "angle": float(a),
            "x": u,
            "y": v,
            "size": float(sz),
            "plane": float(plane),
            "bodyColor": "#{:02x}{:02x}{:02x}".format(
                int(body_color[0] * 255),
                int(body_color[1] * 255),
                int(body_color[2] * 255)),
            "wingColor": "#{:02x}{:02x}{:02x}".format(
                int(wing_color[0] * 255),
                int(wing_color[1] * 255),
                int(wing_color[2] * 255)),
            "hasHalo": has_halo
        })

    atlas = {
        "tag": PORTAL1_TAG,
        "count": PORTAL1_NBEINGS,
        "spin": PORTAL1_SPIN,
        "goldenAngle": float(GA),
        "beings": beings
    }

    fn = os.path.join(OUT_DATA, f"{PORTAL1_TAG}_atlas.json")
    with open(fn, "w") as f:
        json.dump(atlas, f, separators=(",", ":"))
    print(f"ok {fn} ({len(beings)} beings)")


# ═══════════════════════════════════════════════════════════════════════════════
# SAN MARCO
# ═══════════════════════════════════════════════════════════════════════════════

SAN_MARCO_TAG = "san_marco"


def san_marco_base():
    """Generate san_marco base: gold tessera mosaic + decorative rings, WITHOUT figures."""
    fig, ax = newdome()
    base(ax, "#3a2a0e")

    # Gold tessera mosaic grid
    Ng = 118
    ii, jj = np.mgrid[0:Ng, 0:Ng]
    U = (jj - Ng / 2 + 0.5) / (Ng / 2)
    V = (ii - Ng / 2 + 0.5) / (Ng / 2)
    cell = 2.0 / Ng
    gold = hx("#c9a24a")
    polys = []; cols = []
    for x in range(Ng):
        for y in range(Ng):
            if U[x, y] ** 2 + V[x, y] ** 2 > 0.992 ** 2:
                continue
            u0, v0 = U[x, y] - cell / 2, V[x, y] - cell / 2
            jit = (rng.random() - 0.5) * 0.22
            col = np.clip(gold * (1 + jit) + hx("#e8cf86") * 0.12 * rng.random(), 0, 1)
            polys.append([(u0, v0), (u0 + cell, v0), (u0 + cell, v0 + cell), (u0, v0 + cell)])
            cols.append(col)
    clip(ax, ax.add_collection(
        PolyCollection(polys, facecolors=cols, edgecolors="none", zorder=2)
    ) or ax.collections[-1])

    # Decorative rings
    for rr in (0.965, 0.44):
        ax.add_patch(Circle((0, 0), rr, fill=False, ec=hx("#243c78"), lw=6, zorder=3))
        ax.add_patch(Circle((0, 0), rr - 0.012, fill=False, ec=hx("#a5301e"), lw=1.4, zorder=3))

    # Center medallion
    ax.add_patch(Circle((0, 0), 0.17, fc=hx("#1a2a55"), ec=hx("#caa24c"), lw=2.2, zorder=6))
    ax.add_patch(Circle((0, 0.02), 0.055, fc=hx("#e8cf86"), ec="none", zorder=7))
    ax.add_patch(Circle((0, 0.02), 0.085, fill=False, ec=hx("#ffe9a8"), lw=1.1, zorder=7))

    frame(ax, warm="#ffe6a0", ring="#caa24c", glow=0.24, rib=False, dark=0.4)
    _save_base(fig, SAN_MARCO_TAG)


def san_marco_atlas():
    """Generate JSON atlas with 30 processional figures in 2 rings."""
    figures = []
    idx = 0
    for ring_r, count, h in ((0.81, 18, 0.15), (0.53, 12, 0.14)):
        for kk in range(count):
            idx += 1
            a = 2 * np.pi * kk / count + (0 if ring_r > 0.7 else np.pi / count)
            d = np.array([np.cos(a), np.sin(a)])
            ctr = ring_r * d
            body_color = "#243c78" if kk % 2 == 0 else "#7a2a1e"
            halo_radius = float(h * 0.19)

            figures.append({
                "index": idx,
                "r": float(ring_r),
                "angle": float(a),
                "x": float(ctr[0]),
                "y": float(ctr[1]),
                "size": float(h),
                "bodyColor": body_color,
                "haloRadius": halo_radius
            })

    atlas = {
        "tag": SAN_MARCO_TAG,
        "count": len(figures),
        "rings": [
            {"r": 0.81, "count": 18, "figureHeight": 0.15},
            {"r": 0.53, "count": 12, "figureHeight": 0.14}
        ],
        "figures": figures
    }

    fn = os.path.join(OUT_DATA, f"{SAN_MARCO_TAG}_atlas.json")
    with open(fn, "w") as f:
        json.dump(atlas, f, separators=(",", ":"))
    print(f"ok {fn} ({len(figures)} figures)")


# ═══════════════════════════════════════════════════════════════════════════════
# MUQARNAS
# ═══════════════════════════════════════════════════════════════════════════════

MUQARNAS_TAG = "muqarnas"
MUQARNAS_TIERS = [0.985, 0.85, 0.72, 0.60, 0.49, 0.39, 0.30, 0.22, 0.15, 0.09]


def muqarnas_base():
    """Generate muqarnas base: dark background + frame only (no niches)."""
    fig, ax = newdome()
    base(ax, "#141018")
    frame(ax, warm="#f0d091", ring="#caa24c", glow=0.32, rib=False, dark=0.42)
    _save_base(fig, MUQARNAS_TAG)


def muqarnas_atlas():
    """Generate JSON atlas with all niche polygon data for 10 tiers."""
    tiers = MUQARNAS_TIERS
    tile = hx("#b98d4a")
    up = hx("#e6c680")
    niches = []

    for ti in range(len(tiers) - 1):
        r0 = tiers[ti]; r1 = tiers[ti + 1]
        n = max(6, int(round(2 * np.pi * ((r0 + r1) / 2) / ((r0 - r1) * 1.15))))
        off = (ti % 2) * (np.pi / n)
        shade = 0.45 + 0.55 * (ti / len(tiers))
        col = np.clip(tile * shade + up * 0.12, 0, 1)
        col_hex = "#{:02x}{:02x}{:02x}".format(
            int(col[0] * 255), int(col[1] * 255), int(col[2] * 255))

        for kk in range(n):
            a = 2 * np.pi * kk / n + off
            niches.append({
                "tier": ti,
                "index": kk,
                "n": n,
                "angle": float(a),
                "r0": float(r0),
                "r1": float(r1),
                "color": col_hex
            })

    # Center circle
    center = {
        "type": "center",
        "x": 0.0,
        "y": 0.0,
        "r": 0.07,
        "color": "#e6c680"
    }

    atlas = {
        "tag": MUQARNAS_TAG,
        "tiers": [float(t) for t in tiers],
        "nicheCount": len(niches),
        "niches": niches,
        "center": center
    }

    fn = os.path.join(OUT_DATA, f"{MUQARNAS_TAG}_atlas.json")
    with open(fn, "w") as f:
        json.dump(atlas, f, separators=(",", ":"))
    print(f"ok {fn} ({len(niches)} niches)")


# ═══════════════════════════════════════════════════════════════════════════════
# MANDALA
# ═══════════════════════════════════════════════════════════════════════════════

MANDALA_TAG = "mandala"
MANDALA_GOLD = "#d3ac54"


def mandala_base():
    """Generate mandala base: dark background + frame only (no geometric elements)."""
    fig, ax = newdome()
    base(ax, "#140a24")
    frame(ax, warm="#e8d29a", ring="#caa24c", glow=0.28, rib=False, dark=0.45)
    _save_base(fig, MANDALA_TAG)


def mandala_atlas():
    """Generate JSON atlas with rings, meridians, rosettes, and center."""
    elements = []

    # 11 angular rings from 0.10 to 0.96
    ring_radii = np.linspace(0.10, 0.96, 11)
    rings = []
    for rr in ring_radii:
        rings.append({
            "type": "ring",
            "r": float(rr),
            "color": MANDALA_GOLD
        })

    # 24 meridians
    meridians = []
    for k in range(24):
        a = 2 * np.pi * k / 24
        meridians.append({
            "type": "meridian",
            "angle": float(a),
            "r0": 0.06,
            "r1": 0.96,
            "color": MANDALA_GOLD
        })

    # 3 rosette rings: (r, count, radius)
    rosettes = []
    for ring_r, cnt in [(0.42, 12), (0.66, 18), (0.86, 24)]:
        for k in range(cnt):
            a = 2 * np.pi * k / cnt
            rosettes.append({
                "type": "rosette",
                "r": float(ring_r),
                "angle": float(a),
                "x": float(ring_r * np.cos(a)),
                "y": float(ring_r * np.sin(a)),
                "count": cnt,
                "radius": 0.145,
                "color": MANDALA_GOLD
            })

    # Center
    center = {
        "type": "center",
        "r": 0.05,
        "color": "#ffe6a0",
        "edgeColor": "#caa24c"
    }

    atlas = {
        "tag": MANDALA_TAG,
        "rings": rings,
        "meridians": meridians,
        "rosettes": rosettes,
        "center": center
    }

    fn = os.path.join(OUT_DATA, f"{MANDALA_TAG}_atlas.json")
    with open(fn, "w") as f:
        json.dump(atlas, f, separators=(",", ":"))
    print(f"ok {fn} ({len(rings)} rings, {len(meridians)} meridians, {len(rosettes)} rosettes)")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

WORLDS = {
    "portal_1": (portal_1_base, portal_1_atlas),
    "san_marco": (san_marco_base, san_marco_atlas),
    "muqarnas": (muqarnas_base, muqarnas_atlas),
    "mandala": (mandala_base, mandala_atlas),
}

if __name__ == "__main__":
    tags = sys.argv[1:] or list(WORLDS)
    for tag in tags:
        if tag not in WORLDS:
            print(f"unknown tag: {tag}, choices: {list(WORLDS.keys())}")
            continue
        gen_base, gen_atlas = WORLDS[tag]
        print(f"--- {tag} ---")
        gen_base()
        gen_atlas()
    print("done")
