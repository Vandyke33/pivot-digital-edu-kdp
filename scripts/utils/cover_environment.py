"""
Rich & High-Energy Storybook Environment Engine for Cover Spreads and Standalone Front Covers.

Provides:
  - Checkered storybook borders (alternating red and cream tiles)
  - Dense vector pattern collages (paint splatters, doodles, bubbles, sparkle star clusters)
  - Lush jungalow nature elements (red polka-dot toadstool mushrooms, daisies, ladybugs, butterflies with flight trails)
  - Back cover curved ribbon header (TITLES IN THIS SERIES)
  - Mascot boy waving a glowing magic star wand with CAN YOU COLLECT THEM ALL? banner
"""

from __future__ import annotations

import math
import random
from typing import Sequence
from PIL import Image, ImageDraw, ImageFont

# Brand palette constants
CHECKER_RED = (197, 34, 31, 255)
CHECKER_CREAM = (255, 247, 237, 255)
DARK_RED_LINE = (153, 27, 27, 255)
OUTLINE_DARK = (30, 30, 35, 255)


def draw_checkered_border(
    canvas: Image.Image,
    width: int,
    height: int,
    tile_size: int = 44,
    rows: int = 2,
    red_col: tuple = CHECKER_RED,
    cream_col: tuple = CHECKER_CREAM,
) -> None:
    """
    Renders an alternating storybook checkered frame along the 4 outer edges.
    """
    draw = ImageDraw.Draw(canvas)
    cols_w = math.ceil(width / tile_size)
    rows_h = math.ceil(height / tile_size)

    # Top border rows
    for r in range(rows):
        y0 = r * tile_size
        y1 = y0 + tile_size
        for c in range(cols_w):
            x0 = c * tile_size
            x1 = min(x0 + tile_size, width)
            col = red_col if (r + c) % 2 == 0 else cream_col
            draw.rectangle([x0, y0, x1, y1], fill=col)

    # Bottom border rows
    for r in range(rows):
        y0 = height - (rows - r) * tile_size
        y1 = y0 + tile_size
        for c in range(cols_w):
            x0 = c * tile_size
            x1 = min(x0 + tile_size, width)
            col = red_col if (r + c) % 2 == 0 else cream_col
            draw.rectangle([x0, y0, x1, y1], fill=col)

    # Left border cols
    for c in range(rows):
        x0 = c * tile_size
        x1 = x0 + tile_size
        for r in range(rows, rows_h - rows):
            y0 = r * tile_size
            y1 = min(y0 + tile_size, height)
            col = red_col if (r + c) % 2 == 0 else cream_col
            draw.rectangle([x0, y0, x1, y1], fill=col)

    # Right border cols
    for c in range(rows):
        x0 = width - (rows - c) * tile_size
        x1 = x0 + tile_size
        for r in range(rows, rows_h - rows):
            y0 = r * tile_size
            y1 = min(y0 + tile_size, height)
            col = red_col if (r + c) % 2 == 0 else cream_col
            draw.rectangle([x0, y0, x1, y1], fill=col)

    # Inner boundary crisp line
    inner_pad = rows * tile_size
    draw.rectangle([inner_pad, inner_pad, width - inner_pad, height - inner_pad], outline=DARK_RED_LINE, width=3)


