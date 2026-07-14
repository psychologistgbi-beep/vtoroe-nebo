#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three spatial-state domes: parallax, Hopf volume, and inverse caustic time.

The work is code-native.  It does not ask an image model to imitate architecture.
Each image is the trace of a different spatial law:

* parallax_covenant: three undistorted glyphs are reverse-projected from three
  real observer positions onto one hemispherical surface;
* hopf_covenant: linked Hopf fibres are stereographically projected from S3,
  compacted into a ball, and suspended inside the dome volume;
* three_suns: microfacet normals are solved by inverse reflection so that three
  solar directions address three different caustic programmes on the floor.

Outputs keep the 1360 x 1360 centered equidistant Dome Master format used by the
existing Second Sky series.  A JSON proof records numerical invariants.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from make_domes5 import (
    AA,
    CX,
    CY,
    PROJECTION,
    RADIUS,
    SIZE,
    W,
    add_outer_rim,
    dome_xy,
    line_closed,
    mix,
    palette,
    save,
    scale,
    spherical_base,
)


HERE = Path(__file__).resolve().parent
PROOF_PATH = HERE.parent / "DOME_SPATIAL_STATES_PROOFS.json"


def unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n < 1e-12:
        raise ValueError("zero-length vector")
    return np.asarray(v, dtype=float) / n


def dome_from_vector(p: np.ndarray) -> tuple[float, float]:
    p = unit(p)
    theta = math.acos(float(np.clip(p[2], 0.0, 1.0)))
    phi = math.atan2(float(p[1]), float(p[0]))
    return dome_xy(theta, phi)


def glow_polyline(
    image: Image.Image,
    points: list[tuple[float, float]],
    color: str,
    width: int,
    glow: int = 12,
    alpha: int = 150,
    closed: bool = False,
) -> None:
    if len(points) < 2:
        return
    seq = [*points, points[0]] if closed else points
    halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    c = color.lstrip("#")
    rgb = tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))
    hd.line(seq, fill=(*rgb, alpha), width=max(width * 4, 4), joint="curve")
    halo = halo.filter(ImageFilter.GaussianBlur(glow * AA))
    image.alpha_composite(halo)
    ImageDraw.Draw(image).line(seq, fill=(*rgb, 235), width=width, joint="curve")


def ray_sphere(observer: np.ndarray, direction: np.ndarray) -> np.ndarray:
    """Forward intersection of an interior ray with the unit sphere."""
    d = unit(direction)
    od = float(np.dot(observer, d))
    disc = od * od + 1.0 - float(np.dot(observer, observer))
    t = -od + math.sqrt(max(0.0, disc))
    p = observer + t * d
    return unit(p)


def target_glyph(kind: int, layer: int, samples: int = 420) -> np.ndarray:
    """A perceptual state in the tangent image plane of one observer."""
    t = np.linspace(0.0, 2 * math.pi, samples, endpoint=True)
    q = (layer + 1) / 7.0
    if kind == 0:  # germination: nested seed / vertical breath
        a = 0.055 + 0.23 * q
        b = 0.11 + 0.34 * q
        x = a * np.sin(t) * (0.88 + 0.12 * np.cos(2 * t))
        y = b * np.cos(t)
    elif kind == 1:  # relation: nested lemniscates
        a = 0.10 + 0.32 * q
        x = a * np.sin(t)
        y = 0.57 * a * np.sin(2 * t)
    else:  # assembly: a circle that becomes a three-lobed chorus
        a = 0.085 + 0.27 * q
        r = a * (1.0 + 0.12 * q * np.cos(3 * t))
        x = r * np.cos(t)
        y = r * np.sin(t)
    # The image occupies an architectural field of view, not a small retinal icon.
    return 1.65 * np.column_stack([x, y])


