#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Far Voice Cathedral — one C-K-derived architectural concept.

This is not a pattern generator.  It builds one spatial proposition and records
what is proven and what is not:

* twelve pairs of voice niches are the foci of twelve prolate spheroids;
* narrow reflective strips cut from those spheroids become acoustic/structural ribs;
* every geometric-acoustic ray emitted from one focus and reflected by its rib
  reaches the opposite focus, and every reflected path has equal length 2a;
* the remaining inner dome is specified as absorptive so the central gathering
  is a different, deliberately quiet acoustic state.

The script outputs a 1360-square interior study, an architectural plate, and a
machine-readable proof.  It does not claim room-acoustic performance: diffraction,
material impedance, scattering, background noise, speech directivity, and structural
engineering remain RIBA Stage 3/4 work.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)
PROOF_PATH = HERE.parent / "FAR_VOICE_PROOF.json"

SIZE = 1360
AA = 2
W = SIZE * AA

HALL_RADIUS_M = 39.0
SHELL_APEX_M = 42.0
PAIR_COUNT = 12
FOCUS_RADIUS_M = 30.0
FOCUS_Z_M = 1.55
ELLIPSE_A_M = 46.0
ELLIPSE_B_M = math.sqrt(ELLIPSE_A_M**2 - FOCUS_RADIUS_M**2)
RIB_WIDTH_M = 3.2
MU_START = 0.675
CROWN_RADIUS_M = 5.6
SOUND_SPEED_M_S = 343.0

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        raise ValueError("zero vector")
    return np.asarray(v, dtype=float) / n


