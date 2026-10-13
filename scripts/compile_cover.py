"""Compile a print-ready Amazon KDP full-wrap paperback cover PDF."""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any

from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
import resvg_py

# KDP Paper constants (B&W interior, 55 lb / 90 GSM standard white paper)
THICKNESS_PER_PAGE_IN = 0.002252
BLEED_IN = 0.125


def calculate_cover_dimensions(
    trim_width_in: float = 8.5,
    trim_height_in: float = 11.0,
    page_count: int = 32,
    bleed_in: float = BLEED_IN,
    thickness_per_page: float = THICKNESS_PER_PAGE_IN,
) -> dict[str, float]:
    """Calculate exact KDP cover dimensions in inches and points."""
    spine_width_in = round(page_count * thickness_per_page, 4)
    total_width_in = round(2 * trim_width_in + spine_width_in + 2 * bleed_in, 4)
    total_height_in = round(trim_height_in + 2 * bleed_in, 4)

    # Front cover horizontal boundaries (in inches from left edge)
    front_left_in = bleed_in + trim_width_in + spine_width_in
    front_right_in = total_width_in - bleed_in

    # Back cover horizontal boundaries
    back_left_in = bleed_in
    back_right_in = bleed_in + trim_width_in

    return {
        "trim_width_in": trim_width_in,
        "trim_height_in": trim_height_in,
        "page_count": page_count,
        "bleed_in": bleed_in,
        "spine_width_in": spine_width_in,
        "total_width_in": total_width_in,
        "total_height_in": total_height_in,
        "front_left_in": front_left_in,
        "front_right_in": front_right_in,
        "back_left_in": back_left_in,
        "back_right_in": back_right_in,
    }


