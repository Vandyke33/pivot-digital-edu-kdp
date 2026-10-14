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
    {"id": "vol_02", "vol": "Vol. 2",  "title": "Animals",    "pill": "TIGER",     "bg_top": (255, 73, 73),   "bg_bottom": (255, 126, 71),  "neon": (255, 235, 120)},
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


def draw_sparkle_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, outer_r: int = 22, inner_r: int = 5) -> None:
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
    draw.polygon(pts, fill=(255, 255, 255, 255), outline=(255, 240, 130, 255))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255, 255))


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
def render_single_front_cover(
    vol_meta: dict,
    width_px: int,
    height_px: int,
    logo_path: str | Path | None = None,
    hero_path: str | Path | None = None,
    inset_path: str | Path | None = None,
) -> Image.Image:
    """
    PASS 1: Renders a complete, standalone Front Cover for any volume in SERIES_TITLES.
    This image is used both as the Front Cover of that volume AND as the exact miniature
    cover thumbnail on the Back Cover of all volumes in the series.
    """
    front = draw_gradient_background(width_px, height_px, vol_meta["bg_top"], vol_meta["bg_bottom"])
    draw_rolling_hills(front, height_px, width_px)
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
        logo_img.thumbnail((440, 440), Image.Resampling.LANCZOS)
        front.paste(logo_img, (cx - logo_img.width // 2, 90), logo_img)

    # 2. Fancy Bundled Display Fonts (Neon + 3D + Sparkles)
    font_main = load_fancy_font("LuckiestGuy.ttf", 168)
    font_subject = load_fancy_font("LuckiestGuy.ttf", 195)

    # "Copy to Color" — Directly Below Logo: Fancy Extruded 3D Display Text with Sparkles
    draw_neon_sparkle_text(
        front,
        (cx, 630),
        "Copy to Color",
        font_main,
        fill_color=(255, 255, 255, 255),
        outline_color=NAVY_TEXT,
        neon_color=vol_meta["neon"],
        outline_width=12,
        extrusion_depth=14,
        add_sparkles=True,
    )

    # Subject Title (e.g., "ANIMALS", "ALPHABET", "BIRDS") — Directly Below Series Title
    draw_neon_sparkle_text(
        front,
        (cx, 840),
        vol_meta["title"].upper(),
        font_subject,
        fill_color=YELLOW_TEXT,
        outline_color=(95, 25, 10, 255),
        neon_color=vol_meta["neon"],
        outline_width=13,
        extrusion_depth=16,
        add_sparkles=True,
    )

    # 3. Tilted Wax Crayons (Floating on left edge)
    draw_crayons_cluster(front, int(width_px * 0.04), int(height_px * 0.33))

    # 4. Inset "Before & After" Activity Preview Card
    card_w, card_h = int(width_px * 0.38), int(height_px * 0.31)
    cx0, cy0 = width_px - card_w - int(width_px * 0.05), int(height_px * 0.36)
    # Card shadow
    draw.rounded_rectangle([cx0 + 8, cy0 + 10, cx0 + card_w + 8, cy0 + card_h + 10], radius=28, fill=(0, 0, 0, 55))
    # Card body
    draw.rounded_rectangle([cx0, cy0, cx0 + card_w, cy0 + card_h], radius=28, fill="white", outline="#E2E8F0", width=5)

    # Pill badge inside activity card
    pill_w = int(card_w * 0.56)
    px0 = cx0 + (card_w - pill_w) // 2
    draw.rounded_rectangle([px0, cy0 + 16, px0 + pill_w, cy0 + 64], radius=16, fill=vol_meta["bg_top"])
    badge_f = load_fancy_font("Fredoka-Bold.ttf", 32)
    b_txt = vol_meta.get("pill", "COLOR")
    b_bb = draw.textbbox((0, 0), b_txt, font=badge_f)
    draw.text((px0 + (pill_w - (b_bb[2] - b_bb[0])) // 2, cy0 + 20), b_txt, fill="white", font=badge_f)

    if inset_path and os.path.exists(str(inset_path)):
        inset_img = Image.open(str(inset_path)).convert("RGBA")
        inset_max_w = card_w - 30
        inset_max_h = card_h - 120
        inset_sc = min(inset_max_w / inset_img.width, inset_max_h / inset_img.height)
        new_iw = int(inset_img.width * inset_sc)
        new_ih = int(inset_img.height * inset_sc)
        inset_img = inset_img.resize((new_iw, new_ih), Image.Resampling.LANCZOS)
        front.paste(inset_img, (cx0 + (card_w - new_iw) // 2, cy0 + 74), inset_img)

        # "Color Guide" and "Color Me!" labels under inset
        lbl_font = load_fancy_font("Fredoka-Bold.ttf", 20)
        draw.text((cx0 + 24, cy0 + card_h - 36), "Color Guide", fill="#64748B", font=lbl_font)
        draw.text((cx0 + card_w - 130, cy0 + card_h - 36), "Color Me!", fill="#0284C7", font=lbl_font)

    # 5. Hero Character Illustration (Isolated with trapped white pockets removed)
    if hero_path and os.path.exists(str(hero_path)):
        hero = isolate_with_sticker_border(str(hero_path), stroke_size=14, remove_trapped_pockets=True)
        # Proportionally scale up/down to prominently fill the bottom-left area
        target_w = int(width_px * 0.58)
        target_h = int(height_px * 0.44)
        hero_sc = min(target_w / hero.width, target_h / hero.height)
        new_hw = int(hero.width * hero_sc)
        new_hh = int(hero.height * hero_sc)
        hero = hero.resize((new_hw, new_hh), Image.Resampling.LANCZOS)
        hx = int(width_px * 0.05)
        hy = height_px - new_hh - 110
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

        # Resolve hero art
        hero_candidate = None
        if vol_id == "vol_02":
            # For animals, use high-res tiger & monkey
            for cand in ["local_builds/animals/assets/tiger_monkey_transparent.png", os.path.join(thumbnails_dir, f"{vol_id}.png")]:
                if os.path.exists(cand):
                    hero_candidate = cand
                    break
            inset_cand = "local_builds/animals/assets/inset_tiger_split.png"
        else:
            cand = os.path.join(thumbnails_dir, f"{vol_id}.png")
            if not os.path.exists(cand):
                cand = f"local_builds/animals/assets/thumbnails/{vol_id}.png"
            hero_candidate = cand if os.path.exists(cand) else None
            inset_cand = hero_candidate

        front_img = render_single_front_cover(
            vol_meta=item,
            width_px=trim_w_px,
            height_px=trim_h_px,
            logo_path=resolved_logo,
            hero_path=hero_candidate,
            inset_path=inset_cand,
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
    "Titles in this Series" grid so every miniature book on the back cover is a 100%
    faithful replica of the corresponding volume's front cover.
    """
    cols, rows = 3, 4
    cell_w = grid_w // cols
    cell_h = grid_h // rows
    badge_font = load_fancy_font("Fredoka-Bold.ttf", 26)

    for idx, item in enumerate(SERIES_TITLES):
        col = idx % cols
        row = idx // cols

        x0 = start_x + col * cell_w + 16
        y0 = start_y + row * cell_h + 12
        card_w = cell_w - 32
        card_h = cell_h - 24

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
                fill=(20, 10, 5, 90),
            )
            canvas.paste(thumb_copy, (tx, ty), thumb_copy)
            # Crisp white book frame
            draw.rounded_rectangle(
                [tx, ty, tx + thumb_copy.width, ty + thumb_copy.height],
                radius=8,
                outline="white",
                width=4,
            )

            # High-contrast "Vol. #" collector pill badge at top-right of each mini cover
            bw, bh = 94, 38
            bx, by = tx + thumb_copy.width - bw - 8, ty + 8
            draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=14, fill=NAVY_TEXT, outline="white", width=2)
            draw.text((bx + 14, by + 5), item["vol"], fill=YELLOW_TEXT, font=badge_font)


# ---------------------------------------------------------------------------
# 6. MAIN COMPILER FUNCTION (TWO-PASS FULL-WRAP BUILDER)
# ---------------------------------------------------------------------------
def build_kdp_cover(
    page_count: int = 80,
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
        rendered_fronts[active_vol_id] = render_single_front_cover(
            vol_meta=active_meta,
            width_px=trim_w,
            height_px=trim_h,
            logo_path=resolved_logo,
            hero_path=resolved_hero,
            inset_path=resolved_inset,
        )

    print(f"[Pass 2] Assembling Full-Wrap Spread: {w}x{h} px | Spine: {specs['spine_in']:.3f} in ({spine_w} px)")
    cover = draw_gradient_background(w, h, active_meta["bg_top"], active_meta["bg_bottom"])
    draw_rolling_hills(cover, h, w)
    draw = ImageDraw.Draw(cover)

    back_x_end = bleed + trim_w
    spine_x_start = back_x_end
    spine_x_end = spine_x_start + spine_w
    front_x_start = spine_x_end

    # ---------------- BACK COVER SECTION ----------------
    # 1. Top Pivot Kids logo (Top-left)
    if resolved_logo and os.path.exists(resolved_logo):
        logo_back = isolate_with_sticker_border(resolved_logo, stroke_size=10, remove_trapped_pockets=False)
        logo_back.thumbnail((230, 230), Image.Resampling.LANCZOS)
        cover.paste(logo_back, (bleed + int(0.35 * DPI), int(0.32 * DPI)), logo_back)

    # 2. Top "TITLES IN THIS SERIES" blue ribbon banner
    banner_w, banner_h = int(trim_w * 0.60), 88
    bx0 = bleed + int(trim_w * 0.35)
    by0 = int(0.6 * DPI)
    draw.rounded_rectangle([bx0, by0, bx0 + banner_w, by0 + banner_h], radius=28, fill="#0077B6", outline="white", width=4)
    banner_font = load_fancy_font("Fredoka-Bold.ttf", 44)
    draw_sparkle_star(draw, bx0 + 36, by0 + banner_h // 2, outer_r=16, inner_r=4)
    draw_sparkle_star(draw, bx0 + banner_w - 36, by0 + banner_h // 2, outer_r=16, inner_r=4)
    b_txt = "TITLES IN THIS SERIES"
    b_bb = draw.textbbox((0, 0), b_txt, font=banner_font)
    draw.text((bx0 + (banner_w - (b_bb[2] - b_bb[0])) // 2, by0 + 16), b_txt, fill="white", font=banner_font)

    # 3. 4x3 Grid of authentic Front Covers
    grid_start_y = int(1.15 * DPI)
    grid_w = int(trim_w * 0.90)
    grid_h = int(h * 0.64)
    render_back_cover_grid(cover, draw, bleed + int(trim_w * 0.05), grid_start_y, grid_w, grid_h, rendered_fronts)

    # 4. Collector's container (Bottom-left)
    c_w, c_h = int(trim_w * 0.54), 80
    cx0 = bleed + int(0.4 * DPI)
    cy0 = h - bleed - int(1.55 * DPI)
    draw.rounded_rectangle([cx0, cy0, cx0 + c_w, cy0 + c_h], radius=24, fill="#16A34A", outline="#15803D", width=4)
    coll_font = load_fancy_font("Fredoka-Bold.ttf", 28)
    draw_sparkle_star(draw, cx0 + 26, cy0 + c_h // 2, outer_r=14, inner_r=3)
    draw_sparkle_star(draw, cx0 + c_w - 26, cy0 + c_h // 2, outer_r=14, inner_r=3)
    c_txt = "Collector's Series of 12 Interactive Titles"
    c_bb = draw.textbbox((0, 0), c_txt, font=coll_font)
    draw.text((cx0 + (c_w - (c_bb[2] - c_bb[0])) // 2, cy0 + 22), c_txt, fill="white", font=coll_font)

    # Marketing blurb below container (Collision-free)
    blurb_f = load_fancy_font("Fredoka-Bold.ttf", 26)
    draw.text((cx0 + 8, cy0 + 95), "A playful, easy coloring series designed for early learners", fill="white", font=blurb_f)
    draw.text((cx0 + 8, cy0 + 130), "to copy, color, and play!", fill="white", font=blurb_f)

    # 5. Barcode Safe Area (2.0 x 1.2 in = 600 x 360 px strictly preserved)
    bc_w, bc_h = int(2.0 * DPI), int(1.2 * DPI)
    bc_x = back_x_end - bc_w - int(0.5 * DPI)
    bc_y = h - bleed - bc_h - int(0.5 * DPI)
    draw.rounded_rectangle([bc_x, bc_y, bc_x + bc_w, bc_y + bc_h], radius=12, fill="white", outline="#CCCCCC", width=2)
    barcode_f = load_fancy_font("Fredoka-Bold.ttf", 24)
    draw.text((bc_x + 130, bc_y + 160), "[ KDP Barcode Location ]", fill="#888888", font=barcode_f)

    # Copyright notice
    copy_f = load_fancy_font("Fredoka-Bold.ttf", 22)
    draw.text((bc_x - 30, bc_y + bc_h + 30), "© The Pivot Digital Publications. All rights reserved.", fill="white", font=copy_f)

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
    parser.add_argument("--page-count", type=int, default=80, help="Page count for spine calculation (32 or 80)")
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
        hero_default = "local_builds/animals/assets/tiger_monkey_transparent.png"
        inset_default = "local_builds/animals/assets/inset_tiger_split.png"
        hero_p = args.hero or (hero_default if os.path.exists(hero_default) and args.vol_id == "vol_02" else None)
        inset_p = args.inset or (inset_default if os.path.exists(inset_default) and args.vol_id == "vol_02" else None)
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
