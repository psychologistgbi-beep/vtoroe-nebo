#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Surface-first dome graphics: equal-area mosaic, conformal coffers, light muqarnas.

This generator deliberately does not draw motifs in a flat disk and then add spherical
shading. Every boundary starts in dome coordinates (theta, phi) or in a three-dimensional
faceted shell, and only then passes through a centered equidistant Dome Master projection.

Outputs are code-native JPEG graphics, 1360 x 1360, matching the existing series format.
No image-generation model is used.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)

SIZE = 1360
AA = 2
W = SIZE * AA
CX = CY = W / 2
RADIUS = W * 0.455
VOID = (8, 7, 14)
PROJECTION = "centered equidistant azimuthal Dome Master"


def rgb(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i : i + 2], 16) for i in (0, 2, 4)], dtype=float)


def mix(a, b, t: float) -> tuple[int, int, int]:
    t = float(np.clip(t, 0.0, 1.0))
    ca = rgb(a) if isinstance(a, str) else np.asarray(a, dtype=float)
    cb = rgb(b) if isinstance(b, str) else np.asarray(b, dtype=float)
    c = ca * (1 - t) + cb * t
    return tuple(int(round(v)) for v in np.clip(c, 0, 255))


def scale(c, k: float) -> tuple[int, int, int]:
    return tuple(int(round(v)) for v in np.clip(np.asarray(c, dtype=float) * k, 0, 255))


def palette(stops: list[str], t: float) -> tuple[int, int, int]:
    t = float(np.clip(t, 0.0, 0.999999)) * (len(stops) - 1)
    i = int(t)
    return mix(stops[i], stops[i + 1], t - i)


def dome_xy(theta: float, phi: float) -> tuple[float, float]:
    """Centered equidistant projection: rho = theta / (pi/2)."""
    rho = theta / (math.pi / 2)
    return CX + RADIUS * rho * math.cos(phi), CY - RADIUS * rho * math.sin(phi)


def surface_point(theta: float, phi: float, radius: float = 1.0) -> np.ndarray:
    return radius * np.array(
        [math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi), math.cos(theta)],
        dtype=float,
    )


def dome_polygon(theta0: float, theta1: float, phi0: float, phi1: float, samples: int = 7):
    """Boundary of a theta/phi cell, with curved parallels sampled explicitly."""
    if theta0 < 1e-10:
        outer = [dome_xy(theta1, p) for p in np.linspace(phi0, phi1, max(samples, 3))]
        return [dome_xy(0.0, 0.0), *outer]
    outer = [dome_xy(theta1, p) for p in np.linspace(phi0, phi1, samples)]
    inner = [dome_xy(theta0, p) for p in np.linspace(phi1, phi0, samples)]
    return outer + inner


def line_closed(draw: ImageDraw.ImageDraw, pts, fill, width=1):
    draw.line([*pts, pts[0]], fill=fill, width=width, joint="curve")


