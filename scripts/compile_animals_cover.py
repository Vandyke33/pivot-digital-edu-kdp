"""Compile a flat, print-ready full paperback cover spread for 'My First Copy to Colour: Animals'."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
from typing import Any

from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.pdfgen import canvas
import resvg_py

# 12 Titles for the back cover 4x3 grid
SERIES_TITLES_12 = [
    {"title": "Alphabet", "color": "#EA580C", "accent": "#FACC15"},
    {"title": "Birds", "color": "#10B981", "accent": "#FACC15"},
    {"title": "Sports", "color": "#84CC16", "accent": "#FEF08A"},
    {"title": "Monsters", "color": "#D946EF", "accent": "#FDE047"},
    {"title": "Numbers", "color": "#991B1B", "accent": "#FACC15"},
    {"title": "Fruits", "color": "#0D9488", "accent": "#FACC15"},
    {"title": "Shapes", "color": "#FB7185", "accent": "#FDE047"},
    {"title": "Toys", "color": "#0284C7", "accent": "#FACC15"},
    {"title": "Flowers", "color": "#78350F", "accent": "#FACC15"},
    {"title": "Transport", "color": "#1D4ED8", "accent": "#F59E0B"},
    {"title": "Vegetables", "color": "#6B21A8", "accent": "#FACC15"},
    {"title": "Cartoons", "color": "#F59E0B", "accent": "#0F172A"},
]

# Paper thickness: 55# white paper (0.002252 in per page)
THICKNESS_PER_PAGE_IN = 0.002252
BLEED_IN = 0.125


def calculate_animals_cover_dimensions(
    trim_width_in: float = 8.5,
    trim_height_in: float = 11.0,
    page_count: int = 32,
    bleed_in: float = BLEED_IN,
    thickness_per_page: float = THICKNESS_PER_PAGE_IN,
) -> dict[str, float]:
    """Calculate exact KDP cover dimensions in inches."""
    spine_width_in = round(page_count * thickness_per_page, 4)
    total_width_in = round(2 * trim_width_in + spine_width_in + 2 * bleed_in, 4)
    total_height_in = round(trim_height_in + 2 * bleed_in, 4)

    back_left_in = bleed_in
    back_right_in = bleed_in + trim_width_in

    spine_left_in = back_right_in
    spine_right_in = spine_left_in + spine_width_in

    front_left_in = spine_right_in
    front_right_in = total_width_in - bleed_in

    return {
        "trim_width_in": trim_width_in,
        "trim_height_in": trim_height_in,
        "page_count": page_count,
        "bleed_in": bleed_in,
        "spine_width_in": spine_width_in,
        "total_width_in": total_width_in,
        "total_height_in": total_height_in,
        "back_left_in": back_left_in,
        "back_right_in": back_right_in,
        "spine_left_in": spine_left_in,
        "spine_right_in": spine_right_in,
        "front_left_in": front_left_in,
        "front_right_in": front_right_in,
    }


def draw_starburst(c: canvas.Canvas, cx: float, cy: float, r: float, color: str = "#FFF4CC") -> None:
    """Draw a whimsical 4-point starburst."""
    c.saveState()
    c.setFillColor(HexColor(color))
    p = c.beginPath()
    p.moveTo(cx, cy + r)
    p.curveTo(cx, cy, cx, cy, cx + r, cy)
    p.curveTo(cx, cy, cx, cy, cx, cy - r)
    p.curveTo(cx, cy, cx, cy, cx - r, cy)
    p.curveTo(cx, cy, cx, cy, cx, cy + r)
    c.drawPath(p, fill=1, stroke=0)
    c.restoreState()


def draw_crayon(
    c: canvas.Canvas,
    x: float,
    y: float,
    length: float,
    width: float,
    angle_deg: float,
    color_hex: str,
    label: str = "",
) -> None:
    """Draw a tilted wax crayon with paper wrapper and conical tip."""
    c.saveState()
    c.translate(x, y)
    c.rotate(angle_deg)

    # 1. Conical Wax Tip
    tip_len = width * 1.1
    c.setFillColor(HexColor(color_hex))
    tip = c.beginPath()
    tip.moveTo(length, -width / 2.0)
    tip.lineTo(length + tip_len, 0)
    tip.lineTo(length, width / 2.0)
    tip.close()
    c.drawPath(tip, fill=1, stroke=0)

    # 2. Main Wax Body
    c.rect(0, -width / 2.0, length, width, fill=1, stroke=0)

    # 3. Paper Wrapper (slightly contrasting band)
    wrap_start = length * 0.15
    wrap_len = length * 0.75
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFillAlpha(0.2)
    c.rect(wrap_start, -width / 2.0, wrap_len, width, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Decorative wrapper stripes
    c.setStrokeColor(HexColor("#000000"))
    c.setStrokeAlpha(0.25)
    c.setLineWidth(1)
    c.line(wrap_start + 4, -width / 2.0, wrap_start + 4, width / 2.0)
    c.line(wrap_start + wrap_len - 4, -width / 2.0, wrap_start + wrap_len - 4, width / 2.0)

    c.restoreState()


def draw_outlined_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: float,
    fill_color: str,
    outline_color: str,
    outline_width: float = 3.0,
    centered: bool = True,
) -> None:
    """Draw bold text with a thick outer outline."""
    c.saveState()
    c.setFont(font_name, font_size)

    # Draw outline by offsetting text slightly in 8 directions
    c.setFillColor(HexColor(outline_color))
    steps = 8
    radius = outline_width
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        if centered:
            c.drawCentredString(x + dx, y + dy, text)
        else:
            c.drawString(x + dx, y + dy, text)

    # Draw inner fill
    c.setFillColor(HexColor(fill_color))
    if centered:
        c.drawCentredString(x, y, text)
    else:
        c.drawString(x, y, text)
    c.restoreState()


def draw_global_background(c: canvas.Canvas, width_pt: float, height_pt: float) -> None:
    """Draw the rich coral-red to warm orange gradient and bottom grassy hills."""
    # 1. Base Coral-Red to Warm Orange Gradient simulation via fine horizontal bands
    top_color = (255, 76, 76)     # #FF4C4C (Vivid Coral-Red)
    bottom_color = (255, 138, 61) # #FF8A3D (Warm Sunlit Orange)

    bands = 60
    band_h = height_pt / bands
    for i in range(bands):
        t = i / float(bands - 1)
        r = int(bottom_color[0] + t * (top_color[0] - bottom_color[0]))
        g = int(bottom_color[1] + t * (top_color[1] - bottom_color[1]))
        b = int(bottom_color[2] + t * (top_color[2] - bottom_color[2]))
        c.setFillColorRGB(r / 255.0, g / 255.0, b / 255.0)
        c.rect(0, i * band_h, width_pt, band_h + 1, fill=1, stroke=0)

    # 2. Scattered Playful Starbursts and Paint Splatters
    import random
    rng = random.Random(101)  # Deterministic seed for reproducible layout
    for _ in range(45):
        sx = rng.uniform(0, width_pt)
        sy = rng.uniform(height_pt * 0.35, height_pt)
        sr = rng.uniform(4, 11)
        draw_starburst(c, sx, sy, sr, color="#FFF4CC")

    # Paint droplets
    c.setFillColor(HexColor("#FF6B4A"))
    for _ in range(35):
        dx = rng.uniform(0, width_pt)
        dy = rng.uniform(height_pt * 0.3, height_pt * 0.95)
        dr = rng.uniform(1.5, 4.0)
        c.circle(dx, dy, dr, fill=1, stroke=0)

    # 3. Continuous Rolling Green Grassy Hills along bottom edge
    # Midground hill (#22C55E)
    c.saveState()
    c.setFillColor(HexColor("#22C55E"))
    p1 = c.beginPath()
    p1.moveTo(0, 0)
    p1.lineTo(0, 1.8 * inch)
    p1.curveTo(4.0 * inch, 2.3 * inch, 8.0 * inch, 1.4 * inch, 12.0 * inch, 2.0 * inch)
    p1.curveTo(14.5 * inch, 2.4 * inch, 16.5 * inch, 1.7 * inch, width_pt, 2.1 * inch)
    p1.lineTo(width_pt, 0)
    p1.close()
    c.drawPath(p1, fill=1, stroke=0)

    # Foreground hill (#4ADE80)
    c.setFillColor(HexColor("#4ADE80"))
    p2 = c.beginPath()
    p2.moveTo(0, 0)
    p2.lineTo(0, 1.2 * inch)
    p2.curveTo(3.5 * inch, 0.8 * inch, 7.5 * inch, 1.6 * inch, 11.0 * inch, 1.0 * inch)
    p2.curveTo(14.0 * inch, 0.6 * inch, 16.0 * inch, 1.5 * inch, width_pt, 1.1 * inch)
    p2.lineTo(width_pt, 0)
    p2.close()
    c.drawPath(p2, fill=1, stroke=0)

    # Flowers and Ladybugs along the grassy hill
    # Tiny Daisies
    flower_xs = [0.8, 2.2, 3.8, 5.5, 7.0, 9.2, 11.5, 13.0, 14.8, 16.2]
    for fx_in in flower_xs:
        fx = fx_in * inch
        fy = 0.5 * inch + rng.uniform(0.1, 0.6) * inch
        c.setFillColor(white)
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            c.circle(fx + 4 * math.cos(rad), fy + 4 * math.sin(rad), 2.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#FACC15"))
        c.circle(fx, fy, 2.5, fill=1, stroke=0)

    # Cute Ladybugs
    ladybug_xs = [1.5, 6.2, 10.5, 15.5]
    for lx_in in ladybug_xs:
        lx = lx_in * inch
        ly = 0.45 * inch + rng.uniform(0.1, 0.4) * inch
        # Body (Red)
        c.setFillColor(HexColor("#EF4444"))
        c.circle(lx, ly, 4.0, fill=1, stroke=0)
        # Head (Black)
        c.setFillColor(HexColor("#000000"))
        c.circle(lx + 3.5, ly, 2.0, fill=1, stroke=0)
        # Spots
        c.circle(lx - 1, ly + 1.5, 0.8, fill=1, stroke=0)
        c.circle(lx - 1, ly - 1.5, 0.8, fill=1, stroke=0)

    c.restoreState()


def draw_mini_book_cover(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    theme_color: str,
    accent_color: str,
) -> None:
    """Draw a single miniature book cover card for the back cover 4x3 grid."""
    c.saveState()

    # White card base with subtle outline
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#CBD5E1"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)

    # Top Arched Banner in Theme Color
    banner_h = h * 0.32
    c.setFillColor(HexColor(theme_color))
    c.saveState()
    p = c.beginPath()
    p.moveTo(x, y + h - banner_h)
    p.lineTo(x, y + h)
    p.lineTo(x + w, y + h)
    p.lineTo(x + w, y + h - banner_h)
    p.curveTo(x + w * 0.7, y + h - banner_h - 3, x + w * 0.3, y + h - banner_h - 3, x, y + h - banner_h)
    p.close()
    c.clipPath(p, stroke=0)
    c.rect(x - 2, y + h - banner_h - 6, w + 4, banner_h + 10, fill=1, stroke=0)
    c.restoreState()

    # White stitched dashed line on banner
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(0.6)
    c.setDash([2, 2])
    c.line(x + 2, y + h - banner_h + 1, x + w - 2, y + h - banner_h + 1)
    c.setDash([])

    # "My First" tiny pill
    pill_w = w * 0.55
    pill_h = 7.5
    pill_x = x + (w - pill_w) / 2.0
    pill_y = y + h - 9.5
    c.setFillColor(HexColor("#FFF7ED"))
    c.roundRect(pill_x, pill_y, pill_w, pill_h, 3, fill=1, stroke=0)
    c.setFillColor(HexColor("#431407"))
    c.setFont("Helvetica-Bold", 4.5)
    c.drawCentredString(x + w / 2.0, pill_y + 2.0, "My First")

    # "Copy to Colour" tiny text
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 5.0)
    c.drawCentredString(x + w / 2.0, y + h - 16.5, "Copy to Colour")

    # Subject Title in Accent Color (Bolder & slightly larger)
    c.setFillColor(HexColor(accent_color))
    c.setFont("Helvetica-Bold", 7.0)
    c.drawCentredString(x + w / 2.0, y + h - 24.5, title)

    # 3 tiny crayons on left
    crayon_colors = ["#FBBF24", "#EF4444", "#38BDF8"]
    for idx, col in enumerate(crayon_colors):
        cy_y = y + h * 0.45 - idx * 5.0
        draw_crayon(c, x + 2, cy_y, length=12, width=2.2, angle_deg=25, color_hex=col)

    # Miniature sample card thumbnail in center-right
    card_w = w * 0.42
    card_h = h * 0.40
    card_x = x + w * 0.52
    card_y = y + 8
    c.setFillColor(HexColor("#F8FAFC"))
    c.setStrokeColor(HexColor("#E2E8F0"))
    c.setLineWidth(0.5)
    c.roundRect(card_x, card_y, card_w, card_h, 2, fill=1, stroke=1)

    # Little character doodle placeholder inside card
    c.setFillColor(HexColor(theme_color))
    c.circle(card_x + card_w * 0.5, card_y + card_h * 0.5, 4.0, fill=1, stroke=0)

    # Tiny green grass hill at base of book
    c.setFillColor(HexColor("#4ADE80"))
    p_base = c.beginPath()
    p_base.moveTo(x, y)
    p_base.lineTo(x, y + 4)
    p_base.curveTo(x + w * 0.5, y + 7, x + w * 0.8, y + 3, x + w, y + 5)
    p_base.lineTo(x + w, y)
    p_base.close()
    c.drawPath(p_base, fill=1, stroke=0)

    c.restoreState()


def draw_back_cover(
    c: canvas.Canvas,
    dims: dict[str, float],
    logo_path: Path | None = None,
) -> None:
    """Render the Back Cover (Left Third) with 4x3 grid, blurb, and barcode."""
    back_left_pt = dims["back_left_in"] * inch
    back_width_pt = dims["trim_width_in"] * inch
    center_x = back_left_pt + back_width_pt / 2.0

    # 1. Top Row: "THE PIVOT KIDS" logo on left, Blue Banner on right
    top_y = (dims["total_height_in"] - dims["bleed_in"] - 0.95) * inch

    # The Pivot Kids Logo Badge (Left)
    if logo_path and logo_path.exists():
        logo_w = 1.35 * inch
        logo_h = 1.45 * inch
        logo_x = back_left_pt + 0.5 * inch
        logo_y = top_y - 0.4 * inch

        # White pill card for logo
        c.setFillColor(HexColor("#FFFFFF"))
        c.roundRect(logo_x - 4, logo_y - 4, logo_w + 8, logo_h + 8, 8, fill=1, stroke=0)
        c.drawImage(str(logo_path), logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    # Blue Ribbon Banner: "TITLES IN THIS SERIES" (Center-Right)
    banner_w = 4.4 * inch
    banner_h = 0.42 * inch
    banner_x = center_x - banner_w / 2.0 + 0.6 * inch
    banner_y = top_y + 0.15 * inch

    c.saveState()
    c.setFillColor(HexColor("#0284C7"))  # Vivid Sky Blue
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 8, fill=1, stroke=0)

    # White scalloped / dashed border
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(1.2)
    c.setDash([4, 3])
    c.roundRect(banner_x + 2, banner_y + 2, banner_w - 4, banner_h - 4, 6, fill=0, stroke=1)

    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(banner_x + banner_w / 2.0, banner_y + 0.11 * inch, "★ TITLES IN THIS SERIES ★")
    c.restoreState()

    # 2. Centered 4x3 Grid of 12 Miniature Book Covers
    # Grid area parameters
    grid_start_x = back_left_pt + 0.65 * inch
    grid_start_y = top_y - 0.7 * inch
    card_w = 2.05 * inch
    card_h = 1.48 * inch
    gap_x = 0.42 * inch
    gap_y = 0.18 * inch

    for idx, item in enumerate(SERIES_TITLES_12):
        row = idx // 3  # 0, 1, 2, 3 (4 rows)
        col = idx % 3   # 0, 1, 2 (3 columns)

        cx = grid_start_x + col * (card_w + gap_x)
        cy = grid_start_y - row * (card_h + gap_y) - card_h

        draw_mini_book_cover(
            c,
            x=cx,
            y=cy,
            w=card_w,
            h=card_h,
            title=item["title"],
            theme_color=item["color"],
            accent_color=item["accent"],
        )

    # 3. Bottom Row: Marketing Pitch Blurb on Left, Barcode Box on Right
    blurb_x = back_left_pt + 0.6 * inch
    blurb_y = (dims["bleed_in"] + 1.25) * inch

    c.saveState()
    # Semi-translucent soft backdrop for crystal-clear readability
    c.setFillColor(HexColor("#991B1B"))
    c.setFillAlpha(0.25)
    c.roundRect(blurb_x - 8, blurb_y - 0.55 * inch - 6, 4.8 * inch, 1.15 * inch, 8, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(blurb_x, blurb_y, "A playful, easy coloring series designed for early learners")
    c.drawString(blurb_x, blurb_y - 0.20 * inch, "to copy, color, and play!")
    c.setFillColor(HexColor("#FEF08A"))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(blurb_x, blurb_y - 0.44 * inch, "★ Collector's Series of 15 Interactive Titles ★")

    # Publisher Copyright Notice
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica", 8.5)
    c.drawString(blurb_x, (dims["bleed_in"] + 0.35) * inch, "© The Pivot Digital Publications. All rights reserved.")
    c.restoreState()

    # White Amazon KDP Barcode Box Placeholder (Bottom-Right)
    # Amazon KDP reserves 2.0 x 1.2 in at bottom-right of back cover
    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    barcode_x = (dims["back_right_in"] - 2.3) * inch
    barcode_y = (dims["bleed_in"] + 0.3) * inch

    c.saveState()
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#CBD5E1"))
    c.setLineWidth(1)
    c.roundRect(barcode_x, barcode_y, barcode_w, barcode_h, 4, fill=1, stroke=1)
    c.setFillColor(HexColor("#64748B"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(barcode_x + barcode_w / 2.0, barcode_y + barcode_h / 2.0, "[ Amazon KDP Barcode Location ]")
    c.restoreState()


def draw_spine(c: canvas.Canvas, dims: dict[str, float]) -> None:
    """Render the Center Strip (Spine) with vertical typography."""
    spine_left_pt = dims["spine_left_in"] * inch
    spine_w_pt = dims["spine_width_in"] * inch
    height_pt = dims["total_height_in"] * inch

    c.saveState()
    # Spine background (matching coral-red)
    c.setFillColor(HexColor("#FF4C4C"))
    c.rect(spine_left_pt, 0, spine_w_pt, height_pt, fill=1, stroke=0)

    # Vertical text rotated 90 degrees (running from top to bottom)
    c.translate(spine_left_pt + spine_w_pt / 2.0, height_pt / 2.0)
    c.rotate(-90)

    # Spine text: "THE PIVOT KIDS | My First Copy to Colour: Animals"
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 6.0)
    c.drawCentredString(0, -2, "THE PIVOT KIDS   •   My First Copy to Colour: Animals")

    c.restoreState()


def draw_front_cover(
    c: canvas.Canvas,
    dims: dict[str, float],
    logo_path: Path | None = None,
    hero_art_path: Path | None = None,
    card_color_thumb: Path | None = None,
    card_bw_outline: Path | None = None,
) -> None:
    """Render the Front Cover (Right Third) matching GoWoo reference layout."""
    front_left_pt = dims["front_left_in"] * inch
    front_width_pt = dims["trim_width_in"] * inch
    center_x = front_left_pt + front_width_pt / 2.0
    height_pt = dims["total_height_in"] * inch

    # 1. TOP HEADER ARCH: Coral-Red curved ribbon with stitched white border
    header_h = 3.2 * inch
    arch_bottom = height_pt - header_h

    c.saveState()
    # Arched header path
    c.setFillColor(HexColor("#FF4C4C"))
    p_arch = c.beginPath()
    p_arch.moveTo(front_left_pt - 2, height_pt + 2)
    p_arch.lineTo(front_left_pt + front_width_pt + 2, height_pt + 2)
    p_arch.lineTo(front_left_pt + front_width_pt + 2, arch_bottom)
    p_arch.curveTo(
        front_left_pt + front_width_pt * 0.7, arch_bottom - 0.45 * inch,
        front_left_pt + front_width_pt * 0.3, arch_bottom - 0.45 * inch,
        front_left_pt - 2, arch_bottom,
    )
    p_arch.close()
    c.drawPath(p_arch, fill=1, stroke=0)

    # White Hand-Drawn Dotted / Stitched Border along the bottom curve
    c.setStrokeColor(HexColor("#FFFFFF"))
    c.setLineWidth(2.2)
    c.setDash([6, 5])
    p_stitch = c.beginPath()
    p_stitch.moveTo(front_left_pt + 4, arch_bottom + 4)
    p_stitch.curveTo(
        front_left_pt + front_width_pt * 0.7, arch_bottom - 0.42 * inch + 4,
        front_left_pt + front_width_pt * 0.3, arch_bottom - 0.42 * inch + 4,
        front_left_pt + front_width_pt - 4, arch_bottom + 4,
    )
    c.drawPath(p_stitch, stroke=1, fill=0)
    c.setDash([])
    c.restoreState()

    # 2. TOP BRAND LOGO & "My First" BADGE
    # "THE PIVOT KIDS" Brand Logo (Top Center)
    if logo_path and logo_path.exists():
        logo_w = 1.35 * inch
        logo_h = 1.45 * inch
        logo_x = center_x - logo_w / 2.0
        logo_y = height_pt - 1.55 * inch

        # White pill badge behind logo so it pops cleanly
        c.setFillColor(HexColor("#FFFFFF"))
        c.roundRect(logo_x - 6, logo_y - 6, logo_w + 12, logo_h + 12, 10, fill=1, stroke=0)
        c.drawImage(str(logo_path), logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    # "My First" Curved Pill Badge (Below logo)
    badge_w = 2.4 * inch
    badge_h = 0.45 * inch
    badge_x = center_x - badge_w / 2.0
    badge_y = height_pt - 1.95 * inch
    c.setFillColor(HexColor("#FFF7ED"))
    c.roundRect(badge_x, badge_y, badge_w, badge_h, 12, fill=1, stroke=0)
    c.setFillColor(HexColor("#3F1D0B"))
    c.setFont("Helvetica-Bold", 17)
    c.drawCentredString(center_x, badge_y + 0.1 * inch, "My First")

    # 3. MAIN TITLES: "Copy to Colour" & "Animals"
    # Huge rounded white lettering with dark blue outline: "Copy to Colour"
    title1_y = height_pt - 2.65 * inch
    draw_outlined_text(
        c,
        text="Copy to Colour",
        x=center_x,
        y=title1_y,
        font_name="Helvetica-Bold",
        font_size=42,
        fill_color="#FFFFFF",
        outline_color="#0F294A",
        outline_width=4.0,
        centered=True,
    )

    # Giant yellow bubble lettering with dark outline: "Animals"
    title2_y = height_pt - 3.35 * inch
    draw_outlined_text(
        c,
        text="Animals",
        x=center_x,
        y=title2_y,
        font_name="Helvetica-Bold",
        font_size=48,
        fill_color="#FACC15",
        outline_color="#713F12",
        outline_width=4.5,
        centered=True,
    )

    # 4. LEFT CRAYONS TRIO: Yellow, Red, Orange pointing inward at an angle
    crayons_start_x = front_left_pt + 0.1 * inch
    crayons_base_y = height_pt - 4.15 * inch
    crayons_data = [
        {"color": "#FDE047", "angle": -25, "y_off": 0.0},
        {"color": "#EF4444", "angle": -25, "y_off": -0.45 * inch},
        {"color": "#FB923C", "angle": -25, "y_off": -0.90 * inch},
    ]
    for cr in crayons_data:
        draw_crayon(
            c,
            x=crayons_start_x,
            y=crayons_base_y + cr["y_off"],
            length=1.7 * inch,
            width=0.28 * inch,
            angle_deg=cr["angle"],
            color_hex=cr["color"],
        )

    # 5. INSET "BEFORE & AFTER" ACTIVITY CARD: Labeled "TIGER"
    # White rounded rectangle with color thumbnail on left and B&W outline on right
    card_w = 2.9 * inch
    card_h = 3.6 * inch
    card_x = front_left_pt + front_width_pt - card_w - 0.7 * inch
    card_y = height_pt - 7.5 * inch

    c.saveState()
    # White card shadow & base
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#94A3B8"))
    c.setLineWidth(1.2)
    c.roundRect(card_x, card_y, card_w, card_h, 12, fill=1, stroke=1)

    # Header label pill: "TIGER"
    pill_label_w = 1.3 * inch
    pill_label_h = 0.28 * inch
    pill_label_x = card_x + (card_w - pill_label_w) / 2.0
    pill_label_y = card_y + card_h - 0.35 * inch
    c.setFillColor(HexColor("#EA580C"))  # Vivid Orange
    c.roundRect(pill_label_x, pill_label_y, pill_label_w, pill_label_h, 6, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(card_x + card_w / 2.0, pill_label_y + 0.07 * inch, "TIGER")

    # Inset Images inside the card:
    # Left: Full-Color Thumbnail
    thumb_box_w = 1.15 * inch
    thumb_box_h = 1.55 * inch
    thumb_box_x = card_x + 0.15 * inch
    thumb_box_y = card_y + 0.9 * inch

    if card_color_thumb and card_color_thumb.exists():
        c.drawImage(str(card_color_thumb), thumb_box_x, thumb_box_y, width=thumb_box_w, height=thumb_box_h, preserveAspectRatio=True, mask="auto")
    else:
        # Placeholder color indicator
        c.setFillColor(HexColor("#F97316"))
        c.roundRect(thumb_box_x, thumb_box_y, thumb_box_w, thumb_box_h, 4, fill=1, stroke=0)

    c.setFillColor(HexColor("#64748B"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(thumb_box_x + thumb_box_w / 2.0, thumb_box_y - 12, "Color Guide")

    # Right: Black & White Coloring Outline
    outline_box_w = 1.25 * inch
    outline_box_h = 1.7 * inch
    outline_box_x = card_x + card_w - outline_box_w - 0.15 * inch
    outline_box_y = card_y + 0.8 * inch

    if card_bw_outline and card_bw_outline.exists():
        c.drawImage(str(card_bw_outline), outline_box_x, outline_box_y, width=outline_box_w, height=outline_box_h, preserveAspectRatio=True, mask="auto")
    else:
        # Outline placeholder
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#000000"))
        c.setLineWidth(1)
        c.roundRect(outline_box_x, outline_box_y, outline_box_w, outline_box_h, 4, fill=1, stroke=1)

    c.setFillColor(HexColor("#0284C7"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(outline_box_x + outline_box_w / 2.0, outline_box_y - 12, "Color Me!")

    c.restoreState()

    # 6. FOREGROUND HERO CHARACTERS: Cute Cartoon Tiger Cub & Monkey on Grass
    if hero_art_path and hero_art_path.exists():
        hero_w = 4.8 * inch
        hero_h = 4.8 * inch
        hero_x = front_left_pt + 0.3 * inch
        hero_y = (dims["bleed_in"] + 0.4) * inch
        c.drawImage(str(hero_art_path), hero_x, hero_y, width=hero_w, height=hero_h, preserveAspectRatio=True, mask="auto")


def draw_animals_cover_spread(
    output_pdf_path: Path,
    page_count: int = 32,
    logo_path: Path | None = None,
    hero_art_path: Path | None = None,
    card_color_thumb: Path | None = None,
    card_bw_outline: Path | None = None,
) -> Path:
    """Generate the flat, print-ready full paperback cover spread PDF."""
    dims = calculate_animals_cover_dimensions(page_count=page_count)
    width_pt = dims["total_width_in"] * inch
    height_pt = dims["total_height_in"] * inch

    output_pdf_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_pdf_path), pagesize=(width_pt, height_pt))

    # 1. Global Gradient Background & Grassy Landscape
    draw_global_background(c, width_pt, height_pt)

    # 2. Back Cover (Left Third)
    draw_back_cover(c, dims, logo_path=logo_path)

    # 3. Spine (Center Strip)
    draw_spine(c, dims)

    # 4. Front Cover (Right Third)
    draw_front_cover(
        c,
        dims,
        logo_path=logo_path,
        hero_art_path=hero_art_path,
        card_color_thumb=card_color_thumb,
        card_bw_outline=card_bw_outline,
    )

    c.save()
    return output_pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("local_builds/animals/v1.0-core/animals-cover-spread.pdf"), help="Destination PDF path")
    parser.add_argument("--page-count", type=int, default=32, help="Book page count for spine calculation")
    parser.add_argument("--logo", type=Path, default=Path("assets/logos/pivot_kids.png"), help="Logo PNG/SVG")
    parser.add_argument("--hero-art", type=Path, default=Path("local_builds/animals/assets/tiger_monkey_transparent.png"), help="Hero characters PNG")
    parser.add_argument("--card-color", type=Path, default=Path("local_builds/animals/assets/tiger_color_thumb.png"), help="Activity card color guide")
    parser.add_argument("--card-outline", type=Path, default=Path("local_builds/animals/assets/tiger_outline.png"), help="Activity card B&W outline")

    args = parser.parse_args()

    out = draw_animals_cover_spread(
        output_pdf_path=args.output,
        page_count=args.page_count,
        logo_path=args.logo if args.logo.exists() else None,
        hero_art_path=args.hero_art if args.hero_art.exists() else None,
        card_color_thumb=args.card_color if args.card_color.exists() else None,
        card_bw_outline=args.card_outline if args.card_outline.exists() else None,
    )
    print(f"[OK] Full Animals Cover Spread generated successfully: {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