def mix(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = float(np.clip(t, 0.0, 1.0))
    return tuple(int(round(x * (1 - t) + y * t)) for x, y in zip(a, b))


def scale(c: tuple[int, int, int], k: float) -> tuple[int, int, int]:
    return tuple(int(round(np.clip(v * k, 0, 255))) for v in c)


def axis_basis(alpha: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    e = np.array([math.cos(alpha), math.sin(alpha), 0.0])
    v = np.array([-math.sin(alpha), math.cos(alpha), 0.0])
    z = np.array([0.0, 0.0, 1.0])
    return e, v, z


def rib_point(alpha: float, mu: float, side: float = 0.0) -> np.ndarray:
    """Point on a prolate spheroid with foci ±c along horizontal axis alpha.

    side is a physical cross-rib offset in metres, converted to the spheroid's
    azimuth.  The returned point remains on the exact ellipsoid of revolution.
    """
    e, v, z = axis_basis(alpha)
    u = ELLIPSE_A_M * math.cos(mu)
    rho = ELLIPSE_B_M * math.sin(mu)
    psi = math.asin(float(np.clip(side / max(rho, 1e-9), -0.95, 0.95)))
    radial = math.sin(psi) * v + math.cos(psi) * z
    return u * e + rho * radial + np.array([0.0, 0.0, FOCUS_Z_M])


def spheroid_normal(alpha: float, p: np.ndarray) -> np.ndarray:
    e, _, _ = axis_basis(alpha)
    local = p - np.array([0.0, 0.0, FOCUS_Z_M])
    u = float(np.dot(local, e))
    radial = local - u * e
    return unit((u / ELLIPSE_A_M**2) * e + radial / ELLIPSE_B_M**2)


def reflect(direction: np.ndarray, normal: np.ndarray) -> np.ndarray:
    d = unit(direction)
    n = unit(normal)
    return unit(d - 2 * float(np.dot(d, n)) * n)


@dataclass
class Camera:
    position: np.ndarray
    forward: np.ndarray
    right: np.ndarray
    up: np.ndarray
    focal_px: float
    center: tuple[float, float]

    @classmethod
    def looking(cls, position, target, focal_px, center):
        position = np.asarray(position, dtype=float)
        forward = unit(np.asarray(target, dtype=float) - position)
        right = unit(np.cross(forward, np.array([0.0, 0.0, 1.0])))
        up = unit(np.cross(right, forward))
        return cls(position, forward, right, up, focal_px, center)

    def project(self, p: np.ndarray) -> tuple[float, float, float] | None:
        q = np.asarray(p, dtype=float) - self.position
        depth = float(np.dot(q, self.forward))
        if depth <= 0.1:
            return None
        x = float(np.dot(q, self.right)) / depth
        y = float(np.dot(q, self.up)) / depth
        return self.center[0] + self.focal_px * x, self.center[1] - self.focal_px * y, depth


def background() -> Image.Image:
    yy, xx = np.mgrid[0:W, 0:W]
    cx, cy = W * 0.50, W * 0.48
    dx = (xx - cx) / W
    dy = (yy - cy) / W
    r = np.hypot(dx, dy)
    top = np.clip(1 - (yy / W), 0, 1)
    glow = np.exp(-((dx / 0.19) ** 2 + ((dy + 0.20) / 0.17) ** 2))
    vignette = np.clip(1 - 1.35 * r, 0, 1)
    base = np.zeros((W, W, 3), dtype=float)
    base[..., 0] = 4 + 5 * top + 8 * vignette + 11 * glow
    base[..., 1] = 6 + 8 * top + 8 * vignette + 10 * glow
    base[..., 2] = 12 + 15 * top + 14 * vignette + 10 * glow
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def draw_polyline(draw: ImageDraw.ImageDraw, camera: Camera, points, fill, width=1, joint="curve"):
    projected = [camera.project(np.asarray(p)) for p in points]
    projected = [(p[0], p[1]) for p in projected if p is not None]
    if len(projected) > 1:
        draw.line(projected, fill=fill, width=width, joint=joint)


def interior() -> None:
    image = background()
    draw = ImageDraw.Draw(image, "RGBA")
    camera = Camera.looking(
        position=[0.0, -27.5, 1.65],
        target=[0.0, 4.5, 14.0],
        focal_px=1320.0,
        center=(W * 0.50, W * 0.50),
    )

    # Dark outer shell: only construction traces remain visible.
    shell = []
    for lat in np.linspace(0.18, math.pi / 2, 8):
        pts = []
        for phi in np.linspace(0, 2 * math.pi, 361):
            p = np.array([
                HALL_RADIUS_M * math.sin(lat) * math.cos(phi),
                HALL_RADIUS_M * math.sin(lat) * math.sin(phi),
                SHELL_APEX_M * math.cos(lat),
            ])
            pts.append(p)
        shell.append(pts)
    for pts in shell:
        draw_polyline(draw, camera, pts, (77, 85, 104, 34), width=AA)
    for phi in np.linspace(0, 2 * math.pi, 24, endpoint=False):
        pts = [
            np.array([
                HALL_RADIUS_M * math.sin(lat) * math.cos(phi),
                HALL_RADIUS_M * math.sin(lat) * math.sin(phi),
                SHELL_APEX_M * math.cos(lat),
            ])
            for lat in np.linspace(0.04, math.pi / 2, 120)
        ]
        draw_polyline(draw, camera, pts, (74, 81, 99, 28), width=AA)

    # Floor rings establish the enormous human scale without filling the void.
    for rr in (7.5, 16.0, 24.0, 32.0, 39.0):
        pts = [np.array([rr * math.cos(t), rr * math.sin(t), 0.0]) for t in np.linspace(0, 2 * math.pi, 361)]
        draw_polyline(draw, camera, pts, (134, 123, 105, 50 if rr < 32 else 75), width=AA)
    for phi in np.linspace(0, 2 * math.pi, 24, endpoint=False):
        pts = [np.array([r * math.cos(phi), r * math.sin(phi), 0.0]) for r in np.linspace(7.5, 39, 60)]
        draw_polyline(draw, camera, pts, (108, 99, 91, 26), width=AA)

    # Twenty-four voice chambers, one at each acoustic focus.
    chambers = []
    for k in range(PAIR_COUNT * 2):
        phi = 2 * math.pi * k / (PAIR_COUNT * 2)
        center = np.array([FOCUS_RADIUS_M * math.cos(phi), FOCUS_RADIUS_M * math.sin(phi), 0.0])
        tang = np.array([-math.sin(phi), math.cos(phi), 0.0])
        pts = [
            center - 1.55 * tang,
            center + 1.55 * tang,
            center + 1.55 * tang + np.array([0, 0, 4.8]),
            center - 1.55 * tang + np.array([0, 0, 4.8]),
        ]
        proj = [camera.project(p) for p in pts]
        if all(proj):
            chambers.append((sum(p[2] for p in proj) / 4, [(p[0], p[1]) for p in proj], k))
    for _, pts, k in sorted(chambers, reverse=True):
        col = (115, 91, 65, 155) if k % 2 else (154, 126, 79, 185)
        draw.polygon(pts, fill=(15, 14, 18, 235), outline=col)
        # Narrow luminous threshold, not a screen.
        mid0 = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        mid1 = ((pts[2][0] + pts[3][0]) / 2, (pts[2][1] + pts[3][1]) / 2)
        draw.line([mid0, mid1], fill=(215, 175, 97, 125), width=AA)

    # Exact ellipsoidal acoustic ribs.  Their width is structural, their curvature acoustic.
    faces = []
    edges = []
    mus = np.linspace(MU_START, math.pi - MU_START, 96)
    stone0 = (91, 77, 68)
    stone1 = (217, 196, 155)
    light = unit(np.array([-0.28, -0.36, 0.89]))
    for k in range(PAIR_COUNT):
        alpha = math.pi * k / PAIR_COUNT
        left = [rib_point(alpha, float(mu), -RIB_WIDTH_M / 2) for mu in mus]
        right = [rib_point(alpha, float(mu), RIB_WIDTH_M / 2) for mu in mus]
        # Crown removes collision of twelve exact spheroidal strips.
        visible = [math.hypot(float(p[0]), float(p[1])) >= CROWN_RADIUS_M for p in left]
        for i in range(len(mus) - 1):
            if not (visible[i] and visible[i + 1]):
                continue
            verts = [left[i], right[i], right[i + 1], left[i + 1]]
            proj = [camera.project(p) for p in verts]
            if not all(proj):
                continue
            mid = sum(verts) / 4
            n = spheroid_normal(alpha, mid)
            illum = 0.35 + 0.65 * abs(float(np.dot(n, light)))
            axial = 0.5 + 0.5 * math.cos(2 * mus[i] + alpha)
            c = mix(stone0, stone1, 0.18 + 0.53 * illum)
            c = scale(c, 0.91 + 0.08 * axial)
            if k == 0:
                c = mix(c, (236, 184, 91), 0.22)
            faces.append((sum(p[2] for p in proj) / 4, [(p[0], p[1]) for p in proj], c, k))
        edges.append((left, right, k))

    # One blurred field makes the stone appear luminous without turning it into neon.
    halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for _, pts, c, _ in sorted(faces, reverse=True):
        hd.polygon(pts, fill=(*scale(c, 1.12), 34))
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(14 * AA)))
    draw = ImageDraw.Draw(image, "RGBA")
    for _, pts, c, k in sorted(faces, reverse=True):
        draw.polygon(pts, fill=(*c, 235), outline=(42, 35, 32, 165))

    for left, right, k in edges:
        for boundary in (left, right):
            chunks = []
            current = []
            for p in boundary:
                if math.hypot(float(p[0]), float(p[1])) < CROWN_RADIUS_M:
                    if len(current) > 1:
                        chunks.append(current)
                    current = []
                else:
                    current.append(p)
            if len(current) > 1:
                chunks.append(current)
            for chunk in chunks:
                draw_polyline(draw, camera, chunk, (243, 218, 166, 175), width=AA)

    # Compression crown / oculus: the only common architectural object.
    crown_z = FOCUS_Z_M + ELLIPSE_B_M * math.sqrt(1 - (CROWN_RADIUS_M / ELLIPSE_A_M) ** 2)
    ring = [np.array([CROWN_RADIUS_M * math.cos(t), CROWN_RADIUS_M * math.sin(t), crown_z]) for t in np.linspace(0, 2 * math.pi, 361)]
    ring_proj = [camera.project(p) for p in ring]
    ring_xy = [(p[0], p[1]) for p in ring_proj if p]
    crown_halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ch = ImageDraw.Draw(crown_halo)
    ch.line(ring_xy, fill=(242, 210, 138, 120), width=15 * AA)
    image.alpha_composite(crown_halo.filter(ImageFilter.GaussianBlur(18 * AA)))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.line(ring_xy, fill=(250, 229, 181, 245), width=4 * AA, joint="curve")

    # A selected pair is audible as geometry, but the rays remain almost immaterial.
    alpha = 0.0
    e, _, _ = axis_basis(alpha)
    source = FOCUS_RADIUS_M * e + np.array([0.0, 0.0, FOCUS_Z_M])
    target = -FOCUS_RADIUS_M * e + np.array([0.0, 0.0, FOCUS_Z_M])
    ray_layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ray_layer)
    for mu in (0.86, 1.02, 2.12, 2.28):
        p = rib_point(alpha, mu, 0.0)
        points = [source, p, target]
        proj = [camera.project(q) for q in points]
        if all(proj):
            rd.line([(q[0], q[1]) for q in proj], fill=(241, 183, 75, 86), width=AA)
    image.alpha_composite(ray_layer.filter(ImageFilter.GaussianBlur(2 * AA)))

    # Human scale: a sparse, warm field of bodies within the acoustically quiet centre.
    draw = ImageDraw.Draw(image, "RGBA")
    rng = np.random.default_rng(9482)
    people = []
    for _ in range(90):
        rr = math.sqrt(rng.uniform(0.0, 1.0)) * 15.5
        phi = rng.uniform(0, 2 * math.pi)
        p0 = np.array([rr * math.cos(phi), rr * math.sin(phi), 0.0])
        p1 = p0 + np.array([0, 0, rng.uniform(1.55, 1.9)])
        q0, q1 = camera.project(p0), camera.project(p1)
        if q0 and q1:
            people.append(((q0[2] + q1[2]) / 2, q0, q1))
    for _, q0, q1 in sorted(people, reverse=True):
        width = max(1, int(2.4 * AA * 18 / q0[2]))
        draw.line([(q0[0], q0[1]), (q1[0], q1[1])], fill=(124, 113, 96, 205), width=width)
        rr = max(1, width)
        draw.ellipse([q1[0] - rr, q1[1] - rr, q1[0] + rr, q1[1] + rr], fill=(167, 146, 108, 225))

    image = image.convert("RGB").resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    image.save(OUT / "dome_far_voice.jpg", quality=96, subsampling=0, dpi=(170, 170))
    print("ok dome_far_voice.jpg")


