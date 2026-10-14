import math
from PIL import Image, ImageDraw

OUTLINE_DARK = (45, 15, 10, 255)

def draw_five_point_star(draw: ImageDraw.ImageDraw, cx: float, cy: float, outer_r: float, inner_r: float, fill: tuple, outline: tuple | None = None, width: int = 1) -> None:
    pts = []
    for i in range(10):
        r = outer_r if i % 2 == 0 else inner_r
        ang = -math.pi / 2 + i * (math.pi / 5)
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    draw.polygon(pts, fill=fill, outline=outline, width=width)

def draw_sparkle_star(draw: ImageDraw.ImageDraw, cx: int, cy: int, outer_r: int = 22, inner_r: int = 5) -> None:
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

def draw_mascot_boy(canvas: Image.Image, cx: int, cy: int, sc: float = 1.0) -> None:
    draw = ImageDraw.Draw(canvas)
    skin_col = (255, 224, 194, 255)
    hair_col = (120, 53, 15, 255)
    purple_col = (126, 34, 206, 255)
    cap_blue = (2, 132, 199, 255)
    cap_yellow = (250, 204, 21, 255)
    cap_green = (34, 197, 94, 255)
    cap_red = (239, 68, 68, 255)

    def s(v):
        return int(v * sc)

    # 1. Torso / Purple Hoodie
    draw.polygon([
        (cx - s(120), cy + s(80)),
        (cx + s(80), cy + s(80)),
        (cx + s(140), cy + s(200)),
        (cx - s(170), cy + s(200))
    ], fill=purple_col, outline=OUTLINE_DARK, width=s(7))
    # Hoodie collar
    draw.arc([cx - s(50), cy + s(65), cx + s(20), cy + s(115)], start=0, end=180, fill=OUTLINE_DARK, width=s(6))

    # 2. Raised Arm holding Magic Wand (left side)
    # Sleeve
    draw.polygon([
        (cx - s(110), cy + s(90)),
        (cx - s(160), cy + s(30)),
        (cx - s(130), cy + s(10)),
        (cx - s(80), cy + s(75))
    ], fill=purple_col, outline=OUTLINE_DARK, width=s(6))
    # Hand
    draw.ellipse([cx - s(175), cy - s(10), cx - s(130), cy + s(35)], fill=skin_col, outline=OUTLINE_DARK, width=s(6))
    # Wand stick pointing up-left
    draw.line([(cx - s(145), cy + s(15)), (cx - s(215), cy - s(95))], fill=(180, 83, 9, 255), width=s(10))
    # Glowing Star Tip
    star_x, star_y = cx - s(225), cy - s(105)
    draw.ellipse([star_x - s(45), star_y - s(45), star_x + s(45), star_y + s(45)], fill=(254, 240, 138, 160))
    draw_five_point_star(draw, star_x, star_y, outer_r=s(32), inner_r=s(14), fill=(250, 204, 21, 255), outline=OUTLINE_DARK, width=s(4))
    # Little sparkles
    draw_sparkle_star(draw, star_x + s(25), star_y - s(25), outer_r=s(14), inner_r=s(3))
    draw_sparkle_star(draw, star_x - s(25), star_y + s(25), outer_r=s(10), inner_r=s(2))

    # 3. Ears
    draw.ellipse([cx - s(135), cy - s(25), cx - s(95), cy + s(35)], fill=skin_col, outline=OUTLINE_DARK, width=s(6))
    draw.ellipse([cx + s(55), cy - s(25), cx + s(95), cy + s(35)], fill=skin_col, outline=OUTLINE_DARK, width=s(6))
    draw.arc([cx - s(125), cy - s(15), cx - s(105), cy + s(15)], start=270, end=90, fill=(244, 114, 182, 255), width=s(3))
    draw.arc([cx + s(65), cy - s(15), cx + s(85), cy + s(15)], start=90, end=270, fill=(244, 114, 182, 255), width=s(3))

    # 4. Face (Peachy skin)
    draw.ellipse([cx - s(115), cy - s(80), cx + s(75), cy + s(95)], fill=skin_col, outline=OUTLINE_DARK, width=s(7))

    # 5. Cheerful Face Features
    # Rosy Cheeks
    draw.ellipse([cx - s(95), cy + s(10), cx - s(50), cy + s(45)], fill=(255, 150, 170, 190))
    draw.ellipse([cx + s(15), cy + s(10), cx + s(60), cy + s(45)], fill=(255, 150, 170, 190))

    # Big Cartoon Eyes
    for ex in (cx - s(65), cx + s(25)):
        # Eye white
        draw.ellipse([ex - s(22), cy - s(30), ex + s(22), cy + s(18)], fill=(255, 255, 255, 255), outline=OUTLINE_DARK, width=s(4))
        # Iris (Dark Navy/Brown)
        draw.ellipse([ex - s(16), cy - s(24), ex + s(16), cy + s(14)], fill=(30, 27, 75, 255))
        # Specular shine
        draw.ellipse([ex - s(10), cy - s(20), ex + s(2), cy - s(8)], fill="white")
        draw.ellipse([ex + s(4), cy + s(2), ex + s(10), cy + s(8)], fill="white")
        # Eyebrow
        draw.arc([ex - s(20), cy - s(48), ex + s(20), cy - s(32)], start=200, end=340, fill=OUTLINE_DARK, width=s(5))

    # Cute button nose
    draw.ellipse([cx - s(24), cy - s(5), cx - s(14), cy + s(8)], fill=(244, 114, 182, 255))

    # Happy open mouth with pink tongue
    draw.pieslice([cx - s(48), cy + s(18), cx + s(6), cy + s(70)], start=10, end=170, fill=(220, 38, 38, 255), outline=OUTLINE_DARK, width=s(5))
    draw.pieslice([cx - s(36), cy + s(38), cx - s(6), cy + s(70)], start=20, end=160, fill=(251, 146, 60, 255))

    # 6. Brown Hair Tufts
    draw.polygon([(cx - s(105), cy - s(50), cx - s(125), cy - s(20), cx - s(95), cy - s(30))], fill=hair_col, outline=OUTLINE_DARK, width=s(4))
    draw.polygon([(cx + s(55), cy - s(50), cx + s(80), cy - s(20), cx + s(50), cy - s(30))], fill=hair_col, outline=OUTLINE_DARK, width=s(4))
    draw.polygon([(cx - s(40), cy - s(65), cx - s(25), cy - s(45), cx - s(10), cy - s(65))], fill=hair_col, outline=OUTLINE_DARK, width=s(4))

    # 7. Colorful Baseball Cap (Drawn ON TOP of head)
    # Cap band (Red)
    draw.rounded_rectangle([cx - s(125), cy - s(85), cx + s(85), cy - s(50)], radius=s(14), fill=cap_red, outline=OUTLINE_DARK, width=s(6))
    # Cap Crown - 3 colorful panels
    # Left panel (Cyan)
    draw.pieslice([cx - s(120), cy - s(185), cx + s(80), cy + s(15)], start=180, end=235, fill=cap_blue, outline=OUTLINE_DARK, width=s(6))
    # Middle panel (Yellow)
    draw.pieslice([cx - s(120), cy - s(185), cx + s(80), cy + s(15)], start=235, end=290, fill=cap_yellow, outline=OUTLINE_DARK, width=s(6))
    # Right panel (Green)
    draw.pieslice([cx - s(120), cy - s(185), cx + s(80), cy + s(15)], start=290, end=360, fill=cap_green, outline=OUTLINE_DARK, width=s(6))
    # Cap Visor (pointing slightly right/front)
    draw.polygon([
        (cx + s(25), cy - s(65)),
        (cx + s(130), cy - s(45)),
        (cx + s(115), cy - s(25)),
        (cx + s(15), cy - s(45))
    ], fill=cap_yellow, outline=OUTLINE_DARK, width=s(6))
    # Cap top button
    draw.ellipse([cx - s(28), cy - s(195), cx - s(10), cy - s(177)], fill=cap_red, outline=OUTLINE_DARK, width=s(4))

im = Image.new("RGBA", (800, 800), (240, 240, 245, 255))
draw_mascot_boy(im, 400, 400, sc=1.2)
im.save("scratch/test_mascot_out.png")
print("Saved scratch/test_mascot_out.png")
