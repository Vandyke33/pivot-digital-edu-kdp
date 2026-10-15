"""
Generator for all 12 series volume split activity cards.
Each card is 1024x1024 RGBA:
- Left half (x < 512): Rich, vibrant full-color theme illustration.
- Right half (x >= 512): Crisp, pure black & white lineart outline with pure white fill.
- Centerline (x = 512): Subtle dashed vertical divider with sparkle accents.
"""

from __future__ import annotations

import math
import os
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageChops

REPO_ROOT = Path(__file__).resolve().parents[3]


def color_image_to_clean_lineart(color_img: Image.Image, stroke_boost: int = 3) -> Image.Image:
    """Derives pure binary black and white lineart with matching geometry."""
    if color_img.mode in ("RGBA", "LA") or (color_img.mode == "P" and "transparency" in color_img.info):
        bg = Image.new("RGB", color_img.size, (255, 255, 255))
        if color_img.mode == "RGBA":
            bg.paste(color_img, mask=color_img.split()[3])
        else:
            bg.paste(color_img.convert("RGBA"))
        gray = bg.convert("L")
    else:
        gray = color_img.convert("L")

    edges = gray.filter(ImageFilter.FIND_EDGES)
    inverted_edges = ImageOps.invert(edges)

    dark_ink = gray.point(lambda p: 0 if p < 85 else 255)
    edge_ink = inverted_edges.point(lambda p: 0 if p < 180 else 255)
    combined = ImageChops.darker(dark_ink, edge_ink)

    if stroke_boost > 1:
        filter_size = stroke_boost if (stroke_boost % 2 != 0) else (stroke_boost + 1)
        combined = combined.filter(ImageFilter.MinFilter(filter_size))

    bw = combined.point(lambda p: 0 if p < 200 else 255)
    bw_draw = ImageDraw.Draw(bw)
    bw_draw.rectangle([0, 0, bw.width - 1, bw.height - 1], outline=255, width=4)
    return bw.convert("RGBA")


def draw_sparkle_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, outer_r: int = 14, inner_r: int = 4,
                      fill: tuple = (255, 255, 255, 255), outline: tuple = (148, 163, 184, 255)) -> None:
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


def draw_subject_vol_01(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 01: Alphabet — Smiling bright red Apple with cute eyes and Letter A badge."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2 + 30

    # Apple body (Plump rounded shape with dimples)
    d.ellipse([cx - 360, cy - 280, cx + 30, cy + 340], fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx - 30, cy - 280, cx + 360, cy + 340], fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx - 300, cy - 220, cx + 300, cy + 320], fill=(239, 68, 68, 255))

    # Highlight shine
    d.arc([cx - 280, cy - 220, cx - 120, cy], start=120, end=240, fill=(255, 255, 255, 200), width=24)

    # Stem
    d.line([(cx, cy - 280), (cx + 20, cy - 420)], fill=(120, 53, 15, 255), width=26)

    # Green Leaf
    leaf_pts = [(cx + 10, cy - 350), (cx + 180, cy - 440), (cx + 260, cy - 360), (cx + 110, cy - 330)]
    d.polygon(leaf_pts, fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=14)

    # Smiling cartoon eyes
    d.ellipse([cx - 160, cy - 80, cx - 40, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx - 130, cy - 65, cx - 70, cy - 5], fill=(255, 255, 255, 255))
    d.ellipse([cx + 40, cy - 80, cx + 160, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx + 70, cy - 65, cx + 130, cy - 5], fill=(255, 255, 255, 255))

    # Rosy cheeks
    d.ellipse([cx - 240, cy + 40, cx - 140, cy + 110], fill=(251, 113, 133, 180))
    d.ellipse([cx + 140, cy + 40, cx + 240, cy + 110], fill=(251, 113, 133, 180))

    # Happy smile
    d.arc([cx - 80, cy + 40, cx + 80, cy + 170], start=10, end=170, fill=(30, 30, 35, 255), width=16)
    d.pieslice([cx - 60, cy + 70, cx + 60, cy + 170], start=10, end=170, fill=(244, 63, 94, 255))

    return im