def spherical_base(base: str, edge: str, light=(-0.38, 0.46, 0.80)) -> Image.Image:
    """A valid light field evaluated from spherical normals, not a flat radial vignette."""
    yy, xx = np.mgrid[0:W, 0:W]
    dx = (xx - CX) / RADIUS
    dy = -(yy - CY) / RADIUS
    rho = np.hypot(dx, dy)
    inside = rho <= 1.0
    theta = np.clip(rho, 0, 1) * (math.pi / 2)
    phi = np.arctan2(dy, dx)
    nx = np.sin(theta) * np.cos(phi)
    ny = np.sin(theta) * np.sin(phi)
    nz = np.cos(theta)
    lv = np.asarray(light, dtype=float)
    lv /= np.linalg.norm(lv)
    diffuse = np.clip(nx * lv[0] + ny * lv[1] + nz * lv[2], 0, 1)
    grazing = np.power(np.clip(1 - nz, 0, 1), 1.6)
    b = rgb(base)
    e = rgb(edge)
    field = b[None, None, :] * (0.58 + 0.42 * diffuse[..., None])
    field = field * (1 - 0.18 * grazing[..., None]) + e[None, None, :] * (0.11 * grazing[..., None])
    arr = np.zeros((W, W, 3), dtype=np.uint8)
    arr[:] = VOID
    arr[inside] = np.clip(field[inside], 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def add_outer_rim(draw: ImageDraw.ImageDraw, color="#b99a58", width=3):
    # Планетам не нужен золотой карниз: атмосферный лимб рисует край в planetize().
    return


def planetize(image: Image.Image, warm="#f4ead2", dark=0.5) -> Image.Image:
    """Обернуть готовый диск-мастер в выпуклый ШАР: глубокий терминатор, блик,
    атмосферный лимб, прозрачный космос за диском. Свет тот же, что у planet_frame."""
    arr = np.asarray(image.convert("RGB"), dtype=float)
    yy, xx = np.mgrid[0:W, 0:W]
    dx = (xx - CX) / RADIUS
    dy = -(yy - CY) / RADIUS
    r = np.hypot(dx, dy)
    inside = r <= 1.0
    z = np.sqrt(np.clip(1 - np.clip(r, 0, 1) ** 2, 0, 1))
    lx, ly, lz = -0.42, 0.52, 0.74
    ln = (lx * lx + ly * ly + lz * lz) ** 0.5
    lx, ly, lz = lx / ln, ly / ln, lz / ln
    ndotl = np.clip(dx * lx + dy * ly + z * lz, 0, 1)
    shade = 0.38 + 0.62 * ndotl
    dA = np.clip((1 - shade) ** 1.15 * (0.6 + dark * 0.55), 0, 0.92)  # терминатор
    out = arr * (1 - dA[..., None])
    # блик (спекуляр) у подсолнечной точки
    wc = rgb(warm)
    spx, spy = lx * 0.86, ly * 0.86
    sig = 0.22
    sp = np.where(inside, np.exp(-(((dx - spx) ** 2 + (dy - spy) ** 2) / (2 * sig * sig))) * 0.34, 0.0)
    out = out * (1 - sp[..., None]) + wc[None, None, :] * sp[..., None]
    # атмосферный лимб (за пределы диска, ярче на свету)
    lc = rgb("#bcd0f0")
    atmo = np.exp(-((r - 1.0) / 0.05) ** 2) * (0.25 + 0.75 * ndotl)
    alimb = np.clip(atmo * 0.6, 0, 0.6)
    rgbf = out * (1 - alimb[..., None]) + lc[None, None, :] * alimb[..., None]
    rgbf = np.where(inside[..., None], rgbf, lc[None, None, :])
    alpha = np.where(inside, 1.0, alimb)
    rgba = np.dstack([np.clip(rgbf, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(rgba, "RGBA")


def save(image: Image.Image, name: str):
    image = planetize(image).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    path = OUT / f"dome_{name}.png"
    image.save(path, dpi=(170, 170))
    print(f"ok {path.name}")


def equal_area() -> dict:
    """127 exactly equal-area cells: one zenith cap plus six latitude rings."""
    counts = [1, 6, 12, 18, 24, 30, 36]
    total = sum(counts)
    cumulative = np.cumsum([0, *counts]) / total
    boundaries = np.arccos(1 - cumulative)  # area from zenith is 2*pi*(1-cos theta)
    target = 2 * math.pi / total
    areas = []

    image = spherical_base("#0b1c2b", "#163f4c", light=(-0.42, 0.38, 0.82))
    draw = ImageDraw.Draw(image)
    mineral = ["#102f45", "#1f6071", "#378d91", "#b6c9b3", "#c9a15b", "#874b42", "#283b68"]
    light = np.array([-0.42, 0.38, 0.82], dtype=float)
    light /= np.linalg.norm(light)

    for ring, n in enumerate(counts):
        t0, t1 = float(boundaries[ring]), float(boundaries[ring + 1])
        offset = (ring % 2) * math.pi / n
        for k in range(n):
            p0 = offset + 2 * math.pi * k / n
            p1 = offset + 2 * math.pi * (k + 1) / n
            pm = (p0 + p1) / 2
            tm = (t0 + t1) / 2
            area = (2 * math.pi / n) * (math.cos(t0) - math.cos(t1))
            areas.append(area)
            wave = 0.5 + 0.5 * math.sin(2.0 * pm + 0.73 * ring)
            drift = (0.56 * ring / (len(counts) - 1) + 0.44 * wave) % 1.0
            c = palette(mineral, drift)
            normal = surface_point(tm, pm)
            shade = 0.67 + 0.33 * max(0.0, float(np.dot(normal, light)))
            c = scale(c, shade)
            pts = dome_polygon(t0, t1, p0, p1, samples=9)
            draw.polygon(pts, fill=c)
            line_closed(draw, pts, fill="#d0b36e", width=2 * AA)

            if ring > 0:
                # A small material glint follows the cell's own spherical normal.
                q0 = dome_xy(t0 * 0.42 + t1 * 0.58, p0 * 0.42 + p1 * 0.58)
                q1 = dome_xy(t0 * 0.34 + t1 * 0.66, p0 * 0.54 + p1 * 0.46)
                draw.line([q0, q1], fill=scale(c, 1.28), width=AA)

    # The equal-area zenith cap is left as the shared source, but keeps the same area as every tile.
    cap_r = RADIUS * (boundaries[1] / (math.pi / 2))
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for j in range(18, 0, -1):
        rr = cap_r * (1 + j / 20)
        alpha = int(3 + 3 * (18 - j))
        gd.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], fill=(235, 218, 157, alpha))
    image = Image.alpha_composite(image.convert("RGBA"), glow.filter(ImageFilter.GaussianBlur(10 * AA))).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.ellipse([CX - cap_r * 0.72, CY - cap_r * 0.72, CX + cap_r * 0.72, CY + cap_r * 0.72], fill="#f3e5bd")
    draw.ellipse([CX - cap_r * 0.31, CY - cap_r * 0.31, CX + cap_r * 0.31, CY + cap_r * 0.31], fill="#fff9e9")
    add_outer_rim(draw, "#b99a58", 2)
    save(image, "equal_area")

    rel = np.abs(np.asarray(areas) - target) / target
    assert float(rel.max()) < 1e-12
    return {
        "title": "Собор равных ячеек",
        "projection": PROJECTION,
        "cell_count": total,
        "ring_counts": counts,
        "target_cell_area_R2": target,
        "max_relative_area_error": float(rel.max()),
        "zenith_cap_is_one_equal_area_cell": True,
    }


def conformal() -> dict:
    """Five by twenty-eight coffers in spherical Mercator coordinates (u, phi)."""
    sectors = 28
    rings = 5
    dv = 2 * math.pi / sectors
    u = np.linspace(-rings * dv, 0.0, rings + 1)
    theta = 2 * np.arctan(np.exp(u))  # inverse spherical Mercator
    ratios = []

    image = spherical_base("#181923", "#28202b", light=(-0.30, 0.52, 0.80))
    draw = ImageDraw.Draw(image)
    light = np.array([-0.30, 0.52, 0.80], dtype=float)
    light /= np.linalg.norm(light)

    # Smooth upper zone: the deliberate pause between coffer field and oculus.
    inner_r = RADIUS * theta[0] / (math.pi / 2)
    for j in range(18, 0, -1):
        rr = inner_r * j / 18
        t = j / 18
        col = mix("#090b14", "#242637", 0.22 + 0.55 * t)
        draw.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], fill=col)

    for ring in range(rings):
        t0, t1 = float(theta[ring]), float(theta[ring + 1])
        h = t1 - t0
        width = math.sin((t0 + t1) / 2) * dv
        ratios.append(h / width)
        for k in range(sectors):
            v0, v1 = k * dv, (k + 1) * dv
            vm = (v0 + v1) / 2
            tm = (t0 + t1) / 2
            normal = surface_point(tm, vm)
            shade = 0.54 + 0.46 * max(0.0, float(np.dot(normal, light)))

            outer = [dome_xy(t0, v0), dome_xy(t0, v1), dome_xy(t1, v1), dome_xy(t1, v0)]
            draw.polygon(outer, fill=scale((60, 55, 62), shade))
            line_closed(draw, outer, fill="#a8894d", width=2 * AA)

            inset = dv * 0.18
            iu0, iu1 = u[ring] + inset, u[ring + 1] - inset
            it0, it1 = 2 * math.atan(math.exp(iu0)), 2 * math.atan(math.exp(iu1))
            iv0, iv1 = v0 + inset, v1 - inset
            inner = [dome_xy(it0, iv0), dome_xy(it0, iv1), dome_xy(it1, iv1), dome_xy(it1, iv0)]

            # Four bevel rays expose that the coffer is a recess, not a printed square.
            bevel = mix("#4b3d34", "#c2a260", shade)
            for a, b in zip(outer, inner):
                draw.line([a, b], fill=bevel, width=AA)
            field = mix("#0d1630", "#b5c7d0", 0.18 + 0.62 * shade)
            field = mix(field, "#d6b66b", 0.08 + 0.08 * ring)
            draw.polygon(inner, fill=field)
            line_closed(draw, inner, fill=scale(field, 1.16), width=AA)

    # Oculus and two measured transition rings in the coffer-free upper zone.
    oculus_theta = math.radians(7.5)
    oculus_r = RADIUS * oculus_theta / (math.pi / 2)
    for factor, col, width in ((1.0, "#fff5d3", 2), (2.25, "#b69b61", 1), (3.75, "#5f5361", 1)):
        rr = oculus_r * factor
        draw.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=col, width=width * AA)
    draw.ellipse([CX - oculus_r, CY - oculus_r, CX + oculus_r, CY + oculus_r], fill="#fff7dc")
    draw.ellipse([CX - oculus_r * 0.54, CY - oculus_r * 0.54, CX + oculus_r * 0.54, CY + oculus_r * 0.54], fill="#ffffff")
    add_outer_rim(draw, "#a8894d", 2)
    save(image, "conformal")

    return {
        "title": "Конформное небо",
        "projection": PROJECTION,
        "construction_coordinates": "u = ln(tan(theta/2)), v = phi; equal steps du=dv",
        "sectors": sectors,
        "rings": rings,
        "coffers": sectors * rings,
        "du_equals_dv": dv,
        "finite_cell_meridional_to_circumferential_ratios": ratios,
        "max_abs_aspect_deviation_from_square": max(abs(r - 1.0) for r in ratios),
        "coffer_free_upper_zone": True,
    }


