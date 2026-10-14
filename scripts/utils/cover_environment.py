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


def draw_toadstool_mushroom(draw: ImageDraw.ImageDraw, x: int, y: int, width: int = 120, height: int = 140) -> None:
    """Draws a red polka-dot fly-agaric toadstool mushroom."""
    cap_h = int(height * 0.6)
    stem_w = int(width * 0.42)
    stem_h = height - cap_h + 10
    stem_x = x + (width - stem_w) // 2
    stem_y = y + cap_h - 10

    # Stem
    draw.rounded_rectangle([stem_x, stem_y, stem_x + stem_w, stem_y + stem_h], radius=16, fill=(254, 243, 199, 255), outline=OUTLINE_DARK, width=8)
    # Red Cap
    draw.pieslice([x, y, x + width, y + cap_h * 2], start=180, end=360, fill=(220, 38, 38, 255), outline=OUTLINE_DARK, width=10)
    # White Polka Dots
    dots = [
        (x + width * 0.25, y + cap_h * 0.45, width * 0.10),
        (x + width * 0.50, y + cap_h * 0.25, width * 0.12),
        (x + width * 0.75, y + cap_h * 0.48, width * 0.09),
        (x + width * 0.40, y + cap_h * 0.65, width * 0.08),
        (x + width * 0.65, y + cap_h * 0.72, width * 0.08),
    ]
    for dx, dy, dr in dots:
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(255, 255, 255, 255))


def draw_flower_daisy(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int = 35, petal_col: tuple = (255, 255, 255, 255), center_col: tuple = (250, 204, 21, 255)) -> None:
    """Draws a cute flower with radiating rounded petals and a yellow center."""
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        px = cx + int(r * 0.85 * math.cos(rad))
        py = cy + int(r * 0.85 * math.sin(rad))
        draw.ellipse([px - r * 0.45, py - r * 0.45, px + r * 0.45, py + r * 0.45], fill=petal_col, outline=OUTLINE_DARK, width=4)
    draw.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55], fill=center_col, outline=OUTLINE_DARK, width=5)


def draw_butterfly(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 60, wing_col: tuple = (192, 132, 252, 255)) -> None:
    """Draws a colorful cartoon butterfly."""
    draw.ellipse([cx - size, cy - size * 0.8, cx - size * 0.1, cy + size * 0.1], fill=wing_col, outline=OUTLINE_DARK, width=5)
    draw.ellipse([cx - size * 0.8, cy, cx - size * 0.1, cy + size * 0.8], fill=wing_col, outline=OUTLINE_DARK, width=4)
    draw.ellipse([cx + size * 0.1, cy - size * 0.8, cx + size, cy + size * 0.1], fill=wing_col, outline=OUTLINE_DARK, width=5)
    draw.ellipse([cx + size * 0.1, cy, cx + size * 0.8, cy + size * 0.8], fill=wing_col, outline=OUTLINE_DARK, width=4)
    draw.ellipse([cx - size * 0.65, cy - size * 0.45, cx - size * 0.35, cy - size * 0.15], fill=(254, 240, 138, 255))
    draw.ellipse([cx + size * 0.35, cy - size * 0.45, cx + size * 0.65, cy - size * 0.15], fill=(254, 240, 138, 255))
    draw.rounded_rectangle([cx - size * 0.12, cy - size * 0.6, cx + size * 0.12, cy + size * 0.6], radius=8, fill=(30, 30, 30, 255))


def draw_ladybug(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int = 36) -> None:
    """Draws a cute red ladybug with black spots."""
    draw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=(239, 68, 68, 255), outline=OUTLINE_DARK, width=5)
    draw.ellipse([cx - size * 0.5, cy - size * 1.1, cx + size * 0.5, cy - size * 0.5], fill=(20, 20, 20, 255))
    draw.line([(cx, cy - size * 0.6), (cx, cy + size)], fill=(20, 20, 20, 255), width=5)
    dots = [(-size * 0.45, -size * 0.2), (-size * 0.45, size * 0.35), (size * 0.45, -size * 0.2), (size * 0.45, size * 0.35)]
    for dx, dy in dots:
        draw.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5], fill=(20, 20, 20, 255))


