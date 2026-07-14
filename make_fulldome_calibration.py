#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a deterministic 180-degree equidistant Dome Master calibration.

This is code-native fulldome graphics, not a generated image.  The master is a
direction field seen from the audience eye:

    +y = front, +x = audience right, +z = zenith
    theta = acos(z), phi = atan2(x, y)
    radius = theta / (pi / 2)

The bottom of the square is therefore the front springline, the centre is the
zenith, and the top is the rear springline.  The companion rectilinear view is
sampled back out of the master and acts as an orientation check.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)

MASTER_PATH = OUT / "fulldome_calibration_4k.png"
PREVIEW_PATH = OUT / "fulldome_calibration_front_35deg.png"
PROOF_PATH = HERE.parent / "FULLDOME_CALIBRATION_PROOF.json"

SIZE = 4096
RADIUS = SIZE // 2 - 2
CX = CY = SIZE / 2
PREVIEW_W = 1600
PREVIEW_H = 1000
HFOV_DEG = 100.0
VIEW_ALT_DEG = 35.0

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def dome_xy(azimuth_deg: float, altitude_deg: float) -> tuple[float, float]:
    """Map one audience direction to the equidistant Dome Master."""
    phi = math.radians(azimuth_deg)
    radius = (90.0 - altitude_deg) / 90.0 * RADIUS
    return CX + radius * math.sin(phi), CY + radius * math.cos(phi)


def angular_background() -> Image.Image:
    """Encode altitude, azimuth and the IMERSA-style action region as fields."""
    yy, xx = np.mgrid[0:SIZE, 0:SIZE]
    dx = (xx + 0.5 - CX) / RADIUS
    dy = (yy + 0.5 - CY) / RADIUS
    rho = np.hypot(dx, dy)
    inside = rho <= 1.0

    altitude = 90.0 * (1.0 - np.clip(rho, 0.0, 1.0))
    azimuth = np.degrees(np.arctan2(dx, dy))
    safe = inside & (np.abs(azimuth) <= 90.0) & (altitude >= 10.0) & (altitude <= 60.0)

    crown = np.clip(altitude / 90.0, 0.0, 1.0)
    horizon = 1.0 - crown
    frontness = (np.cos(np.radians(azimuth)) + 1.0) / 2.0
    rings = 0.5 + 0.5 * np.cos(np.radians(altitude * 6.0))

    arr = np.zeros((SIZE, SIZE, 3), dtype=np.float32)
    arr[..., 0] = 4.0 + 11.0 * crown + 3.0 * frontness
    arr[..., 1] = 8.0 + 22.0 * crown + 5.0 * frontness
    arr[..., 2] = 14.0 + 32.0 * crown + 8.0 * horizon
    arr += rings[..., None] * 1.5

    # The safe-action sector is intentionally a quiet local lift, not a flat badge.
    arr[safe, 0] += 10.0
    arr[safe, 1] += 12.0
    arr[safe, 2] += 6.0
    arr[~inside] = 0.0
    return Image.fromarray(np.uint8(np.clip(arr, 0, 255)), "RGB")


def draw_arc_polyline(
    draw: ImageDraw.ImageDraw,
    altitude_deg: float,
    start_az: float,
    end_az: float,
    fill: tuple[int, int, int],
    width: int,
    step: float = 1.0,
) -> None:
    values = np.arange(start_az, end_az + step * 0.5, step)
    draw.line([dome_xy(float(az), altitude_deg) for az in values], fill=fill, width=width)


