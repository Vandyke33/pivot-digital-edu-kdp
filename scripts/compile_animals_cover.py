"""Compile a flat, print-ready full paperback cover spread for 'My First Copy to Color: Animals'."""

from __future__ import annotations

import argparse
import math
import os
from pathlib import Path
from typing import Any

from PIL import Image
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
import resvg_py

# 12 distinct miniature titles for the back cover 4x3 grid
SERIES_TITLES_12 = [
    {"title": "Alphabet", "color": "#EA580C", "accent": "#FDE047", "vol": 1},
    {"title": "Birds", "color": "#059669", "accent": "#FDE047", "vol": 2},
    {"title": "Sports", "color": "#65A30D", "accent": "#FEF08A", "vol": 3},
    {"title": "Monsters", "color": "#DB2777", "accent": "#FDE047", "vol": 4},
    {"title": "Numbers", "color": "#881337", "accent": "#FACC15", "vol": 5},
    {"title": "Fruits", "color": "#0D9488", "accent": "#FEF08A", "vol": 6},
    {"title": "Shapes", "color": "#E11D48", "accent": "#FDE047", "vol": 7},
    {"title": "Toys", "color": "#0284C7", "accent": "#FEF08A", "vol": 8},
    {"title": "Flowers", "color": "#78350F", "accent": "#FDE047", "vol": 9},
    {"title": "Transport", "color": "#1D4ED8", "accent": "#FBBF24", "vol": 10},
    {"title": "Vegetables", "color": "#6B21A8", "accent": "#FDE047", "vol": 11},
    {"title": "Cartoons", "color": "#D97706", "accent": "#FFFFFF", "vol": 12},
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


def draw_3d_title(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font_name: str,
    font_size: float,
    fill_hex: str,
    outline_hex: str,
    outline_width: float = 4.0,
    extrusion_depth: int = 5,
    extrusion_hex: str = "#000000",
    secondary_border_hex: str | None = None,
    secondary_width: float = 1.5,
) -> None:
    """Draw chunky 3D bouncing bubble typography with volumetric extrusion and multi-layer borders."""
    w = stringWidth(text, font_name, font_size)
    ox = x - w / 2.0

    # 1. 3D Volumetric Extrusion (stacked downward vector passes)
    c.saveState()
    c.setLineWidth(outline_width)
    c.setLineJoin(1)  # Round join
    c.setLineCap(1)   # Round cap
    for d in range(extrusion_depth, 0, -1):
        ts = c.beginText(ox, y - d)
        ts.setFont(font_name, font_size)
        ts.setTextRenderMode(2)  # Fill and stroke
        ts.setFillColor(HexColor(extrusion_hex))
        ts.setStrokeColor(HexColor(extrusion_hex))
        ts.textOut(text)
        c.drawText(ts)
    c.restoreState()

    # 2. Outer Contour / Thick Border
    c.saveState()
    c.setLineWidth(outline_width)
    c.setLineJoin(1)
    c.setLineCap(1)
    t_out = c.beginText(ox, y)
    t_out.setFont(font_name, font_size)
    t_out.setTextRenderMode(2)
    t_out.setFillColor(HexColor(outline_hex))
    t_out.setStrokeColor(HexColor(outline_hex))
    t_out.textOut(text)
    c.drawText(t_out)
    c.restoreState()

    # 3. Secondary Contrasting Inner Border (if provided)
    if secondary_border_hex:
        c.saveState()
        c.setLineWidth(secondary_width)
        c.setLineJoin(1)
        c.setLineCap(1)
        t_sec = c.beginText(ox, y)
        t_sec.setFont(font_name, font_size)
        t_sec.setTextRenderMode(1)  # Stroke only
        t_sec.setStrokeColor(HexColor(secondary_border_hex))
        t_sec.textOut(text)
        c.drawText(t_sec)
        c.restoreState()

    # 4. Pure Inner Fill (clean top layer)
    c.saveState()
    t_fill = c.beginText(ox, y)
    t_fill.setFont(font_name, font_size)
    t_fill.setTextRenderMode(0)  # Fill only
    t_fill.setFillColor(HexColor(fill_hex))
    t_fill.textOut(text)
    c.drawText(t_fill)
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
    outline_width: float = 3.5,
    shadow_color: str | None = None,
    shadow_offset: tuple[float, float] = (0.0, -3.5),
    centered: bool = True,
) -> None:
    """Draw bold text with a silky smooth, native vector PDF outline and optional drop shadow."""
    w = stringWidth(text, font_name, font_size)
    ox = x - w / 2.0 if centered else x

    # 1. Subtle drop shadow
    if shadow_color:
        c.saveState()
        c.setLineWidth(outline_width)
        c.setLineJoin(1)
        c.setLineCap(1)
        ts = c.beginText(ox + shadow_offset[0], y + shadow_offset[1])
        ts.setFont(font_name, font_size)
        ts.setTextRenderMode(2)
        ts.setFillColor(HexColor(shadow_color))
        ts.setStrokeColor(HexColor(shadow_color))
        ts.textOut(text)
        c.drawText(ts)
        c.restoreState()

    # 2. Main text with native vector stroke & fill
    c.saveState()
    c.setLineWidth(outline_width)
    c.setLineJoin(1)
    c.setLineCap(1)
    t = c.beginText(ox, y)
    t.setFont(font_name, font_size)
    t.setTextRenderMode(2)
    t.setFillColor(HexColor(fill_color))
    t.setStrokeColor(HexColor(outline_color))
    t.textOut(text)
    c.drawText(t)
    c.restoreState()