def draw_subject_vol_02(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 02: Animals — Baby tiger cub."""
    # Check if inset_tiger_split exists first
    p = REPO_ROOT / "local_builds" / "animals" / "assets" / "inset_tiger_split.png"
    if p.exists():
        return Image.open(str(p)).convert("RGBA")

    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Ears
    d.ellipse([cx - 360, cy - 380, cx - 180, cy - 200], fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx - 320, cy - 340, cx - 220, cy - 240], fill=(254, 215, 170, 255))
    d.ellipse([cx + 180, cy - 380, cx + 360, cy - 200], fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx + 220, cy - 340, cx + 320, cy - 240], fill=(254, 215, 170, 255))

    # Face head
    d.ellipse([cx - 320, cy - 260, cx + 320, cy + 300], fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=18)

    # Tiger stripes on forehead
    d.polygon([(cx - 30, cy - 240), (cx + 30, cy - 240), (cx, cy - 140)], fill=(30, 30, 35, 255))
    d.polygon([(cx - 180, cy - 180), (cx - 90, cy - 160), (cx - 160, cy - 120)], fill=(30, 30, 35, 255))
    d.polygon([(cx + 180, cy - 180), (cx + 90, cy - 160), (cx + 160, cy - 120)], fill=(30, 30, 35, 255))

    # White muzzle
    d.ellipse([cx - 180, cy + 20, cx + 180, cy + 260], fill=(255, 250, 240, 255), outline=(30, 30, 35, 255), width=14)

    # Eyes
    d.ellipse([cx - 180, cy - 80, cx - 60, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx - 150, cy - 65, cx - 90, cy - 5], fill=(255, 255, 255, 255))
    d.ellipse([cx + 60, cy - 80, cx + 180, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx + 90, cy - 65, cx + 150, cy - 5], fill=(255, 255, 255, 255))

    # Cute nose and mouth
    d.polygon([(cx - 40, cy + 70), (cx + 40, cy + 70), (cx, cy + 120)], fill=(244, 63, 94, 255), outline=(30, 30, 35, 255), width=6)
    d.arc([cx - 80, cy + 110, cx, cy + 190], start=10, end=170, fill=(30, 30, 35, 255), width=12)
    d.arc([cx, cy + 110, cx + 80, cy + 190], start=10, end=170, fill=(30, 30, 35, 255), width=12)

    return im


def draw_subject_vol_03(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 03: Birds — Tropical Parrot."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Body
    d.ellipse([cx - 260, cy - 260, cx + 220, cy + 320], fill=(16, 185, 129, 255), outline=(30, 30, 35, 255), width=16)

    # Yellow Belly
    d.ellipse([cx - 140, cy - 60, cx + 160, cy + 280], fill=(250, 204, 21, 255), outline=(30, 30, 35, 255), width=14)

    # Red Crest Feathers
    d.polygon([(cx - 80, cy - 250), (cx - 40, cy - 420), (cx + 40, cy - 250)], fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=14)
    d.polygon([(cx + 20, cy - 250), (cx + 90, cy - 380), (cx + 120, cy - 240)], fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=12)

    # Big Curved Beak
    beak_pts = [(cx - 200, cy - 80), (cx - 40, cy - 140), (cx - 40, cy + 40), (cx - 280, cy + 80)]
    d.polygon(beak_pts, fill=(251, 191, 36, 255), outline=(30, 30, 35, 255), width=16)

    # Big Cartoon Eye
    d.ellipse([cx - 20, cy - 160, cx + 110, cy - 30], fill=(255, 255, 255, 255), outline=(30, 30, 35, 255), width=14)
    d.ellipse([cx + 10, cy - 130, cx + 90, cy - 50], fill=(20, 20, 25, 255))
    d.ellipse([cx + 25, cy - 120, cx + 60, cy - 85], fill=(255, 255, 255, 255))

    # Blue Wing
    d.ellipse([cx + 40, cy - 80, cx + 320, cy + 240], fill=(59, 130, 246, 255), outline=(30, 30, 35, 255), width=16)

    return im


def draw_subject_vol_04(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 04: Sports — Cheerful Soccer Ball with athletic red headband."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Soccer ball circle
    r = 320
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255), outline=(30, 30, 35, 255), width=18)

    # Red headband across top
    d.rounded_rectangle([cx - r + 15, cy - 200, cx + r - 15, cy - 70], radius=24, fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=14)
    draw_sparkle_star(d, cx, cy - 135, outer_r=30, inner_r=8, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))

    # Center pentagon patch
    p_pts = []
    for i in range(5):
        ang = math.radians(i * 72 - 90)
        p_pts.append((cx + int(100 * math.cos(ang)), cy + 120 + int(100 * math.sin(ang))))
    d.polygon(p_pts, fill=(30, 30, 35, 255))

    # Eyes
    d.ellipse([cx - 160, cy - 40, cx - 40, cy + 70], fill=(20, 20, 25, 255))
    d.ellipse([cx - 130, cy - 25, cx - 75, cy + 25], fill=(255, 255, 255, 255))
    d.ellipse([cx + 40, cy - 40, cx + 160, cy + 70], fill=(20, 20, 25, 255))
    d.ellipse([cx + 75, cy - 25, cx + 130, cy + 25], fill=(255, 255, 255, 255))

    # Rosy cheeks & smile
    d.ellipse([cx - 220, cy + 50, cx - 140, cy + 110], fill=(251, 113, 133, 180))
    d.ellipse([cx + 140, cy + 50, cx + 220, cy + 110], fill=(251, 113, 133, 180))
    d.arc([cx - 80, cy + 60, cx + 80, cy + 180], start=10, end=170, fill=(30, 30, 35, 255), width=16)

    return im


def draw_subject_vol_05(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 05: Monsters — Friendly Purple One-Eyed Monster with horns."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Horns
    d.polygon([(cx - 240, cy - 220), (cx - 320, cy - 400), (cx - 160, cy - 280)], fill=(250, 204, 21, 255), outline=(30, 30, 35, 255), width=14)
    d.polygon([(cx + 240, cy - 220), (cx + 320, cy - 400), (cx + 160, cy - 280)], fill=(250, 204, 21, 255), outline=(30, 30, 35, 255), width=14)

    # Monster Body
    d.ellipse([cx - 320, cy - 280, cx + 320, cy + 340], fill=(168, 85, 247, 255), outline=(30, 30, 35, 255), width=18)

    # Giant Big Anime Eye
    d.ellipse([cx - 150, cy - 180, cx + 150, cy + 80], fill=(255, 255, 255, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx - 90, cy - 130, cx + 90, cy + 40], fill=(6, 182, 212, 255), outline=(30, 30, 35, 255), width=10)
    d.ellipse([cx - 50, cy - 100, cx + 50, cy], fill=(20, 20, 25, 255))
    d.ellipse([cx - 35, cy - 90, cx + 15, cy - 40], fill=(255, 255, 255, 255))

    # Toothy Smile
    d.arc([cx - 180, cy + 80, cx + 180, cy + 260], start=10, end=170, fill=(30, 30, 35, 255), width=16)
    d.pieslice([cx - 150, cy + 110, cx + 150, cy + 260], start=10, end=170, fill=(244, 63, 94, 255))
    # Two cute teeth
    d.polygon([(cx - 70, cy + 120), (cx - 30, cy + 120), (cx - 50, cy + 160)], fill=(255, 255, 255, 255), outline=(30, 30, 35, 255), width=6)
    d.polygon([(cx + 30, cy + 120), (cx + 70, cy + 120), (cx + 50, cy + 160)], fill=(255, 255, 255, 255), outline=(30, 30, 35, 255), width=6)

    return im


def draw_subject_vol_06(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 06: Numbers — Cheerful Number 1 Character with smiling face."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Number 1 shape
    pts = [
        (cx - 60, cy - 360),
        (cx + 80, cy - 360),
        (cx + 80, cy + 240),
        (cx + 240, cy + 240),
        (cx + 240, cy + 360),
        (cx - 240, cy + 360),
        (cx - 240, cy + 240),
        (cx - 60, cy + 240),
        (cx - 60, cy - 180),
        (cx - 180, cy - 140),
        (cx - 220, cy - 240),
    ]
    d.polygon(pts, fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=18)

    # Eyes on the 1 stem
    d.ellipse([cx - 40, cy - 100, cx + 20, cy - 40], fill=(20, 20, 25, 255))
    d.ellipse([cx - 25, cy - 90, cx + 5, cy - 60], fill=(255, 255, 255, 255))

    # Smile
    d.arc([cx - 30, cy - 50, cx + 30, cy + 20], start=10, end=170, fill=(30, 30, 35, 255), width=10)

    # Party hat on top
    d.polygon([(cx - 40, cy - 360), (cx + 60, cy - 360), (cx + 10, cy - 460)], fill=(250, 204, 21, 255), outline=(30, 30, 35, 255), width=12)
    d.ellipse([cx - 10, cy - 480, cx + 30, cy - 440], fill=(236, 72, 153, 255))

    return im


def draw_subject_vol_07(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 07: Fruits — Smiling Strawberry."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Berry heart/cone shape
    pts = [
        (cx, cy + 360),
        (cx - 300, cy + 120),
        (cx - 320, cy - 180),
        (cx - 120, cy - 260),
        (cx, cy - 200),
        (cx + 120, cy - 260),
        (cx + 320, cy - 180),
        (cx + 300, cy + 120),
    ]
    d.polygon(pts, fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=18)

    # Green Leafy crown
    leaf_pts = [
        (cx - 320, cy - 280), (cx - 160, cy - 220), (cx - 200, cy - 400),
        (cx, cy - 240), (cx, cy - 430), (cx + 160, cy - 220), (cx + 200, cy - 400), (cx + 320, cy - 280), (cx, cy - 180)
    ]
    d.polygon(leaf_pts, fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=16)

    # Golden yellow seeds
    seeds = [(-160, -40), (-60, -80), (80, -70), (180, -20), (-180, 80), (-80, 60), (60, 70), (170, 90), (-60, 180), (70, 190), (0, 260)]
    for sx, sy in seeds:
        d.ellipse([cx + sx - 12, cy + sy - 18, cx + sx + 12, cy + sy + 18], fill=(254, 240, 138, 255), outline=(180, 83, 9, 255), width=4)

    # Cute eyes
    d.ellipse([cx - 140, cy - 40, cx - 40, cy + 60], fill=(20, 20, 25, 255))
    d.ellipse([cx - 115, cy - 25, cx - 65, cy + 20], fill=(255, 255, 255, 255))
    d.ellipse([cx + 40, cy - 40, cx + 140, cy + 60], fill=(20, 20, 25, 255))
    d.ellipse([cx + 65, cy - 25, cx + 115, cy + 20], fill=(255, 255, 255, 255))

    # Smile
    d.arc([cx - 70, cy + 30, cx + 70, cy + 140], start=10, end=170, fill=(30, 30, 35, 255), width=14)

    return im


def draw_subject_vol_08(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 08: Shapes — Smiling Golden Star."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # 5-pointed star
    pts = []
    outer_r = 380
    inner_r = 180
    for i in range(10):
        r = outer_r if i % 2 == 0 else inner_r
        ang = math.radians(i * 36 - 90)
        pts.append((cx + int(r * math.cos(ang)), cy + int(r * math.sin(ang))))
    d.polygon(pts, fill=(250, 204, 21, 255), outline=(217, 119, 6, 255), width=18)

    # Cute eyes
    d.ellipse([cx - 120, cy - 60, cx - 30, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx - 95, cy - 45, cx - 55, cy - 5], fill=(255, 255, 255, 255))
    d.ellipse([cx + 30, cy - 60, cx + 120, cy + 40], fill=(20, 20, 25, 255))
    d.ellipse([cx + 55, cy - 45, cx + 95, cy - 5], fill=(255, 255, 255, 255))

    # Rosy cheeks
    d.ellipse([cx - 180, cy + 30, cx - 110, cy + 85], fill=(251, 113, 133, 190))
    d.ellipse([cx + 110, cy + 30, cx + 180, cy + 85], fill=(251, 113, 133, 190))

    # Smile
    d.arc([cx - 60, cy + 20, cx + 60, cy + 120], start=10, end=170, fill=(30, 30, 35, 255), width=14)

    return im


def draw_subject_vol_09(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 09: Toys — Cute Plush Teddy Bear."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Round ears
    d.ellipse([cx - 320, cy - 360, cx - 140, cy - 180], fill=(180, 83, 9, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx - 280, cy - 320, cx - 180, cy - 220], fill=(253, 230, 138, 255))
    d.ellipse([cx + 140, cy - 360, cx + 320, cy - 180], fill=(180, 83, 9, 255), outline=(30, 30, 35, 255), width=16)
    d.ellipse([cx + 180, cy - 320, cx + 280, cy - 220], fill=(253, 230, 138, 255))

    # Head
    d.ellipse([cx - 280, cy - 260, cx + 280, cy + 240], fill=(217, 119, 6, 255), outline=(30, 30, 35, 255), width=18)

    # Snout
    d.ellipse([cx - 140, cy - 20, cx + 140, cy + 180], fill=(253, 230, 138, 255), outline=(30, 30, 35, 255), width=14)
    # Nose
    d.ellipse([cx - 50, cy + 10, cx + 50, cy + 70], fill=(30, 30, 35, 255))
    d.arc([cx - 60, cy + 50, cx + 60, cy + 140], start=10, end=170, fill=(30, 30, 35, 255), width=12)

    # Button eyes
    d.ellipse([cx - 160, cy - 120, cx - 60, cy - 20], fill=(20, 20, 25, 255))
    d.ellipse([cx - 135, cy - 105, cx - 85, cy - 55], fill=(255, 255, 255, 255))
    d.ellipse([cx + 60, cy - 120, cx + 160, cy - 20], fill=(20, 20, 25, 255))
    d.ellipse([cx + 85, cy - 105, cx + 135, cy - 55], fill=(255, 255, 255, 255))

    # Bowtie
    d.polygon([(cx, cy + 220), (cx - 120, cy + 160), (cx - 120, cy + 280)], fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=12)
    d.polygon([(cx, cy + 220), (cx + 120, cy + 160), (cx + 120, cy + 280)], fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=12)
    d.ellipse([cx - 30, cy + 195, cx + 30, cy + 245], fill=(220, 38, 38, 255), outline=(30, 30, 35, 255), width=8)

    return im


def draw_subject_vol_10(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 10: Flowers — Happy Smiling Sunflower."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Green leaves
    d.ellipse([cx - 420, cy + 80, cx - 180, cy + 280], fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=14)
    d.ellipse([cx + 180, cy + 80, cx + 420, cy + 280], fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=14)

    # 12 Golden petals around center
    petal_r = 360
    for i in range(16):
        ang = math.radians(i * (360 / 16))
        px = cx + int(petal_r * 0.75 * math.cos(ang))
        py = cy + int(petal_r * 0.75 * math.sin(ang))
        d.ellipse([px - 70, py - 70, px + 70, py + 70], fill=(250, 204, 21, 255), outline=(217, 119, 6, 255), width=10)

    # Dark center disk
    d.ellipse([cx - 200, cy - 200, cx + 200, cy + 200], fill=(120, 53, 15, 255), outline=(30, 30, 35, 255), width=16)

    # Cute smiling eyes
    d.ellipse([cx - 110, cy - 60, cx - 30, cy + 20], fill=(255, 255, 255, 255))
    d.ellipse([cx - 85, cy - 45, cx - 40, cy], fill=(20, 20, 25, 255))
    d.ellipse([cx + 30, cy - 60, cx + 110, cy + 20], fill=(255, 255, 255, 255))
    d.ellipse([cx + 40, cy - 45, cx + 85, cy], fill=(20, 20, 25, 255))

    # Smile
    d.arc([cx - 60, cy + 20, cx + 60, cy + 110], start=10, end=170, fill=(254, 240, 138, 255), width=12)

    return im


def draw_subject_vol_11(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 11: Transport — Cute Little Red Car."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Cabin roof
    d.ellipse([cx - 220, cy - 260, cx + 220, cy + 40], fill=(59, 130, 246, 255), outline=(30, 30, 35, 255), width=16)
    # Windshield glass
    d.ellipse([cx - 180, cy - 220, cx + 180, cy + 10], fill=(224, 242, 254, 255))

    # Car body
    d.rounded_rectangle([cx - 360, cy - 60, cx + 360, cy + 200], radius=48, fill=(239, 68, 68, 255), outline=(30, 30, 35, 255), width=18)

    # Headlight eyes
    d.ellipse([cx - 320, cy - 20, cx - 220, cy + 80], fill=(254, 240, 138, 255), outline=(30, 30, 35, 255), width=12)
    d.ellipse([cx - 290, cy, cx - 240, cy + 50], fill=(20, 20, 25, 255))
    d.ellipse([cx + 220, cy - 20, cx + 320, cy + 80], fill=(254, 240, 138, 255), outline=(30, 30, 35, 255), width=12)
    d.ellipse([cx + 240, cy, cx + 290, cy + 50], fill=(20, 20, 25, 255))

    # Smiling bumper grille
    d.arc([cx - 120, cy + 60, cx + 120, cy + 170], start=10, end=170, fill=(30, 30, 35, 255), width=14)

    # Wheels
    d.ellipse([cx - 300, cy + 140, cx - 140, cy + 300], fill=(30, 30, 35, 255))
    d.ellipse([cx - 250, cy + 190, cx - 190, cy + 250], fill=(203, 213, 225, 255))
    d.ellipse([cx + 140, cy + 140, cx + 300, cy + 300], fill=(30, 30, 35, 255))
    d.ellipse([cx + 190, cy + 190, cx + 250, cy + 250], fill=(203, 213, 225, 255))

    return im


def draw_subject_vol_12(w: int = 1024, h: int = 1024) -> Image.Image:
    """Vol 12: Vegetables — Happy Smiling Carrot."""
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    # Green leafy tops
    d.polygon([(cx - 80, cy - 200), (cx - 160, cy - 420), (cx - 40, cy - 240)], fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=14)
    d.polygon([(cx, cy - 200), (cx, cy - 460), (cx + 60, cy - 240)], fill=(22, 163, 74, 255), outline=(30, 30, 35, 255), width=14)
    d.polygon([(cx + 40, cy - 200), (cx + 160, cy - 420), (cx + 80, cy - 240)], fill=(34, 197, 94, 255), outline=(30, 30, 35, 255), width=14)

    # Carrot body (Tapered triangle with rounded top)
    d.ellipse([cx - 180, cy - 240, cx + 180, cy - 140], fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=16)
    pts = [(cx - 180, cy - 190), (cx + 180, cy - 190), (cx, cy + 420)]
    d.polygon(pts, fill=(249, 115, 22, 255), outline=(30, 30, 35, 255), width=18)
    d.ellipse([cx - 160, cy - 220, cx + 160, cy - 160], fill=(249, 115, 22, 255))

    # Horizontal ridges
    for ry in [-60, 40, 160, 270]:
        rw = int(140 * (1.0 - (ry + 60) / 400))
        d.line([(cx - rw, cy + ry), (cx - rw // 2, cy + ry)], fill=(194, 65, 12, 255), width=10)
        d.line([(cx + rw // 3, cy + ry), (cx + rw, cy + ry)], fill=(194, 65, 12, 255), width=10)

    # Eyes
    d.ellipse([cx - 110, cy - 100, cx - 30, cy - 20], fill=(20, 20, 25, 255))
    d.ellipse([cx - 90, cy - 90, cx - 50, cy - 50], fill=(255, 255, 255, 255))
    d.ellipse([cx + 30, cy - 100, cx + 110, cy - 20], fill=(20, 20, 25, 255))
    d.ellipse([cx + 50, cy - 90, cx + 90, cy - 50], fill=(255, 255, 255, 255))

    # Rosy cheeks & smile
    d.ellipse([cx - 150, cy - 20, cx - 80, cy + 30], fill=(251, 113, 133, 190))
    d.ellipse([cx + 80, cy - 20, cx + 150, cy + 30], fill=(251, 113, 133, 190))
    d.arc([cx - 60, cy - 30, cx + 60, cy + 60], start=10, end=170, fill=(30, 30, 35, 255), width=14)

    return im


SUBJECT_DRAWERS = {
    "vol_01": draw_subject_vol_01,
    "vol_02": draw_subject_vol_02,
    "vol_03": draw_subject_vol_03,
    "vol_04": draw_subject_vol_04,
    "vol_05": draw_subject_vol_05,
    "vol_06": draw_subject_vol_06,
    "vol_07": draw_subject_vol_07,
    "vol_08": draw_subject_vol_08,
    "vol_09": draw_subject_vol_09,
    "vol_10": draw_subject_vol_10,
    "vol_11": draw_subject_vol_11,
    "vol_12": draw_subject_vol_12,
}


def build_split_card(vol_id: str, out_path: Path) -> Path:
    """Builds a single 1024x1024 split activity card."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    drawer = SUBJECT_DRAWERS.get(vol_id, draw_subject_vol_01)
    color_im = drawer(1024, 1024)

    # Derive pure B&W lineart outline
    bw_im = color_image_to_clean_lineart(color_im, stroke_boost=3)

    # Create split image
    split_card = Image.new("RGBA", (1024, 1024), (255, 255, 255, 255))
    left_half = color_im.crop((0, 0, 512, 1024))
    right_half = bw_im.crop((512, 0, 1024, 1024))
    split_card.paste(left_half, (0, 0))
    split_card.paste(right_half, (512, 0))

    # Center dashed split seam
    d = ImageDraw.Draw(split_card)
    for y in range(60, 960, 32):
        d.line([(512, y), (512, min(y + 18, 960))], fill=(100, 116, 139, 220), width=4)

    # Center gold sparkle stars on dividing seam
    draw_sparkle_star(d, 512, 120, outer_r=18, inner_r=5, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))
    draw_sparkle_star(d, 512, 512, outer_r=22, inner_r=6, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))
    draw_sparkle_star(d, 512, 900, outer_r=18, inner_r=5, fill=(250, 204, 21, 255), outline=(180, 83, 9, 255))

    split_card.save(str(out_path), "PNG")
    return out_path


def generate_all_12_split_cards(dest_dir: Path = REPO_ROOT / "assets" / "activity_cards") -> list[Path]:
    """Generates all 12 split activity cards and saves to assets/activity_cards/."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    cards = []
    for i in range(1, 13):
        vol_id = f"vol_{i:02d}"
        p = dest_dir / f"{vol_id}_split.png"
        build_split_card(vol_id, p)
        cards.append(p)
        print(f"  [Card {i}/12] Created: {p}")
    return cards


if __name__ == "__main__":
    generate_all_12_split_cards()