def build_master() -> Image.Image:
    image = angular_background()
    draw = ImageDraw.Draw(image)

    # Safe action: front hemisphere, altitude 10–60 degrees.
    for alt in (10.0, 60.0):
        draw_arc_polyline(draw, alt, -90.0, 90.0, (120, 198, 176), 7)
    for az in (-90.0, 90.0):
        draw.line([dome_xy(az, 10), dome_xy(az, 60)], fill=(120, 198, 176), width=7)

    # Altitude rings: 10-degree angular metric, majors at 30 degrees.
    for alt in range(10, 90, 10):
        r = (90 - alt) / 90 * RADIUS
        major = alt % 30 == 0
        color = (92, 130, 151) if major else (53, 82, 104)
        width = 5 if major else 2
        draw.ellipse((CX - r, CY - r, CX + r, CY + r), outline=color, width=width)

    # Azimuth spokes. Front is the lower radius of the file.
    for az in range(-180, 180, 10):
        major = az % 30 == 0
        color = (92, 130, 151) if major else (47, 72, 91)
        width = 5 if major else 2
        draw.line([dome_xy(az, 90), dome_xy(az, 0)], fill=color, width=width)

    # Springline is the only frame: everything outside remains pure black.
    draw.ellipse((CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS), outline=(183, 215, 224), width=10)

    # Cardinal axes have distinct signatures and cannot be confused after projection.
    cardinals = [
        (0, "FRONT 0°", (234, 179, 89)),
        (90, "RIGHT +90°", (209, 112, 102)),
        (-90, "LEFT −90°", (101, 170, 220)),
        (180, "BACK 180°", (161, 139, 205)),
    ]
    label_font = font(46, True)
    for az, label, color in cardinals:
        draw.line([dome_xy(az, 90), dome_xy(az, 0)], fill=color, width=12)
        x, y = dome_xy(az, 5)
        box = draw.textbbox((0, 0), label, font=label_font)
        tw, th = box[2] - box[0], box[3] - box[1]
        # Move labels inward and offset tangentially where necessary.
        if az == 0:
            pos = (x - tw / 2, y - th - 42)
        elif az in (180, -180):
            pos = (x - tw / 2, y + 24)
        elif az == 90:
            pos = (x - tw - 40, y - th / 2)
        else:
            pos = (x + 40, y - th / 2)
        draw.text(pos, label, font=label_font, fill=color)

    # Ring values placed away from the principal front gesture.
    metric_font = font(35, True)
    for alt in range(10, 90, 10):
        x, y = dome_xy(-135, alt)
        draw.text((x + 12, y - 18), f"{alt}°", font=metric_font, fill=(150, 181, 194))

    # Zenith mark and the intended front-view target at altitude 35 degrees.
    zx, zy = dome_xy(0, 90)
    draw.ellipse((zx - 28, zy - 28, zx + 28, zy + 28), fill=(230, 239, 236), outline=(78, 138, 151), width=8)
    draw.text((zx + 46, zy - 25), "ZENITH 90°", font=font(43, True), fill=(214, 231, 229))

    tx, ty = dome_xy(0, VIEW_ALT_DEG)
    draw.ellipse((tx - 34, ty - 34, tx + 34, ty + 34), outline=(244, 196, 102), width=10)
    draw.line((tx - 48, ty, tx + 48, ty), fill=(244, 196, 102), width=5)
    draw.line((tx, ty - 48, tx, ty + 48), fill=(244, 196, 102), width=5)
    draw.text((tx + 58, ty - 30), "VIEW AXIS +35°", font=font(39, True), fill=(244, 196, 102))

    sx, sy = dome_xy(-57, 32)
    draw.text((sx, sy), "SAFE ACTION\n±90° AZ  ·  ALT 10–60°", font=font(35, True), fill=(129, 205, 181), spacing=7)
    return image


def sample_front_preview(master: Image.Image) -> Image.Image:
    """Extract a rectilinear audience view from the Dome Master."""
    yy, xx = np.mgrid[0:PREVIEW_H, 0:PREVIEW_W]
    aspect = PREVIEW_W / PREVIEW_H
    tan_h = math.tan(math.radians(HFOV_DEG) / 2.0)
    tan_v = tan_h / aspect
    sx = (2.0 * (xx + 0.5) / PREVIEW_W - 1.0) * tan_h
    sy = (1.0 - 2.0 * (yy + 0.5) / PREVIEW_H) * tan_v

    altitude = math.radians(VIEW_ALT_DEG)
    forward = np.array([0.0, math.cos(altitude), math.sin(altitude)])
    right = np.array([1.0, 0.0, 0.0])
    up = np.array([0.0, -math.sin(altitude), math.cos(altitude)])

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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_proof() -> dict:
    directions = {
        "zenith": (0, 90),
        "front_springline": (0, 0),
        "right_springline": (90, 0),
        "left_springline": (-90, 0),
        "back_springline": (180, 0),
        "front_view_axis": (0, VIEW_ALT_DEG),
    }
    return {
        "artifact": "Second Sky universal fulldome calibration",
        "version": "0.1",
        "generation": "deterministic code-native direction field; no image model",
        "projection": "equidistant azimuthal fisheye",
        "coverage": {"horizontal_degrees": 360, "vertical_degrees": 180},
        "axes": {"front": "+y", "right": "+x", "zenith": "+z"},
        "file_orientation": {"bottom": "front", "right": "audience right", "center": "zenith", "top": "back"},
        "master": {
            "path": str(MASTER_PATH),
            "size_px": [SIZE, SIZE],
            "active_radius_px": RADIUS,
            "outside_circle": "RGB 0,0,0",
            "sha256": sha256(MASTER_PATH),
        },
        "grid": {"altitude_step_degrees": 10, "azimuth_step_degrees": 10, "major_step_degrees": 30},
        "safe_action": {"azimuth_degrees": [-90, 90], "altitude_degrees": [10, 60]},
        "orientation_samples_px": {
            key: [round(value, 3) for value in dome_xy(*angles)] for key, angles in directions.items()
        },
        "preview": {
            "path": str(PREVIEW_PATH),
            "size_px": [PREVIEW_W, PREVIEW_H],
            "view_azimuth_degrees": 0,
            "view_altitude_degrees": VIEW_ALT_DEG,
            "horizontal_fov_degrees": HFOV_DEG,
            "sha256": sha256(PREVIEW_PATH),
        },
        "gates": {
            "architecture_concept": "not applicable: this artifact calibrates the carrier",
            "dome_master": "PASS for universal 180-degree orientation and angular metric",
            "venue": "OPEN: requires projector warp, blend, black/colour calibration and physical dome test",
        },
    }


def main() -> None:
    master = build_master()
    master.save(MASTER_PATH, format="PNG", optimize=False, compress_level=9, dpi=(72, 72))
    preview = sample_front_preview(master)
    preview.save(PREVIEW_PATH, format="PNG", optimize=False, compress_level=9, dpi=(72, 72))
    PROOF_PATH.write_text(json.dumps(build_proof(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(MASTER_PATH)
    print(PREVIEW_PATH)
    print(PROOF_PATH)


if __name__ == "__main__":
    main()