def draw_global_background(c: canvas.Canvas, width_pt: float, height_pt: float) -> None:
    """Draw rich coral-red to warm orange gradient, starbursts, paint droplets, decorative dotted trails, and hills."""
    # 1. Coral-Red (#FF4949) to Warm Orange (#FF8A3D) Gradient
    top_color = (255, 73, 73)      # #FF4949 (Rich Coral-Red)
    bottom_color = (255, 138, 61)  # #FF8A3D (Warm Orange)

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

    # 3. Playful White Dotted Decorative Curved Trails
    c.saveState()
    c.setStrokeColor(white)
    c.setStrokeAlpha(0.40)
    c.setLineWidth(1.8)
    c.setDash([4, 6])

    p_trail1 = c.beginPath()
    p_trail1.moveTo(0.8 * inch, height_pt - 1.2 * inch)
    p_trail1.curveTo(3.2 * inch, height_pt - 0.7 * inch, 5.8 * inch, height_pt - 1.8 * inch, 8.2 * inch, height_pt - 1.3 * inch)
    c.drawPath(p_trail1, stroke=1, fill=0)

    p_trail2 = c.beginPath()
    p_trail2.moveTo(9.2 * inch, height_pt - 1.0 * inch)
    p_trail2.curveTo(11.8 * inch, height_pt - 1.7 * inch, 14.5 * inch, height_pt - 0.8 * inch, 16.8 * inch, height_pt - 1.4 * inch)
    c.drawPath(p_trail2, stroke=1, fill=0)
    c.restoreState()

    # 4. Continuous Rolling Green Grassy Hills along bottom edge
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
        c.setFillColor(HexColor("#EF4444"))
        c.circle(lx, ly, 4.0, fill=1, stroke=0)
        c.setFillColor(HexColor("#000000"))
        c.circle(lx + 3.5, ly, 2.0, fill=1, stroke=0)
        c.circle(lx - 1, ly + 1.5, 0.8, fill=1, stroke=0)
        c.circle(lx - 1, ly - 1.5, 0.8, fill=1, stroke=0)

    c.restoreState()


