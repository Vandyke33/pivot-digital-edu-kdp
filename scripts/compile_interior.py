"""Build a fail-closed KDP interior PDF from an edition page manifest."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops
from reportlab.lib.colors import black
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas


def _inside_directory(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _validate_raster(path: Path, trim: dict[str, float], minimum_dpi: int, safe_margin_in: float) -> None:
    with Image.open(path) as source:
        source.load()
        width, height = source.size
        minimum_width = math.ceil(trim["width_in"] * minimum_dpi)
        minimum_height = math.ceil(trim["height_in"] * minimum_dpi)
        if width < minimum_width or height < minimum_height:
            raise ValueError(
                f"{path}: {width}x{height}px is below {minimum_width}x{minimum_height}px at {minimum_dpi} DPI"
            )
        if abs((width / height) - (trim["width_in"] / trim["height_in"])) > 0.002:
            raise ValueError(f"{path}: aspect ratio does not match the declared trim size")

        rgba = source.convert("RGBA")
        if rgba.getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"{path}: transparent pixels are not allowed")
        rgb = rgba.convert("RGB")
        red, green, blue = rgb.split()
        if ImageChops.difference(red, green).getbbox() or ImageChops.difference(red, blue).getbbox():
            raise ValueError(f"{path}: artwork must be monochrome")

        grayscale = rgb.convert("L")
        histogram = grayscale.histogram()
        if sum(histogram[1:255]):
            raise ValueError(f"{path}: pixels must be pure black or pure white; thresholding requires separate QA")
        bounds = ImageChops.difference(grayscale, Image.new("L", grayscale.size, 255)).getbbox()
        if bounds is None:
            raise ValueError(f"{path}: image contains no visible artwork")

        pixels_per_inch_x = width / trim["width_in"]
        pixels_per_inch_y = height / trim["height_in"]
        left, upper, right, lower = bounds
        inset_x = safe_margin_in * pixels_per_inch_x
        inset_y = safe_margin_in * pixels_per_inch_y
        if left < inset_x or upper < inset_y or right > width - inset_x or lower > height - inset_y:
            raise ValueError(f"{path}: visible artwork crosses the {safe_margin_in:g} inch safe margin")


def validate_page_plan(manifest: dict[str, Any]) -> None:
    pages = manifest.get("pages", [])
    expected_subjects = manifest.get("expected_subjects", [])
    if len(pages) != manifest.get("expected_page_count"):
        raise ValueError("Manifest page count does not match expected_page_count")
    if [page.get("number") for page in pages] != list(range(1, len(pages) + 1)):
        raise ValueError("Manifest page numbers must be sequential starting at 1")
    if not pages or pages[0].get("type") != "title":
        raise ValueError("The first page must be the title page")
    if not expected_subjects or len(set(expected_subjects)) != len(expected_subjects):
        raise ValueError("expected_subjects must be a non-empty list of unique subject IDs")
    if len(pages) != 2 + 2 * len(expected_subjects):
        raise ValueError("Page plan must contain a title, its reverse, then one illustration/reverse pair per subject")
    if pages[1].get("type") != "reverse":
        raise ValueError("Page 2 must be the title page reverse")

    for subject_index, subject_id in enumerate(expected_subjects):
        illustration = pages[2 + subject_index * 2]
        reverse = pages[3 + subject_index * 2]
        if illustration.get("type") != "illustration" or illustration.get("subject_id") != subject_id:
            raise ValueError(f"Page {illustration.get('number')} must contain subject {subject_id}")
        if reverse.get("type") != "reverse":
            raise ValueError(f"Page {reverse.get('number')} must be the reverse of {subject_id}")


def load_and_validate_manifest(
    manifest_path: Path,
    trim_arg: str,
    bleed_arg: str,
    reverse_arg: str,
) -> tuple[dict[str, Any], Path, list[Path]]:
    manifest_path = manifest_path.resolve(strict=True)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    trim = manifest["trim"]
    expected_trim = f"{trim['width_in']:g}x{trim['height_in']:g}"
    if trim_arg != expected_trim:
        raise ValueError(f"CLI trim {trim_arg} does not match manifest trim {expected_trim}")
    if bleed_arg != trim["bleed"]:
        raise ValueError(f"CLI bleed {bleed_arg} does not match manifest bleed {trim['bleed']}")
    if reverse_arg != manifest["reverse_page"]:
        raise ValueError(f"CLI reverse-page {reverse_arg} does not match manifest reverse_page {manifest['reverse_page']}")
    if reverse_arg == "black" and bleed_arg != "all":
        raise ValueError("Full-page black reverse pages require bleed=all")

    validate_page_plan(manifest)
    pages = manifest["pages"]

    asset_root = (manifest_path.parent / manifest["asset_root"]).resolve()
    asset_paths: list[Path] = []
    illustration_subjects: set[str] = set()
    for page in pages:
        page_type = page.get("type")
        if page_type == "title":
            continue
        if page_type == "reverse":
            if page.get("design") != reverse_arg:
                raise ValueError(f"Page {page['number']} reverse design does not match CLI policy")
            continue
        if page_type != "illustration":
            raise ValueError(f"Page {page.get('number')}: unsupported page type {page_type!r}")
        if page.get("qa_status") != "PASS":
            raise ValueError(f"Page {page['number']} asset is not QA-approved")
        subject_id = page.get("subject_id")
        if not subject_id or subject_id in illustration_subjects:
            raise ValueError(f"Page {page['number']} has a missing or duplicate subject_id")
        illustration_subjects.add(subject_id)

        asset_path = (asset_root / page["asset"]).resolve(strict=True)
        if not _inside_directory(asset_path, asset_root):
            raise ValueError(f"Page {page['number']} asset path escapes asset_root")
        _validate_raster(
            asset_path,
            trim,
            int(manifest["minimum_dpi"]),
            float(manifest["minimum_safe_margin_in"]),
        )
        asset_paths.append(asset_path)

    return manifest, asset_root, asset_paths


def _page_dimensions(trim: dict[str, float], bleed: str) -> tuple[float, float]:
    if bleed == "all":
        return (trim["width_in"] + 0.125) * inch, (trim["height_in"] + 0.25) * inch
    return trim["width_in"] * inch, trim["height_in"] * inch


def _trim_origin(page_number: int, bleed: str) -> tuple[float, float]:
    if bleed != "all":
        return 0.0, 0.0
    # Bleed extends on the outside edge; the binding edge stays at the trim boundary.
    outside_x = 0.125 * inch if page_number % 2 == 0 else 0.0
    return outside_x, 0.125 * inch


def build_pdf(manifest: dict[str, Any], asset_root: Path, output_path: Path) -> None:
    trim = manifest["trim"]
    bleed = trim["bleed"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_width, page_height = _page_dimensions(trim, bleed)
    pdf = canvas.Canvas(str(output_path), pagesize=(page_width, page_height), pageCompression=1)
    pdf.setTitle(manifest["title"])
    pdf.setAuthor(manifest["publisher"])

    for page in manifest["pages"]:
        page_width, page_height = _page_dimensions(trim, bleed)
        pdf.setPageSize((page_width, page_height))
        page_x, page_y = _trim_origin(page["number"], bleed)

        if page["type"] == "reverse":
            pdf.setFillColor(black)
            pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)
        elif page["type"] == "illustration":
            image_path = (asset_root / page["asset"]).resolve(strict=True)
            pdf.drawImage(
                str(image_path),
                page_x,
                page_y,
                width=trim["width_in"] * inch,
                height=trim["height_in"] * inch,
                preserveAspectRatio=True,
                anchor="c",
                mask=None,
            )
        elif page["type"] == "title":
            pdf.setFillColor(black)
            pdf.setFont("Helvetica-Bold", 24)
            pdf.drawCentredString(
                page_x + trim["width_in"] * inch / 2,
                page_y + trim["height_in"] * inch * 0.72,
                manifest["title"],
            )
            pdf.setFont("Helvetica", 12)
            pdf.drawCentredString(
                page_x + trim["width_in"] * inch / 2,
                page_y + trim["height_in"] * inch * 0.67,
                manifest["subtitle"],
            )
            pdf.setFont("Helvetica-Bold", 14)
            pdf.drawCentredString(
                page_x + trim["width_in"] * inch / 2,
                page_y + trim["height_in"] * inch * 0.48,
                "THIS BOOK BELONGS TO:",
            )
            pdf.setLineWidth(1)
            pdf.line(
                page_x + trim["width_in"] * inch * 0.2,
                page_y + trim["height_in"] * inch * 0.43,
                page_x + trim["width_in"] * inch * 0.8,
                page_y + trim["height_in"] * inch * 0.43,
            )
            pdf.setFont("Helvetica", 9)
            pdf.drawCentredString(
                page_x + trim["width_in"] * inch / 2,
                page_y + trim["height_in"] * inch * 0.08,
                manifest["publisher"],
            )

        pdf.showPage()

    pdf.save()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--trim", required=True, choices=["8.5x11"])
    parser.add_argument("--bleed", required=True, choices=["none", "all"])
    parser.add_argument("--reverse-page", required=True, choices=["black"])
    args = parser.parse_args()

    try:
        manifest, asset_root, asset_paths = load_and_validate_manifest(
            args.manifest,
            args.trim,
            args.bleed,
            args.reverse_page,
        )
        build_pdf(manifest, asset_root, args.output)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))

    print(f"Built {manifest['expected_page_count']} pages from {len(asset_paths)} approved illustrations: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())