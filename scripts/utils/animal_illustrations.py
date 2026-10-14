"""
Procedural Animal Character Illustrator.

Provides vector-quality, preschool-friendly cartoon illustrations (1800x1800 RGBA)
for all 30 animals in 'Copy to Color: Animals' (Series Volume 2).
Every illustration is guaranteed to produce clean, 1:1 matching closed-contour
black-and-white coloring line art via `color_image_to_clean_lineart`.
"""

from __future__ import annotations

import math
from PIL import Image, ImageDraw

OUTLINE_COL = (30, 30, 35, 255)
THICK_W = 22
EYE_COL = (20, 20, 25, 255)


def draw_animal_character(animal_name: str, primary_color: tuple = (255, 73, 73)) -> Image.Image:
    """
    Renders a distinct, adorable, preschool-friendly cartoon animal illustration (1800x1800 RGBA).
    Covers all 30 animals in Series Volume 2.
    """
    name = animal_name.upper().strip()
    w, h = 1800, 1800
    im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cx, cy = w // 2, h // 2

    def draw_eyes(eye_y=cy - 90, sep=140, r=55, spec_r=20):
        for sign in (-1, 1):
            ex = cx + sign * sep
            d.ellipse([ex - r, eye_y - r, ex + r, eye_y + r], fill=EYE_COL)
            d.ellipse([ex - r + 15, eye_y - r + 15, ex - r + 15 + spec_r * 2, eye_y - r + 15 + spec_r * 2], fill="white")
            d.ellipse([ex + 10, eye_y + 10, ex + 25, eye_y + 25], fill="white")

    def draw_cheeks(cheek_y=cy + 40, sep=250, r=55, col=(255, 160, 180, 200)):
        for sign in (-1, 1):
            d.ellipse([cx + sign * sep - r, cheek_y - r, cx + sign * sep + r, cheek_y + r], fill=col)

    def draw_mouth(mouth_y=cy + 130, mw=100, mh=60):
        d.arc([cx - mw, mouth_y - mh, cx + mw, mouth_y + mh], start=20, end=160, fill=OUTLINE_COL, width=16)

    # 1. TIGER
    if name == "TIGER":
        body_col = (255, 122, 0, 255)
        d.ellipse([cx - 450, cy - 480, cx - 220, cy - 250], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 480, cx + 450, cy - 250], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 400, cy - 430, cx - 270, cy - 300], fill=(255, 190, 200, 255))
        d.ellipse([cx + 270, cy - 430, cx + 400, cy - 300], fill=(255, 190, 200, 255))
        d.ellipse([cx - 420, cy - 380, cx + 420, cy + 400], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        for s in (-1, 1):
            d.polygon([(cx + s * 390, cy - 100), (cx + s * 270, cy - 70), (cx + s * 380, cy - 40)], fill=OUTLINE_COL)
            d.polygon([(cx + s * 400, cy + 30), (cx + s * 290, cy + 50), (cx + s * 390, cy + 80)], fill=OUTLINE_COL)
        d.polygon([(cx - 30, cy - 360), (cx + 30, cy - 360), (cx, cy - 230)], fill=OUTLINE_COL)
        d.polygon([(cx - 100, cy - 330), (cx - 70, cy - 330), (cx - 60, cy - 250)], fill=OUTLINE_COL)
        d.polygon([(cx + 70, cy - 330), (cx + 100, cy - 330), (cx + 60, cy - 250)], fill=OUTLINE_COL)
        d.ellipse([cx - 210, cy + 10, cx + 210, cy + 280], fill=(255, 250, 240, 255), outline=OUTLINE_COL, width=16)
        d.polygon([(cx - 65, cy + 70), (cx + 65, cy + 70), (cx, cy + 140)], fill=(240, 70, 90, 255), outline=OUTLINE_COL)
        draw_eyes(cy - 60, sep=150)
        draw_cheeks(cy + 80)
        draw_mouth(cy + 130, mw=90)
        d.ellipse([cx - 360, cy + 330, cx - 120, cy + 510], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 120, cy + 330, cx + 360, cy + 510], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 2. MONKEY
    elif name == "MONKEY":
        fur_col = (139, 90, 43, 255)
        skin_col = (255, 218, 185, 255)
        d.ellipse([cx - 520, cy - 260, cx - 250, cy + 80], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 250, cy - 260, cx + 520, cy + 80], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 480, cy - 210, cx - 290, cy + 30], fill=skin_col)
        d.ellipse([cx + 290, cy - 210, cx + 480, cy + 30], fill=skin_col)
        d.ellipse([cx - 380, cy - 360, cx + 380, cy + 380], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 40, cy - 430, cx + 40, cy - 350], fill=fur_col, outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 280, cy - 220, cx, cy + 40], fill=skin_col, outline=OUTLINE_COL, width=14)
        d.ellipse([cx, cy - 220, cx + 280, cy + 40], fill=skin_col, outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 260, cy - 80, cx + 260, cy + 320], fill=skin_col, outline=OUTLINE_COL, width=14)
        draw_eyes(cy - 90, sep=110, r=48)
        draw_cheeks(cy + 60, sep=190)
        d.ellipse([cx - 30, cy + 50, cx - 10, cy + 75], fill=OUTLINE_COL)
        d.ellipse([cx + 10, cy + 50, cx + 30, cy + 75], fill=OUTLINE_COL)
        d.arc([cx - 130, cy + 70, cx + 130, cy + 240], start=10, end=170, fill=OUTLINE_COL, width=18)
        d.ellipse([cx - 330, cy + 320, cx - 110, cy + 500], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 320, cx + 330, cy + 500], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)

    # 3. ELEPHANT
    elif name == "ELEPHANT":
        skin_col = (130, 165, 195, 255)
        d.ellipse([cx - 580, cy - 380, cx - 200, cy + 180], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 200, cy - 380, cx + 580, cy + 180], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 520, cy - 320, cx - 250, cy + 120], fill=(251, 207, 232, 255))
        d.ellipse([cx + 250, cy - 320, cx + 520, cy + 120], fill=(251, 207, 232, 255))
        d.ellipse([cx - 360, cy - 380, cx + 360, cy + 320], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        draw_eyes(cy - 120, sep=170, r=46)
        draw_cheeks(cy + 10, sep=250)
        d.polygon([(cx - 110, cy + 120), (cx - 180, cy + 220), (cx - 100, cy + 180)], fill="white", outline=OUTLINE_COL)
        d.polygon([(cx + 110, cy + 120), (cx + 180, cy + 220), (cx + 100, cy + 180)], fill="white", outline=OUTLINE_COL)
        d.arc([cx - 90, cy - 60, cx + 180, cy + 340], start=40, end=250, fill=OUTLINE_COL, width=78)
        d.arc([cx - 90, cy - 60, cx + 180, cy + 340], start=40, end=250, fill=skin_col, width=54)
        d.line([(cx - 10, cy + 100), (cx + 50, cy + 90)], fill=OUTLINE_COL, width=8)
        d.line([(cx + 10, cy + 160), (cx + 70, cy + 150)], fill=OUTLINE_COL, width=8)
        d.ellipse([cx - 320, cy + 280, cx - 110, cy + 480], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 280, cx + 320, cy + 480], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)

    # 4. GIRAFFE
    elif name == "GIRAFFE":
        yellow = (255, 199, 44, 255)
        brown = (146, 64, 14, 255)
        d.rectangle([cx - 180, cy - 50, cx + 180, cy + 460], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 140, cy + 40, cx - 30, cy + 160], fill=brown)
        d.ellipse([cx + 20, cy + 120, cx + 150, cy + 250], fill=brown)
        d.ellipse([cx - 120, cy + 260, cx + 10, cy + 390], fill=brown)
        d.line([(cx - 110, cy - 280), (cx - 110, cy - 420)], fill=OUTLINE_COL, width=20)
        d.ellipse([cx - 145, cy - 460, cx - 75, cy - 390], fill=brown, outline=OUTLINE_COL, width=12)
        d.line([(cx + 110, cy - 280), (cx + 110, cy - 420)], fill=OUTLINE_COL, width=20)
        d.ellipse([cx + 75, cy - 460, cx + 145, cy - 390], fill=brown, outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 420, cy - 330, cx - 220, cy - 220], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 330, cx + 420, cy - 220], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 280, cy - 360, cx + 280, cy + 80], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 180, cy - 100, cx + 180, cy + 160], fill=(255, 237, 190, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 60, cy - 10, cx - 35, cy + 25], fill=brown)
        d.ellipse([cx + 35, cy - 10, cx + 60, cy + 25], fill=brown)
        draw_eyes(cy - 180, sep=110, r=44)
        draw_cheeks(cy - 60, sep=180)
        draw_mouth(cy + 60, mw=75)

    # 5. LION
    elif name == "LION":
        yellow = (245, 158, 11, 255)
        mane_col = (180, 83, 9, 255)
        for angle in range(0, 360, 24):
            rad = math.radians(angle)
            mx = cx + int(380 * math.cos(rad))
            my = cy - 20 + int(380 * math.sin(rad))
            d.ellipse([mx - 130, my - 130, mx + 130, my + 130], fill=mane_col, outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 320, cy - 340, cx - 160, cy - 180], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 160, cy - 340, cx + 320, cy - 180], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 300, cy - 280, cx + 300, cy + 260], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 190, cy + 20, cx + 190, cy + 220], fill=(255, 248, 220, 255), outline=OUTLINE_COL, width=16)
        d.polygon([(cx - 55, cy + 60), (cx + 55, cy + 60), (cx, cy + 125)], fill=(45, 20, 10, 255))
        for sign in (-1, 1):
            d.line([(cx + sign * 140, cy + 100), (cx + sign * 310, cy + 85)], fill=OUTLINE_COL, width=10)
            d.line([(cx + sign * 140, cy + 135), (cx + sign * 310, cy + 145)], fill=OUTLINE_COL, width=10)
        draw_eyes(cy - 90, sep=120, r=46)
        draw_cheeks(cy + 40, sep=200)
        draw_mouth(cy + 135, mw=80)
        d.ellipse([cx - 300, cy + 280, cx - 90, cy + 460], fill=yellow, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 90, cy + 280, cx + 300, cy + 460], fill=yellow, outline=OUTLINE_COL, width=THICK_W)

    # 6. ZEBRA
    elif name == "ZEBRA":
        body_col = (255, 255, 255, 255)
        # Upright mane crest
        d.polygon([(cx - 40, cy - 440), (cx + 40, cy - 440), (cx + 30, cy - 280), (cx - 30, cy - 280)], fill=(30, 30, 30, 255), outline=OUTLINE_COL, width=12)
        # Ears
        d.ellipse([cx - 360, cy - 440, cx - 180, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 180, cy - 440, cx + 360, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 310, cy - 390, cx - 230, cy - 290], fill=(255, 200, 210, 255))
        d.ellipse([cx + 230, cy - 390, cx + 310, cy - 290], fill=(255, 200, 210, 255))
        # Head
        d.ellipse([cx - 320, cy - 340, cx + 320, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Stripes
        for s in (-1, 1):
            d.polygon([(cx + s * 290, cy - 120), (cx + s * 170, cy - 90), (cx + s * 280, cy - 60)], fill=OUTLINE_COL)
            d.polygon([(cx + s * 300, cy + 10), (cx + s * 190, cy + 30), (cx + s * 290, cy + 60)], fill=OUTLINE_COL)
        d.polygon([(cx - 20, cy - 320), (cx + 20, cy - 320), (cx, cy - 190)], fill=OUTLINE_COL)
        # Muzzle
        d.ellipse([cx - 180, cy + 80, cx + 180, cy + 280], fill=(55, 65, 81, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 60, cy + 150, cx - 30, cy + 185], fill=(200, 200, 200, 255))
        d.ellipse([cx + 30, cy + 150, cx + 60, cy + 185], fill=(200, 200, 200, 255))
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 60, col=(255, 180, 190, 160))
        d.arc([cx - 80, cy + 170, cx + 80, cy + 250], start=20, end=160, fill="white", width=12)
        d.ellipse([cx - 300, cy + 310, cx - 110, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 300, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 7. HIPPO
    elif name == "HIPPO":
        skin_col = (148, 163, 184, 255)
        d.ellipse([cx - 380, cy - 420, cx - 240, cy - 280], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 240, cy - 420, cx + 380, cy - 280], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 320, cy - 360, cx + 320, cy + 200], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 380, cy - 40, cx + 380, cy + 360], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        # Big circular nostrils
        d.ellipse([cx - 150, cy + 70, cx - 50, cy + 170], fill=(71, 85, 105, 255), outline=OUTLINE_COL, width=10)
        d.ellipse([cx + 50, cy + 70, cx + 150, cy + 170], fill=(71, 85, 105, 255), outline=OUTLINE_COL, width=10)
        # Two cute white teeth
        d.polygon([(cx - 130, cy + 280), (cx - 90, cy + 280), (cx - 110, cy + 340)], fill="white", outline=OUTLINE_COL)
        d.polygon([(cx + 90, cy + 280), (cx + 130, cy + 280), (cx + 110, cy + 340)], fill="white", outline=OUTLINE_COL)
        draw_eyes(cy - 140, sep=150, r=48)
        draw_cheeks(cy + 10, sep=260)
        draw_mouth(cy + 220, mw=110)
        d.ellipse([cx - 340, cy + 330, cx - 130, cy + 510], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 130, cy + 330, cx + 340, cy + 510], fill=skin_col, outline=OUTLINE_COL, width=THICK_W)

    # 8. KOALA
    elif name == "KOALA":
        fur_col = (156, 163, 175, 255)
        # Giant fluffy ears
        d.ellipse([cx - 520, cy - 400, cx - 200, cy - 80], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 200, cy - 400, cx + 520, cy - 80], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 470, cy - 350, cx - 250, cy - 130], fill="white")
        d.ellipse([cx + 250, cy - 350, cx + 470, cy - 130], fill="white")
        d.ellipse([cx - 360, cy - 320, cx + 360, cy + 360], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        # Big dark oval nose
        d.ellipse([cx - 85, cy - 20, cx + 85, cy + 180], fill=(31, 41, 55, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 40, cy + 20, cx + 10, cy + 70], fill=(200, 200, 220, 200))
        draw_eyes(cy - 80, sep=140, r=44)
        draw_cheeks(cy + 80, sep=210)
        draw_mouth(cy + 210, mw=80)
        d.ellipse([cx - 310, cy + 320, cx - 110, cy + 500], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 320, cx + 310, cy + 500], fill=fur_col, outline=OUTLINE_COL, width=THICK_W)

    # 9. PANDA
    elif name == "PANDA":
        d.ellipse([cx - 440, cy - 460, cx - 220, cy - 240], fill=(20, 20, 25, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx + 220, cy - 460, cx + 440, cy - 240], fill=(20, 20, 25, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 400, cy - 360, cx + 400, cy + 380], fill="white", outline=OUTLINE_COL, width=THICK_W)
        # Black eye patches
        d.ellipse([cx - 240, cy - 160, cx - 60, cy + 20], fill=(25, 25, 30, 255))
        d.ellipse([cx + 60, cy - 160, cx + 240, cy + 20], fill=(25, 25, 30, 255))
        d.ellipse([cx - 170, cy - 100, cx - 110, cy - 40], fill="white")
        d.ellipse([cx + 110, cy - 100, cx + 170, cy - 40], fill="white")
        d.ellipse([cx - 145, cy - 80, cx - 125, cy - 60], fill=(20, 20, 25, 255))
        d.ellipse([cx + 125, cy - 80, cx + 145, cy - 60], fill=(20, 20, 25, 255))
        d.ellipse([cx - 50, cy + 50, cx + 50, cy + 115], fill=(30, 30, 35, 255))
        draw_cheeks(cy + 110, sep=220)
        draw_mouth(cy + 145, mw=85)
        d.ellipse([cx - 330, cy + 320, cx - 110, cy + 500], fill=(20, 20, 25, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx + 110, cy + 320, cx + 330, cy + 500], fill=(20, 20, 25, 255), outline=OUTLINE_COL, width=12)

    # 10. KANGAROO
    elif name == "KANGAROO":
        body_col = (194, 120, 56, 255)
        d.ellipse([cx - 320, cy - 540, cx - 140, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 140, cy - 540, cx + 320, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 270, cy - 480, cx - 190, cy - 280], fill=(255, 190, 200, 255))
        d.ellipse([cx + 190, cy - 480, cx + 270, cy - 280], fill=(255, 190, 200, 255))
        d.ellipse([cx - 340, cy - 300, cx + 340, cy + 380], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 180, cy + 10, cx + 180, cy + 240], fill=(255, 235, 200, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 50, cx + 45, cy + 110], fill=(30, 30, 35, 255))
        draw_eyes(cy - 80, sep=130)
        draw_cheeks(cy + 50)
        draw_mouth(cy + 130, mw=80)
        # Joey in pouch
        d.ellipse([cx - 140, cy + 240, cx + 140, cy + 420], fill=(255, 220, 180, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 60, cy + 220, cx - 20, cy + 280], fill=body_col)
        d.ellipse([cx + 20, cy + 220, cx + 60, cy + 280], fill=body_col)
        d.ellipse([cx - 30, cy + 280, cx + 30, cy + 320], fill=body_col)

    # 11. RABBIT
    elif name == "RABBIT":
        body_col = (255, 253, 245, 255)
        d.ellipse([cx - 250, cy - 560, cx - 70, cy - 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 70, cy - 560, cx + 250, cy - 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 210, cy - 500, cx - 110, cy - 240], fill=(255, 180, 200, 255))
        d.ellipse([cx + 110, cy - 500, cx + 210, cy - 240], fill=(255, 180, 200, 255))
        d.ellipse([cx - 360, cy - 300, cx + 360, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx - 40, cy + 50), (cx + 40, cy + 50), (cx, cy + 95)], fill=(244, 114, 182, 255))
        # Buck teeth
        d.rectangle([cx - 30, cy + 125, cx, cy + 185], fill="white", outline=OUTLINE_COL, width=8)
        d.rectangle([cx, cy + 125, cx + 30, cy + 185], fill="white", outline=OUTLINE_COL, width=8)
        # Whiskers
        for s in (-1, 1):
            d.line([(cx + s * 90, cy + 60), (cx + s * 280, cy + 40)], fill=OUTLINE_COL, width=8)
            d.line([(cx + s * 90, cy + 85), (cx + s * 280, cy + 95)], fill=OUTLINE_COL, width=8)
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 110, mw=65)
        d.ellipse([cx - 300, cy + 310, cx - 110, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 300, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 12. PUPPY
    elif name == "PUPPY":
        body_col = (224, 169, 109, 255)
        d.ellipse([cx - 510, cy - 280, cx - 240, cy + 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 240, cy - 280, cx + 510, cy + 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 360, cy - 340, cx + 360, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 200, cy + 10, cx + 200, cy + 240], fill=(255, 240, 220, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 60, cy + 40, cx + 60, cy + 115], fill=(30, 30, 35, 255))
        # Panting pink tongue
        d.ellipse([cx - 45, cy + 140, cx + 45, cy + 240], fill=(244, 114, 182, 255), outline=OUTLINE_COL, width=10)
        d.line([(cx, cy + 145), (cx, cy + 215)], fill=(190, 50, 100, 255), width=6)
        draw_eyes(cy - 90, sep=130)
        draw_cheeks(cy + 40)
        draw_mouth(cy + 130, mw=90)
        d.ellipse([cx - 310, cy + 310, cx - 110, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 310, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 13. KITTEN
    elif name == "KITTEN":
        body_col = (251, 146, 60, 255)
        d.polygon([(cx - 380, cy - 200), (cx - 320, cy - 470), (cx - 150, cy - 260)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx + 150, cy - 260), (cx + 320, cy - 470), (cx + 380, cy - 200)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx - 330, cy - 230), (cx - 300, cy - 400), (cx - 200, cy - 270)], fill=(255, 180, 200, 255))
        d.polygon([(cx + 200, cy - 270), (cx + 300, cy - 400), (cx + 330, cy - 230)], fill=(255, 180, 200, 255))
        d.ellipse([cx - 360, cy - 320, cx + 360, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx - 40, cy + 50), (cx + 40, cy + 50), (cx, cy + 95)], fill=(244, 114, 182, 255))
        for s in (-1, 1):
            d.line([(cx + s * 110, cy + 70), (cx + s * 290, cy + 50)], fill=OUTLINE_COL, width=8)
            d.line([(cx + s * 110, cy + 95), (cx + s * 290, cy + 105)], fill=OUTLINE_COL, width=8)
        draw_eyes(cy - 70, sep=130)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 115, mw=75)
        d.ellipse([cx - 300, cy + 300, cx - 110, cy + 470], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 300, cx + 300, cy + 470], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 14. COW
    elif name == "COW":
        body_col = (255, 255, 255, 255)
        # Horns
        d.ellipse([cx - 380, cy - 430, cx - 200, cy - 280], fill=(254, 240, 138, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx + 200, cy - 430, cx + 380, cy - 280], fill=(254, 240, 138, 255), outline=OUTLINE_COL, width=14)
        # Ears
        d.ellipse([cx - 500, cy - 280, cx - 240, cy - 140], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 240, cy - 280, cx + 500, cy - 140], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Cow spots
        d.ellipse([cx - 280, cy - 280, cx - 100, cy - 120], fill=(30, 30, 35, 255))
        d.ellipse([cx + 110, cy - 220, cx + 290, cy - 60], fill=(30, 30, 35, 255))
        # Pink muzzle
        d.ellipse([cx - 240, cy + 30, cx + 240, cy + 270], fill=(251, 207, 232, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 90, cy + 90, cx - 40, cy + 150], fill=(55, 65, 81, 255))
        d.ellipse([cx + 40, cy + 90, cx + 90, cy + 150], fill=(55, 65, 81, 255))
        draw_eyes(cy - 90, sep=140)
        draw_cheeks(cy + 40)
        draw_mouth(cy + 180, mw=95)
        # Bell
        d.polygon([(cx - 45, cy + 320), (cx + 45, cy + 320), (cx + 60, cy + 410), (cx - 60, cy + 410)], fill=(250, 204, 21, 255), outline=OUTLINE_COL, width=12)

    # 15. HORSE
    elif name == "HORSE":
        body_col = (153, 88, 42, 255)
        # Flowing mane
        d.polygon([(cx - 60, cy - 460), (cx + 60, cy - 460), (cx + 140, cy - 220), (cx - 140, cy - 220)], fill=(69, 26, 3, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 320, cy - 480, cx - 160, cy - 260], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 160, cy - 480, cx + 320, cy - 260], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 300, cy - 320, cx + 300, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # White star on forehead
        d.polygon([(cx, cy - 220), (cx + 25, cy - 170), (cx + 70, cy - 160), (cx + 30, cy - 125), (cx + 45, cy - 80), (cx, cy - 110), (cx - 45, cy - 80), (cx - 30, cy - 125), (cx - 70, cy - 160), (cx - 25, cy - 170)], fill="white")
        # Muzzle
        d.ellipse([cx - 190, cy + 60, cx + 190, cy + 280], fill=(217, 119, 6, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 70, cy + 120, cx - 35, cy + 165], fill=(45, 20, 10, 255))
        d.ellipse([cx + 35, cy + 120, cx + 70, cy + 165], fill=(45, 20, 10, 255))
        draw_eyes(cy - 60, sep=140)
        draw_cheeks(cy + 40)
        draw_mouth(cy + 190, mw=85)

    # 16. SHEEP
    elif name == "SHEEP":
        wool_col = (250, 248, 240, 255)
        # Cloud of fluffy wool puffs all around head
        for ang in range(0, 360, 28):
            rad = math.radians(ang)
            wx = cx + int(360 * math.cos(rad))
            wy = cy - 20 + int(320 * math.sin(rad))
            d.ellipse([wx - 110, wy - 110, wx + 110, wy + 110], fill=wool_col, outline=OUTLINE_COL, width=12)
        # Floppy ears
        d.ellipse([cx - 480, cy - 140, cx - 250, cy + 20], fill=(71, 85, 105, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx + 250, cy - 140, cx + 480, cy + 20], fill=(71, 85, 105, 255), outline=OUTLINE_COL, width=14)
        # Dark sheep face
        d.ellipse([cx - 250, cy - 200, cx + 250, cy + 260], fill=(55, 65, 81, 255), outline=OUTLINE_COL, width=THICK_W)
        # Wool puff crown on forehead
        d.ellipse([cx - 150, cy - 270, cx + 150, cy - 110], fill=wool_col, outline=OUTLINE_COL, width=12)
        draw_eyes(cy - 70, sep=110, r=42)
        draw_cheeks(cy + 40, sep=180, col=(255, 160, 180, 140))
        d.arc([cx - 70, cy + 70, cx + 70, cy + 160], start=20, end=160, fill="white", width=12)

    # 17. PIGLET
    elif name == "PIGLET":
        body_col = (244, 114, 182, 255)
        d.polygon([(cx - 360, cy - 260), (cx - 280, cy - 470), (cx - 130, cy - 300)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx + 130, cy - 300), (cx + 280, cy - 470), (cx + 360, cy - 260)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 360, cy - 330, cx + 360, cy + 350], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Oval pig snout
        d.ellipse([cx - 160, cy + 20, cx + 160, cy + 220], fill=(249, 168, 212, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 65, cy + 80, cx - 25, cy + 155], fill=(190, 24, 93, 255))
        d.ellipse([cx + 25, cy + 80, cx + 65, cy + 155], fill=(190, 24, 93, 255))
        draw_eyes(cy - 90, sep=140)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 225, mw=85)
        d.ellipse([cx - 300, cy + 310, cx - 110, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 300, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 18. DEER
    elif name == "DEER":
        body_col = (217, 119, 6, 255)
        # Antlers
        d.line([(cx - 150, cy - 280), (cx - 240, cy - 460)], fill=(120, 53, 15, 255), width=22)
        d.line([(cx - 200, cy - 370), (cx - 280, cy - 390)], fill=(120, 53, 15, 255), width=18)
        d.line([(cx + 150, cy - 280), (cx + 240, cy - 460)], fill=(120, 53, 15, 255), width=22)
        d.line([(cx + 200, cy - 370), (cx + 280, cy - 390)], fill=(120, 53, 15, 255), width=18)
        # Ears
        d.ellipse([cx - 420, cy - 320, cx - 220, cy - 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 320, cx + 420, cy - 180], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 300, cy - 300, cx + 300, cy + 320], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # White spots
        d.ellipse([cx - 80, cy - 220, cx - 50, cy - 190], fill="white")
        d.ellipse([cx + 50, cy - 220, cx + 80, cy - 190], fill="white")
        d.ellipse([cx - 20, cy - 170, cx + 20, cy - 130], fill="white")
        # Muzzle
        d.ellipse([cx - 160, cy + 20, cx + 160, cy + 220], fill=(255, 245, 230, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 50, cx + 45, cy + 105], fill=(30, 30, 35, 255))
        draw_eyes(cy - 70, sep=130, r=48, spec_r=22)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 130, mw=75)

    # 19. FOX
    elif name == "FOX":
        body_col = (234, 88, 12, 255)
        d.polygon([(cx - 380, cy - 200), (cx - 300, cy - 480), (cx - 140, cy - 260)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx + 140, cy - 260), (cx + 300, cy - 480), (cx + 380, cy - 200)], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.polygon([(cx - 320, cy - 220), (cx - 280, cy - 420), (cx - 180, cy - 270)], fill="white")
        d.polygon([(cx + 180, cy - 270), (cx + 280, cy - 420), (cx + 320, cy - 220)], fill="white")
        d.ellipse([cx - 360, cy - 300, cx + 360, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # White cheek ruffs
        d.polygon([(cx - 340, cy + 40), (cx - 120, cy + 200), (cx - 300, cy + 260)], fill="white", outline=OUTLINE_COL, width=12)
        d.polygon([(cx + 340, cy + 40), (cx + 120, cy + 200), (cx + 300, cy + 260)], fill="white", outline=OUTLINE_COL, width=12)
        d.polygon([(cx - 160, cy + 140), (cx + 160, cy + 140), (cx, cy + 280)], fill="white", outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 50, cy + 130, cx + 50, cy + 195], fill=(30, 30, 35, 255))
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 40)
        draw_mouth(cy + 220, mw=65)

    # 20. BEAR
    elif name == "BEAR":
        body_col = (120, 53, 15, 255)
        d.ellipse([cx - 450, cy - 460, cx - 220, cy - 230], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 460, cx + 450, cy - 230], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 390, cy - 400, cx - 280, cy - 290], fill=(217, 119, 6, 255))
        d.ellipse([cx + 280, cy - 400, cx + 390, cy - 290], fill=(217, 119, 6, 255))
        d.ellipse([cx - 390, cy - 340, cx + 390, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 200, cy + 20, cx + 200, cy + 260], fill=(254, 215, 170, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 60, cy + 60, cx + 60, cy + 135], fill=(30, 30, 35, 255))
        draw_eyes(cy - 80, sep=140)
        draw_cheeks(cy + 50)
        draw_mouth(cy + 150, mw=85)
        d.ellipse([cx - 320, cy + 310, cx - 110, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 320, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 21. SQUIRREL
    elif name == "SQUIRREL":
        body_col = (217, 119, 6, 255)
        # Giant bushy tail curving up in back
        d.arc([cx + 80, cy - 460, cx + 640, cy + 320], start=180, end=350, fill=OUTLINE_COL, width=90)
        d.arc([cx + 80, cy - 460, cx + 640, cy + 320], start=180, end=350, fill=(180, 83, 9, 255), width=65)
        d.ellipse([cx - 340, cy - 450, cx - 180, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 180, cy - 450, cx + 340, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 320, cy - 300, cx + 320, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 170, cy + 30, cx + 170, cy + 240], fill=(255, 237, 213, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 40, cy + 60, cx + 40, cy + 115], fill=(30, 30, 35, 255))
        # Holding an acorn
        d.ellipse([cx - 65, cy + 220, cx + 65, cy + 340], fill=(146, 64, 14, 255), outline=OUTLINE_COL, width=12)
        d.ellipse([cx - 75, cy + 200, cx + 75, cy + 260], fill=(120, 53, 15, 255), outline=OUTLINE_COL, width=10)
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 50)
        draw_mouth(cy + 130, mw=75)

    # 22. HEDGEHOG
    elif name == "HEDGEHOG":
        face_col = (254, 215, 170, 255)
        # Spiky quill crown radiating around back
        for ang in range(160, 380, 15):
            rad = math.radians(ang)
            qx = cx + int(360 * math.cos(rad))
            qy = cy - 20 + int(360 * math.sin(rad))
            d.polygon([(cx, cy - 20), (qx - 35, qy), (qx + 35, qy)], fill=(120, 53, 15, 255), outline=OUTLINE_COL, width=10)
        d.ellipse([cx - 300, cy - 240, cx + 300, cy + 340], fill=face_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 50, cy + 80, cx + 50, cy + 145], fill=(30, 30, 35, 255))
        draw_eyes(cy - 40, sep=120)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 160, mw=75)
        d.ellipse([cx - 260, cy + 280, cx - 110, cy + 420], fill=face_col, outline=OUTLINE_COL, width=14)
        d.ellipse([cx + 110, cy + 280, cx + 260, cy + 420], fill=face_col, outline=OUTLINE_COL, width=14)

    # 23. SLOTH
    elif name == "SLOTH":
        body_col = (168, 162, 158, 255)
        d.ellipse([cx - 360, cy - 300, cx + 360, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Eye mask bars
        d.ellipse([cx - 270, cy - 140, cx - 60, cy + 20], fill=(120, 113, 108, 255), outline=OUTLINE_COL, width=10)
        d.ellipse([cx + 60, cy - 140, cx + 270, cy + 20], fill=(120, 113, 108, 255), outline=OUTLINE_COL, width=10)
        # Sleepy curved eyes
        d.arc([cx - 200, cy - 80, cx - 130, cy - 20], start=20, end=160, fill="white", width=14)
        d.arc([cx + 130, cy - 80, cx + 200, cy - 20], start=20, end=160, fill="white", width=14)
        d.ellipse([cx - 180, cy + 20, cx + 180, cy + 220], fill=(245, 245, 244, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 60, cx + 45, cy + 120], fill=(41, 37, 36, 255))
        draw_cheeks(cy + 60)
        draw_mouth(cy + 135, mw=85)

    # 24. CAMEL
    elif name == "CAMEL":
        body_col = (212, 163, 115, 255)
        # Hump
        d.ellipse([cx + 80, cy - 120, cx + 520, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Neck & Head
        d.rectangle([cx - 160, cy + 40, cx + 60, cy + 440], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 320, cy - 360, cx + 140, cy + 120], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Muzzle
        d.ellipse([cx - 420, cy - 180, cx - 120, cy + 80], fill=(254, 243, 199, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 360, cy - 80, cx - 320, cy - 40], fill=(120, 53, 15, 255))
        d.ellipse([cx - 120, cy - 440, cx - 20, cy - 280], fill=body_col, outline=OUTLINE_COL, width=16)
        draw_eyes(cy - 120, sep=80, r=42)
        d.arc([cx - 340, cy - 20, cx - 200, cy + 60], start=20, end=160, fill=OUTLINE_COL, width=14)

    # 25. CHEETAH
    elif name == "CHEETAH":
        body_col = (245, 158, 11, 255)
        d.ellipse([cx - 420, cy - 420, cx - 220, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 420, cx + 420, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 360, cy - 320, cx + 360, cy + 360], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Spots
        for sx, sy in [(-220, -180), (-160, -240), (0, -260), (160, -240), (220, -180), (-260, 40), (260, 40)]:
            d.ellipse([cx + sx - 25, cy + sy - 25, cx + sx + 25, cy + sy + 25], fill=(30, 30, 35, 255))
        # Tear tracks
        d.line([(cx - 110, cy - 20), (cx - 70, cy + 120)], fill=(30, 30, 35, 255), width=16)
        d.line([(cx + 110, cy - 20), (cx + 70, cy + 120)], fill=(30, 30, 35, 255), width=16)
        d.ellipse([cx - 180, cy + 40, cx + 180, cy + 240], fill=(255, 250, 240, 255), outline=OUTLINE_COL, width=14)
        d.polygon([(cx - 45, cy + 70), (cx + 45, cy + 70), (cx, cy + 120)], fill=(30, 30, 35, 255))
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 130, mw=80)

    # 26. RHINO
    elif name == "RHINO":
        body_col = (100, 116, 139, 255)
        d.ellipse([cx - 360, cy - 440, cx - 220, cy - 300], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 440, cx + 360, cy - 300], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 340, cy - 340, cx + 340, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Big Rhino horn
        d.polygon([(cx - 45, cy + 80), (cx + 45, cy + 80), (cx, cy - 80)], fill=(241, 245, 249, 255), outline=OUTLINE_COL, width=14)
        d.polygon([(cx - 25, cy + 130), (cx + 25, cy + 130), (cx, cy + 50)], fill=(241, 245, 249, 255), outline=OUTLINE_COL, width=10)
        draw_eyes(cy - 100, sep=150, r=42)
        draw_cheeks(cy + 20, sep=240)
        draw_mouth(cy + 170, mw=90)
        d.ellipse([cx - 300, cy + 300, cx - 110, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 300, cx + 300, cy + 480], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    # 27. OTTER
    elif name == "OTTER":
        body_col = (113, 63, 18, 255)
        d.ellipse([cx - 380, cy - 360, cx - 240, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 240, cy - 360, cx + 380, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 340, cy - 320, cx + 340, cy + 320], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 190, cy + 10, cx + 190, cy + 220], fill=(254, 243, 199, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 40, cx + 45, cy + 95], fill=(30, 30, 35, 255))
        # Holding smooth river pebble / shell
        d.ellipse([cx - 55, cy + 240, cx + 55, cy + 350], fill=(203, 213, 225, 255), outline=OUTLINE_COL, width=12)
        for s in (-1, 1):
            d.line([(cx + s * 90, cy + 70), (cx + s * 240, cy + 60)], fill=OUTLINE_COL, width=8)
            d.line([(cx + s * 90, cy + 95), (cx + s * 240, cy + 105)], fill=OUTLINE_COL, width=8)
        draw_eyes(cy - 70, sep=130)
        draw_cheeks(cy + 40)
        draw_mouth(cy + 110, mw=75)

    # 28. BEAVER
    elif name == "BEAVER":
        body_col = (92, 51, 23, 255)
        # Paddle tail behind
        d.ellipse([cx + 120, cy + 40, cx + 540, cy + 420], fill=(45, 25, 15, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 360, cy - 380, cx - 220, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 380, cx + 360, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 340, cy - 320, cx + 340, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 180, cy + 20, cx + 180, cy + 220], fill=(254, 215, 170, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 50, cx + 45, cy + 105], fill=(30, 30, 35, 255))
        # Two prominent white buck teeth
        d.rectangle([cx - 30, cy + 120, cx, cy + 185], fill="white", outline=OUTLINE_COL, width=8)
        d.rectangle([cx, cy + 120, cx + 30, cy + 185], fill="white", outline=OUTLINE_COL, width=8)
        draw_eyes(cy - 70, sep=130)
        draw_cheeks(cy + 50)
        draw_mouth(cy + 110, mw=75)

    # 29. LLAMA
    elif name == "LLAMA":
        body_col = (255, 250, 240, 255)
        # Tall ears
        d.ellipse([cx - 240, cy - 540, cx - 80, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 80, cy - 540, cx + 240, cy - 220], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 200, cy - 480, cx - 120, cy - 280], fill=(255, 190, 200, 255))
        d.ellipse([cx + 120, cy - 480, cx + 200, cy - 280], fill=(255, 190, 200, 255))
        # Fluffy neck
        d.rectangle([cx - 160, cy - 20, cx + 160, cy + 440], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 260, cy - 320, cx + 260, cy + 140], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Colorful pom-pom halter
        d.line([(cx - 180, cy - 30), (cx + 180, cy - 30)], fill=(239, 68, 68, 255), width=16)
        for px, pcol in [(-120, (234, 179, 8, 255)), (-40, (59, 130, 246, 255)), (40, (16, 185, 129, 255)), (120, (236, 72, 153, 255))]:
            d.ellipse([cx + px - 25, cy - 10, cx + px + 25, cy + 40], fill=pcol, outline=OUTLINE_COL, width=8)
        d.ellipse([cx - 130, cy - 40, cx + 130, cy + 140], fill=(254, 240, 220, 255), outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 35, cy + 10, cx + 35, cy + 50], fill=(30, 30, 35, 255))
        draw_eyes(cy - 120, sep=110, r=42)
        draw_cheeks(cy - 20, sep=180)
        draw_mouth(cy + 60, mw=65)

    # 30. RACCOON
    elif name == "RACCOON":
        body_col = (148, 163, 184, 255)
        d.ellipse([cx - 420, cy - 440, cx - 220, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 440, cx + 420, cy - 240], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 370, cy - 390, cx - 270, cy - 290], fill="white")
        d.ellipse([cx + 270, cy - 390, cx + 370, cy - 290], fill="white")
        d.ellipse([cx - 360, cy - 300, cx + 360, cy + 340], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        # Black bandit mask
        d.polygon([(cx - 320, cy - 120), (cx, cy - 50), (cx + 320, cy - 120), (cx + 280, cy + 40), (cx, cy + 10), (cx - 280, cy + 40)], fill=(30, 30, 35, 255), outline=OUTLINE_COL, width=10)
        # White muzzle
        d.ellipse([cx - 160, cy + 20, cx + 160, cy + 200], fill="white", outline=OUTLINE_COL, width=14)
        d.ellipse([cx - 45, cy + 50, cx + 45, cy + 105], fill=(30, 30, 35, 255))
        draw_eyes(cy - 60, sep=130)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 120, mw=75)

    # UNIVERSAL FALLBACK
    else:
        body_col = primary_color + (255,)
        d.ellipse([cx - 450, cy - 480, cx - 220, cy - 250], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 220, cy - 480, cx + 450, cy - 250], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 400, cy - 380, cx + 400, cy + 380], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx - 200, cy + 20, cx + 200, cy + 270], fill=(255, 245, 225, 255), outline=OUTLINE_COL, width=16)
        d.ellipse([cx - 45, cy + 70, cx + 45, cy + 140], fill=(240, 60, 90, 255))
        draw_eyes(cy - 80, sep=130)
        draw_cheeks(cy + 60)
        draw_mouth(cy + 130, mw=85)
        d.ellipse([cx - 320, cy + 310, cx - 110, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)
        d.ellipse([cx + 110, cy + 310, cx + 320, cy + 490], fill=body_col, outline=OUTLINE_COL, width=THICK_W)

    return im
