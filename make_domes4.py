# -*- coding: utf-8 -*-
"""
КУПОЛА, набор 4: Небо каустик, Хроносвод, Сверхтекучее небо.

Три sci-fi свода строятся из явных научных моделей, а не из растровой
генерации: тонкая двойная гравитационная линза, причинный порядок 1+1-мерного
пространства-времени и фазовое поле решёточного набора квантованных вихрей.

Канонический формат серии: квадрат 1360 px, чистый круг на тёмном поле,
объёмное fisheye-затенение, без текста.

Запуск:
    /Users/gaidabura/cosmic-success/.venv/bin/python make_domes4.py [tag...]
"""
from __future__ import annotations

import sys

import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Polygon

import make_domes as M


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


def _lens_map(x, y, lenses):
    """Thin-lens map and Jacobian determinant for point masses."""
    beta_x = x.copy()
    beta_y = y.copy()
    gamma_1 = np.zeros_like(x)
    gamma_2 = np.zeros_like(x)
    for lx, ly, mass in lenses:
        dx = x - lx
        dy = y - ly
        r2 = dx * dx + dy * dy + 1.0e-5
        r4 = r2 * r2
        beta_x -= mass * dx / r2
        beta_y -= mass * dy / r2
        gamma_1 += mass * (dy * dy - dx * dx) / r4
        gamma_2 += -2.0 * mass * dx * dy / r4
    determinant = 1.0 - gamma_1 * gamma_1 - gamma_2 * gamma_2
    return beta_x, beta_y, determinant


# -- 1. НЕБО КАУСТИК -- двойная гравитационная линза и критические кривые --
def caustic():
    fig, ax = newdome()
    base(ax, "#050913")

    n = 720
    xs = np.linspace(-1.0, 1.0, n)
    xx, yy = np.meshgrid(xs, xs)
    rr = np.hypot(xx, yy)
    lenses = [(-0.31, 0.045, 0.36), (0.31, -0.045, 0.28)]
    bx, by, det = _lens_map(xx, yy, lenses)

    # Compact sources live in the source plane. Sampling them through the lens
    # equation creates repeated arcs in the observer's image plane.
    sources = [
        (-0.055, 0.015, 0.052, 0.018, 0.28, "#f0cf77", 1.00),
        (0.105, -0.115, 0.042, 0.015, -0.62, "#79b7ef", 0.82),
        (-0.205, 0.185, 0.036, 0.013, 0.92, "#d65742", 0.72),
        (0.245, 0.205, 0.030, 0.011, -0.24, "#b8d8f1", 0.62),
        (-0.315, -0.245, 0.026, 0.010, 0.55, "#d6ae53", 0.55),
    ]
    rgb = np.zeros((n, n, 3)) + hx("#071020")
    total = np.zeros((n, n))
    for sx, sy, major, minor, angle, color, weight in sources:
        dx = bx - sx
        dy = by - sy
        ca = np.cos(angle)
        sa = np.sin(angle)
        u = ca * dx + sa * dy
        v = -sa * dx + ca * dy
        source = np.exp(-0.5 * ((u / major) ** 2 + (v / minor) ** 2))
        halo = np.exp(-0.5 * ((u / (major * 2.8)) ** 2 + (v / (minor * 2.8)) ** 2))
        rgb += hx(color) * (weight * source + 0.12 * weight * halo)[..., None]
        total += weight * source

    # det(A)=0 is the critical curve: geometric optics predicts formally
    # divergent point-source magnification there. We render a finite glow.
    critical = np.exp(-np.abs(det) * 8.0)
    rgb += hx("#e5c46f") * (0.42 * critical)[..., None]
    rgb += hx("#426ea9") * (0.12 * np.clip(np.log1p(np.abs(det)), 0, 3) / 3.0)[..., None]
    rgb *= (0.72 + 0.28 * np.exp(-0.7 * rr * rr))[..., None]
    rgb = np.clip(rgb, 0.0, 1.0)

    image = np.zeros((n, n, 4))
    image[..., :3] = rgb
    image[..., 3] = (rr <= 1.0).astype(float)
    clip(ax, ax.imshow(image, extent=[-1, 1, -1, 1], origin="lower", zorder=3, interpolation="bilinear"))

    # The contour is drawn in the image plane and is therefore correctly
    # called a critical curve, not a caustic. Caustics live in the source plane.
    masked_det = np.where(rr <= 0.995, det, np.nan)
    critical_lines = ax.contour(
        xx,
        yy,
        masked_det,
        levels=[0.0],
        colors=["#ffe3a2"],
        linewidths=0.95,
        alpha=0.86,
        zorder=8,
    )
    clip(ax, critical_lines)

    # The masses remain almost absent: the world is read from how light bends
    # around them, not from a pictogram of the lenses themselves.
    for lx, ly, _ in lenses:
        ax.add_patch(Circle((lx, ly), 0.024, facecolor=hx("#020307"), edgecolor=hx("#9fb7d5"), linewidth=0.35, zorder=10))

    frame(ax, oculus=(0.0, 0.04), warm="#f4d994", ring="#b7954d", glow=0.10, rib=False, dark=0.40)
    save(fig, "caustic")


