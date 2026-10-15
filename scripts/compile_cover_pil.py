"""
Automated KDP Full-Wrap Cover Spread Generator (Two-Pass Series Architecture - PIL Engine)

Pass 1: Generates all 12 standalone Front Covers with custom theme palettes, bundled fancy fonts,
        neon outer glows, 3D extrusions, specular highlights, and 4-point vector sparkles.
Pass 2: Compiles the Full-Wrap Spread (Back + Spine + Front) by injecting the exact 12 rendered
        Front Cover images into the Back Cover's 4x3 "Titles in this Series" grid.

Dependencies: pip install pillow reportlab numpy requests
"""

from __future__ import annotations

import math
import os
import sys
import urllib.request
from pathlib import Path

# Ensure repository root is on sys.path when invoked directly
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

from scripts.utils.alpha_extraction import extract_with_sticker_contour
from scripts.utils.cover_environment import (
    draw_checkered_border,
    draw_curved_ribbon_header,
    draw_five_point_star,
    draw_pattern_collage,
    draw_sparkle_star,
)


# ---------------------------------------------------------------------------
# 1. KDP MECHANICAL CONSTANTS & 12-VOLUME SERIES CONFIGURATION
# ---------------------------------------------------------------------------
DPI = 300
TRIM_W_IN = 8.5
TRIM_H_IN = 11.0
BLEED_IN = 0.125
WHITE_PAPER_THICKNESS_IN = 0.002252

GRASS_COLOR = (76, 187, 23, 255)
GRASS_MID_COLOR = (34, 197, 94, 255)
NAVY_TEXT = (18, 30, 66, 255)
YELLOW_TEXT = (255, 230, 80, 255)

SERIES_TITLES = [
    {"id": "vol_01", "vol": "Vol. 1",  "title": "Alphabet",   "pill": "ABC",       "bg_top": (255, 107, 53),  "bg_bottom": (255, 159, 28),  "neon": (255, 230, 109)},
    {"id": "vol_02", "vol": "Vol. 2",  "title": "Animals",    "pill": "TIGER",     "bg_top": (255, 73, 73),   "bg_bottom": (255, 126, 71),  "neon": (255, 235, 120), "theme_environment": "jungle"},
    {"id": "vol_03", "vol": "Vol. 3",  "title": "Birds",      "pill": "PARROT",    "bg_top": (16, 185, 129),  "bg_bottom": (52, 211, 153),  "neon": (167, 243, 208)},
    {"id": "vol_04", "vol": "Vol. 4",  "title": "Sports",     "pill": "SOCCER",    "bg_top": (101, 163, 13),  "bg_bottom": (132, 204, 22),  "neon": (217, 249, 157)},
    {"id": "vol_05", "vol": "Vol. 5",  "title": "Monsters",   "pill": "MONSTER",   "bg_top": (217, 70, 239),  "bg_bottom": (244, 114, 182), "neon": (251, 207, 232)},
    {"id": "vol_06", "vol": "Vol. 6",  "title": "Numbers",    "pill": "1 2 3",     "bg_top": (153, 27, 27),   "bg_bottom": (220, 38, 38),   "neon": (254, 202, 202)},
    {"id": "vol_07", "vol": "Vol. 7",  "title": "Fruits",     "pill": "FRUITS",    "bg_top": (13, 148, 136),  "bg_bottom": (45, 212, 191),  "neon": (153, 246, 228)},
    {"id": "vol_08", "vol": "Vol. 8",  "title": "Shapes",     "pill": "SHAPES",    "bg_top": (236, 72, 153),  "bg_bottom": (251, 113, 133), "neon": (254, 205, 211)},
    {"id": "vol_09", "vol": "Vol. 9",  "title": "Toys",       "pill": "BEAR",      "bg_top": (2, 132, 199),   "bg_bottom": (56, 189, 248),  "neon": (186, 230, 253)},
    {"id": "vol_10", "vol": "Vol. 10", "title": "Flowers",    "pill": "SUNFLOWER", "bg_top": (120, 53, 15),   "bg_bottom": (180, 83, 9),    "neon": (253, 230, 138)},
    {"id": "vol_11", "vol": "Vol. 11", "title": "Transport",  "pill": "CAR",       "bg_top": (30, 58, 138),   "bg_bottom": (59, 130, 246),  "neon": (191, 219, 254)},
    {"id": "vol_12", "vol": "Vol. 12", "title": "Vegetables", "pill": "CARROT",    "bg_top": (109, 40, 217),  "bg_bottom": (139, 92, 246),  "neon": (221, 214, 254)},
]


# ---------------------------------------------------------------------------
# 2. DIMENSION CALCULATOR & BUNDLED FANCY FONT LOADER
# ---------------------------------------------------------------------------
def calculate_cover_dimensions(page_count: int) -> dict:
    """Computes full-wrap KDP dimensions in inches and 300 DPI pixels."""
    spine_in = page_count * WHITE_PAPER_THICKNESS_IN
    total_w_in = (TRIM_W_IN * 2) + spine_in + (BLEED_IN * 2)
    total_h_in = TRIM_H_IN + (BLEED_IN * 2)
    return {
        "page_count": page_count,
        "spine_in": spine_in,
        "width_px": int(round(total_w_in * DPI)),
        "height_px": int(round(total_h_in * DPI)),
        "spine_px": int(round(spine_in * DPI)),
        "trim_w_px": int(round(TRIM_W_IN * DPI)),
        "trim_h_px": int(round(TRIM_H_IN * DPI)),
        "bleed_px": int(round(BLEED_IN * DPI)),
    }