def draw_jungalow_elements(canvas: Image.Image, width: int, height: int, is_spread: bool = False) -> None:
    """
    Renders lush nature accents across the rolling hills: toadstool mushrooms,
    daisies, ladybugs, and fluttering butterflies with flight trail loops.
    """
    draw = ImageDraw.Draw(canvas)
    hill_base_y = int(height * 0.82)

    if is_spread:
        # Spread layout
        # Back cover left mushroom cluster
        draw_toadstool_mushroom(draw, 120, height - 420, width=180, height=210)
        draw_toadstool_mushroom(draw, 270, height - 320, width=120, height=140)

        # Front cover bottom-left mushroom cluster
        fx_offset = int(width * 0.51)
        draw_toadstool_mushroom(draw, fx_offset + 50, height - 440, width=220, height=250)
        draw_toadstool_mushroom(draw, fx_offset + 250, height - 330, width=140, height=160)

        # Butterflies with dotted curved flight trails
        # Back cover butterfly
        draw_butterfly(draw, 320, height - 750, size=52, wing_col=(236, 72, 153, 255))
        # Front cover right butterfly
        draw_butterfly(draw, width - 260, height - 1650, size=68, wing_col=(251, 146, 60, 255))
        draw_butterfly(draw, width - 220, height - 1100, size=75, wing_col=(192, 132, 252, 255))
        draw_butterfly(draw, width - 420, height - 350, size=60, wing_col=(192, 132, 252, 255))

        # Ladybugs on leaves
        draw_ladybug(draw, fx_offset + 860, height - 420, size=32)
        draw_ladybug(draw, width - 180, height - 280, size=38)

        # Flowers across grass
        draw_flower_daisy(draw, 720, height - 260, r=36, petal_col=(255, 255, 255, 255))
        draw_flower_daisy(draw, 1450, height - 280, r=40, petal_col=(253, 186, 116, 255))
        draw_flower_daisy(draw, fx_offset + 950, height - 380, r=42, petal_col=(244, 114, 182, 255))
        draw_flower_daisy(draw, width - 120, height - 480, r=46, petal_col=(250, 204, 21, 255))
        draw_flower_daisy(draw, fx_offset + 1240, height - 220, r=40, petal_col=(244, 114, 182, 255))

    else:
        # Standalone front cover
        draw_toadstool_mushroom(draw, 60, height - 440, width=220, height=250)
        draw_toadstool_mushroom(draw, 260, height - 330, width=140, height=160)

        # Butterflies
        draw_butterfly(draw, width - 260, height - 1650, size=68, wing_col=(251, 146, 60, 255))
        draw_butterfly(draw, width - 200, height - 1100, size=75, wing_col=(192, 132, 252, 255))
        draw_butterfly(draw, width - 380, height - 350, size=60, wing_col=(192, 132, 252, 255))

        # Ladybugs
        draw_ladybug(draw, width - 180, height - 280, size=38)
        # Flowers
        draw_flower_daisy(draw, width - 120, height - 480, r=46, petal_col=(250, 204, 21, 255))
        draw_flower_daisy(draw, width - 320, height - 220, r=40, petal_col=(244, 114, 182, 255))


def draw_curved_ribbon_header(canvas: Image.Image, cx: int, cy: int, text: str, font: ImageFont.FreeTypeFont) -> None:
    """
    Renders an ornate parchment ribbon banner with 3D drop shadow and triangular notched ends.
    Text: TITLES IN THIS SERIES (flanked by procedural golden vector stars)
    """
    draw = ImageDraw.Draw(canvas)
    # Strip any accidental unicode stars from text to avoid missing glyph tofu boxes
    clean_text = text.replace("\u2605", "").replace("\u2606", "").strip()
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

    # Flank with procedural golden vector sparkle stars
    star_offset = tw // 2 + 42
    draw_sparkle_star(draw, cx - star_offset, cy - 2, outer_r=20, inner_r=5, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))
    draw_sparkle_star(draw, cx + star_offset, cy - 2, outer_r=20, inner_r=5, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))