def parallax_covenant() -> dict:
    """Reverse-project three coherent images from three places onto one dome."""
    image = spherical_base("#070b17", "#10253a", light=(-0.18, 0.40, 0.90)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # The three standing places form an open triangle around the centre.
    observers = [
        np.array([-0.42, -0.18, 0.055]),
        np.array([0.42, -0.18, 0.055]),
        np.array([0.00, 0.42, 0.055]),
    ]
    orientations = [math.radians(22), math.radians(158), math.radians(-90)]
    colors = ["#f2b75d", "#74d6cf", "#cf83f3"]
    titles = ["seed", "relation", "assembly"]
    focal = 0.65
    rms: list[float] = []
    surface_paths: list[tuple[list[tuple[float, float]], str, int]] = []

    # Subtle geodesic field makes clear that the three anamorphs share one skin.
    for ring in np.linspace(0.17, 0.92, 7):
        rr = RADIUS * ring
        draw.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=(83, 111, 139, 44), width=AA)
    for k in range(24):
        p = 2 * math.pi * k / 24
        draw.line([dome_xy(0.03, p), dome_xy(math.pi / 2, p)], fill=(75, 102, 130, 35), width=AA)

    for kind, (observer, yaw, color) in enumerate(zip(observers, orientations, colors)):
        right = np.array([math.cos(yaw), math.sin(yaw), 0.0])
        up = np.array([-math.sin(yaw), math.cos(yaw), 0.0])
        forward = np.array([0.0, 0.0, 1.0])
        errors = []
        for layer in range(7):
            glyph = target_glyph(kind, layer)
            path = []
            for uv in glyph:
                d = focal * forward + uv[0] * right + uv[1] * up
                p = ray_sphere(observer, d)
                path.append(dome_from_vector(p))

                # Reproject to the author's standing point: this should recover uv.
                q = p - observer
                denom = float(np.dot(q, forward))
                recovered = np.array([np.dot(q, right), np.dot(q, up)]) / denom * focal
                errors.append(float(np.linalg.norm(recovered - uv)))
            surface_paths.append((path, color, layer))

        rms.append(float(np.sqrt(np.mean(np.square(errors)))))

    # First lay broad translucent traces, then draw the exact emissive seams.
    for path, color, layer in surface_paths:
        glow_polyline(image, path, color, max(2, (5 - layer // 3) * AA), glow=8, alpha=90, closed=True)

    draw = ImageDraw.Draw(image)
    # Three floor places are shown at the springing as small orientation marks.
    for observer, yaw, color in zip(observers, orientations, colors):
        phi = math.atan2(observer[1], observer[0])
        x, y = dome_xy(math.pi / 2 * 0.965, phi)
        rr = 7 * AA
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill=color, outline="#fff4d8", width=AA)
        x2, y2 = dome_xy(math.pi / 2 * 0.91, phi + 0.035 * math.sin(yaw))
        draw.line([(x, y), (x2, y2)], fill="#fff4d8", width=AA)

    # The central absence is not an image source: all three images are distributed on the skin.
    for j in range(14, 0, -1):
        rr = RADIUS * (0.026 + 0.004 * j)
        draw.ellipse([CX - rr, CY - rr, CX + rr, CY + rr], outline=(240, 228, 195, 13 + 4 * j), width=AA)
    add_outer_rim(draw, "#9f875e", 2)
    save(image.convert("RGB"), "parallax_covenant")

    return {
        "title": "Свод несводимых взглядов",
        "state_law": "three reverse-projected images share one hemispherical skin",
        "observer_positions_R": [p.round(6).tolist() for p in observers],
        "observer_states": titles,
        "closed_curves_per_observer": 7,
        "samples_per_curve": 420,
        "projection": PROJECTION,
        "reprojection_rms": rms,
        "maximum_reprojection_rms": max(rms),
        "claim_boundary": "emissive/anamorphic seam geometry; no structural or glare engineering",
    }


def hopf_spinor(n: np.ndarray) -> tuple[complex, complex]:
    """One spinor whose Hopf image is n in S2."""
    n = unit(n)
    if n[2] <= -0.999999:
        return 0j, 1 + 0j
    z1 = math.sqrt((1.0 + float(n[2])) / 2.0)
    z2 = complex(float(n[0]), -float(n[1])) / math.sqrt(2.0 * (1.0 + float(n[2])))
    return complex(z1, 0.0), z2


def hopf_curve(n: np.ndarray, samples: int = 720) -> np.ndarray:
    """Stereographic image in R3 of one Hopf fibre in S3."""
    z1, z2 = hopf_spinor(n)
    t = np.linspace(0.0, 2 * math.pi, samples, endpoint=False)
    phase = np.exp(1j * t)
    a = z1 * phase
    b = z2 * phase
    den = 1.0 - b.imag
    den = np.where(np.abs(den) < 1e-8, np.sign(den) * 1e-8 + (den == 0) * 1e-8, den)
    return np.column_stack([a.real / den, a.imag / den, b.real / den])


def gauss_linking(a: np.ndarray, b: np.ndarray) -> float:
    """Midpoint quadrature of the Gauss linking integral for polygonal curves."""
    an = np.roll(a, -1, axis=0)
    bn = np.roll(b, -1, axis=0)
    da = an - a
    db = bn - b
    am = (a + an) * 0.5
    bm = (b + bn) * 0.5
    total = 0.0
    chunk = 96
    for i in range(0, len(a), chunk):
        d = am[i : i + chunk, None, :] - bm[None, :, :]
        cross = np.cross(da[i : i + chunk, None, :], db[None, :, :])
        denom = np.maximum(np.linalg.norm(d, axis=2) ** 3, 1e-12)
        total += float(np.sum(np.einsum("ijk,ijk->ij", d, cross) / denom))
    return total / (4 * math.pi)


@dataclass
class FibreSegment:
    depth: float
    points: list[tuple[float, float]]
    color: str
    width: int


def hopf_covenant() -> dict:
    """Bring linked 4D fibres into the habitable volume of a dome."""
    image = spherical_base("#050812", "#101b2d", light=(-0.40, 0.22, 0.88)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    # Latitude bands in the base S2 become nested families of linked fibres.
    base_points = []
    counts = [5, 8, 11]
    latitudes = [0.78, 0.08, -0.62]
    for band, (count, z) in enumerate(zip(counts, latitudes)):
        r = math.sqrt(1 - z * z)
        for k in range(count):
            phi = 2 * math.pi * (k + 0.31 * band) / count
            base_points.append(np.array([r * math.cos(phi), r * math.sin(phi), z]))

    curves_r3 = [hopf_curve(n) for n in base_points]
    segments: list[FibreSegment] = []
    colors = ["#f4c66d", "#67dfd4", "#b78aff"]
    rot_x = math.radians(-18)
    rot_z = math.radians(17)
    rx = np.array([[1, 0, 0], [0, math.cos(rot_x), -math.sin(rot_x)], [0, math.sin(rot_x), math.cos(rot_x)]])
    rz = np.array([[math.cos(rot_z), -math.sin(rot_z), 0], [math.sin(rot_z), math.cos(rot_z), 0], [0, 0, 1]])
    rotation = rz @ rx

    for idx, curve in enumerate(curves_r3):
        norm = np.linalg.norm(curve, axis=1, keepdims=True)
        compact = curve / (0.28 + norm)  # radial homeomorphism R3 -> open unit ball
        compact = compact @ rotation.T
        physical = compact * 0.455 + np.array([0.0, 0.0, 0.515])
        color = colors[0 if idx < counts[0] else 1 if idx < sum(counts[:2]) else 2]

        projected = [dome_from_vector(p) for p in physical]
        depths = np.linalg.norm(physical, axis=1)
        # Short segments allow a painter's depth ordering while preserving each closed fibre.
        stride = 8
        for i in range(0, len(projected), stride):
            ids = [(i + j) % len(projected) for j in range(stride + 1)]
            pts = [projected[j] for j in ids]
            depth = float(np.mean(depths[ids]))
            width = int(round(2.0 * AA + 2.3 * AA * (1.22 - min(depth, 1.22))))
            segments.append(FibreSegment(depth, pts, color, max(2 * AA, width)))

    # Far fibres first, near fibres last.  Luminous thickness is therefore spatial evidence.
    # All halos share one optical field so the volume needs only one expensive blur.
    segments.sort(key=lambda s: s.depth, reverse=True)
    halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    for seg in segments:
        c = seg.color.lstrip("#")
        crgb = tuple(int(c[i : i + 2], 16) for i in (0, 2, 4))
        hd.line(seg.points, fill=(*crgb, 50), width=max(5 * AA, seg.width * 3), joint="curve")
    image.alpha_composite(halo.filter(ImageFilter.GaussianBlur(6 * AA)))
    core = ImageDraw.Draw(image)
    for seg in segments:
        core.line(seg.points, fill=seg.color, width=seg.width, joint="curve")

    draw = ImageDraw.Draw(image)
    # A few pearl nodes reveal that strands pass through volume, not only across the skin.
    for idx, curve in enumerate(curves_r3):
        if idx % 3:
            continue
        compact = curve / (0.28 + np.linalg.norm(curve, axis=1, keepdims=True))
        compact = compact @ rotation.T
        physical = compact * 0.455 + np.array([0.0, 0.0, 0.515])
        for j in (70, 310, 550):
            x, y = dome_from_vector(physical[j])
            rr = 2.8 * AA
            draw.ellipse([x - rr, y - rr, x + rr, y + rr], fill="#fff6db")

    # The floor horizon and crown mark the actual architectural containing hemisphere.
    add_outer_rim(draw, "#786b63", 2)
    crown = RADIUS * 0.035
    draw.ellipse([CX - crown, CY - crown, CX + crown, CY + crown], outline="#f6e7bd", width=AA)
    save(image.convert("RGB"), "hopf_covenant")

    # Verify representative pairwise links away from the stereographic pole.
    link_pairs = [(0, 1), (1, 6), (6, 15), (3, 20)]
    links = []
    for ia, ib in link_pairs:
        value = gauss_linking(curves_r3[ia][::2], curves_r3[ib][::2])
        links.append({"pair": [ia, ib], "gauss_linking": value, "rounded": int(round(value))})
    assert all(abs(abs(item["gauss_linking"]) - 1.0) < 0.04 for item in links)

    return {
        "title": "Собор неразрывных связей",
        "state_law": "distinct Hopf fibres are disjoint yet pairwise linked",
        "base_S2_latitude_counts": counts,
        "fibre_count": len(base_points),
        "samples_per_fibre": 720,
        "embedding": "S3 Hopf fibre -> stereographic R3 -> radial compactification r/(0.28+|r|) -> affine dome volume",
        "representative_gauss_linking_integrals": links,
        "projection": PROJECTION,
        "claim_boundary": "topological spatial study; tube structure, fire safety and maintenance are not engineered",
    }


def reflect(incoming: np.ndarray, normal: np.ndarray) -> np.ndarray:
    incoming = unit(incoming)
    normal = unit(normal)
    return unit(incoming - 2.0 * float(np.dot(incoming, normal)) * normal)


def caustic_target(kind: int, t: float) -> np.ndarray:
    """Three social geometries drawn on the floor by three solar states."""
    if kind == 0:  # dawn: a path from the threshold toward the shared centre
        y = -0.78 + 1.30 * t
        x = 0.085 * math.sin(5 * math.pi * t) * (0.35 + 0.65 * t)
    elif kind == 1:  # noon: an equal circle around the assembly
        a = 2 * math.pi * t
        x, y = 0.46 * math.cos(a), 0.46 * math.sin(a)
    else:  # dusk: two sides fold into one centre
        a = 2 * math.pi * t
        x = 0.56 * math.sin(a)
        y = 0.30 * math.sin(2 * a) * (0.75 + 0.25 * math.cos(a))
    return np.array([x, y, 0.0])


def panel_polygon(theta: float, phi: float, dt: float, dp: float) -> list[tuple[float, float]]:
    return [
        dome_xy(theta - dt, phi - dp),
        dome_xy(theta - dt, phi + dp),
        dome_xy(theta + dt, phi + dp),
        dome_xy(theta + dt, phi - dp),
    ]


def three_suns() -> dict:
    """Solve one interleaved microfacet field for dawn, noon, and dusk caustics."""
    image = spherical_base("#120914", "#2c1825", light=(-0.12, 0.54, 0.83)).convert("RGBA")
    draw = ImageDraw.Draw(image)

    sun_from = [
        unit(np.array([-0.76, -0.34, 0.55])),
        unit(np.array([0.00, 0.03, 1.00])),
        unit(np.array([0.72, -0.38, 0.58])),
    ]
    colors = ["#f2a451", "#f6e5a2", "#c57be2"]
    names = ["threshold_path", "assembly_ring", "converging_vesica"]
    panel_records = []
    land_errors = [[], [], []]
    counts = [0, 0, 0]

    rings = 16
    sectors = 72
    for ir in range(rings):
        theta = 0.16 + (math.pi / 2 - 0.23) * (ir + 0.5) / rings
        dt = (math.pi / 2 - 0.39) / rings * 0.39
        offset = (ir % 2) * math.pi / sectors
        for k in range(sectors):
            phi = 2 * math.pi * k / sectors + offset
            group = (k + 2 * ir) % 3
            p = np.array([
                math.sin(theta) * math.cos(phi),
                math.sin(theta) * math.sin(phi),
                math.cos(theta),
            ])
            local_index = counts[group]
            counts[group] += 1
            # Golden-ratio sequencing distributes each target along the whole dome.
            tau = (local_index * 0.6180339887498949) % 1.0
            target = caustic_target(group, tau)
            outgoing = unit(target - p)
            normal = unit(sun_from[group] + outgoing)
            ray = reflect(-sun_from[group], normal)
            travel = -p[2] / ray[2]
            landed = p + travel * ray
            error = float(np.linalg.norm(landed[:2] - target[:2]))
            land_errors[group].append(error)
            panel_records.append((theta, phi, dt, math.pi / sectors * 0.39, group, normal, tau, error))

    # Render the normals as physical microfacets, not as a target image painted on the shell.
    normal_palette = ["#8a421f", "#c89b54", "#503469"]
    for theta, phi, dt, dp, group, normal, tau, _ in panel_records:
        facing = float(np.clip(normal[2] * 0.54 + normal[0] * -0.22 + normal[1] * 0.18, -1, 1))
        c = mix(normal_palette[group], colors[group], 0.31 + 0.47 * (facing + 1) / 2)
        pts = panel_polygon(theta, phi, dt, dp)
        # Each optical address is a shallow four-sided crystal.  Its apex shift
        # follows the solved normal, so the visible relief is not decorative noise.
        x, y = dome_xy(theta, phi)
        tangent = np.array([normal[0], -normal[1]])
        tangent /= max(1e-9, float(np.linalg.norm(tangent)))
        apex = (x + tangent[0] * 2.4 * AA, y + tangent[1] * 2.4 * AA)
        for side in range(4):
            tri = [pts[side], pts[(side + 1) % 4], apex]
            side_light = 0.72 + 0.11 * side + 0.12 * max(0.0, float(normal[(side + 1) % 2]))
            draw.polygon(tri, fill=scale(c, side_light))
        draw.line([*pts, pts[0]], fill="#281622", width=AA)

        # A sparse normal cut makes the inverse optical field legible.
        if int(round(tau * 1000)) % 23 == 0:
            tangent = np.array([normal[0], normal[1]])
            tangent /= max(1e-9, float(np.linalg.norm(tangent)))
            length = (4.0 + 5.0 * abs(normal[2])) * AA
            draw.line([(x, y), (x + tangent[0] * length, y - tangent[1] * length)], fill="#fff0c3", width=AA)

    # Three caustic traces are drawn as light, floating over the facet field.
    # They describe what the same material becomes over time, not a coating.
    for group, color in enumerate(colors):
        path = []
        for t in np.linspace(0.0, 1.0, 500):
            target = caustic_target(group, float(t))
            # The floor diagram is placed in the crown as a reciprocal map of the room.
            theta = 0.075 + 0.25 * math.hypot(float(target[0]), float(target[1]))
            phi = math.atan2(float(target[1]), float(target[0])) + math.pi / 2
            path.append(dome_xy(theta, phi))
        glow_polyline(image, path, color, 3 * AA, glow=9, alpha=105, closed=(group != 0))

    draw = ImageDraw.Draw(image)
    crown = RADIUS * 0.048
    draw.ellipse([CX - crown, CY - crown, CX + crown, CY + crown], fill="#fff2c1", outline="#fff9e4", width=AA)
    add_outer_rim(draw, "#9f6e52", 2)
    save(image.convert("RGB"), "three_suns")

    max_error = [max(v) for v in land_errors]
    assert max(max_error) < 1e-10
    return {
        "title": "Свод трёх времён",
        "state_law": "one interleaved microfacet skin addresses three floor programmes under three sun directions",
        "sun_directions_from_surface": [v.round(8).tolist() for v in sun_from],
        "programmes": names,
        "panels_per_programme": counts,
        "total_microfacets": sum(counts),
        "maximum_floor_landing_error_R": max_error,
        "normal_solution": "n = normalize(direction_to_sun + direction_to_target)",
        "projection": PROJECTION,
        "claim_boundary": "ideal geometric reflection; finite sun size, weather, BRDF, glare and fabrication tolerances are not yet simulated",
    }


GENERATORS = {
    "parallax_covenant": parallax_covenant,
    "hopf_covenant": hopf_covenant,
    "three_suns": three_suns,
}


def main(argv: list[str]) -> int:
    names = argv or list(GENERATORS)
    unknown = [name for name in names if name not in GENERATORS]
    if unknown:
        raise SystemExit(f"unknown variants: {', '.join(unknown)}")
    proof = {
        "format": [SIZE, SIZE],
        "projection": PROJECTION,
        "code_native": True,
        "image_generation_model": False,
        "design_axis": ["observer", "linked volume", "solar time"],
        "variants": {},
    }
    for name in names:
        proof["variants"][name] = GENERATORS[name]()
    if set(names) == set(GENERATORS):
        PROOF_PATH.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"ok {PROOF_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