def draw_paint_splatter(draw: ImageDraw.ImageDraw, cx: int, cy: int, radius: int, color: tuple) -> None:
    """Draws an organic paint splatter with a central splash blob and droplets."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        dist = radius * 0.95
        r_sub = radius * 0.45
        bx = cx + int(dist * math.cos(rad))
        by = cy + int(dist * math.sin(rad))
        draw.ellipse([bx - r_sub, by - r_sub, bx + r_sub, by + r_sub], fill=color)

    rng = random.Random(cx * 1000 + cy)
    for _ in range(8):
        d_ang = rng.uniform(0, 2 * math.pi)
        d_dist = radius * rng.uniform(1.3, 2.3)
        d_rad = radius * rng.uniform(0.12, 0.28)
        dx = cx + int(d_dist * math.cos(d_ang))
        dy = cy + int(d_dist * math.sin(d_ang))
        draw.ellipse([dx - d_rad, dy - d_rad, dx + d_rad, dy + d_rad], fill=color)


def draw_spiral_doodle(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 50, color: tuple = (180, 40, 20, 180), width: int = 6) -> None:
    """Draws a cute whimsical spiral doodle."""
    pts = []
    loops = 2.5
    for i in range(40):
        t = i / 40.0
        ang = t * loops * 2 * math.pi
        r = t * size
        px = cx + r * math.cos(ang)
        py = cy + r * math.sin(ang)
        pts.append((px, py))
    if len(pts) > 1:
        draw.line(pts, fill=color, width=width)


def draw_pattern_collage(canvas: Image.Image, width: int, height: int, is_spread: bool = False) -> None:
    """
    Overlays a dense vector pattern collage of paint splatters, doodle swirls,
    sparkle clusters, and bubbles onto the gradient sky.
    """
    draw = ImageDraw.Draw(canvas)

    # Palette for splatters and accents
    yellow_splatter = (253, 224, 71, 230)
    pink_splatter = (236, 72, 153, 210)
    cyan_splatter = (56, 189, 248, 220)
    dark_red_splatter = (153, 27, 27, 210)

    # Deterministic placements based on canvas width
    if is_spread:
        # Full wrap spread (5197 x 3375 px)
        splatter_locs = [
            (int(width * 0.08), 280, 55, yellow_splatter),
            (int(width * 0.22), 240, 45, pink_splatter),
            (int(width * 0.38), 280, 40, dark_red_splatter),
            (int(width * 0.44), 320, 50, yellow_splatter),
            (int(width * 0.56), 260, 60, dark_red_splatter),
            (int(width * 0.65), 320, 45, yellow_splatter),
            (int(width * 0.88), 280, 50, yellow_splatter),
            (int(width * 0.94), 350, 45, dark_red_splatter),
            (int(width * 0.12), 1100, 38, cyan_splatter),
            (int(width * 0.92), 1250, 48, pink_splatter),
        ]
        doodle_locs = [
            (int(width * 0.05), 850, 55),
            (int(width * 0.48), 650, 45),
            (int(width * 0.53), 1350, 50),
            (int(width * 0.95), 1450, 60),
            (int(width * 0.60), 650, 45),
        ]
        bubble_locs = [
            (int(width * 0.06), 550, 30, (255, 255, 255, 120)),
            (int(width * 0.46), 450, 24, (253, 224, 71, 140)),
            (int(width * 0.52), 480, 28, (236, 72, 153, 130)),
            (int(width * 0.93), 850, 32, (56, 189, 248, 140)),
        ]
    else:
        # Standalone front cover (2550 x 3300 px)
        splatter_locs = [
            (int(width * 0.14), 280, 55, dark_red_splatter),
            (int(width * 0.32), 320, 45, yellow_splatter),
            (int(width * 0.82), 260, 50, yellow_splatter),
            (int(width * 0.92), 340, 45, dark_red_splatter),
            (int(width * 0.88), 1250, 48, pink_splatter),
        ]
        doodle_locs = [
            (int(width * 0.07), 1350, 55),
            (int(width * 0.93), 1400, 60),
        ]
        bubble_locs = [
            (int(width * 0.08), 850, 30, (255, 255, 255, 120)),
            (int(width * 0.92), 850, 32, (56, 189, 248, 140)),
        ]

    for cx, cy, rad, col in splatter_locs:
        draw_paint_splatter(draw, cx, cy, rad, col)

    for cx, cy, sz in doodle_locs:
        draw_spiral_doodle(draw, cx, cy, size=sz)

    for cx, cy, rad, col in bubble_locs:
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=col)
        draw.arc([cx - rad * 0.7, cy - rad * 0.7, cx + rad * 0.7, cy + rad * 0.7], start=200, end=320, fill="white", width=4)


def draw_five_point_star(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    outer_r: float = 20,
    inner_r: float = 8,
    fill: tuple = (250, 204, 21, 255),
    outline: tuple | None = (180, 83, 9, 255),
    width: int = 2,
) -> None:
    """Draws a crisp 5-point vector star polygon with optional outline."""
    pts = []
    for i in range(10):
        r = outer_r if i % 2 == 0 else inner_r
        ang = -math.pi / 2 + i * (math.pi / 5)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=outline, width=width)


def draw_curved_ribbon_header(canvas: Image.Image, cx: int, cy: int, text: str, font: ImageFont.FreeTypeFont) -> None:
    """
    Renders an ornate parchment ribbon banner with 3D drop shadow and triangular notched ends.
    Text: TITLES IN THIS SERIES (flanked by crisp vector 5-point gold stars)
    """
    draw = ImageDraw.Draw(canvas)
    # Strip any accidental unicode stars from text to avoid missing glyph tofu boxes
    clean_text = text.replace("\u2605", "").replace("\u2606", "").replace("★", "").replace("✦", "").strip()
    bbox = draw.textbbox((0, 0), clean_text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

    bw = tw + 200
    bh = th + 45
    x0 = cx - bw // 2
    y0 = cy - bh // 2
    x1 = x0 + bw
    y1 = y0 + bh

    # Folded ribbon tail flaps behind
    tail_w = 70
    tail_h = bh + 15
    # Left tail
    draw.polygon([(x0 - tail_w, y0 + 10), (x0 + 10, y0 + 10), (x0 + 10, y1 + 10), (x0 - tail_w, y1 + 10), (x0 - tail_w + 25, y0 + tail_h // 2)], fill=(180, 83, 9, 255), outline=OUTLINE_DARK, width=4)
    # Right tail
    draw.polygon([(x1 - 10, y0 + 10), (x1 + tail_w, y0 + 10), (x1 + tail_w - 25, y0 + tail_h // 2), (x1 + tail_w, y1 + 10), (x1 - 10, y1 + 10)], fill=(180, 83, 9, 255), outline=OUTLINE_DARK, width=4)

    # Ribbon drop shadow
    draw.rounded_rectangle([x0 + 6, y0 + 8, x1 + 6, y1 + 8], radius=24, fill=(30, 15, 10, 120))
    # Ribbon body (Warm Parchment Cream)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(255, 251, 235, 255), outline=OUTLINE_DARK, width=5)
    # Inner stitched dashed line
    draw.rounded_rectangle([x0 + 8, y0 + 8, x1 - 8, y1 - 8], radius=16, outline=(245, 158, 11, 255), width=3)

    # Center text
    draw.text((cx - tw // 2, cy - th // 2 - 4), clean_text, fill=(69, 26, 3, 255), font=font)

    # Flank with crisp vector 5-point gold stars
    star_offset = tw // 2 + 42
    draw_five_point_star(draw, cx - star_offset, cy - 2, outer_r=18, inner_r=8, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))
    draw_five_point_star(draw, cx + star_offset, cy - 2, outer_r=18, inner_r=8, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))


def draw_sparkle_star(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    outer_r: int = 22,
    inner_r: int = 5,
    fill: tuple = (255, 255, 255, 255),
    outline: tuple = (255, 240, 130, 255),
) -> None:
    """Draws a crisp 4-point vector diamond sparkle star with a bright white core."""
    pts = [
        (cx, cy - outer_r),
        (cx + inner_r, cy - inner_r),
        (cx + outer_r, cy),
        (cx + inner_r, cy + inner_r),
        (cx, cy + outer_r),
        (cx - inner_r, cy + inner_r),
        (cx - outer_r, cy),
        (cx - inner_r, cy - inner_r),
    ]
    draw.polygon(pts, fill=fill, outline=outline)
    core_r = max(2, inner_r - 1)
    draw.ellipse([cx - core_r, cy - core_r, cx + core_r, cy + core_r], fill=(255, 255, 255, 255))

