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

try:
    from scripts.asset_reuse import check_manifest_reuse, load_registry
except ModuleNotFoundError:
    from asset_reuse import check_manifest_reuse, load_registry


def _inside_directory(path: Path, directory: Path) -> bool:
    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def _validate_raster(
    path: Path,
    trim: dict[str, float],
    minimum_dpi: int,
    safe_margin_in: float,
    allow_color: bool = False,
    require_color: bool = False,
) -> None:
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
        source_native_dpi = source.info.get("source_native_dpi")
        if source_native_dpi is not None and float(source_native_dpi) < minimum_dpi:
            raise ValueError(
                f"{path}: generated source is only {source_native_dpi} native DPI; trace to reviewed vector art or replace with native 300-DPI artwork"
            )
        if rgba.getchannel("A").getextrema() != (255, 255):
            raise ValueError(f"{path}: transparent pixels are not allowed")
        rgb = rgba.convert("RGB")
        grayscale = rgb.convert("L")
        if require_color:
            red, green, blue = rgb.split()
            if not (ImageChops.difference(red, green).getbbox() or ImageChops.difference(red, blue).getbbox()):
                raise ValueError(f"{path}: colored reference must contain actual color pixels")
        if not allow_color:
            red, green, blue = rgb.split()
            if ImageChops.difference(red, green).getbbox() or ImageChops.difference(red, blue).getbbox():
                raise ValueError(f"{path}: artwork must be monochrome")
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
    if manifest.get("page_plan_mode") == "flexible_activity":
        allowed_types = {
            "title",
            "reverse",
            "illustration",
            "multi_panel",
            "color_reference",
            "connect_dots",
            "trace_path",
        }
        for page in pages:
            if page.get("type") not in allowed_types:
                raise ValueError(f"Page {page.get('number')} has unsupported activity type {page.get('type')!r}")
        if pages[0].get("type") != "title":
            raise ValueError("The first page must be the title page")
        return

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

    def validate_asset(asset_name: str, qa_status: str, page_number: int, allow_color: bool = False) -> Path:
        if qa_status != "PASS":
            raise ValueError(f"Page {page_number} asset is not QA-approved")
        asset_path = (asset_root / asset_name).resolve(strict=True)
        if not _inside_directory(asset_path, asset_root):
            raise ValueError(f"Page {page_number} asset path escapes asset_root")
        _validate_raster(
            asset_path,
            trim,
            int(manifest["minimum_dpi"]),
            float(manifest["minimum_safe_margin_in"]),
            allow_color=allow_color,
        )
        asset_paths.append(asset_path)
        return asset_path

    for page in pages:
        page_type = page.get("type")
        if page_type == "title":
            continue
        if page_type == "reverse":
            if page.get("design") != reverse_arg:
                raise ValueError(f"Page {page['number']} reverse design does not match CLI policy")
            continue
        if page_type == "illustration":
            subject_id = page.get("subject_id")
            if not subject_id or subject_id in illustration_subjects:
                raise ValueError(f"Page {page['number']} has a missing or duplicate subject_id")
            illustration_subjects.add(subject_id)
            validate_asset(page["asset"], page.get("qa_status", ""), page["number"])
            continue

        if page_type == "multi_panel":
            panels = page.get("panels", [])
            if not 2 <= len(panels) <= 4:
                raise ValueError(f"Page {page['number']} multi_panel requires 2-4 panels")
            rectangles: list[tuple[float, float, float, float]] = []
            for panel in panels:
                rectangle = panel.get("rect", {})
                x, y, width, height = (float(rectangle[key]) for key in ("x", "y", "width", "height"))
                if min(x, y, width, height) < 0 or width <= 0 or height <= 0 or x + width > 1 or y + height > 1:
                    raise ValueError(f"Page {page['number']} has a panel rectangle outside normalized page bounds")
                if width < 0.3 or height < 0.25:
                    raise ValueError(f"Page {page['number']} has a panel too small for print")
                safe_margin = float(manifest["minimum_safe_margin_in"])
                trim_width = float(trim["width_in"])
                trim_height = float(trim["height_in"])
                if (
                    x * trim_width < safe_margin
                    or y * trim_height < safe_margin
                    or (1 - x - width) * trim_width < safe_margin
                    or (1 - y - height) * trim_height < safe_margin
                ):
                    raise ValueError(f"Page {page['number']} panel crosses the safe area")
                for prior_x, prior_y, prior_width, prior_height in rectangles:
                    overlaps = x < prior_x + prior_width and x + width > prior_x and y < prior_y + prior_height and y + height > prior_y
                    if overlaps:
                        raise ValueError(f"Page {page['number']} multi_panel rectangles must not overlap")
                    horizontal_gap = max(prior_x - (x + width), x - (prior_x + prior_width), 0) * trim_width
                    vertical_gap = max(prior_y - (y + height), y - (prior_y + prior_height), 0) * trim_height
                    if horizontal_gap < 0.15 and vertical_gap < 0.15:
                        raise ValueError(f"Page {page['number']} multi_panel gutter must be at least 0.15 inch")
                rectangles.append((x, y, width, height))
                validate_asset(panel["asset"], panel.get("qa_status", ""), page["number"])
            continue

        if page_type == "color_reference":
            if manifest.get("interior_color_mode") != "color":
                raise ValueError("color_reference pages require manifest interior_color_mode=color")
            for key in ("line_art", "colored_reference"):
                component = page.get(key, {})
                validate_asset(
                    component["asset"],
                    component.get("qa_status", ""),
                    page["number"],
                    allow_color=(key == "colored_reference"),
                )
                if key == "colored_reference":
                    reference_path = (asset_root / component["asset"]).resolve(strict=True)
                    _validate_raster(
                        reference_path,
                        trim,
                        int(manifest["minimum_dpi"]),
                        float(manifest["minimum_safe_margin_in"]),
                        allow_color=True,
                        require_color=True,
                    )
            split_ratio = float(page.get("line_art_width_ratio", 0.68))
            if not 0.6 <= split_ratio <= 0.8:
                raise ValueError(f"Page {page['number']} coloring panel must use 60-80 percent of the live width")
            continue

        if page_type in {"connect_dots", "trace_path"}:
            points = page.get("points", [])
            minimum_points = 8 if page_type == "connect_dots" else 3
            maximum_points = 40 if page_type == "connect_dots" else 80
            if not minimum_points <= len(points) <= maximum_points:
                raise ValueError(f"Page {page['number']} {page_type} requires {minimum_points}-{maximum_points} ordered points")
            if page_type == "connect_dots" and int(page.get("minimum_age_years", 4)) < 4:
                raise ValueError("Numbered connect_dots pages are restricted to minimum_age_years >= 4")
            safe_margin = float(manifest["minimum_safe_margin_in"])
            min_x = safe_margin / float(trim["width_in"])
            max_x = 1 - min_x
            min_y = safe_margin / float(trim["height_in"])
            max_y = 1 - min_y
            for point in points:
                x, y = float(point["x"]), float(point["y"])
                if not min_x <= x <= max_x or not min_y <= y <= max_y:
                    raise ValueError(f"Page {page['number']} activity point crosses the safe area")
            if page_type == "connect_dots":
                labels = [int(point.get("label", index + 1)) for index, point in enumerate(points)]
                if labels != list(range(1, len(points) + 1)):
                    raise ValueError(f"Page {page['number']} connect_dots labels must be sequential from 1")
                for first_index, first in enumerate(points):
                    for second in points[first_index + 1 :]:
                        distance = math.hypot(
                            (float(first["x"]) - float(second["x"])) * float(trim["width_in"]),
                            (float(first["y"]) - float(second["y"])) * float(trim["height_in"]),
                        )
                        if distance < 0.22:
                            raise ValueError(f"Page {page['number']} connect_dots labels are too close for print readability")
            else:
                for first, second in zip(points, points[1:]):
                    distance = math.hypot(
                        (float(first["x"]) - float(second["x"])) * float(trim["width_in"]),
                        (float(first["y"]) - float(second["y"])) * float(trim["height_in"]),
                    )
                    if not 0.12 <= distance <= 0.45:
                        raise ValueError(f"Page {page['number']} trace_path dots must be spaced 0.12-0.45 inch apart")
            continue

        if page_type != "illustration":
            raise ValueError(f"Page {page.get('number')}: unsupported page type {page_type!r}")

    if manifest.get("asset_registry"):
        registry_path = (manifest_path.parent / manifest["asset_registry"]).resolve(strict=True)
        registry = load_registry(registry_path)
        check_manifest_reuse(manifest, asset_root, registry)

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