def load_fancy_font(font_name: str, size: int, fonts_dir: str = "assets/fonts") -> ImageFont.FreeTypeFont:
    """
    Downloads and caches kid-friendly display fonts (Luckiest Guy, Fredoka Bold)
    so covers never fall back to flat system Arial.
    """
    os.makedirs(fonts_dir, exist_ok=True)
    font_urls = {
        "LuckiestGuy.ttf": "https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf",
        "LuckiestGuy-Regular.ttf": "https://github.com/google/fonts/raw/main/apache/luckiestguy/LuckiestGuy-Regular.ttf",
        "Fredoka-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/fredoka/Fredoka%5Bwdth%2Cwght%5D.ttf",
    }
    ttf_path = os.path.join(fonts_dir, font_name)
    if not os.path.exists(ttf_path) and font_name in font_urls:
        try:
            urllib.request.urlretrieve(font_urls[font_name], ttf_path)
        except Exception:
            pass

    # Try exact path, then alternative names
    for cand in [ttf_path, os.path.join(fonts_dir, "LuckiestGuy.ttf"), os.path.join(fonts_dir, "Fredoka-Bold.ttf")]:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass

    return ImageFont.load_default()


def pull_remote_asset(url_or_path: str | Path | None, dest_path: str | Path) -> str | None:
    """
    Downloads a presigned URL exported from Adobe Express MCP (or any remote image URL)
    into the local workspace so external designs integrate seamlessly.
    """
    if not url_or_path:
        return None
    p_str = str(url_or_path)
    if os.path.exists(p_str):
        return p_str
    if p_str.startswith(("http://", "https://")):
        dest_p = Path(dest_path)
        dest_p.parent.mkdir(parents=True, exist_ok=True)
        try:
            urllib.request.urlretrieve(p_str, str(dest_p))
            return str(dest_p)
        except Exception as exc:
            print(f"[Warning] Failed to pull remote asset {url_or_path}: {exc}")
            return None
    return None


# ---------------------------------------------------------------------------
# 3. ALPHA ISOLATION & STICKER CONTOUR ENGINE
# ---------------------------------------------------------------------------
def isolate_with_sticker_border(
    img_path: str | Path,
    stroke_size: int = 15,
    tolerance: int = 25,
    remove_trapped_pockets: bool = True,
    min_pocket_area: int = 1800,
) -> Image.Image:
    """
    Removes solid white outer backgrounds AND large trapped white pockets (e.g., between
    the Tiger and Monkey) while preserving small interior whites (eyes, teeth) via
    SciPy/NumPy connected-component filtering, then generates a smooth white sticker contour.
    """
    with Image.open(str(img_path)) as img:
        if img.mode == "RGBA":
            extrema = img.getextrema()
            if len(extrema) == 4 and extrema[3][0] == 0:
                # Already transparent RGBA image, preserve clean alpha
                return img.copy()
        return extract_with_sticker_contour(
            image=img,
            tolerance=tolerance,
            contour_radius=stroke_size,
            blur_radius=1.5,
            remove_trapped_pockets=remove_trapped_pockets,
            min_pocket_area=min_pocket_area,
        )