def font(size: int, bold: bool = False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def board() -> None:
    bw, bh = 1920, 1440
    image = Image.new("RGB", (bw, bh), (10, 10, 14))
    draw = ImageDraw.Draw(image)
    ink = (229, 222, 207)
    muted = (154, 150, 146)
    gold = (213, 170, 85)
    line = (68, 66, 70)
    blue = (107, 151, 175)

    draw.text((72, 48), "СОБОР ДАЛЬНЕГО ГОЛОСА", font=font(48, True), fill=ink)
    draw.text((74, 108), "один замысел · C-K → RIBA Stage 2 · не изображение, а пассивная связь", font=font(22), fill=muted)
    draw.line((72, 151, bw - 72, 151), fill=line, width=2)

    # PLAN
    ox, oy, rr = 350, 490, 270
    draw.text((72, 185), "01  ПЛАН · Ø78 м", font=font(24, True), fill=gold)
    draw.ellipse((ox - rr, oy - rr, ox + rr, oy + rr), outline=ink, width=2)
    draw.ellipse((ox - rr * 0.77, oy - rr * 0.77, ox + rr * 0.77, oy + rr * 0.77), outline=line, width=1)
    draw.ellipse((ox - rr * CROWN_RADIUS_M / HALL_RADIUS_M, oy - rr * CROWN_RADIUS_M / HALL_RADIUS_M,
                  ox + rr * CROWN_RADIUS_M / HALL_RADIUS_M, oy + rr * CROWN_RADIUS_M / HALL_RADIUS_M), outline=gold, width=4)
    for k in range(PAIR_COUNT):
        a = math.pi * k / PAIR_COUNT
        x0, y0 = ox - rr * 0.91 * math.cos(a), oy - rr * 0.91 * math.sin(a)
        x1, y1 = ox + rr * 0.91 * math.cos(a), oy + rr * 0.91 * math.sin(a)
        draw.line((x0, y0, x1, y1), fill=(148, 128, 98), width=5)
        for sign in (-1, 1):
            x = ox + sign * rr * FOCUS_RADIUS_M / HALL_RADIUS_M * math.cos(a)
            y = oy + sign * rr * FOCUS_RADIUS_M / HALL_RADIUS_M * math.sin(a)
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=gold)
    draw.ellipse((ox - rr * 0.40, oy - rr * 0.40, ox + rr * 0.40, oy + rr * 0.40), outline=blue, width=2)
    draw.text((91, 790), "24 ниши-фокуса", font=font(19, True), fill=ink)
    draw.text((91, 820), "12 акустических пар", font=font(18), fill=muted)
    draw.text((356, 790), "центр · 1200 человек", font=font(19, True), fill=ink)
    draw.text((356, 820), "поглощающее тихое поле", font=font(18), fill=muted)

    # SECTION
    sx0, sy0, sw, sh = 790, 220, 1040, 620
    draw.text((sx0, 185), "02  РАЗРЕЗ · РАВНЫЙ ПУТЬ ЗВУКА", font=font(24, True), fill=gold)
    floor_y = sy0 + sh - 40
    scale_x = sw / (2 * HALL_RADIUS_M + 8)
    scale_z = (sh - 100) / SHELL_APEX_M
    cx = sx0 + sw / 2
    draw.line((sx0, floor_y, sx0 + sw, floor_y), fill=line, width=2)
    # Outer dome.
    shell_pts = []
    for t in np.linspace(-math.pi / 2, math.pi / 2, 240):
        x = HALL_RADIUS_M * math.sin(t)
        z = SHELL_APEX_M * math.cos(t)
        shell_pts.append((cx + x * scale_x, floor_y - z * scale_z))
    draw.line(shell_pts, fill=(73, 80, 97), width=3)
    # Ellipse rib centreline and crown cut.
    rib_pts = []
    for mu in np.linspace(MU_START, math.pi - MU_START, 300):
        x = ELLIPSE_A_M * math.cos(mu)
        z = FOCUS_Z_M + ELLIPSE_B_M * math.sin(mu)
        if abs(x) >= CROWN_RADIUS_M:
            rib_pts.append((cx + x * scale_x, floor_y - z * scale_z))
        elif len(rib_pts) > 1:
            draw.line(rib_pts, fill=(224, 202, 163), width=10)
            rib_pts = []
    if len(rib_pts) > 1:
        draw.line(rib_pts, fill=(224, 202, 163), width=10)
    # Foci, one reflection and equal path.
    f1 = (cx - FOCUS_RADIUS_M * scale_x, floor_y - FOCUS_Z_M * scale_z)
    f2 = (cx + FOCUS_RADIUS_M * scale_x, floor_y - FOCUS_Z_M * scale_z)
    for f in (f1, f2):
        draw.ellipse((f[0] - 8, f[1] - 8, f[0] + 8, f[1] + 8), fill=gold)
    mu = 1.02
    px = cx + ELLIPSE_A_M * math.cos(mu) * scale_x
    py = floor_y - (FOCUS_Z_M + ELLIPSE_B_M * math.sin(mu)) * scale_z
    draw.line((f1[0], f1[1], px, py, f2[0], f2[1]), fill=gold, width=3)
    draw.text((f1[0] - 70, f1[1] + 18), "голос A", font=font(17), fill=ink)
    draw.text((f2[0] + 12, f2[1] + 18), "слушатель B", font=font(17), fill=ink)
    draw.text((sx0 + 25, sy0 + 36), "|A–P| + |P–B| = 2a = 92 м", font=font(22, True), fill=ink)
    draw.text((sx0 + 25, sy0 + 72), "время прохождения ≈ 268 мс · прямой путь экранирован нишей", font=font(18), fill=muted)

    draw.line((72, 890, bw - 72, 890), fill=line, width=2)

    # MODULE
    draw.text((72, 925), "03  РЕБРО · ОДНА ФОРМА, ТРИ РАБОТЫ", font=font(24, True), fill=gold)
    mx, my = 95, 1005
    layers = [
        (54, (194, 151, 86), "60 мм плотная терракота · отражение 1–4 кГц"),
        (92, (107, 82, 61), "320 мм клеёная древесина · несущий пояс"),
        (62, (56, 70, 77), "150 мм минеральный поглотитель вокруг ребра"),
        (30, (28, 31, 38), "перфорированная обшивка тёмного свода"),
    ]
    y = my
    for h, c, text in layers:
        draw.rectangle((mx, y, mx + 285, y + h), fill=c, outline=(10, 10, 12))
        draw.text((mx + 320, y + h / 2 - 11), text, font=font(18), fill=ink if h != 30 else muted)
        y += h
    draw.text((mx, y + 28), "ширина ребра 3,2 м · разборное крепление панелей", font=font(18, True), fill=blue)
    draw.text((mx, y + 62), "конструкция = акустический рефлектор = пространственный знак", font=font(18), fill=muted)

    # C-K and delivery gates.
    gx = 1010
    draw.text((gx, 925), "04  C-K ОТБОР → ДОСТИЖЕНИЕ", font=font(24, True), fill=gold)
    ck_lines = [
        ("C0", "общее небо без изображения", ink),
        ("×", "масштаб / экран / световой паттерн — фиксации", muted),
        ("K+", "эллипсоид сохраняет сумму путей", blue),
        ("C1", "далёкий человек слышим без усилителя", ink),
        ("×", "один фокус — иерархия; возврат себе — солипсизм", muted),
        ("C★", "12 равных пар + тихое центральное собрание", gold),
    ]
    y = 980
    for mark, text, color in ck_lines:
        draw.text((gx, y), mark, font=font(18, True), fill=color)
        draw.text((gx + 54, y), text, font=font(18), fill=color)
        y += 36
    draw.line((gx, y + 8, bw - 72, y + 8), fill=line, width=1)
    y += 35
    gates = [
        "0–2  PASS: brief, geometry, ritual, ray proof",
        "3     full wave/FDTD + structure + accessibility",
        "4     1:10 acoustic bay + 1:1 rib/fire mock-up",
        "5–6  construction + ISO 3382 commissioning",
        "7     post-occupancy: pair focus / central quiet",
    ]
    for idx, text in enumerate(gates):
        draw.text((gx, y), text, font=font(17, idx == 0), fill=ink if idx == 0 else muted)
        y += 31

    image.save(OUT / "far_voice_plate.png", dpi=(170, 170))
    print("ok far_voice_plate.png")