def draw_thumb_art(c: canvas.Canvas, subject_idx: int, cx: float, cy: float, sz: float) -> None:
    """Draw distinct, recognizable cartoon vector artwork for each of the 12 series covers."""
    c.saveState()
    if subject_idx == 0:  # Alphabet: A B C blocks
        c.setFillColor(HexColor("#EF4444"))
        c.roundRect(cx - 15, cy - 9, 13, 13, 2, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 9); c.drawCentredString(cx - 8.5, cy - 7, "A")
        c.setFillColor(HexColor("#3B82F6"))
        c.roundRect(cx + 2, cy - 9, 13, 13, 2, fill=1, stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 9); c.drawCentredString(cx + 8.5, cy - 7, "B")
        c.setFillColor(HexColor("#FACC15"))
        c.roundRect(cx - 6.5, cy + 3, 13, 13, 2, fill=1, stroke=0)
        c.setFillColor(HexColor("#1E293B")); c.setFont("Helvetica-Bold", 9); c.drawCentredString(cx, cy + 5, "C")

    elif subject_idx == 1:  # Birds: Cute parrot
        c.setFillColor(HexColor("#10B981"))
        c.ellipse(cx - 9, cy - 13, cx + 7, cy + 9, fill=1, stroke=0)
        c.setFillColor(HexColor("#EF4444"))
        c.circle(cx - 2, cy + 5, 7.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#F59E0B"))
        p = c.beginPath(); p.moveTo(cx - 8, cy + 6); p.lineTo(cx - 15, cy + 3); p.lineTo(cx - 8, cy + 0); p.close()
        c.drawPath(p, fill=1, stroke=0)
        c.setFillColor(white); c.circle(cx - 4, cy + 7, 2.8, fill=1, stroke=0)
        c.setFillColor(HexColor("#000000")); c.circle(cx - 4.5, cy + 7, 1.4, fill=1, stroke=0)
        c.setFillColor(HexColor("#3B82F6"))
        p_w = c.beginPath(); p_w.moveTo(cx - 2, cy + 1); p_w.curveTo(cx + 7, cy + 3, cx + 11, cy - 8, cx + 3, cy - 10); p_w.close()
        c.drawPath(p_w, fill=1, stroke=0)

    elif subject_idx == 2:  # Sports: Soccer & basketball
        c.setFillColor(white); c.setStrokeColor(HexColor("#0F172A")); c.setLineWidth(1)
        c.circle(cx - 6, cy, 10.5, fill=1, stroke=1)
        c.setFillColor(HexColor("#0F172A"))
        c.circle(cx - 6, cy, 3.5, fill=1, stroke=0)
        for ang in [0, 72, 144, 216, 288]:
            rad = math.radians(ang)
            c.circle(cx - 6 + 6.5 * math.cos(rad), cy + 6.5 * math.sin(rad), 1.8, fill=1, stroke=0)
        c.setFillColor(HexColor("#EA580C"))
        c.circle(cx + 8, cy - 4, 7.5, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#7C2D12")); c.setLineWidth(0.8)
        c.line(cx + 1, cy - 4, cx + 15, cy - 4)

    elif subject_idx == 3:  # Monsters: Fuzzy blue monster
        c.setFillColor(HexColor("#38BDF8"))
        c.roundRect(cx - 11, cy - 11, 22, 22, 7, fill=1, stroke=0)
        c.setFillColor(HexColor("#FDE047"))
        p_h1 = c.beginPath(); p_h1.moveTo(cx - 8, cy + 9); p_h1.lineTo(cx - 12, cy + 16); p_h1.lineTo(cx - 4, cy + 10); p_h1.close(); c.drawPath(p_h1, fill=1, stroke=0)
        p_h2 = c.beginPath(); p_h2.moveTo(cx + 8, cy + 9); p_h2.lineTo(cx + 12, cy + 16); p_h2.lineTo(cx + 4, cy + 10); p_h2.close(); c.drawPath(p_h2, fill=1, stroke=0)
        c.setFillColor(white); c.circle(cx - 4.5, cy + 3, 4.5, fill=1, stroke=0); c.circle(cx + 4.5, cy + 3, 4.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#0F172A")); c.circle(cx - 3.8, cy + 3, 1.8, fill=1, stroke=0); c.circle(cx + 3.8, cy + 3, 1.8, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#0F172A")); c.setLineWidth(1.1)
        c.arc(cx - 5, cy - 8, cx + 5, cy - 2, 190, 160)
        c.setFillColor(white); c.rect(cx - 1.8, cy - 5.5, 2.8, 2.8, fill=1, stroke=0)

    elif subject_idx == 4:  # Numbers: Giraffe & 1 2 3
        c.setFillColor(HexColor("#FACC15"))
        c.circle(cx - 6, cy + 5, 7.5, fill=1, stroke=0)
        c.rect(cx - 8, cy - 11, 5.5, 14, fill=1, stroke=0)
        c.circle(cx - 9, cy + 13, 1.8, fill=1, stroke=0); c.circle(cx - 3, cy + 13, 1.8, fill=1, stroke=0)
        c.setFillColor(HexColor("#92400E"))
        c.circle(cx - 5, cy - 2, 1.8, fill=1, stroke=0); c.circle(cx - 6, cy - 7, 1.6, fill=1, stroke=0)
        c.circle(cx - 7, cy + 6, 1.1, fill=1, stroke=0)
        c.setFillColor(HexColor("#DC2626")); c.setFont("Helvetica-Bold", 10); c.drawString(cx + 3, cy + 4, "1")
        c.setFillColor(HexColor("#2563EB")); c.drawString(cx + 6, cy - 4, "2")
        c.setFillColor(HexColor("#16A34A")); c.drawString(cx + 4, cy - 12, "3")

    elif subject_idx == 5:  # Fruits: Pineapple & banana
        c.setFillColor(HexColor("#F59E0B"))
        c.ellipse(cx - 11, cy - 11, cx + 1, cy + 7, fill=1, stroke=0)
        c.setFillColor(HexColor("#16A34A"))
        p_c = c.beginPath(); p_c.moveTo(cx - 8, cy + 5); p_c.lineTo(cx - 11, cy + 15); p_c.lineTo(cx - 5, cy + 10); p_c.lineTo(cx - 2, cy + 16); p_c.lineTo(cx + 1, cy + 7); p_c.close()
        c.drawPath(p_c, fill=1, stroke=0)
        c.setFillColor(HexColor("#FACC15"))
        p_b = c.beginPath(); p_b.moveTo(cx + 2, cy + 4); p_b.curveTo(cx + 13, cy + 5, cx + 15, cy - 8, cx + 4, cy - 11); p_b.curveTo(cx + 11, cy - 6, cx + 9, cy + 1, cx + 2, cy + 4); p_b.close()
        c.drawPath(p_b, fill=1, stroke=0)

    elif subject_idx == 6:  # Shapes: Star with kawaii face
        c.setFillColor(HexColor("#FACC15"))
        p_s = c.beginPath()
        for i in range(10):
            r = 13 if i % 2 == 0 else 5.5
            ang = math.radians(i * 36 - 90)
            px = cx + r * math.cos(ang); py = cy + r * math.sin(ang)
            if i == 0: p_s.moveTo(px, py)
            else: p_s.lineTo(px, py)
        p_s.close(); c.drawPath(p_s, fill=1, stroke=0)
        c.setFillColor(HexColor("#0F172A"))
        c.circle(cx - 3.5, cy, 1.4, fill=1, stroke=0); c.circle(cx + 3.5, cy, 1.4, fill=1, stroke=0)
        c.arc(cx - 2.5, cy - 4.5, cx + 2.5, cy - 0.5, 190, 160)

    elif subject_idx == 7:  # Toys: Teddy bear
        c.setFillColor(HexColor("#92400E"))
        c.circle(cx - 7.5, cy + 7.5, 3.8, fill=1, stroke=0); c.circle(cx + 7.5, cy + 7.5, 3.8, fill=1, stroke=0)
        c.circle(cx, cy + 2.5, 8.5, fill=1, stroke=0)
        c.circle(cx, cy - 7.5, 9.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#FDE68A"))
        c.circle(cx, cy + 0.5, 4.2, fill=1, stroke=0)
        c.circle(cx, cy - 7.5, 5.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#000000"))
        c.circle(cx - 2.8, cy + 3.5, 1.1, fill=1, stroke=0); c.circle(cx + 2.8, cy + 3.5, 1.1, fill=1, stroke=0)
        c.circle(cx, cy + 1.5, 1.4, fill=1, stroke=0)

    elif subject_idx == 8:  # Flowers: Cheerful sunflower
        c.setFillColor(HexColor("#FACC15"))
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            c.circle(cx + 9.5 * math.cos(rad), cy + 2 + 9.5 * math.sin(rad), 4.2, fill=1, stroke=0)
        c.setFillColor(HexColor("#78350F"))
        c.circle(cx, cy + 2, 7.5, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#16A34A")); c.setLineWidth(2.2)
        c.line(cx, cy - 5.5, cx, cy - 15)

    elif subject_idx == 9:  # Transport: Cute red car
        c.setFillColor(HexColor("#EF4444"))
        p_car = c.beginPath()
        p_car.moveTo(cx - 14, cy - 5.5)
        p_car.lineTo(cx - 14, cy - 1)
        p_car.lineTo(cx - 7, cy + 1)
        p_car.lineTo(cx - 3.5, cy + 7.5)
        p_car.lineTo(cx + 6.5, cy + 7.5)
        p_car.lineTo(cx + 10.5, cy + 1)
        p_car.lineTo(cx + 15, cy - 1)
        p_car.lineTo(cx + 15, cy - 5.5)
        p_car.close(); c.drawPath(p_car, fill=1, stroke=0)
        c.setFillColor(HexColor("#BAE6FD"))
        c.rect(cx - 2.5, cy + 1, 8.5, 5.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#0F172A"))
        c.circle(cx - 8.5, cy - 5.5, 4.2, fill=1, stroke=0); c.circle(cx + 8.5, cy - 5.5, 4.2, fill=1, stroke=0)
        c.setFillColor(HexColor("#CBD5E1"))
        c.circle(cx - 8.5, cy - 5.5, 1.8, fill=1, stroke=0); c.circle(cx + 8.5, cy - 5.5, 1.8, fill=1, stroke=0)

    elif subject_idx == 10:  # Vegetables: Carrot & eggplant
        c.setFillColor(HexColor("#EA580C"))
        p_crt = c.beginPath(); p_crt.moveTo(cx - 11, cy + 5); p_crt.lineTo(cx - 4, cy + 7); p_crt.lineTo(cx - 7, cy - 13); p_crt.close()
        c.drawPath(p_crt, fill=1, stroke=0)
        c.setFillColor(HexColor("#16A34A"))
        c.circle(cx - 7, cy + 10, 3.2, fill=1, stroke=0)
        c.setFillColor(HexColor("#7E22CE"))
        c.ellipse(cx + 2, cy - 11, cx + 13, cy + 3.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#16A34A"))
        c.rect(cx + 5.5, cy + 1.5, 3.8, 5.5, fill=1, stroke=0)

    elif subject_idx == 11:  # Cartoons: Police officer
        c.setFillColor(HexColor("#FED7AA"))
        c.circle(cx, cy, 7.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#1E3A8A"))
        c.rect(cx - 7.5, cy - 11, 15, 6.5, fill=1, stroke=0)
        p_cap = c.beginPath(); p_cap.moveTo(cx - 9.5, cy + 4.5); p_cap.lineTo(cx - 8.5, cy + 12); p_cap.lineTo(cx + 8.5, cy + 12); p_cap.lineTo(cx + 9.5, cy + 4.5); p_cap.close()
        c.drawPath(p_cap, fill=1, stroke=0)
        c.setFillColor(HexColor("#FACC15"))
        c.circle(cx, cy + 10, 2.2, fill=1, stroke=0)
        c.setFillColor(HexColor("#0F172A"))
        c.circle(cx - 2.8, cy + 1, 1.1, fill=1, stroke=0); c.circle(cx + 2.8, cy + 1, 1.1, fill=1, stroke=0)
        c.setStrokeColor(HexColor("#0F172A")); c.setLineWidth(0.8)
        c.arc(cx - 2.8, cy - 3.8, cx + 2.8, cy, 190, 160)

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
    vol_num: int = 1,
    subject_idx: int = 0,
) -> None:
    """Draw a single miniature children's book cover with Vol # badge and recognizable cartoon art."""
    c.saveState()

    # White card base with subtle outline and soft shadow
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#CBD5E1"))
    c.setLineWidth(0.8)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)

    # Top Arched Banner in Theme Color
    banner_h = h * 0.35
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

    # Tiny "VOL. #" Badge in top-right corner
    vol_w = 21
    vol_h = 7.5
    vol_x = x + w - vol_w - 2.5
    vol_y = y + h - vol_h - 2.5
    c.setFillColor(HexColor("#FFFFFF"))
    c.roundRect(vol_x, vol_y, vol_w, vol_h, 2.5, fill=1, stroke=0)
    c.setFillColor(HexColor(theme_color))
    c.setFont("Helvetica-Bold", 4.5)
    c.drawCentredString(vol_x + vol_w / 2.0, vol_y + 1.8, f"Vol. {vol_num}")

    # Top brand / series: "Copy to Color"
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 5.0)
    c.drawString(x + 4, y + h - 8.5, "Copy to Color")

    # Subject Title in Accent Color (Bolder & readable)
    c.setFillColor(HexColor(accent_color))
    c.setFont("Helvetica-Bold", 7.2)
    c.drawCentredString(x + w / 2.0, y + h - 23.0, title)

    # 3 tiny crayons on left edge (Yellow, Red, Blue)
    crayon_colors = ["#FBBF24", "#EF4444", "#38BDF8"]
    for idx, col in enumerate(crayon_colors):
        cy_y = y + h * 0.45 - idx * 5.0
        draw_crayon(c, x + 2, cy_y, length=12, width=2.2, angle_deg=25, color_hex=col)

    # Miniature sample card in center-right with recognizable cartoon artwork
    card_w = w * 0.44
    card_h = h * 0.42
    card_x = x + w * 0.50
    card_y = y + 8
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#E2E8F0"))
    c.setLineWidth(0.6)
    c.roundRect(card_x, card_y, card_w, card_h, 3, fill=1, stroke=1)

    # Check for generated high-res thumbnail icon PNG
    thumb_dir = Path("local_builds/animals/assets/thumbnails")
    thumb_file = None
    if thumb_dir.exists():
        candidates = sorted(list(thumb_dir.glob(f"vol_{vol_num:02d}*.png")))
        if candidates:
            thumb_file = candidates[0]

    if thumb_file and thumb_file.exists():
        pad = 1.5
        c.drawImage(
            str(thumb_file),
            card_x + pad,
            card_y + pad,
            width=card_w - 2 * pad,
            height=card_h - 2 * pad,
            preserveAspectRatio=True,
            mask="auto",
        )
    else:
        # Recognizable cartoon vector art inside the card!
        draw_thumb_art(c, subject_idx=subject_idx, cx=card_x + card_w * 0.5, cy=card_y + card_h * 0.5, sz=card_w * 0.7)


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
    """Render the Back Cover (Left Third) with transparent sticker logo, 4x3 grid, green container, and barcode."""
    back_left_pt = dims["back_left_in"] * inch
    back_width_pt = dims["trim_width_in"] * inch
    center_x = back_left_pt + back_width_pt / 2.0

    # 1. Top Row: "THE PIVOT KIDS COLOR & PLAY" brand logo on left, Blue Banner on right
    top_y = (dims["total_height_in"] - dims["bleed_in"] - 0.95) * inch

    # Transparent sticker logo (NO square white background box)
    if logo_path and logo_path.exists():
        logo_w = 1.35 * inch
        logo_h = 1.45 * inch
        logo_x = back_left_pt + 0.5 * inch
        logo_y = top_y - 0.40 * inch
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

    # 2. Centered 4x3 Grid of 12 Miniature Book Covers (No placeholder dots!)
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
            vol_num=item.get("vol", idx + 1),
            subject_idx=idx,
        )

    # 3. Bottom Left: Playful Green Container with Collector's Series
    container_x = back_left_pt + 0.55 * inch
    container_y = (dims["bleed_in"] + 1.05) * inch
    container_w = 4.6 * inch
    container_h = 0.38 * inch

    c.saveState()
    # Playful Green Container
    c.setFillColor(HexColor("#16A34A"))
    c.setStrokeColor(HexColor("#15803D"))
    c.setLineWidth(1.2)
    c.roundRect(container_x, container_y, container_w, container_h, 8, fill=1, stroke=1)

    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 10.5)
    c.drawCentredString(container_x + container_w / 2.0, container_y + 0.10 * inch, "★ Collector's Series of 15 Interactive Titles ★")

    # Text below green container
    c.setFont("Helvetica-Bold", 10.0)
    c.drawString(container_x + 4, container_y - 0.24 * inch, "A playful, easy coloring series designed for early learners")
    c.drawString(container_x + 4, container_y - 0.44 * inch, "to copy, color, and play!")
    c.restoreState()

    # 4. Bottom Center-Right: White Barcode Box with Copyright Below
    barcode_w = 2.0 * inch
    barcode_h = 1.2 * inch
    barcode_x = (dims["back_right_in"] - 2.4) * inch
    barcode_y = (dims["bleed_in"] + 0.45) * inch

    c.saveState()
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#CBD5E1"))
    c.setLineWidth(1)
    c.roundRect(barcode_x, barcode_y, barcode_w, barcode_h, 4, fill=1, stroke=1)
    c.setFillColor(HexColor("#64748B"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(barcode_x + barcode_w / 2.0, barcode_y + barcode_h / 2.0, "[ Amazon KDP Barcode Location ]")

    # Copyright below barcode box
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 7.8)
    c.drawCentredString(barcode_x + barcode_w / 2.0, (dims["bleed_in"] + 0.20) * inch, "© The Pivot Digital Publications. All rights reserved.")
    c.restoreState()


def draw_spine(c: canvas.Canvas, dims: dict[str, float], logo_path: Path | None = None) -> None:
    """Render the Center Strip (Spine) with vertical typography and base logo."""
    spine_left_pt = dims["spine_left_in"] * inch
    spine_w_pt = dims["spine_width_in"] * inch
    height_pt = dims["total_height_in"] * inch

    c.saveState()
    # Spine background (matching coral-red)
    c.setFillColor(HexColor("#FF4949"))
    c.rect(spine_left_pt, 0, spine_w_pt, height_pt, fill=1, stroke=0)

    # Vertical text rotated 90 degrees (running from top to bottom)
    c.translate(spine_left_pt + spine_w_pt / 2.0, height_pt / 2.0)
    c.rotate(-90)

    # Spine text: "THE PIVOT KIDS   |   My First Copy to Color: Animals   |   Vol. 2"
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 5.8)
    c.drawCentredString(0, -2, "THE PIVOT KIDS   |   My First Copy to Color: Animals   |   Vol. 2")

    c.restoreState()


def draw_front_cover(
    c: canvas.Canvas,
    dims: dict[str, float],
    logo_path: Path | None = None,
    hero_art_path: Path | None = None,
    card_color_thumb: Path | None = None,
    card_bw_outline: Path | None = None,
) -> None:
    """Render the Front Cover (Right Third) with 3D bubble fonts, curved My First banner, and hero art."""
    front_left_pt = dims["front_left_in"] * inch
    front_width_pt = dims["trim_width_in"] * inch
    center_x = front_left_pt + front_width_pt / 2.0
    height_pt = dims["total_height_in"] * inch

    # 1. TOP HEADER ARCH: Coral-Red curved ribbon with stitched white border
    header_h = 4.05 * inch
    arch_bottom = height_pt - header_h

    c.saveState()
    c.setFillColor(HexColor("#FF4949"))
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

    # 2. TOP BRAND LOGO: Prominent transparent sticker logo with white contour (NO square white box!)
    if logo_path and logo_path.exists():
        logo_w = 1.85 * inch
        logo_h = 2.00 * inch
        logo_x = center_x - logo_w / 2.0
        logo_y = height_pt - 2.16 * inch
        c.drawImage(str(logo_path), logo_x, logo_y, width=logo_w, height=logo_h, preserveAspectRatio=True, mask="auto")

    # 3. TOP TITLE: Slightly curved white banner reading "My First"
    banner_w = 2.35 * inch
    banner_h = 0.40 * inch
    banner_x = center_x - banner_w / 2.0
    banner_y = height_pt - 2.58 * inch

    c.saveState()
    # Soft drop shadow
    c.setFillColor(HexColor("#991B1B"))
    c.roundRect(banner_x, banner_y - 2, banner_w, banner_h, 10, fill=1, stroke=0)
    # White banner body
    c.setFillColor(HexColor("#FFFFFF"))
    c.setStrokeColor(HexColor("#FDE047"))
    c.setLineWidth(1.4)
    c.roundRect(banner_x, banner_y, banner_w, banner_h, 10, fill=1, stroke=1)
    # Banner text
    c.setFillColor(HexColor("#1E3A8A"))
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(center_x, banner_y + 0.09 * inch, "My First")
    c.restoreState()

    # 4. MAIN TITLE: Heavy, bouncing, 3D bubble fonts "Copy to Color"
    title1_y = height_pt - 3.16 * inch
    draw_3d_title(
        c,
        text="Copy to Color",
        x=center_x,
        y=title1_y,
        font_name="Helvetica-Bold",
        font_size=44,
        fill_hex="#FFFFFF",
        outline_hex="#0F294A",
        outline_width=4.5,
        extrusion_depth=5,
        extrusion_hex="#081726",
        secondary_border_hex="#1E3A8A",
        secondary_width=1.5,
    )

    # 5. BOOK SUBJECT: Giant, chunky, playful "Animals" bubble text with 3D volumetric extrusion
    title2_y = height_pt - 3.84 * inch
    draw_3d_title(
        c,
        text="Animals",
        x=center_x,
        y=title2_y,
        font_name="Helvetica-Bold",
        font_size=48,
        fill_hex="#FACC15",
        outline_hex="#78350F",
        outline_width=4.8,
        extrusion_depth=6,
        extrusion_hex="#451A03",
        secondary_border_hex="#DC2626",
        secondary_width=2.0,
    )

    # 6. LEFT CHUNKY CRAYONS TRIO: Yellow, Red, Blue pointing inward from the edge
    crayons_start_x = front_left_pt + 0.1 * inch
    crayons_base_y = height_pt - 4.65 * inch
    crayons_data = [
        {"color": "#FDE047", "angle": -25, "y_off": 0.0},
        {"color": "#EF4444", "angle": -25, "y_off": -0.45 * inch},
        {"color": "#2563EB", "angle": -25, "y_off": -0.90 * inch},
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

    # 7. INSET "BEFORE & AFTER" ACTIVITY CARD: Paper-like card with drop-shadow labeled "TIGER"
    card_w = 2.85 * inch
    card_h = 3.55 * inch
    card_x = front_left_pt + front_width_pt - card_w - 0.65 * inch
    card_y = height_pt - 8.10 * inch

    c.saveState()
    # Paper-like card drop shadow
    c.setFillColor(HexColor("#000000"))
    c.setFillAlpha(0.18)
    c.roundRect(card_x + 3, card_y - 3, card_w, card_h, 12, fill=1, stroke=0)
    c.setFillAlpha(1.0)

    # Main white card body
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
        c.setFillColor(HexColor("#FFFFFF"))
        c.setStrokeColor(HexColor("#000000"))
        c.setLineWidth(1)
        c.roundRect(outline_box_x, outline_box_y, outline_box_w, outline_box_h, 4, fill=1, stroke=1)

    c.setFillColor(HexColor("#0284C7"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(outline_box_x + outline_box_w / 2.0, outline_box_y - 12, "Color Me!")

    c.restoreState()

    # 8. FOREGROUND HERO CHARACTERS: Cute Cartoon Tiger Cub & Monkey on Grass
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
    draw_spine(c, dims, logo_path=logo_path)

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
    parser.add_argument("--page-count", type=int, default=74, help="Book page count for spine calculation (default 74)")
    parser.add_argument("--logo", type=Path, default=Path("assets/logos/pivot_kids_sticker.png"), help="Logo PNG/SVG")
    parser.add_argument("--hero-art", type=Path, default=Path("local_builds/animals/assets/tiger_monkey_transparent.png"), help="Hero characters PNG")
    parser.add_argument("--card-color", type=Path, default=Path("local_builds/animals/assets/tiger_color_thumb.png"), help="Activity card color guide")
    parser.add_argument("--card-outline", type=Path, default=Path("local_builds/animals/assets/tiger_outline.png"), help="Activity card B&W outline")

    args = parser.parse_args()

    # Fallback to standard pivot_kids.png if sticker not found
    logo_file = args.logo if args.logo.exists() else Path("assets/logos/pivot_kids.png")

    out = draw_animals_cover_spread(
        output_pdf_path=args.output,
        page_count=args.page_count,
        logo_path=logo_file if logo_file.exists() else None,
        hero_art_path=args.hero_art if args.hero_art.exists() else None,
        card_color_thumb=args.card_color if args.card_color.exists() else None,
        card_bw_outline=args.card_outline if args.card_outline.exists() else None,
    )
    print(f"[OK] Full Animals Cover Spread generated successfully: {out}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
