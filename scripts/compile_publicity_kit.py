"""
Publicity & Retail Marketing Kit Generator for 'The Pivot Kids: Copy to Color' Series.

Generates:
1. High-Resolution Series Showcase Poster (2400 x 3600 px, 300 DPI equivalent)
   featuring all 12 authentic Front Covers in a premium retail grid with feature callouts.
2. Formatted for Amazon A+ Content, social publicity, and retail catalog sell sheets.
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from scripts.compile_cover_pil import (
    NAVY_TEXT,
    SERIES_TITLES,
    YELLOW_TEXT,
    draw_sparkle_star,
    isolate_with_sticker_border,
    load_fancy_font,
)


def draw_poster_gradient(width: int, height: int) -> Image.Image:
    """Creates a vivid cosmic/royal indigo gradient backdrop."""
    bg_top = (15, 23, 42)       # Slate 900
    bg_mid = (30, 27, 75)       # Indigo 950
    bg_bot = (13, 148, 136)     # Teal 600
    im = Image.new("RGBA", (width, height), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)

    mid_y = int(height * 0.65)
    for y in range(mid_y):
        t = y / max(1, mid_y)
        r = int(bg_top[0] + (bg_mid[0] - bg_top[0]) * t)
        g = int(bg_top[1] + (bg_mid[1] - bg_top[1]) * t)
        b = int(bg_top[2] + (bg_mid[2] - bg_top[2]) * t)
        d.line([(0, y), (width, y)], fill=(r, g, b, 255))

    for y in range(mid_y, height):
        t = (y - mid_y) / max(1, height - mid_y)
        r = int(bg_mid[0] + (bg_bot[0] - bg_mid[0]) * t)
        g = int(bg_mid[1] + (bg_bot[1] - bg_mid[1]) * t)
        b = int(bg_mid[2] + (bg_bot[2] - bg_mid[2]) * t)
        d.line([(0, y), (width, y)], fill=(r, g, b, 255))

    return im


def generate_series_poster(
    output_path: str = "local_builds/publicity_kit/series_promotional_poster.png",
    fronts_dir: str = "local_builds/series_fronts",
    logo_path: str | None = None,
    width: int = 2400,
    height: int = 3600,
) -> Path:
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    poster = draw_poster_gradient(width, height)
    draw = ImageDraw.Draw(poster)
    cx = width // 2

    # Background sparkle stars
    sparkle_coords = [
        (180, 220, 24), (width - 180, 260, 28),
        (320, 480, 18), (width - 290, 520, 20),
        (120, 920, 16), (width - 140, 880, 18),
        (200, 3100, 20), (width - 220, 3150, 22),
    ]
    for sx, sy, sr in sparkle_coords:
        draw_sparkle_star(draw, sx, sy, outer_r=sr, inner_r=4)

    # 1. Top Brand Logo
    resolved_logo = None
    for cand in [logo_path, "assets/logos/pivot_kids_sticker.png", "assets/logos/pivot_kids.png"]:
        if cand and os.path.exists(cand):
            resolved_logo = cand
            break

    if resolved_logo:
        logo_im = isolate_with_sticker_border(resolved_logo, stroke_size=12, remove_trapped_pockets=False)
        logo_im.thumbnail((420, 420), Image.Resampling.LANCZOS)
        poster.paste(logo_im, (cx - logo_im.width // 2, 70), logo_im)

    # 2. Header Typography
    f_series = load_fancy_font("LuckiestGuy.ttf", 140)
    f_sub = load_fancy_font("Fredoka-Bold.ttf", 46)
    f_tag = load_fancy_font("Fredoka-Bold.ttf", 34)

    # "COPY TO COLOR" in 3D Neon Sparkle
    y_title = 510
    title_text = "COPY TO COLOR"
    tb = draw.textbbox((0, 0), title_text, font=f_series)
    tw = tb[2] - tb[0]
    tx = cx - tw // 2

    # Drop extrusion
    for d_off in range(12, 0, -1):
        draw.text((tx + d_off, y_title + d_off), title_text, font=f_series, fill=(10, 15, 30, 255))
    # Outline
    for ox in range(-6, 7):
        for oy in range(-6, 7):
            if ox * ox + oy * oy <= 36:
                draw.text((tx + ox, y_title + oy), title_text, font=f_series, fill=(255, 230, 80, 255))
    # Fill
    draw.text((tx, y_title), title_text, font=f_series, fill=(255, 255, 255, 255))

    # Sparkles on Title
    draw_sparkle_star(draw, tx - 30, y_title + 40, outer_r=22, inner_r=5)
    draw_sparkle_star(draw, tx + tw + 30, y_title + 40, outer_r=22, inner_r=5)

    # Subtitle Ribbon Badge
    badge_w, badge_h = 1380, 72
    bx = cx - badge_w // 2
    by = 680
    draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=24, fill="#0284C7", outline="white", width=3)
    draw_sparkle_star(draw, bx + 36, by + badge_h // 2, outer_r=16, inner_r=4)
    draw_sparkle_star(draw, bx + badge_w - 36, by + badge_h // 2, outer_r=16, inner_r=4)
    sub_txt = "12-BOOK COLLECTOR'S SERIES FOR EARLY LEARNERS"
    st_b = draw.textbbox((0, 0), sub_txt, font=f_sub)
    draw.text((cx - (st_b[2] - st_b[0]) // 2, by + 12), sub_txt, fill="white", font=f_sub)

    # Secondary Tagline
    tag_txt = "Ages 2-6  |  Learn by Copying  |  Rich Full-Color Guides & Bold Coloring Outlines"
    tg_b = draw.textbbox((0, 0), tag_txt, font=f_tag)
    draw.text((cx - (tg_b[2] - tg_b[0]) // 2, by + 90), tag_txt, fill="#CBD5E1", font=f_tag)

    # 3. 12-Book Showcase Grid (4 columns x 3 rows)
    grid_top = 870
    grid_w = 2160
    grid_h = 2050
    grid_x0 = (width - grid_w) // 2

    cols, rows = 4, 3
    cell_w = grid_w // cols
    cell_h = grid_h // rows
    badge_font = load_fancy_font("Fredoka-Bold.ttf", 26)
    title_font = load_fancy_font("Fredoka-Bold.ttf", 24)

    for idx, item in enumerate(SERIES_TITLES):
        c = idx % cols
        r = idx // cols
        x0 = grid_x0 + c * cell_w + 14
        y0 = grid_top + r * cell_h + 10
        cw = cell_w - 28
        ch = cell_h - 20

        # Try to load the rendered front cover
        cover_path = os.path.join(fronts_dir, f"{item['id']}_front.png")
        if os.path.exists(cover_path):
            with Image.open(cover_path) as im:
                front_im = im.copy()
            front_im.thumbnail((cw, ch - 40), Image.Resampling.LANCZOS)
            fw, fh = front_im.width, front_im.height
            fx = x0 + (cw - fw) // 2
            fy = y0 + 10

            # 3D shadow
            draw.rounded_rectangle([fx + 8, fy + 10, fx + fw + 8, fy + fh + 10], radius=14, fill=(0, 0, 0, 110))
            poster.paste(front_im, (fx, fy), front_im)
            # White border
            draw.rounded_rectangle([fx, fy, fx + fw, fy + fh], radius=12, outline="white", width=4)

            # Vol Badge
            bw, bh = 88, 36
            bx_pos, by_pos = fx + fw - bw - 6, fy + 6
            draw.rounded_rectangle([bx_pos, by_pos, bx_pos + bw, by_pos + bh], radius=12, fill=NAVY_TEXT, outline="white", width=2)
            draw.text((bx_pos + 12, by_pos + 5), item["vol"], fill=YELLOW_TEXT, font=badge_font)

            # Book Title under cover
            tit_txt = f"{item['title']}"
            tb = draw.textbbox((0, 0), tit_txt, font=title_font)
            draw.text((x0 + (cw - (tb[2] - tb[0])) // 2, fy + fh + 8), tit_txt, fill="white", font=title_font)

    # 4. Key Selling Points Ribbon (4 Feature Badges)
    feat_y = 3020
    feat_h = 130
    draw.rounded_rectangle([grid_x0, feat_y, grid_x0 + grid_w, feat_y + feat_h], radius=24, fill=(15, 23, 42, 230), outline="#38BDF8", width=3)

    features = [
        "1:1 Color Match Guide",
        "Bold 3pt Safe Outlines",
        "Cheerful Kid Avatars",
        "Official Award Page",
    ]
    feat_f = load_fancy_font("Fredoka-Bold.ttf", 30)
    feat_col_w = grid_w // 4
    for i, ft in enumerate(features):
        fx_c = grid_x0 + i * feat_col_w
        fb = draw.textbbox((0, 0), ft, font=feat_f)
        draw_sparkle_star(draw, fx_c + (feat_col_w - (fb[2] - fb[0])) // 2 - 24, feat_y + feat_h // 2, outer_r=10, inner_r=3)
        draw.text(((fx_c + (feat_col_w - (fb[2] - fb[0])) // 2), feat_y + (feat_h - (fb[3] - fb[1])) // 2 - 2), ft, fill="#F8FAFC", font=feat_f)

    # 5. Bottom Retail Footer
    foot_y = 3230
    foot_title_f = load_fancy_font("LuckiestGuy.ttf", 54)
    foot_sub_f = load_fancy_font("Fredoka-Bold.ttf", 28)

    ft_t = "THE PIVOT KIDS  •  COLOR & PLAY"
    fb = draw.textbbox((0, 0), ft_t, font=foot_title_f)
    draw.text(((cx - (fb[2] - fb[0])) // 2, foot_y), ft_t, fill="#FDE047", font=foot_title_f)

    ft_s = "32 Pages • 8.5 x 11 in • Single-Sided Printing on 55# White Paper • Print-Ready Amazon KDP Paperback"
    fsb = draw.textbbox((0, 0), ft_s, font=foot_sub_f)
    draw.text(((cx - (fsb[2] - fsb[0])) // 2, foot_y + 70), ft_s, fill="#94A3B8", font=foot_sub_f)

    copy_txt = "© The Pivot Digital Publication. All rights reserved."
    cb = draw.textbbox((0, 0), copy_txt, font=foot_sub_f)
    draw.text(((cx - (cb[2] - cb[0])) // 2, foot_y + 115), copy_txt, fill="#64748B", font=foot_sub_f)

    # Save output
    poster.save(str(out_p), "PNG")
    print(f"\n[OK] Series Promotional Poster generated: {out_p}")
    return out_p


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Series Promotional Poster")
    parser.add_argument("--output", default="local_builds/publicity_kit/series_promotional_poster.png", help="Output path")
    parser.add_argument("--fronts-dir", default="local_builds/series_fronts", help="Directory of rendered front covers")
    parser.add_argument("--logo", default=None, help="Path to brand logo")
    args = parser.parse_args()

    generate_series_poster(
        output_path=args.output,
        fronts_dir=args.fronts_dir,
        logo_path=args.logo,
    )