def proof() -> dict:
    angular_errors = []
    path_errors = []
    miss_distances = []
    ray_count = 0
    for k in range(PAIR_COUNT):
        alpha = math.pi * k / PAIR_COUNT
        e, _, _ = axis_basis(alpha)
        source = FOCUS_RADIUS_M * e + np.array([0.0, 0.0, FOCUS_Z_M])
        target = -FOCUS_RADIUS_M * e + np.array([0.0, 0.0, FOCUS_Z_M])
        for mu in np.linspace(MU_START, math.pi - MU_START, 85):
            for side in np.linspace(-RIB_WIDTH_M / 2, RIB_WIDTH_M / 2, 9):
                p = rib_point(alpha, float(mu), float(side))
                if math.hypot(float(p[0]), float(p[1])) < CROWN_RADIUS_M:
                    continue
                n = spheroid_normal(alpha, p)
                reflected = reflect(p - source, n)
                desired = unit(target - p)
                angle = math.acos(float(np.clip(np.dot(reflected, desired), -1.0, 1.0)))
                angular_errors.append(angle)
                length = float(np.linalg.norm(p - source) + np.linalg.norm(target - p))
                path_errors.append(abs(length - 2 * ELLIPSE_A_M))
                # Distance from target to the reflected line.
                w = target - p
                miss = float(np.linalg.norm(w - np.dot(w, reflected) * reflected))
                miss_distances.append(miss)
                ray_count += 1

    max_angle = max(angular_errors)
    max_path = max(path_errors)
    max_miss = max(miss_distances)
    assert max_angle < 3e-8
    assert max_path < 1e-11
    assert max_miss < 1e-11
    direct = 2 * FOCUS_RADIUS_M
    reflected = 2 * ELLIPSE_A_M
    return {
        "title": "Собор дальнего голоса",
        "agency_task": 9482,
        "frameworks": {
            "idea_development": "C-K theory",
            "delivery": "RIBA Plan of Work 2020",
            "quality_questions": "AIA Framework for Design Excellence",
        },
        "geometry_m": {
            "hall_diameter": 2 * HALL_RADIUS_M,
            "outer_shell_apex": SHELL_APEX_M,
            "voice_focus_radius": FOCUS_RADIUS_M,
            "voice_focus_height": FOCUS_Z_M,
            "prolate_spheroid_a": ELLIPSE_A_M,
            "prolate_spheroid_b": ELLIPSE_B_M,
            "rib_width": RIB_WIDTH_M,
            "crown_radius": CROWN_RADIUS_M,
            "pair_count": PAIR_COUNT,
            "voice_niche_count": 2 * PAIR_COUNT,
        },
        "geometrical_acoustics_proof": {
            "tested_reflections": ray_count,
            "maximum_reflection_angular_error_rad": max_angle,
            "maximum_target_line_miss_m": max_miss,
            "maximum_equal_path_error_m": max_path,
            "constant_reflected_path_m": reflected,
            "direct_focus_distance_m": direct,
            "reflected_arrival_s": reflected / SOUND_SPEED_M_S,
            "direct_arrival_s": direct / SOUND_SPEED_M_S,
            "relative_delay_s": (reflected - direct) / SOUND_SPEED_M_S,
        },
        "programme": {
            "central_capacity_concept": 1200,
            "ritual": "twenty-four people exchange an unamplified phrase across twelve acoustic pairs, then enter the quiet central assembly",
            "direct_path": "must be screened by the paired niche lips; not verified in this geometric proof",
        },
        "stage_2_pass": [
            "one spatial law rather than a family of visual variants",
            "structure, acoustic geometry, and ritual share the same ribs",
            "ellipsoidal reflection and equal path length numerically verified",
        ],
        "open_gates": [
            "full-wave/FDTD room acoustics across speech spectrum",
            "paired-focus level advantage and STI target",
            "central quiet-field level uniformity",
            "structural analysis of twelve split spheroidal ribs and crown",
            "fire, egress, accessibility, hearing and non-hearing equivalent experience",
            "1:10 acoustic bay and 1:1 material/fabrication mock-up",
        ],
        "image_generation_model": False,
    }


def main() -> int:
    interior()
    board()
    result = proof()
    PROOF_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ok {PROOF_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
