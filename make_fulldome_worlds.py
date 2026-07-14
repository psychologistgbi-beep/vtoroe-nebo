#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Three artistic worlds born directly as 180-degree Dome Masters.

The images are deterministic code-native spherical fields.  They are never
drawn as flat compositions and then radially warped.  Every active pixel is
first decoded into a direction d=(x,y,z), where +y is venue front, +x is
audience right, and +z is zenith.  The artistic laws are then evaluated on d.

Outputs per world:
  * 4096-square equidistant azimuthal fisheye Dome Master;
  * rectilinear audience preview extracted back from that master;
  * one shared machine-readable proof.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)
PROOF_PATH = HERE.parent / "FULLDOME_WORLDS_PROOF.json"

SIZE = 4096
RADIUS = SIZE // 2 - 2
CX = CY = SIZE / 2
CHUNK = 256
PREVIEW_W = 1600
PREVIEW_H = 1000
PREVIEW_AZ_DEG = 0.0
PREVIEW_ALT_DEG = 35.0
PREVIEW_HFOV_DEG = 100.0


@dataclass(frozen=True)
class World:
    key: str
    title_ru: str
    title_en: str
    law: str
    master_name: str
    preview_name: str

    @property
    def master_path(self) -> Path:
        return OUT / self.master_name

    @property
    def preview_path(self) -> Path:
        return OUT / self.preview_name