def _draw_fitted_image(
    pdf: canvas.Canvas,
    image_path: Path,
    x: float,
    y: float,
    width: float,
    height: float,
) -> None:
    pdf.drawImage(
        str(image_path),
        x,
        y,
        width=width,
        height=height,
        preserveAspectRatio=True,
        anchor="c",
        mask=None,
    )


def _draw_multi_panel(pdf: canvas.Canvas, page: dict[str, Any], asset_root: Path, trim: dict[str, float]) -> None:
    page_x, page_y = _trim_origin(page["number"], trim["bleed"])
    page_width = trim["width_in"] * inch
    page_height = trim["height_in"] * inch
    panel_inset = 0.08 * inch
    for panel in page["panels"]:
        rectangle = panel["rect"]
        x = page_x + float(rectangle["x"]) * page_width
        y = page_y + float(rectangle["y"]) * page_height
        width = float(rectangle["width"]) * page_width
        height = float(rectangle["height"]) * page_height
        pdf.setStrokeColor(black)
        pdf.setLineWidth(0.75)
        pdf.rect(x, y, width, height, fill=0, stroke=1)
        image_path = (asset_root / panel["asset"]).resolve(strict=True)
        _draw_fitted_image(
            pdf,
            image_path,
            x + panel_inset,
            y + panel_inset,
            width - 2 * panel_inset,
            height - 2 * panel_inset,
        )