def _causal_links(events):
    """Hasse links of the causal order in flat 1+1 spacetime."""
    x = events[:, 0]
    t = events[:, 1]
    dt = t[None, :] - t[:, None]
    dx = np.abs(x[None, :] - x[:, None])
    causal = dt > dx + 0.018
    links = []
    for i in range(len(events)):
        for j in np.flatnonzero(causal[i]):
            if not np.any(causal[i] & causal[:, j]):
                links.append((events[i], events[j]))
    return links


# -- 2. ХРОНОСВОД -- световые конусы и причинное частичное упорядочение --
def chrono():
    fig, ax = newdome()
    base(ax, "#080812")

    # A central event separates its future, past and spacelike exterior.
    future = Polygon([(0, 0), (-0.94, 0.94), (0.94, 0.94)], closed=True, facecolor=hx("#17375b"), edgecolor="none", alpha=0.30, zorder=2)
    past = Polygon([(0, 0), (-0.94, -0.94), (0.94, -0.94)], closed=True, facecolor=hx("#571d27"), edgecolor="none", alpha=0.26, zorder=2)
    clip(ax, future)
    clip(ax, past)
    ax.add_patch(future)
    ax.add_patch(past)

    # Null-coordinate lattice: u=t-x and v=t+x. Its diagonals are possible
    # light paths; their cells are causal diamonds.
    null_segments = []
    for value in np.linspace(-1.30, 1.30, 15):
        s = np.linspace(-1.30, 1.30, 120)
        null_segments.append(np.column_stack([s, s + value]))
        null_segments.append(np.column_stack([s, -s + value]))
    grid = LineCollection(null_segments, colors=hx("#31547d"), linewidths=0.36, alpha=0.38, zorder=3)
    clip(ax, grid)
    ax.add_collection(grid)

    # A deterministic Poisson-like sprinkling of events. The retained links
    # are the transitive reduction: only immediate causal relations remain.
    rng = np.random.default_rng(9472)
    events = [(0.0, 0.0)]
    while len(events) < 92:
        x, t = rng.uniform(-0.92, 0.92, 2)
        if x * x + t * t < 0.86**2:
            events.append((x, t))
    events = np.asarray(events)
    order = np.argsort(events[:, 1])
    events = events[order]
    links = _causal_links(events)

    future_links = []
    past_links = []
    crossing_links = []
    for start, end in links:
        segment = np.vstack([start, end])
        midpoint_t = 0.5 * (start[1] + end[1])
        if start[1] < 0 < end[1]:
            crossing_links.append(segment)
        elif midpoint_t >= 0:
            future_links.append(segment)
        else:
            past_links.append(segment)
    for segments, color, width, alpha, zorder in [
        (past_links, "#a7473f", 0.52, 0.55, 5),
        (future_links, "#6f9fd3", 0.52, 0.58, 5),
        (crossing_links, "#e3c56e", 0.90, 0.78, 6),
    ]:
        collection = LineCollection(segments, colors=hx(color), linewidths=width, alpha=alpha, zorder=zorder)
        clip(ax, collection)
        ax.add_collection(collection)

    # Central light cone and a family of nested causal diamonds.
    for sign in (-1.0, 1.0):
        line = ax.plot(
            [-0.985, 0.985],
            [sign * -0.985, sign * 0.985],
            color="#eed797",
            lw=0.92,
            alpha=0.72,
            zorder=8,
        )[0]
        clip(ax, line)
    for radius in (0.23, 0.44, 0.66, 0.86):
        diamond = Polygon([(0, radius), (radius, 0), (0, -radius), (-radius, 0)], closed=True, fill=False, edgecolor=hx("#d3b765"), linewidth=0.40, alpha=0.34, zorder=7)
        clip(ax, diamond)
        ax.add_patch(diamond)

    x = events[:, 0]
    t = events[:, 1]
    future_mask = t > np.abs(x)
    past_mask = -t > np.abs(x)
    outside_mask = ~(future_mask | past_mask)
    ax.scatter(x[outside_mask], t[outside_mask], s=4.2, c="#6f667f", alpha=0.58, edgecolors="none", zorder=9)
    ax.scatter(x[past_mask], t[past_mask], s=5.2, c="#d25a49", alpha=0.82, edgecolors="#f1b09d", linewidths=0.15, zorder=9)
    ax.scatter(x[future_mask], t[future_mask], s=5.2, c="#7db4e8", alpha=0.84, edgecolors="#cbe5f5", linewidths=0.15, zorder=9)
    ax.add_patch(Circle((0, 0), 0.030, facecolor=hx("#f3dfaa"), edgecolor=hx("#fff2c8"), linewidth=0.75, zorder=11))

    frame(ax, oculus=(0.0, 0.0), warm="#f2dba4", ring="#b69a58", glow=0.17, rib=False, dark=0.44)
    save(fig, "chrono")


