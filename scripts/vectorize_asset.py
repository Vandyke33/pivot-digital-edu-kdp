"""Vectorize line-art raster candidates into scaled, printable SVG masters and 300-DPI previews."""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import sys
import tempfile
import warnings
import xml.etree.ElementTree as ET
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageOps
import resvg_py
import vtracer

try:
    from scripts.asset_reuse import (
        load_registry,
        register_asset_record,
        validate_preview,
        validate_svg_master,
    )
    from scripts.asset_registry import write_registry
    from scripts.compile_interior import _validate_raster
except ModuleNotFoundError:
    from asset_reuse import (
        load_registry,
        register_asset_record,
        validate_preview,
        validate_svg_master,
    )
    from asset_registry import write_registry
    from compile_interior import _validate_raster


def crop_to_content(
    image: Image.Image,
    threshold: int = 200,
    padding_px: int = 12,
) -> tuple[Image.Image, tuple[int, int, int, int]]:
    """Crop image tightly to its black line-art bounds with safety padding."""
    grayscale = ImageOps.exif_transpose(image).convert("L")
    binary = grayscale.point(lambda p: 0 if p < threshold else 255, mode="1").convert("L")
    diff = ImageChops.difference(binary, Image.new("L", binary.size, 255))
    bbox = diff.getbbox()
    if bbox is None:
        raise ValueError("Image contains no dark artwork contours above threshold")

    left, top, right, bottom = bbox
    crop_box = (
        max(0, left - padding_px),
        max(0, top - padding_px),
        min(image.width, right + padding_px),
        min(image.height, bottom + padding_px),
    )
    cropped = grayscale.crop(crop_box)
    return cropped, crop_box


def vectorize_image(
    image: Image.Image,
    filter_speckle: int = 4,
    corner_threshold: int = 60,
    length_threshold: float = 4.0,
    max_iterations: int = 10,
    splice_threshold: int = 45,
    path_precision: int = 2,
) -> str:
    """Trace a cropped raster image into raw SVG path elements using vtracer."""
    rgba = image.convert("RGBA")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        pixels = list(rgba.getdata())

    svg_markup = vtracer.convert_pixels_to_svg(
        pixels,
        rgba.size,
        colormode="binary",
        filter_speckle=filter_speckle,
        corner_threshold=corner_threshold,
        length_threshold=length_threshold,
        max_iterations=max_iterations,
        splice_threshold=splice_threshold,
        path_precision=path_precision,
    )
    return svg_markup


def build_framed_svg(
    inner_svg_markup: str,
    art_width: int,
    art_height: int,
    page_width_in: float = 8.5,
    page_height_in: float = 11.0,
    dpi: int = 300,
    safe_margin_in: float = 0.5,
    fill_ratio: float = 0.88,
) -> tuple[str, dict[str, Any]]:
    """Place vectorized art into a standard print canvas centered inside safe margins."""
    page_w = int(round(page_width_in * dpi))
    page_h = int(round(page_height_in * dpi))
    safe_margin_px = safe_margin_in * dpi
    safe_w = page_w - 2 * safe_margin_px
    safe_h = page_h - 2 * safe_margin_px

    max_target_w = safe_w * fill_ratio
    max_target_h = safe_h * fill_ratio

    scale = min(max_target_w / art_width, max_target_h / art_height)
    scaled_w = art_width * scale
    scaled_h = art_height * scale
    offset_x = (page_w - scaled_w) / 2
    offset_y = (page_h - scaled_h) / 2

    # Extract inner path / group elements from vtracer SVG
    content = re.sub(r"<\?xml.*?\?>", "", inner_svg_markup, flags=re.DOTALL)
    content = re.sub(r"^.*?<svg[^>]*>", "", content, flags=re.DOTALL)
    content = re.sub(r"</svg>.*$", "", content, flags=re.DOTALL).strip()

    full_svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
        f'width="{page_w}" height="{page_h}" viewBox="0 0 {page_w} {page_h}">\n'
        f'  <rect width="{page_w}" height="{page_h}" fill="#ffffff"/>\n'
        f'  <g transform="translate({offset_x:.2f}, {offset_y:.2f}) scale({scale:.5f})">\n'
        f"    {content}\n"
        f"  </g>\n"
        f"</svg>\n"
    )
    metadata = {
        "page_width_px": page_w,
        "page_height_px": page_h,
        "dpi": dpi,
        "safe_margin_in": safe_margin_in,
        "fill_ratio": fill_ratio,
        "scale": round(scale, 5),
        "offset_x": round(offset_x, 2),
        "offset_y": round(offset_y, 2),
        "scaled_art_width_px": round(scaled_w, 2),
        "scaled_art_height_px": round(scaled_h, 2),
    }
    return full_svg, metadata