def _draw_color_reference(
    pdf: canvas.Canvas,
    page: dict[str, Any],
    asset_root: Path,
    trim: dict[str, float],
    page_number: int,
) -> None:
    page_x, page_y = _trim_origin(page_number, trim["bleed"])
    safe = 0.5 * inch
    live_x = page_x + safe
    live_y = page_y + safe
    live_width = trim["width_in"] * inch - 2 * safe
    live_height = trim["height_in"] * inch - 2 * safe
    gutter = 0.22 * inch
    split_ratio = float(page.get("line_art_width_ratio", 0.68))
    panel_width = live_width - gutter
    line_width = panel_width * split_ratio
    reference_width = panel_width - line_width

    line_asset = (asset_root / page["line_art"]["asset"]).resolve(strict=True)
    reference_asset = (asset_root / page["colored_reference"]["asset"]).resolve(strict=True)
    _draw_fitted_image(pdf, line_asset, live_x, live_y, line_width, live_height)
    divider_x = live_x + line_width + gutter / 2
    pdf.setStrokeColor(black)
    pdf.setLineWidth(0.75)
    pdf.line(divider_x, live_y, divider_x, live_y + live_height)
    _draw_fitted_image(
        pdf,
        reference_asset,
        live_x + line_width + gutter,
        live_y,
        reference_width,
        live_height,
    )


def _draw_activity_points(
    pdf: canvas.Canvas,
    page: dict[str, Any],
    trim: dict[str, float],
    page_number: int,
) -> None:
    page_x, page_y = _trim_origin(page_number, trim["bleed"])
    page_width = trim["width_in"] * inch
    page_height = trim["height_in"] * inch
    points = page["points"]
    coordinates = [
        (page_x + float(point["x"]) * page_width, page_y + float(point["y"]) * page_height)
        for point in points
    ]

    if page.get("show_solution", False):
        pdf.setStrokeColor(black)
        pdf.setLineWidth(1.5)
        pdf.setLineJoin(1)
        path = pdf.beginPath()
        path.moveTo(*coordinates[0])
        for x, y in coordinates[1:]:
            path.lineTo(x, y)
        pdf.drawPath(path, stroke=1, fill=0)

    for index, (x, y) in enumerate(coordinates):
        if page["type"] == "connect_dots":
            pdf.setFillColor(black)
            pdf.circle(x, y, 2.5, fill=1, stroke=0)
            pdf.setFillColor(black)
            pdf.setFont("Helvetica", 8)
            pdf.drawString(x + 4, y + 3, str(page["points"][index].get("label", index + 1)))
        else:
            pdf.setFillColor(black)
            pdf.circle(x, y, 2.5, fill=1, stroke=0)


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
            _draw_fitted_image(pdf, image_path, page_x, page_y, trim["width_in"] * inch, trim["height_in"] * inch)
        elif page["type"] == "multi_panel":
            _draw_multi_panel(pdf, page, asset_root, trim)
        elif page["type"] == "color_reference":
            _draw_color_reference(pdf, page, asset_root, trim, page["number"])
        elif page["type"] in {"connect_dots", "trace_path"}:
            _draw_activity_points(pdf, page, trim, page["number"])
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