import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

fonts_dir = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp/assets/fonts")
font = ImageFont.truetype(str(fonts_dir / "Fredoka-Bold.ttf"), 36)

# Test Ribbon drawing with procedural vector stars instead of unicode ★
im = Image.new("RGBA", (700, 120), (255, 255, 255, 0))
draw = ImageDraw.Draw(im)

def draw_sparkle_star(draw, cx, cy, outer_r=16, inner_r=4):
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
    draw.polygon(pts, fill=(245, 158, 11, 255), outline=(180, 83, 9, 255))
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(255, 255, 255, 255))

text = "TITLES IN THIS SERIES"
bbox = draw.textbbox((0, 0), text, font=font)
tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

cx, cy = 350, 60
# Ribbon body
bw, bh = tw + 140, th + 30
x0, y0 = cx - bw // 2, cy - bh // 2
x1, y1 = x0 + bw, y0 + bh
draw.rounded_rectangle([x0, y0, x1, y1], radius=16, fill=(255, 251, 235, 255), outline=(30, 30, 35, 255), width=4)
# Stitched line
draw.rounded_rectangle([x0 + 6, y0 + 6, x1 - 6, y1 - 6], radius=12, outline=(245, 158, 11, 255), width=2)
# Text
draw.text((cx - tw // 2, cy - th // 2 - 2), text, fill=(69, 26, 3, 255), font=font)
# Procedural stars
draw_sparkle_star(draw, cx - tw // 2 - 35, cy, outer_r=15, inner_r=4)
draw_sparkle_star(draw, cx + tw // 2 + 35, cy, outer_r=15, inner_r=4)

out_file = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp/.agents/teamwork/explorer_survey_2/clean_ribbon.png")
im.save(out_file)
print(f"Saved clean ribbon: {out_file}")