def render_svg_to_preview(
    svg_string: str,
    width_px: int = 2550,
    height_px: int = 3300,
    threshold: int = 128,
) -> Image.Image:
    """Render SVG to a 300-DPI pure monochrome RGB raster image."""
    png_bytes = resvg_py.svg_to_bytes(
        svg_string=svg_string,
        width=width_px,
        height=height_px,
        background="#ffffff",
        shape_rendering="geometric_precision",
    )
    with Image.open(BytesIO(png_bytes)) as rendered:
        grayscale = rendered.convert("L")
        binary = grayscale.point(lambda p: 0 if p < threshold else 255, mode="1")
        monochrome_rgb = binary.convert("RGB")
    return monochrome_rgb


def vectorize_and_render_asset(
    input_image_path: Path,
    output_svg_path: Path,
    output_preview_path: Path,
    page_width_in: float = 8.5,
    page_height_in: float = 11.0,
    dpi: int = 300,
    safe_margin_in: float = 0.5,
    fill_ratio: float = 0.88,
    crop_threshold: int = 200,
    crop_padding_px: int = 12,
) -> dict[str, Any]:
    """Execute the full end-to-end vectorization, auto-framing, and 300-DPI rendering."""
    with Image.open(input_image_path) as raw_im:
        cropped, crop_box = crop_to_content(raw_im, threshold=crop_threshold, padding_px=crop_padding_px)
        art_w, art_h = cropped.size

    inner_svg = vectorize_image(cropped)
    full_svg, frame_meta = build_framed_svg(
        inner_svg_markup=inner_svg,
        art_width=art_w,
        art_height=art_h,
        page_width_in=page_width_in,
        page_height_in=page_height_in,
        dpi=dpi,
        safe_margin_in=safe_margin_in,
        fill_ratio=fill_ratio,
    )

    output_svg_path.parent.mkdir(parents=True, exist_ok=True)
    output_svg_path.write_text(full_svg, encoding="utf-8")
    validate_svg_master(output_svg_path)

    preview_im = render_svg_to_preview(
        svg_string=full_svg,
        width_px=frame_meta["page_width_px"],
        height_px=frame_meta["page_height_px"],
    )
    output_preview_path.parent.mkdir(parents=True, exist_ok=True)
    preview_im.save(output_preview_path, format="PNG")
    validate_preview(output_preview_path)

    _validate_raster(
        output_preview_path,
        {"width_in": page_width_in, "height_in": page_height_in},
        dpi,
        safe_margin_in,
        allow_color=False,
    )

    frame_meta.update(
        {
            "crop_box": list(crop_box),
            "original_art_size": [art_w, art_h],
            "svg_path": str(output_svg_path),
            "preview_path": str(output_preview_path),
        }
    )
    return frame_meta