def _vortex_lattice(spacing=0.245, radius=0.79):
    """Triangular same-sign vortex lattice inside a circular condensate."""
    points = []
    row_height = spacing * np.sqrt(3.0) / 2.0
    for row in range(-5, 6):
        y = row * row_height
        offset = 0.5 * spacing if row % 2 else 0.0
        for column in range(-5, 6):
            x = column * spacing + offset
            if x * x + y * y < radius * radius:
                points.append((x, y))
    return np.asarray(points)


# -- 3. СВЕРХТЕКУЧЕЕ НЕБО -- фаза и решётка квантованных вихрей --
def superfluid():
    fig, ax = newdome()
    base(ax, "#060b17")

    vortices = _vortex_lattice()
    n = 680
    xs = np.linspace(-1.0, 1.0, n)
    xx, yy = np.meshgrid(xs, xs)
    rr = np.hypot(xx, yy)
    phase = np.zeros_like(xx)
    nearest = np.full_like(xx, 10.0)
    for vx, vy in vortices:
        dx = xx - vx
        dy = yy - vy
        phase += np.arctan2(dy, dx)
        nearest = np.minimum(nearest, np.hypot(dx, dy))
    phase01 = (np.mod(phase + np.pi, 2.0 * np.pi)) / (2.0 * np.pi)

    # The phase winds by 2pi around each core. Density is suppressed at the
    # core over a visualized healing-length scale; this is not a solved GP field.
    density = np.tanh(nearest / 0.030) ** 2
    envelope = np.clip(1.0 - (rr / 1.02) ** 8, 0.0, 1.0)
    palette = _ramp(
        phase01,
        [
            (0.00, "#112a56"),
            (0.18, "#2d73a7"),
            (0.38, "#45336f"),
            (0.58, "#8c2737"),
            (0.79, "#c28138"),
            (1.00, "#112a56"),
        ],
    )
    rgb = palette * (0.24 + 0.76 * density[..., None])
    rgb += hx("#d8bf72") * (0.11 * np.exp(-nearest / 0.020))[..., None]
    rgb *= (0.52 + 0.48 * envelope)[..., None]
    rgb = np.clip(rgb, 0.0, 1.0)
    image = np.zeros((n, n, 4))
    image[..., :3] = rgb
    image[..., 3] = (rr <= 1.0).astype(float)
    clip(ax, ax.imshow(image, extent=[-1, 1, -1, 1], origin="lower", zorder=3, interpolation="bilinear"))

    # Streamlines show the circulation implied by the phase gradient.
    flow_axis = np.linspace(-0.98, 0.98, 150)
    fx, fy = np.meshgrid(flow_axis, flow_axis)
    ux = np.zeros_like(fx)
    uy = np.zeros_like(fy)
    core_distance = np.full_like(fx, 10.0)
    for vx, vy in vortices:
        dx = fx - vx
        dy = fy - vy
        r2 = dx * dx + dy * dy + 0.0020
        ux += -dy / r2
        uy += dx / r2
        core_distance = np.minimum(core_distance, np.hypot(dx, dy))
    speed = np.hypot(ux, uy) + 1.0e-9
    ux /= speed
    uy /= speed
    mask = (np.hypot(fx, fy) > 0.965) | (core_distance < 0.028)
    ux = np.ma.array(ux, mask=mask)
    uy = np.ma.array(uy, mask=mask)
    streams = ax.streamplot(
        flow_axis,
        flow_axis,
        ux,
        uy,
        density=1.15,
        color="#ead59a",
        linewidth=0.34,
        arrowsize=0.01,
        minlength=0.08,
        zorder=7,
    )
    clip(ax, streams.lines)
    clip(ax, streams.arrows)

    for index, (vx, vy) in enumerate(vortices):
        edge = "#f1d88e" if index % 3 else "#9fc9e8"
        ax.add_patch(Circle((vx, vy), 0.021, facecolor=hx("#03050a"), edgecolor=hx(edge), linewidth=0.48, zorder=10))
        ax.add_patch(Circle((vx, vy), 0.006, facecolor=hx("#e8d49c"), edgecolor="none", alpha=0.82, zorder=11))

    frame(ax, oculus=(0.0, 0.0), warm="#efe0b4", ring="#b99445", glow=0.12, rib=False, dark=0.36)
    save(fig, "superfluid")


WORKS = {"caustic": caustic, "chrono": chrono, "superfluid": superfluid}


if __name__ == "__main__":
    for tag in (sys.argv[1:] or list(WORKS)):
        WORKS[tag]()
    print("done")
