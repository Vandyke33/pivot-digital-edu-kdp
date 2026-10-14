import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Set utf-8 stdout
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

fonts_dir = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp/assets/fonts")
test_chars = ["\u2605", "\u00a9", "\u2022", "\u25a1", "A", "Z"]

for f in sorted(fonts_dir.glob("*.ttf")):
    try:
        font = ImageFont.truetype(str(f), 40)
        print(f"\nFont: {f.name}")
        for ch in test_chars:
            try:
                mask = font.getmask(ch)
                bbox = font.getbbox(ch)
                # Check if glyph is .notdef / empty or if bbox is non-zero
                print(f"  Char U+{ord(ch):04X}: bbox={bbox}, mask size={mask.size}")
            except Exception as e:
                print(f"  Char U+{ord(ch):04X}: ERROR {e}")
    except Exception as exc:
        print(f"Error loading {f.name}: {exc}")

# Check what Fredoka-Bold.ttf renders for '★'
f_fredoka = ImageFont.truetype(str(fonts_dir / "Fredoka-Bold.ttf"), 40)
im = Image.new("RGB", (300, 100), "white")
d = ImageDraw.Draw(im)
d.text((10, 10), "\u2605 TEST \u2605", fill="black", font=f_fredoka)
out_img = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp/.agents/teamwork/explorer_survey_2/test_star.png")
im.save(out_img)
print(f"\nSaved {out_img}")