def process_single_asset(
    input_path: Path,
    asset_id: str,
    category: str,
    subject_id: str,
    svg_master_path: Path | None = None,
    preview_path: Path | None = None,
    registry_path: Path | None = None,
    copy_to_path: Path | None = None,
    fill_ratio: float = 0.88,
) -> dict[str, Any]:
    """Vectorize asset, write master & preview, and optionally register in asset registry."""
    repo_root = Path(__file__).resolve().parents[1]
    svg_out = svg_master_path or (repo_root / "assets" / "svg" / category / asset_id / "v1.svg")
    preview_out = preview_path or (repo_root / "assets" / "previews" / category / asset_id / "v1.png")

    meta = vectorize_and_render_asset(
        input_image_path=input_path,
        output_svg_path=svg_out,
        output_preview_path=preview_out,
        fill_ratio=fill_ratio,
    )

    if copy_to_path:
        copy_to_path.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(preview_out) as preview:
            preview.save(copy_to_path, format="PNG")

    if registry_path:
        reg = load_registry(registry_path)
        if asset_id not in reg["assets"]:
            record = register_asset_record(
                registry=reg,
                asset_id=asset_id,
                category=category,
                subject_id=subject_id,
                svg_path=svg_out,
                preview_path=preview_out,
            )
            write_registry(registry_path, reg)
            meta["registered"] = True
            meta["record"] = record
        else:
            meta["registered"] = False
            meta["note"] = f"Asset {asset_id} already exists in registry"

    return meta


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Path to raw or candidate line art image")
    parser.add_argument("--asset-id", help="Canonical asset ID, e.g. solar_system_explorers.sun.v1")
    parser.add_argument("--category", help="Registry category (e.g. solar-system, animals, vehicles)")
    parser.add_argument("--subject-id", help="Subject identifier, e.g. sun")
    parser.add_argument("--output-svg", type=Path, help="Destination path for SVG master")
    parser.add_argument("--output-preview", type=Path, help="Destination path for 300 DPI preview PNG")
    parser.add_argument("--fill-ratio", type=float, default=0.88, help="Target fill ratio within safe area (0.7-0.95)")
    parser.add_argument("--registry", type=Path, default=Path("catalogs/asset_registry.json"), help="Asset registry path")
    parser.add_argument("--register", action="store_true", help="Register asset record into catalogs/asset_registry.json")
    parser.add_argument("--copy-to", type=Path, help="Optional destination path to copy the approved-size preview")
    parser.add_argument("--batch-manifest", type=Path, help="Path to generation-manifest.json to vectorize all generated items")

    args = parser.parse_args()

    if args.batch_manifest:
        manifest_data = json.loads(args.batch_manifest.read_text(encoding="utf-8"))
        repo_root = Path(__file__).resolve().parents[1]
        category = args.category or "solar-system"
        registry_path = args.registry if args.register else None
        processed_count = 0

        for asset_entry in manifest_data.get("assets", []):
            subject_id = asset_entry.get("subject_id")
            asset_id = asset_entry.get("asset_id")
            raw_path_str = asset_entry.get("output_path") or asset_entry.get("source_local_path")
            if not raw_path_str:
                continue
            raw_path = Path(raw_path_str)
            if not raw_path.is_absolute():
                raw_path = repo_root / raw_path
            if not raw_path.exists():
                continue

            print(f"Vectorizing {asset_id} from {raw_path}...")
            res = process_single_asset(
                input_path=raw_path,
                asset_id=asset_id,
                category=category,
                subject_id=subject_id,
                registry_path=registry_path,
                copy_to_path=args.copy_to,
                fill_ratio=args.fill_ratio,
            )
            processed_count += 1
            print(f"  -> SVG: {res['svg_path']}")
            print(f"  -> Preview: {res['preview_path']} (scale: {res['scale']})")

        print(f"Batch processing complete: {processed_count} assets processed.")
        return 0

    if not args.input:
        parser.error("--input or --batch-manifest is required")
    if not (args.asset_id and args.category and args.subject_id):
        parser.error("--asset-id, --category, and --subject-id are required with --input")

    res = process_single_asset(
        input_path=args.input,
        asset_id=args.asset_id,
        category=args.category,
        subject_id=args.subject_id,
        svg_master_path=args.output_svg,
        preview_path=args.output_preview,
        registry_path=args.registry if args.register else None,
        copy_to_path=args.copy_to,
        fill_ratio=args.fill_ratio,
    )
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
