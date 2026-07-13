# -*- coding: utf-8 -*-
"""
КУПОЛА, набор 3: Камертон, Апейрон, Тяга.

Три самостоятельных закона в каноническом формате серии: квадрат 1360 px,
чистый круг на тёмном поле, объёмное fisheye-затенение, без текста.

Запуск:
    /Users/gaidabura/cosmic-success/.venv/bin/python make_domes3.py [tag...]
"""
from __future__ import annotations

from collections import deque
import sys

import numpy as np
from scipy.special import jn_zeros, jv

import make_domes as M
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle


hx = M.hx
clip = M.clip
base = M.base
frame = M.frame
newdome = M.newdome
save = M.save


def _ramp(values, stops):
    """Piecewise-linear RGB palette for a scalar field in [0, 1]."""
    out = np.zeros(values.shape + (3,))
    xs = [stop[0] for stop in stops]
    for channel in range(3):
        ys = [hx(stop[1])[channel] for stop in stops]
        out[..., channel] = np.interp(values, xs, ys)
    return out


# ── 1. КАМЕРТОН — узловые линии связанных мод круглой мембраны ──
def chladni():
    fig, ax = newdome()
    base(ax, "#080914")

    n = 720
    xs = np.linspace(-1.0, 1.0, n)
    xx, yy = np.meshgrid(xs, xs)
    rr = np.hypot(xx, yy)
    theta = np.arctan2(yy, xx)

    # Две слабосвязанные собственные моды круглой мембраны. Нули функций
    # Бесселя задают радиальные узлы; cos(m*theta) — угловые.
    a = jn_zeros(7, 3)[-1]
    b = jn_zeros(3, 5)[-1]
    mode_a = jv(7, a * rr) * np.cos(7 * theta)
    mode_b = jv(3, b * rr) * np.sin(3 * theta + 0.34)
    field = mode_a + 0.46 * mode_b
    field /= np.nanmax(np.abs(field)) + 1e-12

    signed = np.clip(0.5 + 0.5 * field, 0.0, 1.0)
    rgb = _ramp(
        signed,
        [
            (0.00, "#4a1218"),
            (0.31, "#1e1732"),
            (0.50, "#090a17"),
            (0.69, "#102d61"),
            (1.00, "#2c67a8"),
        ],
    )

    # У узлов свет собирается в песчаную золотую линию.
    node = np.exp(-np.abs(field) * 46.0)
    gold = hx("#e2bd62")
    rgb = np.clip(rgb * (0.72 + 0.28 * (1.0 - node[..., None])) + gold * node[..., None] * 0.88, 0, 1)
    img = np.zeros((n, n, 4))
    img[..., :3] = rgb
    img[..., 3] = (rr <= 1.0).astype(float)
    clip(ax, ax.imshow(img, extent=[-1, 1, -1, 1], origin="lower", zorder=3, interpolation="bilinear"))

    masked = np.where(rr <= 0.995, field, np.nan)
    ax.contour(xx, yy, masked, levels=[0.0], colors=["#ffe2a0"], linewidths=1.05, zorder=6)
    ax.contour(xx, yy, masked, levels=[-0.11, 0.11], colors=["#8aa9dc"], linewidths=0.32, alpha=0.55, zorder=5)
    frame(ax, warm="#f0d692", ring="#caa24c", glow=0.16, rib=False, dark=0.38)
    save(fig, "chladni")


# ── 2. АПЕЙРОН — аполлониева упаковка окружностей ──
def _apollonian_circles(max_depth=8, min_radius=0.0065):
    """Return unique inner circles from a deterministic Apollonian gasket."""
    inner_r = 2.0 * np.sqrt(3.0) - 3.0
    inner_b = 1.0 / inner_r
    center_r = 1.0 - inner_r
    angles = np.deg2rad([90.0, 210.0, 330.0])

    outer = (-1.0, 0.0 + 0.0j, 0)
    inner = [(inner_b, center_r * np.exp(1j * angle), 0) for angle in angles]
    start = tuple([outer] + inner)

    circles = {}
    queue = deque([(start, 0, -1)])
    seen_configs = set()

    def remember(circle):
        curvature, center, generation = circle
        if curvature <= 0:
            return
        radius = 1.0 / curvature
        if radius < min_radius or abs(center) + radius > 1.0008:
            return
        key = (round(center.real, 7), round(center.imag, 7), round(radius, 7))
        old = circles.get(key)
        if old is None or generation < old[2]:
            circles[key] = (curvature, center, generation)

    for circle in inner:
        remember(circle)

    while queue:
        config, depth, blocked = queue.popleft()
        if depth >= max_depth:
            continue
        signature = tuple(sorted((round(c[0], 6), round(c[1].real, 6), round(c[1].imag, 6)) for c in config))
        if (signature, blocked) in seen_configs:
            continue
        seen_configs.add((signature, blocked))

        for index in range(4):
            if index == blocked:
                continue
            others = [config[j] for j in range(4) if j != index]
            old = config[index]
            new_b = 2.0 * sum(c[0] for c in others) - old[0]
            if abs(new_b) < 1e-12:
                continue
            new_z = (2.0 * sum(c[0] * c[1] for c in others) - old[0] * old[1]) / new_b
            new_circle = (new_b, new_z, depth + 1)
            remember(new_circle)
            if new_b > 0 and 1.0 / new_b >= min_radius:
                next_config = list(config)
                next_config[index] = new_circle
                queue.append((tuple(next_config), depth + 1, index))

    return list(circles.values())