# ---------------------------------------------------------------------------
# 4. DRAWING HELPERS (NEON GLOW, 3D EXTRUSION & SPARKLE TYPOGRAPHY)
# ---------------------------------------------------------------------------
def draw_gradient_background(width: int, height: int, bg_top: tuple, bg_bottom: tuple) -> Image.Image:
    """Generates a smooth vertical color gradient tailored to the volume's theme palette."""
    base = Image.new("RGBA", (width, height), bg_top + (255,))
    draw = ImageDraw.Draw(base)
    for y in range(height):
        ratio = y / max(1, height - 1)
        r = int(bg_top[0] + (bg_bottom[0] - bg_top[0]) * ratio)
        g = int(bg_top[1] + (bg_bottom[1] - bg_top[1]) * ratio)
        b = int(bg_top[2] + (bg_bottom[2] - bg_top[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return base


def draw_rolling_hills(canvas: Image.Image, height: int, width: int) -> None:
    """Draws layered organic rolling green hills along the bottom edge."""
    draw = ImageDraw.Draw(canvas)
    hill_top = int(height * 0.77)

    # Midground hill (#22C55E)
    pts_mid = [
        (0, hill_top + 60),
        (int(width * 0.28), hill_top + 10),
        (int(width * 0.58), hill_top + 50),
        (int(width * 0.82), hill_top + 15),
        (width, hill_top + 45),
        (width, height),
        (0, height),
    ]
    draw.polygon(pts_mid, fill=GRASS_MID_COLOR)

    # Foreground hill (#4ADE80)
    pts_fore = [
        (0, hill_top + 120),
        (int(width * 0.22), hill_top + 70),
        (int(width * 0.50), hill_top + 110),
        (int(width * 0.76), hill_top + 65),
        (width, hill_top + 95),
        (width, height),
        (0, height),
    ]
    draw.polygon(pts_fore, fill=GRASS_COLOR)


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



def draw_crayon_graphic(length: int = 240, width: int = 46, color: tuple = (255, 204, 0, 255)) -> Image.Image:
    """Creates a colorful wax crayon with wrapper stripes and conical tip."""
    tip_len = int(width * 1.1)
    im = Image.new("RGBA", (length + tip_len, width), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    # Conical wax tip
    d.polygon([(length, 0), (length + tip_len, width // 2), (length, width)], fill=color)
    # Main wax body
    d.rectangle([0, 0, length, width], fill=color)
    # Paper wrapper band
    w_start = int(length * 0.16)
    w_end = int(length * 0.84)
    d.rectangle([w_start, 0, w_end, width], fill=(255, 255, 255, 75))
    d.line([(w_start + 8, 0), (w_start + 8, width)], fill=(0, 0, 0, 85), width=3)
    d.line([(w_end - 8, 0), (w_end - 8, width)], fill=(0, 0, 0, 85), width=3)

    return im


def draw_crayons_cluster(canvas: Image.Image, x: int, y: int) -> None:
    """Draws 3 tilted wax crayons (Yellow, Red, Blue) floating on the left side."""
    crayons = [
        ((255, 204, 0, 255), 26, 0, 0),
        ((239, 68, 68, 255), 26, 12, 54),
        ((56, 189, 248, 255), 26, 24, 108),
    ]
    for col, angle, dx, dy in crayons:
        cr = draw_crayon_graphic(length=220, width=42, color=col)
        cr_rot = cr.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas.paste(cr_rot, (x + dx, y + dy), cr_rot)


def draw_neon_sparkle_text(
    canvas: Image.Image,
    center_pos: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill_color: tuple,
    outline_color: tuple,
    neon_color: tuple,
    outline_width: int = 10,
    extrusion_depth: int = 12,
    add_sparkles: bool = True,
) -> None:
    """
    Renders premium children's cover typography featuring:
    1. Soft Gaussian-blurred Neon Outer Aura
    2. Diagonal 3D Block Extrusion
    3. Smooth Radial Sticker Stroke
    4. Inner Fill + Top Glossy Specular Highlight
    5. Decorative 4-Point Vector Sparkle Stars
    """
    cx, cy = center_pos
    dummy_draw = ImageDraw.Draw(canvas)
    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad = outline_width * 3 + extrusion_depth + 45

    layer_w, layer_h = tw + pad * 2, th + pad * 2
    tx, ty = pad - bbox[0], pad - bbox[1]

    # 1. Neon Outer Glow Layer
    glow_layer = Image.new("RGBA", (layer_w, layer_h), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    for dx in range(-outline_width - 8, outline_width + 9, 4):
        for dy in range(-outline_width - 8, outline_width + 9, 4):
            glow_draw.text((tx + dx, ty + dy), text, font=font, fill=neon_color + (160,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=14))

    # 2. 3D Extrusion + Outline + Fill Layer
    text_layer = Image.new("RGBA", (layer_w, layer_h), (0, 0, 0, 0))
    t_draw = ImageDraw.Draw(text_layer)

    # Extruded 3D shadow trail
    for depth in range(extrusion_depth, 0, -1):
        t_draw.text((tx + depth, ty + depth), text, font=font, fill=(25, 15, 10, 220))

    # Circular outline stroke
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx * dx + dy * dy <= outline_width * outline_width:
                t_draw.text((tx + dx, ty + dy), text, font=font, fill=outline_color)

    # Main vibrant fill
    t_draw.text((tx, ty), text, font=font, fill=fill_color)

    # Top specular gloss highlight
    t_draw.text((tx - 2, ty - 3), text, font=font, fill=(255, 255, 255, 95))

    # 3. Sparkle Star Accents on Text Corners
    if add_sparkles:
        draw_sparkle_star(t_draw, tx + 14, ty + 10, outer_r=22, inner_r=5)
        draw_sparkle_star(t_draw, tx + tw - 12, ty + 16, outer_r=24, inner_r=5)
        draw_sparkle_star(t_draw, tx + tw // 2, ty - 10, outer_r=16, inner_r=4)

    combined = Image.alpha_composite(glow_layer, text_layer)
    paste_x = cx - layer_w // 2
    paste_y = cy - layer_h // 2
    canvas.alpha_composite(combined, (paste_x, paste_y))


# ---------------------------------------------------------------------------
# 5. TWO-PASS FRONT COVER GENERATOR & BACK COVER REPLICA GRID
# ---------------------------------------------------------------------------
def render_two_panel_activity_card(
    card_w: int,
    card_h: int,
    color_path: str | Path | None,
    lineart_path: str | Path | None,
    pill_text: str = "TIGER",
    pill_color: tuple = (255, 73, 73, 255),
) -> Image.Image:
    """
    Renders the premium two-panel floating activity card:
      - Left sub-panel: 'Color Guide' with the complete, uncropped full-color subject.
      - Right sub-panel: 'Color Me!' with the complete, uncropped B&W coloring lineart.
      - Top pill badge with theme item name.
      - Crisp vector borders and drop shadow.
    """
    card = Image.new("RGBA", (card_w + 16, card_h + 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)

    # 1. Soft Drop Shadow
    draw.rounded_rectangle([10, 12, card_w + 10, card_h + 12], radius=26, fill=(0, 0, 0, 65))

    # 2. Main Crisp White Container
    draw.rounded_rectangle([2, 2, card_w + 2, card_h + 2], radius=26, fill="white", outline="#CBD5E1", width=4)

    # 3. Top Theme Pill Badge
    pill_w = min(int(card_w * 0.52), 260)
    pill_h = 44
    px0 = (card_w + 4 - pill_w) // 2
    py0 = 14
    draw.rounded_rectangle([px0, py0, px0 + pill_w, py0 + pill_h], radius=14, fill=pill_color)
    badge_f = load_fancy_font("Fredoka-Bold.ttf", 26)
    b_bb = draw.textbbox((0, 0), pill_text, font=badge_f)
    bw, bh = b_bb[2] - b_bb[0], b_bb[3] - b_bb[1]
    draw.text((px0 + (pill_w - bw) // 2, py0 + (pill_h - bh) // 2 - 2), pill_text, fill="white", font=badge_f)

    # 4. Dimensions for the Two Sub-Panels
    margin_x = 16
    margin_bottom = 16
    top_y = py0 + pill_h + 12
    gap = 12
    avail_w = card_w - (margin_x * 2) - gap
    panel_w = avail_w // 2
    panel_h = card_h - top_y - margin_bottom

    # Sub-header font
    hdr_font = load_fancy_font("Fredoka-Bold.ttf", 22)

    # --- LEFT SUB-PANEL: COLOR GUIDE ---
    lx0 = margin_x + 2
    ly0 = top_y
    lx1 = lx0 + panel_w
    ly1 = ly0 + panel_h
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=16, fill="#F8FAFC", outline="#E2E8F0", width=3)
    draw.rounded_rectangle([lx0 + 6, ly0 + 6, lx1 - 6, ly0 + 36], radius=10, fill="#FEF3C7")
    hdr_txt = "Color Guide"
    h_bb = draw.textbbox((0, 0), hdr_txt, font=hdr_font)
    draw.text((lx0 + (panel_w - (h_bb[2] - h_bb[0])) // 2, ly0 + 8), hdr_txt, fill="#B45309", font=hdr_font)

    if color_path and os.path.exists(str(color_path)):
        try:
            with Image.open(str(color_path)) as c_im:
                c_rgba = c_im.convert("RGBA")
                max_w = panel_w - 16
                max_h = panel_h - 48
                sc = min(max_w / c_rgba.width, max_h / c_rgba.height)
                nw, nh = max(1, int(c_rgba.width * sc)), max(1, int(c_rgba.height * sc))
                c_res = c_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
                card.paste(c_res, (lx0 + (panel_w - nw) // 2, ly0 + 40 + (max_h - nh) // 2), c_res)
        except Exception as e:
            print(f"[Warning] Failed to render color guide in card: {e}")

    # --- RIGHT SUB-PANEL: COLOR ME! ---
    rx0 = lx1 + gap
    ry0 = top_y
    rx1 = rx0 + panel_w
    ry1 = ry0 + panel_h
    draw.rounded_rectangle([rx0, ry0, rx1, ry1], radius=16, fill="#FFFFFF", outline="#0284C7", width=3)
    draw.rounded_rectangle([rx0 + 6, ry0 + 6, rx1 - 6, ry0 + 36], radius=10, fill="#E0F2FE")
    hdr_txt2 = "Color Me!"
    h_bb2 = draw.textbbox((0, 0), hdr_txt2, font=hdr_font)
    draw.text((rx0 + (panel_w - (h_bb2[2] - h_bb2[0])) // 2, ry0 + 8), hdr_txt2, fill="#0369A1", font=hdr_font)

    if lineart_path and os.path.exists(str(lineart_path)):
        try:
            with Image.open(str(lineart_path)) as l_im:
                l_rgba = l_im.convert("RGBA")
                max_w = panel_w - 16
                max_h = panel_h - 48
                sc = min(max_w / l_rgba.width, max_h / l_rgba.height)
                nw, nh = max(1, int(l_rgba.width * sc)), max(1, int(l_rgba.height * sc))
                l_res = l_rgba.resize((nw, nh), Image.Resampling.LANCZOS)
                card.paste(l_res, (rx0 + (panel_w - nw) // 2, ry0 + 40 + (max_h - nh) // 2), l_res)
        except Exception as e:
            print(f"[Warning] Failed to render lineart in card: {e}")

    return card


def render_single_front_cover(
    vol_meta: dict,
    width_px: int,
    height_px: int,
    logo_path: str | Path | None = None,
    hero_path: str | Path | None = None,
    color_guide_path: str | Path | None = None,
    lineart_path: str | Path | None = None,
    inset_path: str | Path | None = None,
) -> Image.Image:
    """
    PASS 1: Renders a complete, standalone Front Cover for any volume in SERIES_TITLES.
    This image is used both as the Front Cover of that volume AND as the exact miniature
    cover thumbnail on the Back Cover of all volumes in the series.
    """
    front = draw_gradient_background(width_px, height_px, vol_meta["bg_top"], vol_meta["bg_bottom"])
    # 1. Dense vector pattern collage (paint splatters, doodles, bubbles)
    draw_pattern_collage(front, width_px, height_px, is_spread=False)
    # 2. Layered green rolling hills
    draw_rolling_hills(front, height_px, width_px)
    # 3. Storybook checkered outer border
    draw_checkered_border(front, width_px, height_px, tile_size=44, rows=2)
    draw = ImageDraw.Draw(front)
    cx = width_px // 2

    # Decorative background sparkle stars
    for sx, sy, sr in [
        (int(width_px * 0.14), 620, 16),
        (int(width_px * 0.86), 660, 18),
        (int(width_px * 0.22), 920, 14),
        (int(width_px * 0.80), 980, 15),
    ]:
        draw_sparkle_star(draw, sx, sy, outer_r=sr, inner_r=3)

    # 1. Top Brand Logo (Auto-isolated with smooth sticker contour)
    if logo_path and os.path.exists(str(logo_path)):
        logo_img = isolate_with_sticker_border(str(logo_path), stroke_size=12, remove_trapped_pockets=False)
        logo_img.thumbnail((480, 480), Image.Resampling.LANCZOS)
        front.paste(logo_img, (cx - logo_img.width // 2, 85), logo_img)

    # 2. Fancy Bundled Display Fonts (Neon + 3D + Sparkles)
    font_main = load_fancy_font("LuckiestGuy.ttf", 205)
    font_subject = load_fancy_font("LuckiestGuy.ttf", 238)

    # "Copy to Color" — Directly Below Logo: Fancy Extruded 3D Display Text with Sparkles
    draw_neon_sparkle_text(
        front,
        (cx, 630),
        "Copy to Color",
        font_main,
        fill_color=(255, 255, 255, 255),
        outline_color=NAVY_TEXT,
        neon_color=vol_meta["neon"],
        outline_width=13,
        extrusion_depth=16,
        add_sparkles=True,
    )

    # Subject Title (e.g., "ANIMALS", "ALPHABET", "BIRDS") — Directly Below Series Title
    draw_neon_sparkle_text(
        front,
        (cx, 855),
        vol_meta["title"].upper(),
        font_subject,
        fill_color=YELLOW_TEXT,
        outline_color=(95, 25, 10, 255),
        neon_color=vol_meta["neon"],
        outline_width=14,
        extrusion_depth=18,
        add_sparkles=True,
    )

    # 3. Glossy 3D Crayons (Floating on left edge)
    crayons_ai = Path("assets/cover/crayons_3d.png")
    if crayons_ai.exists():
        try:
            with Image.open(str(crayons_ai)) as cr_im:
                cr_rgba = cr_im.convert("RGBA")
                cr_w = int(width_px * 0.28)
                cr_h = int(cr_rgba.height * (cr_w / cr_rgba.width))
                cr_res = cr_rgba.resize((cr_w, cr_h), Image.Resampling.LANCZOS)
                front.paste(cr_res, (int(width_px * 0.03), int(height_px * 0.32)), cr_res)
        except Exception:
            draw_crayons_cluster(front, int(width_px * 0.04), int(height_px * 0.33))
    else:
        draw_crayons_cluster(front, int(width_px * 0.04), int(height_px * 0.33))

    # 4. Premium Two-Panel Activity Card (Color Guide | Color Me!)
    card_w = int(width_px * 0.44)
    card_h = int(height_px * 0.32)
    resolved_col = color_guide_path or inset_path
    resolved_line = lineart_path
    if not resolved_col:
        v_col = Path(f"assets/series_ai/{vol_meta['id']}/subj_01_color.png")
        if v_col.exists():
            resolved_col = v_col
    if not resolved_line:
        v_line = Path(f"assets/series_ai/{vol_meta['id']}/subj_01_lineart.png")
        if v_line.exists():
            resolved_line = v_line

    activity_card = render_two_panel_activity_card(
        card_w=card_w,
        card_h=card_h,
        color_path=resolved_col,
        lineart_path=resolved_line,
        pill_text=vol_meta.get("pill", "COLOR"),
        pill_color=vol_meta["bg_top"],
    )
    cx0 = width_px - activity_card.width - int(width_px * 0.04)
    cy0 = int(height_px * 0.34)
    front.paste(activity_card, (cx0, cy0), activity_card)

    # 5. Optional Thematic Foreground Framing (ONLY for Volume 2: Animals)
    # Layered BEFORE hero so the hero character is never occluded!
    if vol_meta.get("theme_environment") == "jungle" or vol_meta.get("id") == "vol_02":
        jungle_frame = Path("assets/cover/jungle_foreground_frame.png")
        if jungle_frame.exists():
            try:
                with Image.open(str(jungle_frame)) as j_im:
                    j_rgba = j_im.convert("RGBA")
                    jw = width_px
                    jh = int(j_rgba.height * (jw / j_rgba.width))
                    j_res = j_rgba.resize((jw, jh), Image.Resampling.LANCZOS)
                    front.paste(j_res, (0, height_px - jh), j_res)
            except Exception as e:
                print(f"[Warning] Failed to render jungle foreground frame: {e}")

    # 6. Hero Character Illustration (Layered on top of background & framing, 100% visible!)
    if hero_path and os.path.exists(str(hero_path)):
        hero = isolate_with_sticker_border(str(hero_path), stroke_size=15, remove_trapped_pockets=True)
        # Proportionally scale up to prominently fill the bottom-left area (~60% of trim width)
        target_w = int(width_px * 0.60)
        target_h = int(height_px * 0.46)
        hero_sc = min(target_w / hero.width, target_h / hero.height)
        new_hw = int(hero.width * hero_sc)
        new_hh = int(hero.height * hero_sc)
        hero = hero.resize((new_hw, new_hh), Image.Resampling.LANCZOS)
        hx = int(width_px * 0.04)
        hy = height_px - new_hh - 80
        front.paste(hero, (hx, hy), hero)

    return front


def prebuild_all_series_front_covers(
    trim_w_px: int = int(round(8.5 * DPI)),
    trim_h_px: int = int(round(11.0 * DPI)),
    logo_path: str | Path | None = None,
    thumbnails_dir: str = "assets/cover_thumbnails",
    output_fronts_dir: str = "local_builds/series_fronts",
    force: bool = False,
) -> dict[str, Image.Image]:
    """
    PASS 1 BATCH RUNNER: Generates all 12 standalone Front Covers first and saves them
    to `local_builds/series_fronts/{id}_front.png` so the Back Cover grid can embed
    authentic miniature replicas of every book's real front cover.
    """
    os.makedirs(output_fronts_dir, exist_ok=True)
    rendered_fronts: dict[str, Image.Image] = {}

    # Fast disk-cache check: if all 12 covers already exist and not forced, load from disk
    if not force:
        all_exist = all(
            os.path.exists(os.path.join(output_fronts_dir, f"{item['id']}_front.png"))
            and os.path.getsize(os.path.join(output_fronts_dir, f"{item['id']}_front.png")) > 1000
            for item in SERIES_TITLES
        )
        if all_exist:
            for item in SERIES_TITLES:
                fp = os.path.join(output_fronts_dir, f"{item['id']}_front.png")
                with Image.open(fp) as im:
                    rendered_fronts[item["id"]] = im.copy()
            return rendered_fronts

    # Standard fallback logo
    resolved_logo = None
    for cand in [logo_path, "assets/logos/pivot_kids_sticker.png", "assets/logos/pivot_kids.png"]:
        if cand and os.path.exists(str(cand)):
            resolved_logo = str(cand)
            break

    for item in SERIES_TITLES:
        vol_id = item["id"]
        out_file = os.path.join(output_fronts_dir, f"{vol_id}_front.png")

        # Resolve hero art and activity card assets
        hero_candidate = None
        color_cand = Path(f"assets/series_ai/{vol_id}/subj_01_color.png")
        lineart_cand = Path(f"assets/series_ai/{vol_id}/subj_01_lineart.png")

        # Resolve dedicated Kid Avatar Hero artwork (prioritizing high-res 1024x1024 sticker)
        for cand in [
            f"assets/cover_heroes/{vol_id}_hero.png",
            f"assets/cover_heroes/{vol_id}.png",
            "assets/cover/hero_tiger_monkey.png" if vol_id == "vol_02" else None,
            "local_builds/animals/assets/tiger_monkey_transparent.png" if vol_id == "vol_02" else None,
            os.path.join(thumbnails_dir, f"{vol_id}.png"),
            f"local_builds/animals/assets/thumbnails/{vol_id}.png",
        ]:
            if cand and os.path.exists(cand):
                hero_candidate = cand
                break

        front_img = render_single_front_cover(
            vol_meta=item,
            width_px=trim_w_px,
            height_px=trim_h_px,
            logo_path=resolved_logo,
            hero_path=hero_candidate,
            color_guide_path=str(color_cand) if color_cand.exists() else None,
            lineart_path=str(lineart_cand) if lineart_cand.exists() else None,
        )
        front_img.save(out_file, "PNG")
        rendered_fronts[vol_id] = front_img
        print(f"  [Pass 1] Rendered Front Cover: {item['vol']} {item['title']} -> {out_file}")

    return rendered_fronts


def render_back_cover_grid(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    start_x: int,
    start_y: int,
    grid_w: int,
    grid_h: int,
    rendered_fronts: dict[str, Image.Image],
) -> None:
    """
    PASS 2 BACK COVER GRID: Places the 12 actual rendered Front Covers into the 4x3
    "Titles in this Series" grid inside a warm ivory container so every miniature book
    on the back cover is a 100% faithful replica of the corresponding volume's front cover.
    """
    # Large light cream / pale ivory container card with drop shadow
    draw.rounded_rectangle(
        [start_x - 14, start_y - 14, start_x + grid_w + 14, start_y + grid_h + 14],
        radius=28,
        fill=(255, 252, 240, 245),
        outline=(254, 215, 170, 255),
        width=4,
    )

    cols, rows = 4, 3
    cell_w = grid_w // cols
    cell_h = grid_h // rows
    badge_font = load_fancy_font("Fredoka-Bold.ttf", 22)

    for idx, item in enumerate(SERIES_TITLES):
        col = idx % cols
        row = idx // cols

        x0 = start_x + col * cell_w + 8
        y0 = start_y + row * cell_h + 8
        card_w = cell_w - 16
        card_h = cell_h - 16

        front_thumb = rendered_fronts.get(item["id"])
        if front_thumb:
            # Resize the actual Front Cover proportionally to fit the miniature book slot
            thumb_copy = front_thumb.copy()
            thumb_copy.thumbnail((card_w, card_h), Image.Resampling.LANCZOS)
            tx = x0 + (card_w - thumb_copy.width) // 2
            ty = y0 + (card_h - thumb_copy.height) // 2

            # 3D book drop shadow
            draw.rounded_rectangle(
                [tx + 6, ty + 8, tx + thumb_copy.width + 6, ty + thumb_copy.height + 8],
                radius=10,
                fill=(20, 10, 5, 80),
            )
            canvas.paste(thumb_copy, (tx, ty), thumb_copy)
            # Crisp white book frame
            draw.rounded_rectangle(
                [tx, ty, tx + thumb_copy.width, ty + thumb_copy.height],
                radius=8,
                outline="white",
                width=4,
            )

            # High-contrast "Vol. #" collector star pill badge at top-right
            bw, bh = 84, 34
            bx, by = tx + thumb_copy.width - bw - 6, ty + 6
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=NAVY_TEXT, outline="white", width=2)
            draw.text((bx + 12, by + 4), item["vol"], fill=YELLOW_TEXT, font=badge_font)



# ---------------------------------------------------------------------------
# 6. MAIN COMPILER FUNCTION (TWO-PASS FULL-WRAP BUILDER)
# ---------------------------------------------------------------------------
def build_kdp_cover(
    page_count: int = 32,
    output_path: str = "local_builds/animals/v1.0-core/animals-cover-spread.pdf",
    active_vol_id: str = "vol_02",
    hero_image_path: str | None = None,
    inset_image_path: str | None = None,
    logo_path: str | None = None,
    thumbnails_dir: str = "assets/cover_thumbnails",
    force_fronts: bool = False,
    rendered_fronts: dict[str, Image.Image] | None = None,
) -> Path:
    """Compiles print-ready Amazon KDP full-wrap paperback cover spread PDF & proof."""
    specs = calculate_cover_dimensions(page_count)
    w, h = specs["width_px"], specs["height_px"]
    spine_w = specs["spine_px"]
    trim_w = specs["trim_w_px"]
    trim_h = specs["trim_h_px"]
    bleed = specs["bleed_px"]

    active_meta = next((item for item in SERIES_TITLES if item["id"] == active_vol_id), SERIES_TITLES[1])

    # Standard fallback logo
    resolved_logo = None
    for cand in [logo_path, "assets/logos/pivot_kids_sticker.png", "assets/logos/pivot_kids.png"]:
        if cand and os.path.exists(str(cand)):
            resolved_logo = str(cand)
            break

    # Remote URL resolution for assets (e.g., from Adobe Express MCP presigned URLs)
    resolved_hero = pull_remote_asset(hero_image_path, f"assets/adobe_exports/{active_vol_id}_hero.png")
    resolved_inset = pull_remote_asset(inset_image_path, f"assets/adobe_exports/{active_vol_id}_inset.png")

    if rendered_fronts is None:
        rendered_fronts = prebuild_all_series_front_covers(
            trim_w_px=trim_w,
            trim_h_px=trim_h,
            logo_path=resolved_logo,
            thumbnails_dir=thumbnails_dir,
            force=force_fronts,
        )

    # Override active volume's front cover if high-res hero/inset paths are explicitly supplied
    if resolved_hero or resolved_inset:
        color_cand = Path(f"assets/series_ai/{active_vol_id}/subj_01_color.png")
        lineart_cand = Path(f"assets/series_ai/{active_vol_id}/subj_01_lineart.png")
        active_color = str(color_cand) if color_cand.exists() else resolved_inset
        active_lineart = str(lineart_cand) if lineart_cand.exists() else None
        rendered_fronts[active_vol_id] = render_single_front_cover(
            vol_meta=active_meta,
            width_px=trim_w,
            height_px=trim_h,
            logo_path=resolved_logo,
            hero_path=resolved_hero,
            color_guide_path=active_color,
            lineart_path=active_lineart,
            inset_path=resolved_inset if not color_cand.exists() else None,
        )

    print(f"[Pass 2] Assembling Full-Wrap Spread: {w}x{h} px | Spine: {specs['spine_in']:.3f} in ({spine_w} px)")
    cover = draw_gradient_background(w, h, active_meta["bg_top"], active_meta["bg_bottom"])
    # 1. Overlay dense vector pattern collage across full spread
    draw_pattern_collage(cover, w, h, is_spread=True)
    # 2. Layered green rolling hills
    draw_rolling_hills(cover, h, w)
    # 3. Checkered storybook frame around perimeter of spread
    draw_checkered_border(cover, w, h, tile_size=44, rows=2)

    draw = ImageDraw.Draw(cover)

    back_x_end = bleed + trim_w
    spine_x_start = back_x_end
    spine_x_end = spine_x_start + spine_w
    front_x_start = spine_x_end

    # ---------------- BACK COVER SECTION ----------------
    # 1. Top Pivot Kids logo (Top-left with safe margins, no collision)
    if resolved_logo and os.path.exists(resolved_logo):
        logo_back = isolate_with_sticker_border(resolved_logo, stroke_size=10, remove_trapped_pockets=False)
        logo_back.thumbnail((190, 190), Image.Resampling.LANCZOS)
        cover.paste(logo_back, (bleed + int(0.42 * DPI), int(0.40 * DPI)), logo_back)

    # 2. Top "TITLES IN THIS SERIES" curved ribbon banner
    banner_font = load_fancy_font("Fredoka-Bold.ttf", 46)
    ribbon_cx = bleed + trim_w // 2 + 25
    ribbon_cy = int(0.52 * DPI)
    draw_curved_ribbon_header(cover, ribbon_cx, ribbon_cy, "TITLES IN THIS SERIES", banner_font)

    # 3. "CAN YOU COLLECT THEM ALL?" banner pill
    pill_w = int(trim_w * 0.52)
    pill_h = 72
    px0 = bleed + int(0.18 * trim_w)
    py0 = int(0.92 * DPI)
    draw.rounded_rectangle([px0, py0, px0 + pill_w, py0 + pill_h], radius=24, fill=(254, 240, 138, 255), outline=(220, 38, 38, 255), width=5)
    collect_font = load_fancy_font("Fredoka-Bold.ttf", 30)
    coll_txt = "CAN YOU COLLECT THEM ALL?"
    cbb = draw.textbbox((0, 0), coll_txt, font=collect_font)
    tw = cbb[2] - cbb[0]
    th = cbb[3] - cbb[1]
    tx = px0 + (pill_w - tw) // 2
    ty = py0 + (pill_h - th) // 2 - 2
    draw.text((tx, ty), coll_txt, fill=(185, 28, 28, 255), font=collect_font)
    draw_sparkle_star(draw, tx - 32, py0 + pill_h // 2, outer_r=16, inner_r=4, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))
    draw_sparkle_star(draw, tx + tw + 32, py0 + pill_h // 2, outer_r=16, inner_r=4, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))

    # 4. 4x3 Grid of authentic Front Covers
    grid_start_y = int(1.22 * DPI)
    grid_w = int(trim_w * 0.90)
    grid_h = int(h * 0.60)
    render_back_cover_grid(cover, draw, bleed + int(trim_w * 0.05), grid_start_y, grid_w, grid_h, rendered_fronts)

    # Mascot Boy waving star wand (Layered ON TOP of grid corner, placed comfortably below top border with hat fully visible)
    mascot_path = Path("assets/cover/mascot_kid_wand.png")
    if mascot_path.exists():
        try:
            with Image.open(str(mascot_path)) as m_im:
                m_rgba = m_im.convert("RGBA")
                m_target_w = int(trim_w * 0.22)
                m_target_h = int(m_rgba.height * (m_target_w / m_rgba.width))
                m_res = m_rgba.resize((m_target_w, m_target_h), Image.Resampling.LANCZOS)
                mx = bleed + int(0.74 * trim_w)
                my = int(0.76 * DPI)
                cover.paste(m_res, (mx, my), m_res)
        except Exception as e:
            print(f"[Warning] Failed to render back-cover mascot: {e}")

    # 5. Collector's container (Bottom-left)
    c_w, c_h = int(trim_w * 0.54), 80
    cx0 = bleed + int(0.4 * DPI)
    cy0 = h - bleed - int(1.55 * DPI)
    draw.rounded_rectangle([cx0, cy0, cx0 + c_w, cy0 + c_h], radius=24, fill="#16A34A", outline="#15803D", width=4)
    coll_font = load_fancy_font("Fredoka-Bold.ttf", 28)
    draw_sparkle_star(draw, cx0 + 26, cy0 + c_h // 2, outer_r=14, inner_r=3, fill=(255, 255, 255, 255), outline=(255, 240, 130, 255))
    draw_sparkle_star(draw, cx0 + c_w - 26, cy0 + c_h // 2, outer_r=14, inner_r=3, fill=(255, 255, 255, 255), outline=(255, 240, 130, 255))
    c_txt = "Collector's Series of 12 Interactive Titles"
    c_bb = draw.textbbox((0, 0), c_txt, font=coll_font)
    draw.text((cx0 + (c_w - (c_bb[2] - c_bb[0])) // 2, cy0 + 22), c_txt, fill="white", font=coll_font)

    # Marketing blurb below container
    blurb_f = load_fancy_font("Fredoka-Bold.ttf", 26)
    draw.text((cx0 + 8, cy0 + 95), "A playful, easy coloring series designed for early learners", fill="white", font=blurb_f)
    draw.text((cx0 + 8, cy0 + 130), "to copy, color, and play!", fill="white", font=blurb_f)

    # 6. Barcode Safe Area (2.0 x 1.2 in = 600 x 360 px strictly preserved)
    bc_w, bc_h = int(2.0 * DPI), int(1.2 * DPI)
    bc_x = back_x_end - bc_w - int(0.5 * DPI)
    bc_y = h - bleed - bc_h - int(0.5 * DPI)
    draw.rounded_rectangle([bc_x, bc_y, bc_x + bc_w, bc_y + bc_h], radius=12, fill="white", outline="#CCCCCC", width=2)
    barcode_f = load_fancy_font("Fredoka-Bold.ttf", 24)
    for bx in range(bc_x + 30, bc_x + bc_w - 30, 8):
        bar_w = 4 if (bx % 16 == 0) else 2
        draw.line([(bx, bc_y + 25), (bx, bc_y + bc_h - 65)], fill="black", width=bar_w)
    draw.text((bc_x + 220, bc_y + bc_h - 45), "2.0 x 1.2 in", fill="#666666", font=barcode_f)

    # Copyright notice
    copy_f = load_fancy_font("Fredoka-Bold.ttf", 22)
    draw.text((bc_x - 30, bc_y + bc_h + 30), "© The Pivot Digital Publication. All rights reserved.", fill="white", font=copy_f)


    # ---------------- SPINE SECTION ----------------
    # Amazon KDP rule: strictly suppress spine text if page count < 79
    if page_count >= 79 and specs["spine_in"] >= 0.18:
        spine_font = load_fancy_font("Fredoka-Bold.ttf", 36)
        spine_text = f"THE PIVOT KIDS   |   Copy to Color: {active_meta['title']}   |   {active_meta['vol']}"
        # Render vertical spine text
        text_im = Image.new("RGBA", (h, spine_w), (0, 0, 0, 0))
        t_d = ImageDraw.Draw(text_im)
        t_bbox = t_d.textbbox((0, 0), spine_text, font=spine_font)
        st_w = t_bbox[2] - t_bbox[0]
        st_h = t_bbox[3] - t_bbox[1]
        t_d.text(((h - st_w) // 2, (spine_w - st_h) // 2 - 4), spine_text, fill="white", font=spine_font)
        rot_spine = text_im.rotate(270, expand=True)
        cover.paste(rot_spine, (spine_x_start, 0), rot_spine)
    else:
        print(f"[KDP Compliance] Page count ({page_count}) < 79: Spine text automatically omitted per Amazon KDP rules.")

    # ---------------- FRONT COVER SECTION ----------------
    active_front = rendered_fronts[active_vol_id].resize((trim_w + bleed, h), Image.Resampling.LANCZOS)
    cover.paste(active_front, (front_x_start, 0), active_front)

    # Save Output PDF and PNG proof
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    cover.convert("RGB").save(str(out_p), "PDF", resolution=DPI)
    proof_path = out_p.parent / f"{out_p.stem}-proof.png"
    cover.save(str(proof_path), "PNG")
    print(f"\n[OK] Full-wrap Cover Spread compiled: {out_p}")
    print(f"[OK] 300 DPI Preview Proof saved: {proof_path}")

    return out_p


def build_all_12_series_covers(
    page_count: int = 32,
    logo_path: str | Path | None = None,
    thumbnails_dir: str = "assets/cover_thumbnails",
    output_dir: str = "local_builds/series_covers_32p",
    force_fronts: bool = False,
) -> list[Path]:
    """
    Compiles all 12 standalone Front Covers (Pass 1) and all 12 Full-Wrap KDP Spreads (Pass 2)
    for the entire 32-page series in a single automated batch.
    """
    specs = calculate_cover_dimensions(page_count)
    out_d = Path(output_dir)
    out_d.mkdir(parents=True, exist_ok=True)

    resolved_logo = None
    for cand in [logo_path, "assets/logos/pivot_kids_sticker.png", "assets/logos/pivot_kids.png"]:
        if cand and os.path.exists(str(cand)):
            resolved_logo = str(cand)
            break

    print(f"\n[Batch Cover Runner] Pre-rendering all 12 series front covers (Pass 1)...")
    rendered_fronts = prebuild_all_series_front_covers(
        trim_w_px=specs["trim_w_px"],
        trim_h_px=specs["trim_h_px"],
        logo_path=resolved_logo,
        thumbnails_dir=thumbnails_dir,
        force=force_fronts,
    )

    generated: list[Path] = []
    print(f"\n[Batch Cover Runner] Compiling all 12 full-wrap cover spreads (Pass 2)...")
    for item in SERIES_TITLES:
        vol_id = item["id"]
        slug = item["title"].lower()
        out_pdf = out_d / f"{vol_id}_{slug}_fullwrap_{page_count}p.pdf"
        p = build_kdp_cover(
            page_count=page_count,
            output_path=str(out_pdf),
            active_vol_id=vol_id,
            logo_path=resolved_logo,
            thumbnails_dir=thumbnails_dir,
            force_fronts=False,
            rendered_fronts=rendered_fronts,
        )
        generated.append(p)

    print(f"\n[Batch Cover Runner] Successfully compiled {len(generated)} full-wrap cover spreads into {out_d}")
    return generated


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Automated KDP Full-Wrap Cover Spread Generator")
    parser.add_argument("--vol-id", default="vol_02", help="Active volume ID (e.g. vol_01 to vol_12)")
    parser.add_argument("--page-count", type=int, default=32, help="Page count for spine calculation (32 or 80, default 32)")
    parser.add_argument("--output", default=None, help="Output PDF path")
    parser.add_argument("--hero", default=None, help="Path or remote URL to hero illustration")
    parser.add_argument("--inset", default=None, help="Path or remote URL to inset illustration")
    parser.add_argument("--logo", default=None, help="Path to brand logo")
    parser.add_argument("--all", action="store_true", help="Compile full spreads for all 12 series volumes")
    parser.add_argument("--force-fronts", action="store_true", help="Force re-rendering of all front covers")

    args = parser.parse_args()

    if args.all:
        build_all_12_series_covers(
            page_count=args.page_count,
            logo_path=args.logo,
            force_fronts=args.force_fronts,
        )
    else:
        hero_default = (
            f"assets/cover_heroes/{args.vol_id}_hero.png"
            if os.path.exists(f"assets/cover_heroes/{args.vol_id}_hero.png")
            else "local_builds/animals/assets/tiger_monkey_transparent.png"
        )
        color_ai = f"assets/series_ai/{args.vol_id}/subj_01_color.png"
        inset_default = color_ai if os.path.exists(color_ai) else None
        hero_p = args.hero or (hero_default if os.path.exists(hero_default) and args.vol_id == "vol_02" else None)
        inset_p = args.inset or inset_default
        out_p = args.output or f"local_builds/animals/v1.0-core/animals-cover-spread-{args.page_count}p.pdf"

        build_kdp_cover(
            page_count=args.page_count,
            output_path=out_p,
            active_vol_id=args.vol_id,
            hero_image_path=hero_p,
            inset_image_path=inset_p,
            logo_path=args.logo,
            force_fronts=args.force_fronts,
        )
