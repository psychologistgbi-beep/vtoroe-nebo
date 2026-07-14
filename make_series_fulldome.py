#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Migrate every public Second Sky world to one honest 4K Dome Master carrier.

The legacy works are not radially distorted pictures.  Each source generator
already defines its law in a normalized polar chart (r, phi), or directly in
hemisphere/volume coordinates.  For every output direction d this migration
uses the equidistant angular chart

    theta = acos(d.z), phi = atan2(d.x, d.y), rho = theta / (pi/2)

and samples the deterministic law carrier at that same (rho, phi).  This is a
chart lift: source radius becomes angular distance from zenith.  The three new
native works are copied bit-for-bit because they already fill a 4096 Dome
Master.  No arbitrary radial warp and no image-generation model are used.
"""

from __future__ import annotations

import hashlib
import json
import math
import shutil
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE / "img"
OUT = SOURCE_DIR / "fulldome"
PREVIEWS = OUT / "previews"
WEB = OUT / "web"
OUT.mkdir(exist_ok=True)
PREVIEWS.mkdir(exist_ok=True)
WEB.mkdir(exist_ok=True)
PROOF_PATH = HERE.parent / "SERIES_FULLDOME_PROOF.json"

SIZE = 4096
RADIUS = SIZE // 2 - 2
CX = CY = SIZE / 2
PREVIEW_W = 1600
PREVIEW_H = 1000
WEB_SIZE = 1024
VIEW_AZIMUTH_DEG = 0.0
VIEW_ALTITUDE_DEG = 35.0
VIEW_HFOV_DEG = 100.0

MATPLOTLIB_RADIUS_RATIO = 1.0 / (2.0 * 1.13)
SURFACE_RADIUS_RATIO = 0.455
NATIVE_RADIUS_RATIO = RADIUS / SIZE


@dataclass(frozen=True)
class Work:
    key: str
    title: str
    source: str
    family: str
    formula: str
    generator: str
    radius_ratio: float
    transfer: str = "equidistant_chart_lift"

    @property
    def source_path(self) -> Path:
        return SOURCE_DIR / self.source

    @property
    def master_path(self) -> Path:
        return OUT / f"{self.key}_domemaster_4k.png"

    @property
    def preview_path(self) -> Path:
        return PREVIEWS / f"{self.key}_front_35.png"

    @property
    def web_path(self) -> Path:
        return WEB / f"{self.key}_domemaster_1024.png"


WORKS = [
    Work("phyllo", "Филлотаксис", "dome_phyllo.png", "polar_formula", "r=sqrt(i/N), phi=i*pi*(3-sqrt(5)); 1400 equal-address seeds", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("reaction", "Живая кожа", "dome_reaction.png", "planar_field_chart", "Gray-Scott reaction-diffusion: Du=0.16, Dv=0.08, f=0.0545, k=0.062", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("beam", "Автопортрет слуха", "dome_beam.png", "analytic_polar", "Airy intensity P(r)=(2*J1(11r)/(11r))^2", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("percol", "Перколь", "dome_percol.png", "discrete_field_chart", "site percolation on deterministic 150x150 lattice at p=0.5927", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("vitel", "Витель", "dome_vitel.png", "vector_field_chart", "normalized stream integration through eight signed point vortices", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("frost", "Изморозь", "dome_frost.png", "growth_field_chart", "deterministic diffusion-limited aggregation from the rim inward", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("mayatnik", "Маятник", "dome_mayatnik.png", "trajectory_chart", "eight double-pendulum RK4 trajectories, dt=0.005", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("nabor", "Набор", "dome_nabor.png", "polar_formula", "Rule 30 cellular automaton written on 52 polar rings", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("chern", "Чернь-домен", "dome_chern.png", "discrete_field_chart", "2D Ising field near critical temperature Tc=2.269", "make_domes.py", MATPLOTLIB_RADIUS_RATIO),
    Work("chladni", "Камертон", "dome_chladni.png", "analytic_polar", "J7(a*r)cos(7phi)+0.46*J3(b*r)sin(3phi+0.34)", "make_domes3.py", MATPLOTLIB_RADIUS_RATIO),
    Work("apollon", "Апейрон", "dome_apollon.png", "polar_formula", "Descartes-circle recursion / deterministic Apollonian gasket", "make_domes3.py", MATPLOTLIB_RADIUS_RATIO),
    Work("tyaga", "Тяга", "dome_tyaga.png", "polar_formula", "96 boundary lines aggregate pairwise through five polar load levels", "make_domes3.py", MATPLOTLIB_RADIUS_RATIO),
    Work("caustic", "Небо каустик", "dome_caustic.png", "analytic_chart", "binary thin-lens map beta=theta-sum(m_i*(theta-theta_i)/|theta-theta_i|^2)", "make_domes4.py", MATPLOTLIB_RADIUS_RATIO),
    Work("chrono", "Хроносвод", "dome_chrono.png", "causal_chart", "1+1 Minkowski causal order dt>|dx| and its Hasse reduction", "make_domes4.py", MATPLOTLIB_RADIUS_RATIO),
    Work("superfluid", "Сверхтекучее небо", "dome_superfluid.png", "phase_field_chart", "phase=sum atan2(y-y_i,x-x_i) over triangular same-sign vortex lattice", "make_domes4.py", MATPLOTLIB_RADIUS_RATIO),
    Work("equal_area", "Собор равных ячеек", "dome_equal_area.png", "intrinsic_surface", "127 equal spherical areas: A=2*pi*(cos(theta0)-cos(theta1))/n", "make_domes5.py", SURFACE_RADIUS_RATIO),
    Work("conformal", "Конформное небо", "dome_conformal.png", "intrinsic_surface", "Mercator sphere coordinates u=ln(tan(theta/2)), v=phi with du=dv", "make_domes5.py", SURFACE_RADIUS_RATIO),
    Work("light_muqarnas", "Световая мукарна", "dome_light_muqarnas.png", "faceted_surface", "4->8->16->32 radial plan lifted into 112 niches and 448 3D facets", "make_domes5.py", SURFACE_RADIUS_RATIO),
    Work("parallax_covenant", "Свод несводимых взглядов", "dome_parallax_covenant.png", "observer_surface", "three tangent-plane glyph families reverse-projected from three observer positions", "make_domes6.py", SURFACE_RADIUS_RATIO),
    Work("hopf_covenant", "Собор неразрывных связей", "dome_hopf_covenant.png", "volume_projection", "24 Hopf fibres: S3 -> stereographic R3 -> compactified dome volume", "make_domes6.py", SURFACE_RADIUS_RATIO),
    Work("three_suns", "Свод трёх времён", "dome_three_suns.png", "optical_surface", "1152 solved reflector normals for dawn/noon/dusk floor programmes", "make_domes6.py", SURFACE_RADIUS_RATIO),
    Work("mutual_horizons", "Собор взаимных горизонтов", "dome_mutual_horizons_domemaster_4k.png", "native_direction_field", "15 great circles n_i dot d=0 and exact pairwise intersections", "make_fulldome_worlds.py", NATIVE_RADIUS_RATIO, "native_4k"),
    Work("common_pulse", "Свод совместной паузы", "dome_common_pulse_domemaster_4k.png", "native_direction_field", "12 coherent scalar waves with delta=acos(s_i dot d)", "make_fulldome_worlds.py", NATIVE_RADIUS_RATIO, "native_4k"),
    Work("habitable_boundary", "Собор обитаемой границы", "dome_habitable_boundary_domemaster_4k.png", "native_direction_field", "(1-D*Laplace_Beltrami)T=max(d dot star,0), Legendre degree 32", "make_fulldome_worlds.py", NATIVE_RADIUS_RATIO, "native_4k"),
    Work("portal_1", "Портал I", "dome_portal_1.png", "symbolic_polar", "seven coffer registers plus golden-angle figure addresses, run I", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("portal_2", "Портал II", "dome_portal_2.png", "symbolic_polar", "seven coffer registers plus golden-angle figure addresses, run II", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("portal_3", "Портал III", "dome_portal_3.png", "symbolic_polar", "seven coffer registers plus golden-angle figure addresses, run III", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("san_marco", "Сан-Марко", "dome_san_marco.png", "symbolic_polar", "polar tessera field with two processional icon registers", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("muqarnas", "Мукарны", "dome_muqarnas.png", "symbolic_polar", "ten nested polar tiers with adaptive cell count and niche profile", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
    Work("mandala", "Мандала", "dome_mandala.png", "symbolic_polar", "eleven angular-distance rings, 24 meridians and three rosette registers", "make_domes2.py", MATPLOTLIB_RADIUS_RATIO),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def save_png(image: Image.Image, path: Path) -> None:
    image.save(path, format="PNG", optimize=False, compress_level=9, dpi=(72, 72))


def chart_lift(work: Work) -> dict:
    """Lift the source law chart to a full-diameter equidistant master.

    The transformation is a direction lookup, not a nonlinear image effect:
    source_r/Rs = output_r/R = theta/(pi/2), and source_phi=output_phi.
    """
    source = Image.open(work.source_path).convert("RGBA")
    sw, sh = source.size
    if sw != sh:
        raise ValueError(f"source must be square: {work.source_path}")
    source_radius = work.radius_ratio * sw
    center = sw / 2.0
    box = (
        int(round(center - source_radius)),
        int(round(center - source_radius)),
        int(round(center + source_radius)),
        int(round(center + source_radius)),
    )
    law_square = source.crop(box).resize((RADIUS * 2, RADIUS * 2), Image.Resampling.LANCZOS)

    # Transparent legacy corners become black; the active circle is defined anew
    # from the hemisphere, so atmospheric pixels outside the law chart cannot leak.
    law_rgb = Image.new("RGB", law_square.size, (0, 0, 0))
    law_rgb.paste(law_square.convert("RGB"), mask=law_square.getchannel("A"))
    mask = Image.new("L", law_square.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, RADIUS * 2 - 1, RADIUS * 2 - 1), fill=255)
    master = Image.new("RGB", (SIZE, SIZE), (0, 0, 0))
    master.paste(law_rgb, (SIZE // 2 - RADIUS, SIZE // 2 - RADIUS), mask)
    save_png(master, work.master_path)
    return {
        "source_size_px": [sw, sh],
        "source_active_radius_px": source_radius,
        "mapping": "rho=theta/(pi/2); xs=cxs+Rs*rho*sin(phi); ys=cys+Rs*rho*cos(phi)",
        "angular_scale_degrees_per_output_radius": 90.0,
    }


def sample_preview(master: Image.Image) -> Image.Image:
    yy, xx = np.mgrid[0:PREVIEW_H, 0:PREVIEW_W]
    aspect = PREVIEW_W / PREVIEW_H
    tan_h = math.tan(math.radians(VIEW_HFOV_DEG) / 2.0)
    tan_v = tan_h / aspect
    sx = ((2.0 * (xx.astype(np.float32) + 0.5) / PREVIEW_W) - 1.0) * tan_h
    sy = (1.0 - 2.0 * (yy.astype(np.float32) + 0.5) / PREVIEW_H) * tan_v

    az = math.radians(VIEW_AZIMUTH_DEG)
    alt = math.radians(VIEW_ALTITUDE_DEG)
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


def build_contact_sheet(records: list[dict]) -> Path:
    font_path = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font_bold_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    font = ImageFont.truetype(font_path, 20)
    bold = ImageFont.truetype(font_bold_path, 23)
    cols, rows = 5, 6
    cell_w, cell_h = 360, 330
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (7, 8, 15))
    draw = ImageDraw.Draw(sheet)

    def wrapped_title(number: int, title: str) -> list[str]:
        words = f"{number:02d}  {title}".split()
        lines: list[str] = []
        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and draw.textlength(candidate, font=bold) > cell_w - 28:
                lines.append(line)
                line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        return lines[:2]

    for index, (work, record) in enumerate(zip(WORKS, records)):
        x0 = (index % cols) * cell_w
        y0 = (index // cols) * cell_h
        preview = Image.open(work.preview_path).convert("RGB")
        preview.thumbnail((336, 210), Image.Resampling.LANCZOS)
        sheet.paste(preview, (x0 + 12, y0 + 12))
        for line_index, line in enumerate(wrapped_title(index + 1, work.title)):
            draw.text((x0 + 14, y0 + 228 + line_index * 27), line, font=bold, fill=(235, 229, 215))
        draw.text((x0 + 14, y0 + 292), work.family, font=font, fill=(143, 174, 192))
    path = OUT / "series_front_35_contact_sheet.png"
    save_png(sheet, path)
    return path


def main() -> None:
    records = []
    for index, work in enumerate(WORKS, start=1):
        if not work.source_path.exists():
            raise FileNotFoundError(work.source_path)
        if work.transfer == "native_4k":
            shutil.copyfile(work.source_path, work.master_path)
            transfer_proof = {
                "source_size_px": [SIZE, SIZE],
                "source_active_radius_px": RADIUS,
                "mapping": "native direction field; bit-for-bit master copy",
                "angular_scale_degrees_per_output_radius": 90.0,
            }
        else:
            transfer_proof = chart_lift(work)

        master = Image.open(work.master_path).convert("RGB")
        if master.size != (SIZE, SIZE):
            raise AssertionError((work.key, master.size))
        for corner in ((0, 0), (SIZE - 1, 0), (0, SIZE - 1), (SIZE - 1, SIZE - 1)):
            if master.getpixel(corner) != (0, 0, 0):
                raise AssertionError((work.key, "non-black corner", corner, master.getpixel(corner)))
        preview = sample_preview(master)
        save_png(preview, work.preview_path)
        web_master = master.resize((WEB_SIZE, WEB_SIZE), Image.Resampling.LANCZOS)
        save_png(web_master, work.web_path)

        record = {
            "ordinal": index,
            **asdict(work),
            "source_path": str(work.source_path),
            "source_sha256": sha256(work.source_path),
            "master_path": str(work.master_path),
            "master_sha256": sha256(work.master_path),
            "master_size_px": [SIZE, SIZE],
            "preview_path": str(work.preview_path),
            "preview_sha256": sha256(work.preview_path),
            "preview_size_px": [PREVIEW_W, PREVIEW_H],
            "web_path": str(work.web_path),
            "web_sha256": sha256(work.web_path),
            "web_size_px": [WEB_SIZE, WEB_SIZE],
            "transfer_proof": transfer_proof,
            "dome_master_pass": True,
            "venue_pass": False,
        }
        records.append(record)
        print(f"{index:02d}/30 {work.key}")

    contact_sheet = build_contact_sheet(records)
    proof = {
        "artifact": "Second Sky — complete 30-world fulldome migration",
        "version": "0.1",
        "agency_task": 9486,
        "generation": "deterministic mathematical chart lift and native direction fields; no image model",
        "projection": "equidistant azimuthal fisheye",
        "coverage": {"horizontal_degrees": 360, "vertical_degrees": 180},
        "axes": {"front": "+y / file bottom", "right": "+x / file right", "zenith": "+z / file center"},
        "master_size_px": [SIZE, SIZE],
        "preview": {"azimuth_degrees": VIEW_AZIMUTH_DEG, "altitude_degrees": VIEW_ALTITUDE_DEG, "hfov_degrees": VIEW_HFOV_DEG},
        "counts": {
            "total": len(records),
            "native_direction_field": sum(r["family"] == "native_direction_field" for r in records),
            "intrinsic_or_spatial": sum(r["family"] in {"intrinsic_surface", "faceted_surface", "observer_surface", "volume_projection", "optical_surface"} for r in records),
            "mathematical_chart_lift": sum(r["family"] not in {"native_direction_field", "intrinsic_surface", "faceted_surface", "observer_surface", "volume_projection", "optical_surface", "symbolic_polar"} for r in records),
            "symbolic_polar": sum(r["family"] == "symbolic_polar" for r in records),
            "dome_master_pass": sum(r["dome_master_pass"] for r in records),
            "venue_pass": sum(r["venue_pass"] for r in records),
        },
        "contact_sheet": {"path": str(contact_sheet), "sha256": sha256(contact_sheet)},
        "generator": {"path": str(Path(__file__).resolve()), "sha256": sha256(Path(__file__).resolve())},
        "works": records,
        "claim_boundary": "Dome Master geometry and deterministic transfer pass; physical venue projection, line visibility, black level and comfort remain open",
    }
    PROOF_PATH.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(PROOF_PATH)


if __name__ == "__main__":
    main()
