# -*- coding: utf-8 -*-
"""
Generate Portal III layered assets:
  1) Base dome (cassons only, no beings) -> portal_3_base_{512,1024}.webp
  2) Figure atlas JSON (positions, sizes, palette of all 64 beings)

Uses same formulas as make_domes2.py _portal("portal_3", ..., 64, ..., 1.4)
Run: python make_portal3_layers.py
"""
import os, sys, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PolyCollection
from PIL import Image

# Import helpers from make_domes.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_domes as M
hx = M.hx; clip = M.clip; base = M.base; frame = M.frame; newdome = M.newdome; rng = M.rng

OUT_WEB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "fulldome", "web")
OUT_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "fulldome")
os.makedirs(OUT_WEB, exist_ok=True)
os.makedirs(OUT_DATA, exist_ok=True)

GA = np.pi * (3 - np.sqrt(5))

# Portal 3 parameters (from make_domes2.py line 175)
TAG = "portal_3"
BASE_COL = "#0c1226"
WARM = "#ffe8b0"
RING = "#c9a24c"
CLO_H = "#283a64"
CHI_H = "#caa040"
NBEINGS = 64
BW_H = "#f4d69a"
BD_H = "#2c3660"
SPIN = 1.4


def generate_base():
    """Generate portal_3 base dome WITHOUT beings (nbeings=0)."""
    fig, ax = newdome()
    base(ax, BASE_COL)

    # Casson grid (exact copy from _portal)
    ringr = [0.985, 0.86, 0.73, 0.60, 0.47, 0.35, 0.24, 0.15]
    ribs = [36, 30, 24, 20, 16, 12, 8]
    clo = hx(CLO_H)
    chi = hx(CHI_H)
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

    # Oculus glow (without beings)
    for rr, al in [(0.19, 0.14), (0.13, 0.22), (0.08, 0.34), (0.045, 0.6)]:
        ax.add_patch(Circle((0, 0), rr, fc=hx(WARM), ec="none", alpha=al, zorder=5))

    # Sparkle dots in center
    for _ in range(60):
        a = rng.random() * 2 * np.pi
        r = rng.random() * 0.13
        ax.add_patch(Circle((r * np.cos(a), r * np.sin(a)), 0.006,
                            fc=hx("#fff2cf"), ec="none", zorder=8))

    frame(ax, oculus=(0.0, 0.0), warm=WARM, ring=RING, glow=0.7, rib=False)

    # Save at multiple resolutions
    for size in [512, 1024]:
        dpi = size / 8  # fig is 8x8 inches
        fn_png = os.path.join(OUT_WEB, f"portal_3_base_{size}.png")
        fig.savefig(fn_png, transparent=False, dpi=dpi,
                    facecolor=fig.get_facecolor())
        # Convert to webp
        fn_webp = os.path.join(OUT_WEB, f"portal_3_base_{size}.webp")
        img = Image.open(fn_png)
        img.save(fn_webp, "WEBP", quality=88)
        print(f"ok {fn_webp}")
        os.remove(fn_png)  # keep only webp

    plt.close(fig)


def generate_atlas():
    """Generate JSON atlas with being positions/sizes/colors."""
    beings = []
    for i in range(1, NBEINGS + 1):
        plane = i / NBEINGS
        r = 0.90 * np.sqrt(plane)
        a = i * GA + SPIN
        u = float(r * np.cos(a))
        v = float(r * np.sin(a))
        sz = 0.026 + 0.026 * plane
        # Color interpolation (warm body → dark body by plane)
        bw = hx(BW_H)
        bd = hx(BD_H)
        body_color = np.clip(bw * plane + bd * (1 - plane), 0, 1)
        wing_color = np.clip(body_color * 0.82, 0, 1)
        # Halo threshold
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
                int(body_color[2] * 255)
            ),
            "wingColor": "#{:02x}{:02x}{:02x}".format(
                int(wing_color[0] * 255),
                int(wing_color[1] * 255),
                int(wing_color[2] * 255)
            ),
            "hasHalo": has_halo
        })

    atlas = {
        "tag": TAG,
        "count": NBEINGS,
        "spin": SPIN,
        "goldenAngle": float(GA),
        "beings": beings
    }

    fn = os.path.join(OUT_DATA, "portal_3_atlas.json")
    with open(fn, "w") as f:
        json.dump(atlas, f, separators=(",", ":"))
    print(f"ok {fn} ({len(beings)} beings)")


if __name__ == "__main__":
    generate_base()
    generate_atlas()
    print("done: portal_3 layers generated")