def apollon():
    fig, ax = newdome()
    base(ax, "#100811")
    circles = _apollonian_circles()

    # Крупные чаши ложатся первыми, малые заполняют оставшиеся просветы.
    circles.sort(key=lambda circle: 1.0 / circle[0], reverse=True)
    for curvature, center, generation in circles:
        radius = 1.0 / curvature
        angle = (np.angle(center) + np.pi) / (2.0 * np.pi)
        depth = np.clip(np.log10(1.0 / radius) / 2.25, 0.0, 1.0)
        if generation % 5 == 0:
            edge = hx("#c0442c")
        elif angle < 0.34:
            edge = hx("#d3a94d")
        elif angle < 0.67:
            edge = hx("#8aa9d6")
        else:
            edge = hx("#e7cf91")

        fill = np.clip(hx("#201227") * (0.72 + 0.25 * depth) + edge * (0.05 + 0.10 * (1.0 - depth)), 0, 1)
        lw = np.clip(0.34 + 1.45 * np.sqrt(radius), 0.35, 1.45)
        ax.add_patch(
            Circle(
                (center.real, center.imag),
                radius,
                facecolor=fill,
                edgecolor=edge,
                linewidth=lw,
                alpha=0.96,
                zorder=3 + min(generation, 12) * 0.02,
            )
        )

    frame(ax, oculus=(0.0, 0.0), warm="#f0d499", ring="#caa24c", glow=0.24, rib=False, dark=0.42)
    save(fig, "apollon")


# ── 3. ТЯГА — попарно ветвящаяся сеть усилий ──
def _polar_curve(r0, a0, r1, a1, count=30):
    """Smooth polar branch between two network nodes."""
    delta = (a1 - a0 + np.pi) % (2.0 * np.pi) - np.pi
    t = np.linspace(0.0, 1.0, count)
    smooth = t * t * (3.0 - 2.0 * t)
    radius = r0 + (r1 - r0) * smooth
    angle = a0 + delta * smooth + 0.012 * np.sin(np.pi * t) * np.sign(delta or 1.0)
    return np.column_stack([radius * np.cos(angle), radius * np.sin(angle)])


def tyaga():
    fig, ax = newdome()
    base(ax, "#09101c")

    radii = [0.985, 0.835, 0.690, 0.550, 0.420, 0.305]
    levels = []
    angles = np.linspace(0.0, 2.0 * np.pi, 96, endpoint=False)
    angles += 0.007 * np.sin(np.arange(96) * np.pi / 3.0)
    levels.append([(radii[0], angle) for angle in angles])

    branches_by_level = []
    for level_index, next_radius in enumerate(radii[1:], start=1):
        children = levels[-1]
        parents = []
        branches = []
        for pair_index in range(0, len(children), 2):
            left = children[pair_index]
            right = children[(pair_index + 1) % len(children)]
            vector = np.exp(1j * left[1]) + np.exp(1j * right[1])
            parent_angle = np.angle(vector) + 0.010 * np.sin((pair_index // 2 + level_index) * 1.7)
            parent = (next_radius, parent_angle)
            parents.append(parent)
            branches.append(_polar_curve(*left, *parent))
            branches.append(_polar_curve(*right, *parent))
        levels.append(parents)
        branches_by_level.append(branches)

    # Последние три несущие ветви принимают усилие у малого центрального света.
    central = []
    for index, node in enumerate(levels[-1]):
        target = (0.070, node[1] + (index - 1) * 0.025)
        central.append(_polar_curve(*node, *target, count=36))
    branches_by_level.append(central)

    palette = ["#8a6a2f", "#aa8236", "#c69a42", "#d8ad52", "#ebca78", "#f4dda0"]
    for level_index, branches in enumerate(branches_by_level):
        width = 0.75 + level_index * 0.38
        # Тёмная подкладка делает каждую линию читаемой как отдельное ребро.
        clip(
            ax,
            ax.add_collection(
                LineCollection(branches, colors=hx("#03050a"), linewidths=width * 3.2, alpha=0.72, zorder=3)
            ) or ax.collections[-1],
        )
        clip(
            ax,
            ax.add_collection(
                LineCollection(
                    branches,
                    colors=hx(palette[min(level_index, len(palette) - 1)]),
                    linewidths=width,
                    capstyle="round",
                    joinstyle="round",
                    zorder=4 + level_index,
                )
            ) or ax.collections[-1],
        )

    # Узлы остаются видимыми: это точки передачи, а не декоративные бусины.
    for level_index, nodes in enumerate(levels[1:]):
        radius = 0.0065 + level_index * 0.0011
        for node_index, (ring_r, angle) in enumerate(nodes):
            color = "#a93b2b" if (node_index + level_index) % 4 == 0 else "#88a9d5"
            ax.add_patch(
                Circle(
                    (ring_r * np.cos(angle), ring_r * np.sin(angle)),
                    radius,
                    facecolor=hx(color),
                    edgecolor=hx("#ead39a"),
                    linewidth=0.22,
                    zorder=12,
                )
            )

    ax.add_patch(Circle((0, 0), 0.071, facecolor=hx("#efe0b6"), edgecolor=hx("#caa24c"), linewidth=1.2, zorder=13))
    ax.add_patch(Circle((0, 0), 0.045, facecolor=hx("#111725"), edgecolor="none", zorder=14))
    frame(ax, oculus=(0.0, 0.0), warm="#f1d99b", ring="#caa24c", glow=0.34, rib=False, dark=0.36)
    save(fig, "tyaga")


WORKS = {"chladni": chladni, "apollon": apollon, "tyaga": tyaga}


if __name__ == "__main__":
    for tag in (sys.argv[1:] or list(WORKS)):
        WORKS[tag]()
    print("done")