def draw_front_hero_scene(c: canvas.Canvas, cx: float, cy: float) -> None:
    """Draw a rich, vibrant full-color space illustration for the front cover."""
    # 1. Soft glowing nebula backdrop
    c.saveState()
    for r, col, alpha in [
        (2.6 * inch, "#1E3A8A", 0.35),
        (2.0 * inch, "#3B82F6", 0.20),
        (1.4 * inch, "#06B6D4", 0.15),
    ]:
        c.setFillColor(HexColor(col))
        c.setFillAlpha(alpha)
        c.circle(cx, cy, r, fill=1, stroke=0)
    c.restoreState()

    # 2. Orbital trajectory path (dashed arc)
    c.saveState()
    c.setStrokeColor(HexColor("#38BDF8"))
    c.setLineWidth(1.8)
    c.setDash([6, 6])
    p = c.beginPath()
    p.moveTo(cx - 2.5 * inch, cy - 1.8 * inch)
    p.curveTo(cx - 1.2 * inch, cy - 2.2 * inch, cx + 1.2 * inch, cy - 0.5 * inch, cx + 1.8 * inch, cy + 2.0 * inch)
    c.drawPath(p, stroke=1, fill=0)
    c.restoreState()

    # 3. Saturn with Rings (Left side, slightly below center)
    saturn_x = cx - 1.2 * inch
    saturn_y = cy - 0.4 * inch
    saturn_r = 0.9 * inch

    # Back half of ring
    c.saveState()
    c.setStrokeColor(HexColor("#FBBF24"))
    c.setLineWidth(14)
    c.setStrokeAlpha(0.7)
    c.ellipse(saturn_x - 1.6 * inch, saturn_y - 0.4 * inch, saturn_x + 1.6 * inch, saturn_y + 0.4 * inch, stroke=1, fill=0)
    c.restoreState()

    # Planet body
    c.setFillColor(HexColor("#F59E0B"))
    c.circle(saturn_x, saturn_y, saturn_r, fill=1, stroke=0)
    # Band accents
    c.setFillColor(HexColor("#D97706"))
    c.rect(saturn_x - saturn_r + 0.1 * inch, saturn_y - 0.15 * inch, saturn_r * 1.8, 0.18 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#FDE68A"))
    c.rect(saturn_x - saturn_r + 0.18 * inch, saturn_y + 0.15 * inch, saturn_r * 1.6, 0.12 * inch, fill=1, stroke=0)

    # Front half of ring
    c.saveState()
    c.setStrokeColor(HexColor("#FDE68A"))
    c.setLineWidth(8)
    c.setStrokeAlpha(0.9)
    c.ellipse(saturn_x - 1.6 * inch, saturn_y - 0.4 * inch, saturn_x + 1.6 * inch, saturn_y + 0.4 * inch, stroke=1, fill=0)
    c.restoreState()

    # 4. Colorful Rocket Ship (Right side, angled upward)
    rx = cx + 0.9 * inch
    ry = cy + 0.5 * inch

    # Rocket Exhaust Flame
    c.saveState()
    c.setFillColor(HexColor("#EF4444"))
    flame1 = c.beginPath()
    flame1.moveTo(rx - 0.3 * inch, ry - 0.7 * inch)
    flame1.lineTo(rx - 0.55 * inch, ry - 1.5 * inch)
    flame1.lineTo(rx - 0.05 * inch, ry - 0.75 * inch)
    c.drawPath(flame1, fill=1, stroke=0)
    c.setFillColor(HexColor("#FBBF24"))
    flame2 = c.beginPath()
    flame2.moveTo(rx - 0.25 * inch, ry - 0.7 * inch)
    flame2.lineTo(rx - 0.45 * inch, ry - 1.25 * inch)
    flame2.lineTo(rx - 0.1 * inch, ry - 0.75 * inch)
    c.drawPath(flame2, fill=1, stroke=0)
    c.restoreState()

    # Rocket Body (clean white capsule)
    c.saveState()
    c.setFillColor(white)
    c.roundRect(rx - 0.35 * inch, ry - 0.7 * inch, 0.7 * inch, 1.4 * inch, 0.35 * inch, fill=1, stroke=0)
    # Red Nose Cone
    c.setFillColor(HexColor("#EF4444"))
    nose = c.beginPath()
    nose.moveTo(rx - 0.35 * inch, ry + 0.3 * inch)
    nose.curveTo(rx - 0.35 * inch, ry + 0.9 * inch, rx, ry + 1.2 * inch, rx, ry + 1.2 * inch)
    nose.curveTo(rx, ry + 1.2 * inch, rx + 0.35 * inch, ry + 0.9 * inch, rx + 0.35 * inch, ry + 0.3 * inch)
    nose.close()
    c.drawPath(nose, fill=1, stroke=0)
    # Red Fins
    c.setFillColor(HexColor("#DC2626"))
    fin_l = c.beginPath()
    fin_l.moveTo(rx - 0.35 * inch, ry - 0.3 * inch)
    fin_l.lineTo(rx - 0.75 * inch, ry - 0.75 * inch)
    fin_l.lineTo(rx - 0.35 * inch, ry - 0.65 * inch)
    fin_l.close()
    c.drawPath(fin_l, fill=1, stroke=0)
    fin_r = c.beginPath()
    fin_r.moveTo(rx + 0.35 * inch, ry - 0.3 * inch)
    fin_r.lineTo(rx + 0.75 * inch, ry - 0.75 * inch)
    fin_r.lineTo(rx + 0.35 * inch, ry - 0.65 * inch)
    fin_r.close()
    c.drawPath(fin_r, fill=1, stroke=0)
    # Cyan Porthole Window
    c.setFillColor(HexColor("#0284C7"))
    c.circle(rx, ry + 0.1 * inch, 0.22 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#38BDF8"))
    c.circle(rx, ry + 0.1 * inch, 0.17 * inch, fill=1, stroke=0)
    c.setFillColor(white)
    c.circle(rx + 0.05 * inch, ry + 0.15 * inch, 0.05 * inch, fill=1, stroke=0)
    c.restoreState()

    # 5. Moon & Distant Friendly Planets
    # Crescent Moon (top left)
    mx, my = cx - 2.0 * inch, cy + 1.6 * inch
    c.saveState()
    c.setFillColor(HexColor("#FEF08A"))
    c.circle(mx, my, 0.45 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#0B132B"))
    c.circle(mx + 0.18 * inch, my + 0.08 * inch, 0.42 * inch, fill=1, stroke=0)
    c.restoreState()

    # Distant Earth (top center-right)
    ex, ey = cx + 0.2 * inch, cy + 1.8 * inch
    c.setFillColor(HexColor("#3B82F6"))
    c.circle(ex, ey, 0.32 * inch, fill=1, stroke=0)
    c.setFillColor(HexColor("#10B981"))
    c.circle(ex - 0.08 * inch, ey + 0.05 * inch, 0.12 * inch, fill=1, stroke=0)

    # Distant Mars (bottom right)
    mars_x, mars_y = cx + 2.1 * inch, cy - 1.4 * inch
    c.setFillColor(HexColor("#F87171"))
    c.circle(mars_x, mars_y, 0.24 * inch, fill=1, stroke=0)

    # 6. Sparkle & Golden Stars around scene
    for sx, sy, sz in [
        (cx - 0.8 * inch, cy + 1.2 * inch, 7),
        (cx + 1.8 * inch, cy + 1.3 * inch, 9),
        (cx - 2.1 * inch, cy - 0.2 * inch, 6),
        (cx + 2.2 * inch, cy + 0.2 * inch, 8),
        (cx + 0.1 * inch, cy - 1.5 * inch, 6),
    ]:
        c.saveState()
        c.setFillColor(HexColor("#FDE047"))
        star = c.beginPath()
        star.moveTo(sx, sy + sz)
        star.curveTo(sx, sy, sx, sy, sx + sz, sy)
        star.curveTo(sx, sy, sx, sy, sx, sy - sz)
        star.curveTo(sx, sy, sx, sy, sx - sz, sy)
        star.curveTo(sx, sy, sx, sy, sx, sy + sz)
        c.drawPath(star, fill=1, stroke=0)
        c.restoreState()


def draw_cover(
    output_pdf_path: Path,
    title: str = "SOLAR SYSTEM EXPLORERS",
    subtitle: str = "Coloring Book for Kids Ages 4-6",
    author: str | None = None,
    publisher_name: str = "The Pivot Digital Publication",
    front_art_path: Path | None = None,
    thumbnail_paths: list[Path] | None = None,
    logo_path: Path | None = None,
    page_count: int = 32,
) -> Path:
    """Generate an Amazon KDP compliant full-wrap paperback cover PDF."""
    dims = calculate_cover_dimensions(page_count=page_count)
    width_pt = dims["total_width_in"] * inch
    height_pt = dims["total_height_in"] * inch

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf_path), pagesize=(width_pt, height_pt))

    # 1. Background (Rich Deep Space Navy)
    c.setFillColor(HexColor("#0B132B"))
    c.rect(0, 0, width_pt, height_pt, fill=1, stroke=0)

    # Decorative space stars / nebulae dots
    import random
    rng = random.Random(42)  # Stable star background
    c.setFillColor(white)
    for _ in range(120):
        sx = rng.uniform(0, width_pt)
        sy = rng.uniform(0, height_pt)
        sr = rng.uniform(0.6, 2.2)
        alpha = rng.uniform(0.3, 0.9)
        c.setFillAlpha(alpha)
        c.circle(sx, sy, sr, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # 2. Spine Area
    spine_x_pt = (dims["bleed_in"] + dims["trim_width_in"]) * inch
    spine_w_pt = dims["spine_width_in"] * inch
    c.setFillColor(HexColor("#1C2541"))
    c.rect(spine_x_pt, 0, spine_w_pt, height_pt, fill=1, stroke=0)

    # 3. FRONT COVER (Right half)
    front_center_x = (dims["front_left_in"] + dims["trim_width_in"] / 2.0) * inch

    # Title Banner / Badge Area
    c.setFillColor(HexColor("#FBBF24"))
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(front_center_x, height_pt - 1.6 * inch, title)

    # Subtitle
    c.setFillColor(HexColor("#E2E8F0"))
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(front_center_x, height_pt - 2.1 * inch, subtitle)

    # Age Badge
    c.setFillColor(HexColor("#2563EB"))
    badge_w, badge_h = 2.4 * inch, 0.45 * inch
    badge_x = front_center_x - badge_w / 2.0
    badge_y = height_pt - 2.8 * inch
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 8, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(front_center_x, badge_y + 0.12 * inch, "AGES 4 - 6  •  PRESCHOOL")

    # Front Artwork / Central Focal Illustration
    hero_center_y = height_pt - 5.6 * inch
    if front_art_path and front_art_path.exists():
        art_box_w = 5.2 * inch
        art_box_h = 5.2 * inch
        art_box_x = front_center_x - art_box_w / 2.0
        art_box_y = hero_center_y - art_box_h / 2.0

        c.drawImage(
            str(front_art_path),
            art_box_x,
            art_box_y,
            width=art_box_w,
            height=art_box_h,
            preserveAspectRatio=True,
            anchor="c",
            mask="auto",
        )
    else:
        # Draw rich, colorful space hero scene
        draw_front_hero_scene(c, front_center_x, hero_center_y)

    # Educational Feature Callout
    c.setFillColor(HexColor("#38BDF8"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(front_center_x, 1.4 * inch, "★ Big & Bold 3pt Lines  •  Single-Sided Pages  •  Bleed-Stop Backs ★")

    # Author and Publisher / Brand at bottom of Front Cover
    if author:
        c.setFillColor(HexColor("#CBD5E1"))
        c.setFont("Helvetica", 11)
        c.drawCentredString(front_center_x, 1.05 * inch, f"by {author}")
        c.setFillColor(HexColor("#94A3B8"))
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(front_center_x, 0.7 * inch, publisher_name)
    else:
        c.setFillColor(HexColor("#94A3B8"))
        c.setFont("Helvetica", 11)
        c.drawCentredString(front_center_x, 0.8 * inch, publisher_name)

    # 4. BACK COVER (Left half)
    back_center_x = (dims["back_left_in"] + dims["trim_width_in"] / 2.0) * inch

    # Back Header
    c.setFillColor(HexColor("#FBBF24"))
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(back_center_x, height_pt - 1.6 * inch, "Explore the Wonders of Space!")

    # Description Blurb
    blurb_lines = [
        "Ignite your child's curiosity with friendly, easy-to-color space adventures!",
        "Designed specifically for preschool and kindergarten artists (ages 4-6),",
        "each page features bold, continuous outlines tailored for little hands.",
        "",
        "✔ 15 Original Space Illustrations (Sun, Planets, Rockets & Astronauts)",
        "✔ Pure Black Bleed-Stop Reverse Pages to protect artwork from marker bleed",
        "✔ Certified 300-DPI Print-Ready Artwork on premium 8.5 x 11 inch paper",
        "✔ Aligned with early STEM & Next Generation Science Standards",
    ]
    c.setFillColor(HexColor("#E2E8F0"))
    c.setFont("Helvetica", 11)
    line_y = height_pt - 2.2 * inch
    for line in blurb_lines:
        c.drawString(back_center_x - 3.2 * inch, line_y, line)
        line_y -= 0.26 * inch

    # Interior Thumbnails Preview Grid (Parents love seeing what's inside!)
    if thumbnail_paths:
        c.setFillColor(HexColor("#38BDF8"))
        c.setFont("Helvetica-Bold", 13)
        c.drawString(back_center_x - 3.2 * inch, line_y - 0.1 * inch, "LOOK INSIDE:")
        thumb_y = line_y - 1.8 * inch
        thumb_w = 1.3 * inch
        thumb_h = 1.6 * inch
        spacing = 0.25 * inch
        start_tx = back_center_x - 3.2 * inch

        for idx, thumb in enumerate(thumbnail_paths[:4]):
            tx = start_tx + idx * (thumb_w + spacing)
            if thumb.exists():
                c.setFillColor(white)
                c.rect(tx - 2, thumb_y - 2, thumb_w + 4, thumb_h + 4, fill=1, stroke=0)
                c.drawImage(str(thumb), tx, thumb_y, width=thumb_w, height=thumb_h, preserveAspectRatio=True, anchor="c", mask="auto")

    # Barcode Area (Amazon KDP reserves 2.0 x 1.2 in at bottom-right of back cover)
    # 0.25 in from spine and bottom margin
    barcode_x = (dims["back_right_in"] - 2.2) * inch
    barcode_y = (dims["bleed_in"] + 0.25) * inch
    c.setFillColor(HexColor("#1C2541"))
    c.roundRect(barcode_x, barcode_y, 2.0 * inch, 1.2 * inch, 4, fill=1, stroke=1)
    c.setFillColor(HexColor("#64748B"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(barcode_x + 1.0 * inch, barcode_y + 0.55 * inch, "[ Amazon KDP Barcode Location ]")

    # Publisher Logo on Back Cover (Bottom Left)
    tmp_logo_path: Path | None = None
    if logo_path and logo_path.exists():
        if logo_path.suffix.lower() == ".svg":
            import tempfile
            logo_png_bytes = resvg_py.svg_to_bytes(svg_path=str(logo_path), width=700)
            with tempfile.NamedTemporaryFile("wb", suffix=".png", delete=False) as tmp_logo:
                tmp_logo.write(logo_png_bytes)
                tmp_logo_path = Path(tmp_logo.name)
            img_to_draw = tmp_logo_path
        else:
            img_to_draw = logo_path

        with Image.open(img_to_draw) as logo_im:
            lw, lh = logo_im.size
        aspect = lh / lw

        logo_x = (dims["back_left_in"] + 0.5) * inch

        if aspect > 0.5:
            # Vertical / Badge logo (e.g. Pivot Kids emblem)
            target_w = 1.6 * inch
            target_h = target_w * aspect
            logo_y = 0.45 * inch

            # Elegant white card so vibrant colors pop cleanly against space navy
            c.setFillColor(HexColor("#FFFFFF"))
            c.roundRect(
                logo_x - 0.08 * inch,
                logo_y - 0.08 * inch,
                target_w + 0.16 * inch,
                target_h + 0.16 * inch,
                8,
                fill=1,
                stroke=0,
            )
            c.drawImage(
                str(img_to_draw),
                logo_x,
                logo_y,
                width=target_w,
                height=target_h,
                preserveAspectRatio=True,
                anchor="sw",
                mask="auto",
            )
            # Imprint credit beside logo
            text_x = logo_x + target_w + 0.25 * inch
            c.setFillColor(HexColor("#E2E8F0"))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(text_x, logo_y + target_h / 2.0 + 4, "Published by")
            c.setFillColor(HexColor("#94A3B8"))
            c.setFont("Helvetica", 9)
            c.drawString(text_x, logo_y + target_h / 2.0 - 9, publisher_name)
        else:
            # Horizontal banner logo
            target_w = 2.4 * inch
            target_h = target_w * aspect
            logo_y = 0.7 * inch
            c.drawImage(
                str(img_to_draw),
                logo_x,
                logo_y,
                width=target_w,
                height=target_h,
                preserveAspectRatio=True,
                anchor="sw",
                mask="auto",
            )
    else:
        c.setFillColor(HexColor("#94A3B8"))
        c.setFont("Helvetica-Bold", 10)
        c.drawString((dims["back_left_in"] + 0.5) * inch, 0.8 * inch, publisher_name)

    c.save()
    if tmp_logo_path and tmp_logo_path.exists():
        try:
            tmp_logo_path.unlink()
        except OSError:
            pass
    return output_pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Destination path for cover PDF")
    parser.add_argument("--title", default="SOLAR SYSTEM EXPLORERS", help="Book title")
    parser.add_argument("--subtitle", default="Coloring Book for Kids Ages 4-6", help="Book subtitle")
    parser.add_argument("--publisher", default="The Pivot Digital Publication", help="Publisher name")
    parser.add_argument("--author", default=None, help="Author name to display on cover")
    parser.add_argument("--front-art", type=Path, help="Focal front cover artwork (PNG/JPG)")
    parser.add_argument("--thumbnails", type=Path, nargs="*", help="Interior preview thumbnails (up to 4)")
    parser.add_argument("--logo", type=Path, default=None, help="Publisher logo (PNG or SVG)")
    parser.add_argument("--logo-svg", type=Path, default=None, help="Publisher logo SVG (alias)")
    parser.add_argument("--page-count", type=int, default=32, help="Interior total page count")

    args = parser.parse_args()
    logo_file = args.logo or args.logo_svg
    if not logo_file:
        for cand in [
            Path("assets/logos/pivot_kids.png"),
            Path("assets/logo/pivot_kids.png"),
            Path("assets/logos/pivot_kids.svg"),
            Path("assets/logo/pivot_kids.svg"),
        ]:
            if cand.exists():
                logo_file = cand
                break

    out = draw_cover(
        output_pdf_path=args.output,
        title=args.title,
        subtitle=args.subtitle,
        author=args.author,
        publisher_name=args.publisher,
        front_art_path=args.front_art,
        thumbnail_paths=args.thumbnails or [],
        logo_path=logo_file if logo_file and logo_file.exists() else None,
        page_count=args.page_count,
    )
    print(f"Cover PDF generated successfully: {out}")
    return 0
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