def light_muqarnas() -> dict:
    """A radial tier plan lifted into four-faced spatial niches.

    Each annular plan cell acquires a recessed 3D point. The four edges of the plan cell and
    that point generate four planar facets. Tier counts double toward the springing line,
    producing the characteristic muqarnas transition instead of a triangulated texture.
    """
    theta = np.radians([7, 18, 31, 45, 60, 75, 90])
    tier_counts = [4, 8, 8, 16, 16, 32, 32]
    distances = [0.78, 0.91, 0.81, 0.96, 0.83, 0.98, 1.00]
    recess_depths = [0.105, 0.085, 0.115, 0.090, 0.120, 0.085]

    def ring_point(j: int, phi: float) -> np.ndarray:
        # A small plan-frequency corrugation makes every tier a built polygonal ring.
        corrugation = 0.016 * math.cos(tier_counts[j] * phi + (j % 2) * math.pi / 2)
        return surface_point(float(theta[j]), phi, distances[j] * (1 + corrugation))

    def projected(p: np.ndarray):
        q = p / np.linalg.norm(p)
        th = math.acos(float(np.clip(q[2], -1, 1)))
        ph = math.atan2(float(q[1]), float(q[0]))
        return dome_xy(th, ph)

    faces = []
    niche_centers = []
    band_cell_counts = []
    for j in range(len(theta) - 1):
        cells = max(tier_counts[j], tier_counts[j + 1])
        band_cell_counts.append(cells)
        step = 2 * math.pi / cells
        offset = (j % 2) * step / 2
        for k in range(cells):
            p0 = offset + k * step
            p1 = offset + (k + 1) * step
            pm = (p0 + p1) / 2
            a = ring_point(j, p0)
            b = ring_point(j + 1, p0)
            c = ring_point(j + 1, p1)
            d = ring_point(j, p1)
            tm = float((theta[j] + theta[j + 1]) / 2)
            radius = min(distances[j], distances[j + 1]) - recess_depths[j]
            center = surface_point(tm, pm, radius)
            niche_centers.append((j, k, center))
            faces.extend(
                [
                    (j, k, 0, [a, b, center]),
                    (j, k, 1, [b, c, center]),
                    (j, k, 2, [c, d, center]),
                    (j, k, 3, [d, a, center]),
                ]
            )

    image = spherical_base("#160f19", "#35202a", light=(-0.22, 0.38, 0.90))
    draw = ImageDraw.Draw(image)
    point_light = np.array([-0.28, 0.34, 0.16], dtype=float)
    shadow = np.array([12, 18, 32], dtype=float)
    bronze = np.array([111, 62, 40], dtype=float)
    gold = np.array([211, 163, 76], dtype=float)
    ivory = np.array([240, 224, 184], dtype=float)

    # Each triangle is shaded from its true 3D normal and a point light inside the shell.
    for band, k, side, verts in faces:
        p0, p1, p2 = verts
        n = np.cross(p1 - p0, p2 - p0)
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        n /= nn
        centroid = (p0 + p1 + p2) / 3
        if np.dot(n, -centroid) < 0:
            n = -n
        lv = point_light - centroid
        lv /= np.linalg.norm(lv)
        diffuse = max(0.0, float(np.dot(n, lv)))
        viewer = -centroid / np.linalg.norm(centroid)
        facing = max(0.0, float(np.dot(n, viewer)))
        t = float(np.clip(0.10 + 0.76 * diffuse + 0.14 * facing, 0, 1))
        if t < 0.42:
            col = shadow * (1 - t / 0.42) + bronze * (t / 0.42)
        elif t < 0.82:
            q = (t - 0.42) / 0.40
            col = bronze * (1 - q) + gold * q
        else:
            q = (t - 0.82) / 0.18
            col = gold * (1 - q) + ivory * q
        # The four sides of a niche remain distinguishable even in low diffuse light.
        col *= 0.88 + 0.08 * side + 0.05 * math.sin((k + 1) * 2.399 + band)
        pts = [projected(v) for v in verts]
        draw.polygon(pts, fill=tuple(int(v) for v in np.clip(col, 0, 255)))
        line_closed(draw, pts, fill="#30242a", width=AA)

    # Tier boundaries and acoustic slots are both derived from the radial plan.
    for j in range(len(theta)):
        samples = max(64, tier_counts[j] * 2)
        pts = [projected(ring_point(j, 2 * math.pi * k / samples)) for k in range(samples)]
        line_closed(draw, pts, fill="#b58b4f", width=AA)

    for band, k, center in niche_centers:
        if band not in (1, 3, 5) or k % 2:
            continue
        x, y = projected(center)
        s = max(2.1 * AA, RADIUS * (0.0048 - 0.00035 * band))
        diamond = [(x, y - s), (x + s * 0.66, y), (x, y + s), (x - s * 0.66, y)]
        draw.polygon(diamond, fill="#070910")

    oculus_r = RADIUS * 0.045
    draw.ellipse([CX - oculus_r * 1.8, CY - oculus_r * 1.8, CX + oculus_r * 1.8, CY + oculus_r * 1.8], fill="#5b3f2e")
    draw.ellipse([CX - oculus_r, CY - oculus_r, CX + oculus_r, CY + oculus_r], fill="#fff1c4")
    add_outer_rim(draw, "#9c7748", 2)
    save(image, "light_muqarnas")

    return {
        "title": "Световая мукарна",
        "projection": PROJECTION,
        "plan_tier_theta_degrees": [round(math.degrees(v), 3) for v in theta],
        "plan_cell_counts": tier_counts,
        "band_cell_counts": band_cell_counts,
        "shell_radial_distances": distances,
        "triangular_facets": len(faces),
        "spatial_niches": len(niche_centers),
        "lighting": "per-facet true 3D normal with an interior point light",
        "acoustic_slots": "plan-derived apertures; no acoustic performance claim",
    }


GENERATORS = {
    "equal_area": equal_area,
    "conformal": conformal,
    "light_muqarnas": light_muqarnas,
}


def main(argv: list[str]) -> int:
    names = argv or list(GENERATORS)
    unknown = [name for name in names if name not in GENERATORS]
    if unknown:
        raise SystemExit(f"unknown variants: {', '.join(unknown)}")
    proof = {
        "format": [SIZE, SIZE],
        "projection": PROJECTION,
        "surface_first": True,
        "image_generation_model": False,
        "variants": {},
    }
    for name in names:
        proof["variants"][name] = GENERATORS[name]()
    proof_path = HERE.parent / "DOME_GEOMETRY_PROOFS.json"
    if set(names) == set(GENERATORS):
        proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"ok {proof_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