def draw_mascot_boy_with_wand(canvas: Image.Image, cx: int, cy: int) -> None:
    """
    Renders the playful boy mascot wearing a colorful backwards baseball cap,
    holding a glowing magic star wand next to the 'CAN YOU COLLECT THEM ALL?' banner.
    """
    draw = ImageDraw.Draw(canvas)

    # 1. Backwards Baseball Cap (Cyan crown, yellow bill to back, red band)
    # Bill turned backwards (pointing right)
    draw.polygon([(cx + 40, cy - 150), (cx + 170, cy - 130), (cx + 160, cy - 80), (cx + 30, cy - 90)], fill=(250, 204, 21, 255), outline=OUTLINE_DARK, width=8)
    # Main Cap Crown (Cyan)
    draw.pieslice([cx - 150, cy - 250, cx + 110, cy + 10], start=180, end=360, fill=(2, 132, 199, 255), outline=OUTLINE_DARK, width=10)
    # Cap edge band (Red)
    draw.rounded_rectangle([cx - 160, cy - 130, cx + 100, cy - 90], radius=16, fill=(239, 68, 68, 255), outline=OUTLINE_DARK, width=8)
    # Top cap button
    draw.ellipse([cx - 35, cy - 265, cx - 5, cy - 235], fill=(250, 204, 21, 255), outline=OUTLINE_DARK, width=6)

    # 2. Boy Face & Brown Hair Tuft
    # Hair tuft peeking from cap
    draw.polygon([(cx - 130, cy - 100), (cx - 160, cy - 60), (cx - 110, cy - 70)], fill=(120, 53, 15, 255), outline=OUTLINE_DARK, width=6)
    draw.polygon([(cx + 40, cy - 90), (cx + 80, cy - 50), (cx + 50, cy - 60)], fill=(120, 53, 15, 255), outline=OUTLINE_DARK, width=6)

    # Face (Peachy skin)
    skin_col = (255, 224, 194, 255)
    draw.ellipse([cx - 140, cy - 110, cx + 80, cy + 110], fill=skin_col, outline=OUTLINE_DARK, width=10)

    # Ears
    draw.ellipse([cx - 165, cy - 30, cx - 120, cy + 40], fill=skin_col, outline=OUTLINE_DARK, width=8)
    draw.ellipse([cx + 60, cy - 30, cx + 105, cy + 40], fill=skin_col, outline=OUTLINE_DARK, width=8)

    # Eyes (Big cheerful anime/cartoon eyes)
    for ex in (cx - 85, cx + 25):
        draw.ellipse([ex - 24, cy - 40, ex + 24, cy + 15], fill=(20, 20, 25, 255))
        draw.ellipse([ex - 12, cy - 32, ex + 12, cy - 8], fill="white")
        draw.ellipse([ex + 2, cy + 2, ex + 10, cy + 10], fill="white")

    # Rosy Cheeks
    draw.ellipse([cx - 115, cy + 5, cx - 65, cy + 45], fill=(255, 150, 170, 190))
    draw.ellipse([cx + 10, cy + 5, cx + 60, cy + 45], fill=(255, 150, 170, 190))

    # Cute nose and wide open smile
    draw.ellipse([cx - 33, cy - 2, cx - 21, cy + 12], fill=(240, 110, 120, 255))
    draw.arc([cx - 65, cy + 5, cx + 5, cy + 75], start=10, end=170, fill=OUTLINE_DARK, width=8)
    draw.pieslice([cx - 55, cy + 25, cx - 5, cy + 75], start=10, end=170, fill=(239, 68, 68, 255))

    # 3. Hoodie / Shirt (Purple/Blue)
    draw.polygon([(cx - 130, cy + 90), (cx + 70, cy + 90), (cx + 120, cy + 220), (cx - 180, cy + 220)], fill=(126, 34, 206, 255), outline=OUTLINE_DARK, width=10)

    # 4. Raised Arm holding Magic Wand
    # Hand
    draw.ellipse([cx - 200, cy - 130, cx - 145, cy - 75], fill=skin_col, outline=OUTLINE_DARK, width=8)
    # Wand stick
    draw.line([(cx - 170, cy - 90), (cx - 230, cy - 220)], fill=(146, 64, 14, 255), width=12)
    # Glowing Yellow Star Tip
    star_cx, star_cy = cx - 240, cy - 240
    # Outer yellow glow halo
    draw.ellipse([star_cx - 50, star_cy - 50, star_cx + 50, star_cy + 50], fill=(254, 240, 138, 140))
    # 4-point Starburst
    draw_sparkle_star(draw, star_cx, star_cy, outer_r=38, inner_r=9, fill=(255, 230, 80, 255), outline=(245, 158, 11, 255))


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