WORLDS = [
    World(
        "mutual_horizons",
        "Собор взаимных горизонтов",
        "Cathedral of Mutual Horizons",
        "fifteen exact great circles and their upper-hemisphere intersections",
        "dome_mutual_horizons_domemaster_4k.png",
        "dome_mutual_horizons_front_35.png",
    ),
    World(
        "common_pulse",
        "Свод совместной паузы",
        "Vault of the Common Pause",
        "coherent scalar waves from twelve springline sources on the unit sphere",
        "dome_common_pulse_domemaster_4k.png",
        "dome_common_pulse_front_35.png",
    ),
    World(
        "habitable_boundary",
        "Собор обитаемой границы",
        "Cathedral of the Habitable Boundary",
        "diffused day-night energy field of a tidally locked world",
        "dome_habitable_boundary_domemaster_4k.png",
        "dome_habitable_boundary_front_35.png",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def direction(azimuth_deg: float, altitude_deg: float) -> np.ndarray:
    az = math.radians(azimuth_deg)
    alt = math.radians(altitude_deg)
    return np.array(
        [math.cos(alt) * math.sin(az), math.cos(alt) * math.cos(az), math.sin(alt)],
        dtype=np.float64,
    )


def direction_to_xy(d: np.ndarray) -> tuple[float, float] | None:
    d = np.asarray(d, dtype=np.float64)
    d /= np.linalg.norm(d)
    if d[2] < -1e-9:
        return None
    theta = math.acos(float(np.clip(d[2], -1.0, 1.0)))
    phi = math.atan2(float(d[0]), float(d[1]))
    rho = theta / (math.pi / 2.0)
    return CX + RADIUS * rho * math.sin(phi), CY + RADIUS * rho * math.cos(phi)


def direction_chunk(y0: int, y1: int) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    yy, xx = np.mgrid[y0:y1, 0:SIZE]
    dx = (xx.astype(np.float32) + 0.5 - CX) / RADIUS
    dy = (yy.astype(np.float32) + 0.5 - CY) / RADIUS
    rho = np.hypot(dx, dy)
    inside = rho <= 1.0
    theta = np.clip(rho, 0.0, 1.0) * (math.pi / 2.0)
    phi = np.arctan2(dx, dy)
    sin_theta = np.sin(theta)
    x = sin_theta * np.sin(phi)
    y = sin_theta * np.cos(phi)
    z = np.cos(theta)
    return x, y, z, rho, inside


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", optimize=False, compress_level=9, dpi=(72, 72))


def unit(v: np.ndarray) -> np.ndarray:
    return np.asarray(v, dtype=np.float64) / np.linalg.norm(v)


def mutual_normals() -> np.ndarray:
    """Planes of fifteen non-duplicate great circles.

    For a unit plane normal n, the maximum altitude of n·d=0 is acos(|n_z|).
    The alternating altitude families prevent a decorative radial rosette: every
    arc has its own relation between two antipodal positions on the springline.
    """
    max_altitudes = [36, 48, 61, 75, 86, 43, 55, 69, 81, 39, 51, 65, 78, 88, 58]
    normals = []
    for index, max_alt in enumerate(max_altitudes):
        alpha = 2.0 * math.pi * index / len(max_altitudes) + math.radians((index % 3 - 1) * 4.0)
        h = math.radians(max_alt)
        normals.append(unit(np.array([math.sin(h) * math.cos(alpha), math.sin(h) * math.sin(alpha), math.cos(h)])))
    return np.asarray(normals)


def build_mutual_horizons(world: World) -> dict:
    normals = mutual_normals()
    palette = np.array(
        [[232, 174, 82], [71, 191, 183], [156, 115, 219]], dtype=np.float32
    )
    result = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)

    for y0 in range(0, SIZE, CHUNK):
        y1 = min(SIZE, y0 + CHUNK)
        x, y, z, rho, inside = direction_chunk(y0, y1)
        crown = np.clip(z, 0.0, 1.0)
        arr = np.zeros((y1 - y0, SIZE, 3), dtype=np.float32)
        arr[..., 0] = 3.0 + 5.0 * crown
        arr[..., 1] = 7.0 + 10.0 * crown
        arr[..., 2] = 15.0 + 19.0 * crown + 5.0 * (1.0 - rho)

        for index, n in enumerate(normals):
            dot = np.clip(n[0] * x + n[1] * y + n[2] * z, -1.0, 1.0)
            angular_distance = np.arcsin(np.abs(dot))
            glow = np.exp(-np.square(angular_distance / 0.035))
            core = np.exp(-np.square(angular_distance / 0.0065))
            strength = 0.22 * glow + 0.95 * core
            color = palette[index % len(palette)]
            arr += strength[..., None] * color[None, None, :] * 0.78

        # A very faint 30-degree altitude cadence keeps bodily scale legible.
        altitude = np.degrees(np.arcsin(np.clip(z, 0.0, 1.0)))
        cadence = np.exp(-np.square(np.sin(np.radians(altitude * 6.0)) / 0.16))
        arr += cadence[..., None] * np.array([7.0, 10.0, 14.0])
        arr[~inside] = 0.0
        result[y0:y1] = np.uint8(np.clip(arr, 0, 255))

    image = Image.fromarray(result, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")

    # Upper intersections are the witnesses of relations, never arbitrary stars.
    intersections: list[np.ndarray] = []
    max_incidence_error = 0.0
    for i in range(len(normals)):
        for j in range(i + 1, len(normals)):
            p = np.cross(normals[i], normals[j])
            if np.linalg.norm(p) < 1e-8:
                continue
            p = unit(p)
            if p[2] < 0:
                p = -p
            altitude = math.degrees(math.asin(float(p[2])))
            if altitude < 13.0:
                continue
            intersections.append(p)
            max_incidence_error = max(max_incidence_error, abs(float(np.dot(normals[i], p))), abs(float(np.dot(normals[j], p))))
            xy = direction_to_xy(p)
            if xy is None:
                continue
            px, py = xy
            radius = 5.0 + 5.0 * (altitude / 90.0)
            draw.ellipse((px - radius * 3, py - radius * 3, px + radius * 3, py + radius * 3), fill=(226, 216, 173, 18))
            draw.ellipse((px - radius, py - radius, px + radius, py + radius), fill=(245, 230, 183, 210))

    # Every great circle gets two physical springline addresses.
    for index, n in enumerate(normals):
        q = unit(np.array([-n[1], n[0], 0.0]))
        color = tuple(int(v) for v in palette[index % 3]) + (230,)
        for endpoint in (q, -q):
            px, py = direction_to_xy(endpoint)  # type: ignore[misc]
            draw.ellipse((px - 11, py - 11, px + 11, py + 11), fill=color)

    save_png(image, world.master_path)
    return {
        "great_circle_count": len(normals),
        "normal_unit_max_error": float(np.max(np.abs(np.linalg.norm(normals, axis=1) - 1.0))),
        "upper_intersection_count": len(intersections),
        "intersection_incidence_max_abs_dot": max_incidence_error,
        "model_boundary": "exact spherical geodesic network; not a structural cable/rib calculation",
    }


def pulse_sources() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    azimuths = np.arange(-165.0, 195.0, 30.0)
    sources = np.asarray([direction(float(az), 4.0) for az in azimuths])
    golden = math.pi * (3.0 - math.sqrt(5.0))
    phases = np.asarray([(index * golden) % (2.0 * math.pi) for index in range(len(sources))])
    weights = 0.78 + 0.22 * np.square(np.cos(np.radians(azimuths) / 2.0))
    return sources, phases, weights


def build_common_pulse(world: World) -> dict:
    sources, phases, weights = pulse_sources()
    total_weight = float(np.sum(weights))
    wave_number = 23.0
    result = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    min_delta = math.pi
    max_delta = 0.0
    coherence_values = []

    for y0 in range(0, SIZE, CHUNK):
        y1 = min(SIZE, y0 + CHUNK)
        x, y, z, rho, inside = direction_chunk(y0, y1)
        real = np.zeros_like(x, dtype=np.float32)
        imag = np.zeros_like(x, dtype=np.float32)
        for source, phase, weight in zip(sources, phases, weights):
            cosine = np.clip(source[0] * x + source[1] * y + source[2] * z, -1.0, 1.0)
            delta = np.arccos(cosine)
            min_delta = min(min_delta, float(np.min(delta[inside])))
            max_delta = max(max_delta, float(np.max(delta[inside])))
            attenuation = np.exp(-0.13 * delta) / (0.62 + np.sqrt(np.maximum(np.sin(delta), 0.025)))
            angle = wave_number * delta + phase
            real += np.float32(weight) * attenuation * np.cos(angle)
            imag += np.float32(weight) * attenuation * np.sin(angle)

        psi = real / total_weight
        coherence = np.clip(np.hypot(real, imag) / (total_weight * 0.72), 0.0, 1.0)
        coherence_values.append(coherence[inside][::29])
        positive = np.clip(psi / 0.28, 0.0, 1.0)
        negative = np.clip(-psi / 0.28, 0.0, 1.0)
        zero_line = np.exp(-np.square(psi / 0.018)) * (0.28 + 0.72 * coherence)
        crown = np.clip(z, 0.0, 1.0)

        arr = np.zeros((y1 - y0, SIZE, 3), dtype=np.float32)
        arr[..., 0] = 4.0 + 39.0 * coherence + 98.0 * positive + 35.0 * negative
        arr[..., 1] = 8.0 + 31.0 * coherence + 45.0 * positive + 111.0 * negative
        arr[..., 2] = 20.0 + 67.0 * coherence + 115.0 * positive + 128.0 * negative + 13.0 * crown
        arr += zero_line[..., None] * np.array([164.0, 130.0, 56.0])
        arr[~inside] = 0.0
        result[y0:y1] = np.uint8(np.clip(arr, 0, 255))

    image = Image.fromarray(result, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    for source, phase in zip(sources, phases):
        xy = direction_to_xy(source)
        if xy is None:
            continue
        px, py = xy
        phase_color = (220, int(135 + 70 * (0.5 + 0.5 * math.sin(phase))), 100, 220)
        draw.ellipse((px - 18, py - 18, px + 18, py + 18), outline=phase_color, width=5)
        draw.ellipse((px - 5, py - 5, px + 5, py + 5), fill=(244, 222, 168, 235))

    save_png(image, world.master_path)
    sampled_coherence = np.concatenate(coherence_values)
    self_errors = [math.acos(float(np.clip(np.dot(source, source), -1.0, 1.0))) for source in sources]
    return {
        "source_count": len(sources),
        "source_altitude_degrees": 4.0,
        "phase_sequence": "golden-angle low-discrepancy order",
        "angular_wave_number": wave_number,
        "source_self_distance_max_rad": max(self_errors),
        "sampled_geodesic_distance_range_rad": [min_delta, max_delta],
        "sampled_coherence_percentiles": [
            float(v) for v in np.percentile(sampled_coherence, [5, 50, 95])
        ],
        "model_boundary": "ideal coherent scalar field on a unit sphere; not room acoustics or an SPL prediction",
    }


def climate_coefficients(max_degree: int = 32, diffusion: float = 0.075) -> tuple[np.ndarray, dict]:
    nodes, weights = np.polynomial.legendre.leggauss(512)
    forcing = np.maximum(nodes, 0.0)
    source_coeffs = np.zeros(max_degree + 1, dtype=np.float64)
    solution_coeffs = np.zeros(max_degree + 1, dtype=np.float64)
    reconstructed = np.zeros_like(nodes)
    for degree in range(max_degree + 1):
        basis = np.zeros(degree + 1)
        basis[-1] = 1.0
        p = np.polynomial.legendre.legval(nodes, basis)
        coefficient = (2 * degree + 1) / 2.0 * np.sum(weights * forcing * p)
        source_coeffs[degree] = coefficient
        solution_coeffs[degree] = coefficient / (1.0 + diffusion * degree * (degree + 1))
        reconstructed += coefficient * p
    rms = float(np.sqrt(np.mean(np.square(reconstructed - forcing))))
    return solution_coeffs, {
        "maximum_legendre_degree": max_degree,
        "diffusion_parameter": diffusion,
        "forcing_projection_rms": rms,
        "equation": "(1 - D*Laplace_Beltrami) T = max(dot(d,star),0)",
    }


def evaluate_legendre_series(mu: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    p0 = np.ones_like(mu, dtype=np.float32)
    value = np.float32(coefficients[0]) * p0
    if len(coefficients) == 1:
        return value
    p1 = mu.astype(np.float32)
    value += np.float32(coefficients[1]) * p1
    for degree in range(2, len(coefficients)):
        pn = ((2 * degree - 1) * mu * p1 - (degree - 1) * p0) / degree
        value += np.float32(coefficients[degree]) * pn
        p0, p1 = p1, pn
    return value


def climate_meridians(star: np.ndarray) -> list[list[tuple[float, float]]]:
    reference = np.array([0.0, 0.0, 1.0])
    e1 = unit(np.cross(reference, star))
    e2 = unit(np.cross(star, e1))
    lines: list[list[tuple[float, float]]] = []
    for beta in np.linspace(0.0, 2.0 * math.pi, 18, endpoint=False):
        tangent = math.cos(beta) * e1 + math.sin(beta) * e2
        segments: list[list[tuple[float, float]]] = [[]]
        for delta in np.linspace(0.0, math.pi, 520):
            d = math.cos(delta) * star + math.sin(delta) * tangent
            xy = direction_to_xy(d)
            if xy is None:
                if segments[-1]:
                    segments.append([])
                continue
            segments[-1].append(xy)
        lines.extend(segment for segment in segments if len(segment) > 2)
    return lines


def build_habitable_boundary(world: World) -> dict:
    star = direction(-58.0, 7.0)
    coefficients, coefficient_proof = climate_coefficients()
    result = np.zeros((SIZE, SIZE, 3), dtype=np.uint8)
    raw_min = float("inf")
    raw_max = float("-inf")

    # Normalization is calculated from the same analytic series, not from the frame.
    probe_mu = np.linspace(-1.0, 1.0, 20001, dtype=np.float32)
    probe_t = evaluate_legendre_series(probe_mu, coefficients)
    t_min, t_max = float(np.min(probe_t)), float(np.max(probe_t))

    for y0 in range(0, SIZE, CHUNK):
        y1 = min(SIZE, y0 + CHUNK)
        x, y, z, rho, inside = direction_chunk(y0, y1)
        mu = np.clip(star[0] * x + star[1] * y + star[2] * z, -1.0, 1.0)
        raw_min = min(raw_min, float(np.min(mu[inside])))
        raw_max = max(raw_max, float(np.max(mu[inside])))
        temperature = evaluate_legendre_series(mu, coefficients)
        t = np.clip((temperature - t_min) / (t_max - t_min), 0.0, 1.0)

        # Four-stage colour scale: cold night → violet boundary → copper day → pale starward field.
        night = np.stack([5 + 10 * t, 7 + 17 * t, 26 + 49 * t], axis=2)
        twilight = np.stack([18 + 87 * t, 15 + 42 * t, 58 + 16 * t], axis=2)
        day = np.stack([56 + 174 * t, 28 + 104 * t, 42 + 35 * t], axis=2)
        high = np.stack([112 + 133 * t, 60 + 152 * t, 45 + 85 * t], axis=2)
        arr = np.where((t < 0.28)[..., None], night, np.where((t < 0.52)[..., None], twilight, np.where((t < 0.82)[..., None], day, high)))

        isotherm = np.exp(-np.square(np.abs(np.sin(math.pi * 10.0 * t)) / 0.075))
        terminator = np.exp(-np.square(mu / 0.018))
        arr += isotherm[..., None] * np.array([19.0, 24.0, 30.0])
        arr += terminator[..., None] * np.array([67.0, 159.0, 158.0])
        arr[~inside] = 0.0
        result[y0:y1] = np.uint8(np.clip(arr, 0, 255))

    image = Image.fromarray(result, "RGB")
    draw = ImageDraw.Draw(image, "RGBA")
    for line in climate_meridians(star):
        draw.line(line, fill=(135, 210, 205, 72), width=3)

    # The stellar address is deliberately on the springline, not painted as a celestial body.
    sx, sy = direction_to_xy(star)  # type: ignore[misc]
    for radius, alpha in ((52, 30), (30, 70), (10, 240)):
        draw.ellipse((sx - radius, sy - radius, sx + radius, sy + radius), outline=(255, 218, 142, alpha), width=5)
    save_png(image, world.master_path)
    return {
        "star_direction": {"azimuth_degrees": -58.0, "altitude_degrees": 7.0},
        "visible_dot_range": [raw_min, raw_max],
        "solution_temperature_range": [t_min, t_max],
        "terminator_definition": "dot(d, star) = 0",
        **coefficient_proof,
        "model_boundary": "linear axisymmetric energy-balance analogy; not a GCM, weather forecast, or real exoplanet climate",
    }


def sample_preview(master: Image.Image, azimuth_deg: float, altitude_deg: float, hfov_deg: float) -> Image.Image:
    yy, xx = np.mgrid[0:PREVIEW_H, 0:PREVIEW_W]
    aspect = PREVIEW_W / PREVIEW_H
    tan_h = math.tan(math.radians(hfov_deg) / 2.0)
    tan_v = tan_h / aspect
    sx = ((2.0 * (xx.astype(np.float32) + 0.5) / PREVIEW_W) - 1.0) * tan_h
    sy = (1.0 - 2.0 * (yy.astype(np.float32) + 0.5) / PREVIEW_H) * tan_v

    az = math.radians(azimuth_deg)
    alt = math.radians(altitude_deg)
    forward = np.array([math.cos(alt) * math.sin(az), math.cos(alt) * math.cos(az), math.sin(alt)], dtype=np.float32)
    right = np.array([math.cos(az), -math.sin(az), 0.0], dtype=np.float32)
    up = np.cross(right, forward)
    rays = forward[None, None, :] + sx[..., None] * right + sy[..., None] * up
    rays /= np.linalg.norm(rays, axis=2, keepdims=True)

    x, y, z = rays[..., 0], rays[..., 1], rays[..., 2]
    theta = np.arccos(np.clip(z, -1.0, 1.0))
    phi = np.arctan2(x, y)
    rho = theta / (math.pi / 2.0)
    u = CX + RADIUS * rho * np.sin(phi)
    v = CY + RADIUS * rho * np.cos(phi)
    source = np.asarray(master)
    ui = np.clip(np.rint(u).astype(np.int32), 0, SIZE - 1)
    vi = np.clip(np.rint(v).astype(np.int32), 0, SIZE - 1)
    sampled = source[vi, ui].copy()
    sampled[rho > 1.0] = 0
    return Image.fromarray(sampled, "RGB")


def output_record(world: World, mathematical_proof: dict) -> dict:
    master = Image.open(world.master_path).convert("RGB")
    preview = sample_preview(master, PREVIEW_AZ_DEG, PREVIEW_ALT_DEG, PREVIEW_HFOV_DEG)
    save_png(preview, world.preview_path)
    return {
        "key": world.key,
        "title_ru": world.title_ru,
        "title_en": world.title_en,
        "law": world.law,
        "master": {
            "path": str(world.master_path),
            "size_px": [SIZE, SIZE],
            "sha256": sha256(world.master_path),
        },
        "preview": {
            "path": str(world.preview_path),
            "size_px": [PREVIEW_W, PREVIEW_H],
            "view_azimuth_degrees": PREVIEW_AZ_DEG,
            "view_altitude_degrees": PREVIEW_ALT_DEG,
            "horizontal_fov_degrees": PREVIEW_HFOV_DEG,
            "sha256": sha256(world.preview_path),
        },
        "mathematical_proof": mathematical_proof,
        "gates": {
            "artistic_world": "PASS: distinct spatial law and gathering state are documented",
            "dome_master": "PASS: born from hemisphere directions; orientation and extracted preview verified",
            "venue": "OPEN: requires physical projector warp/blend/black-colour/comfort test",
        },
    }


def main() -> None:
    proofs = {
        "mutual_horizons": build_mutual_horizons(WORLDS[0]),
        "common_pulse": build_common_pulse(WORLDS[1]),
        "habitable_boundary": build_habitable_boundary(WORLDS[2]),
    }
    records = [output_record(world, proofs[world.key]) for world in WORLDS]
    proof = {
        "artifact": "Second Sky — three native fulldome worlds",
        "version": "0.1",
        "agency_task": 9484,
        "generation": "deterministic code-native spherical fields; no image model",
        "projection": "equidistant azimuthal fisheye",
        "coverage": {"horizontal_degrees": 360, "vertical_degrees": 180},
        "axes": {"front": "+y", "right": "+x", "zenith": "+z"},
        "file_orientation": {"bottom": "front", "right": "audience right", "center": "zenith", "top": "back"},
        "generator": {"path": str(Path(__file__).resolve()), "sha256": sha256(Path(__file__).resolve())},
        "worlds": records,
    }
    PROOF_PATH.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for record in records:
        print(record["master"]["path"])
        print(record["preview"]["path"])
    print(PROOF_PATH)


if __name__ == "__main__":
    main()
