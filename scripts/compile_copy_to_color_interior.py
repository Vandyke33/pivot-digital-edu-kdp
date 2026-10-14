"""
Automated 32-Page 'Copy to Color' Interior Compiler for All 12 Series Volumes.

Replicates the exact commercial 'Copy to Color' retail page layout:
  - Page 1: Decorative Welcome & 'This Book Belongs To' page under official imprint
            'The Pivot Kids (Color & Play)' and title 'Copy to Color: <Subject>'.
  - Pages 2..31: 30 Interactive 'Copy to Color' activity pages:
      * Top-Left: Giant bold index code / letter (e.g., '01', '02', 'Aa', 'Bb')
      * Top-Right: Warm peach brushstroke banner with uppercase subject name (e.g., 'TIGER', 'MONKEY')
      * Top-Right: Framed 'Color Guide' thumbnail reference illustration
      * Main Center-Left: Crisp, bold 300 DPI B&W coloring outline (1:1 geometry with Color Guide)
      * Bottom Footer: Double-layered colorful wave, circular page number badge, and series title
  - Page 32: 'Super Colorist Award' Completion Certificate.

Strict Brand & Title Naming Policy:
  - Canonical Title: 'Copy to Color: <Subject>'
  - Prohibited: Strictly NEVER includes 'My First'.

Dependencies: pillow reportlab numpy
"""

from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps

# Ensure repo root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from scripts.utils.animal_illustrations import draw_animal_character
except ImportError:
    try:
        from utils.animal_illustrations import draw_animal_character
    except ImportError:
        draw_animal_character = None


# ---------------------------------------------------------------------------
# 1. KDP PHYSICAL & CANVAS CONSTANTS (8.5 x 11.0 in @ 300 DPI)
# ---------------------------------------------------------------------------
DPI = 300
PAGE_W = int(8.5 * DPI)       # 2550 px
PAGE_H = int(11.0 * DPI)      # 3300 px
SAFE_MARGIN = int(0.5 * DPI)  # 150 px

# ---------------------------------------------------------------------------
# 2. 12-VOLUME SERIES CATALOG & 30-SUBJECT CURATED REGISTRY
# ---------------------------------------------------------------------------
SERIES_CATALOG: dict[str, dict[str, Any]] = {
    "vol_01": {
        "title": "Alphabet",
        "primary": (255, 107, 53),
        "secondary": (220, 38, 38),
        "accent": (255, 230, 109),
        "subjects": [
            ("Aa", "APPLE"), ("Bb", "BALL"), ("Cc", "CAKE"), ("Dd", "DEER"), ("Ee", "ELEPHANT"),
            ("Ff", "FISH"), ("Gg", "GIRAFFE"), ("Hh", "HOUSE"), ("Ii", "ICE CREAM"), ("Jj", "JEEP"),
            ("Kk", "KITE"), ("Ll", "LION"), ("Mm", "MONKEY"), ("Nn", "NEST"), ("Oo", "OWL"),
            ("Pp", "PARROT"), ("Qq", "QUEEN BEE"), ("Rr", "RABBIT"), ("Ss", "SUN"), ("Tt", "TIGER"),
            ("Uu", "UMBRELLA"), ("Vv", "VAN"), ("Ww", "WHALE"), ("Xx", "XYLOPHONE"), ("Yy", "YACHT"),
            ("Zz", "ZEBRA"), ("01", "STAR"), ("02", "BELL"), ("03", "TREE"), ("04", "BOAT"),
        ],
    },
    "vol_02": {
        "title": "Animals",
        "primary": (255, 73, 73),
        "secondary": (234, 88, 12),
        "accent": (255, 235, 120),
        "subjects": [
            ("01", "TIGER"), ("02", "MONKEY"), ("03", "ELEPHANT"), ("04", "GIRAFFE"), ("05", "LION"),
            ("06", "ZEBRA"), ("07", "HIPPO"), ("08", "KOALA"), ("09", "PANDA"), ("10", "KANGAROO"),
            ("11", "RABBIT"), ("12", "PUPPY"), ("13", "KITTEN"), ("14", "COW"), ("15", "HORSE"),
            ("16", "SHEEP"), ("17", "PIGLET"), ("18", "DEER"), ("19", "FOX"), ("20", "BEAR"),
            ("21", "SQUIRREL"), ("22", "HEDGEHOG"), ("23", "SLOTH"), ("24", "CAMEL"), ("25", "CHEETAH"),
            ("26", "RHINO"), ("27", "OTTER"), ("28", "BEAVER"), ("29", "LLAMA"), ("30", "RACCOON"),
        ],
    },
    "vol_03": {
        "title": "Birds",
        "primary": (16, 185, 129),
        "secondary": (5, 150, 105),
        "accent": (167, 243, 208),
        "subjects": [
            ("01", "PARROT"), ("02", "OWL"), ("03", "PEACOCK"), ("04", "FLAMINGO"), ("05", "EAGLE"),
            ("06", "PENGUIN"), ("07", "TOUCAN"), ("08", "HUMMINGBIRD"), ("09", "SWAN"), ("10", "DUCK"),
            ("11", "ROOSTER"), ("12", "PIGEON"), ("13", "WOODPECKER"), ("14", "ROBIN"), ("15", "BLUE JAY"),
            ("16", "CANARY"), ("17", "SEAGULL"), ("18", "SPARROW"), ("19", "PELICAN"), ("20", "KINGFISHER"),
            ("21", "OSTRICH"), ("22", "HERON"), ("23", "STORK"), ("24", "FALCON"), ("25", "SWALLOW"),
            ("26", "GOOSE"), ("27", "GOLDFINCH"), ("28", "FINCH"), ("29", "DOVE"), ("30", "CARDINAL"),
        ],
    },
    "vol_04": {
        "title": "Sports",
        "primary": (101, 163, 13),
        "secondary": (77, 124, 15),
        "accent": (217, 249, 157),
        "subjects": [
            ("01", "SOCCER"), ("02", "BASKETBALL"), ("03", "BASEBALL"), ("04", "TENNIS"), ("05", "SWIMMING"),
            ("06", "CYCLING"), ("07", "SKATEBOARD"), ("08", "RUNNING"), ("09", "GYMNASTICS"), ("10", "VOLLEYBALL"),
            ("11", "HOCKEY"), ("12", "GOLF"), ("13", "RUGBY"), ("14", "BADMINTON"), ("15", "BOXING"),
            ("16", "SURFING"), ("17", "SKIING"), ("18", "KARATE"), ("19", "ARCHERY"), ("20", "ROWING"),
            ("21", "BOWLING"), ("22", "HORSE RIDING"), ("23", "FENCING"), ("24", "DIVING"), ("25", "SAILING"),
            ("26", "ROLLER SKATING"), ("27", "CANOEING"), ("28", "ICE SKATING"), ("29", "CRICKET"), ("30", "TABLE TENNIS"),
        ],
    },
    "vol_05": {
        "title": "Monsters",
        "primary": (217, 70, 239),
        "secondary": (162, 28, 175),
        "accent": (251, 207, 232),
        "subjects": [
            ("01", "GLOWY"), ("02", "FUZZY"), ("03", "SPARKY"), ("04", "BUBBLE"), ("05", "SPIKE"),
            ("06", "TOOTHY"), ("07", "CHUBBY"), ("08", "GIGGLES"), ("09", "CYCLOPS"), ("10", "TENTACLES"),
            ("11", "STRIPEY"), ("12", "DOTTY"), ("13", "WINGY"), ("14", "HORNED"), ("15", "BLOBBY"),
            ("16", "FLUFFY"), ("17", "SNUGGLE"), ("18", "BOUNCY"), ("19", "CHOMPER"), ("20", "ZOOMY"),
            ("21", "SPOOKY"), ("22", "HAPPY"), ("23", "PEEKABOO"), ("24", "WOBBLY"), ("25", "WHISKERS"),
            ("26", "STARBURST"), ("27", "TINY"), ("28", "GIANT"), ("29", "FRIENDLY"), ("30", "SLEEPY"),
        ],
    },
    "vol_06": {
        "title": "Numbers",
        "primary": (153, 27, 27),
        "secondary": (185, 28, 28),
        "accent": (254, 202, 202),
        "subjects": [
            ("01", "ONE SUN"), ("02", "TWO BIRDS"), ("03", "THREE CATS"), ("04", "FOUR APPLES"), ("05", "FIVE STARS"),
            ("06", "SIX BEES"), ("07", "SEVEN FISH"), ("08", "EIGHT CUPS"), ("09", "NINE CARS"), ("10", "TEN FLOWERS"),
            ("11", "ELEVEN BALLS"), ("12", "TWELVE HATS"), ("13", "THIRTEEN HEARTS"), ("14", "FOURTEEN LEAVES"), ("15", "FIFTEEN BOATS"),
            ("16", "SIXTEEN DOTS"), ("17", "SEVENTEEN CAKES"), ("18", "EIGHTEEN TREES"), ("19", "NINETEEN DUCKS"), ("20", "TWENTY EGGS"),
            ("21", "COUNT CLOUD"), ("22", "COUNT PENCIL"), ("23", "COUNT CLOCK"), ("24", "COUNT COIN"), ("25", "COUNT CRAYON"),
            ("26", "PLUS SIGN"), ("27", "MINUS SIGN"), ("28", "EQUAL SIGN"), ("29", "NUMBER TREE"), ("30", "MATH WIZARD"),
        ],
    },
    "vol_07": {
        "title": "Fruits",
        "primary": (13, 148, 136),
        "secondary": (15, 118, 110),
        "accent": (153, 246, 228),
        "subjects": [
            ("01", "APPLE"), ("02", "BANANA"), ("03", "ORANGE"), ("04", "STRAWBERRY"), ("05", "GRAPES"),
            ("06", "WATERMELON"), ("07", "MANGO"), ("08", "PINEAPPLE"), ("09", "PEACH"), ("10", "CHERRY"),
            ("11", "BLUEBERRY"), ("12", "KIWI"), ("13", "LEMON"), ("14", "PEAR"), ("15", "PLUM"),
            ("16", "PAPAYA"), ("17", "AVOCADO"), ("18", "COCONUT"), ("19", "POMEGRANATE"), ("20", "RASPBERRY"),
            ("21", "FIG"), ("22", "LIME"), ("23", "GUAVA"), ("24", "APRICOT"), ("25", "BLACKBERRY"),
            ("26", "DRAGON FRUIT"), ("27", "PASSION FRUIT"), ("28", "CANTALOUPE"), ("29", "GRAPEFRUIT"), ("30", "FRUIT BASKET"),
        ],
    },
    "vol_08": {
        "title": "Shapes",
        "primary": (236, 72, 153),
        "secondary": (190, 24, 93),
        "accent": (254, 205, 211),
        "subjects": [
            ("01", "CIRCLE"), ("02", "SQUARE"), ("03", "TRIANGLE"), ("04", "RECTANGLE"), ("05", "STAR"),
            ("06", "HEART"), ("07", "OVAL"), ("08", "DIAMOND"), ("09", "PENTAGON"), ("10", "HEXAGON"),
            ("11", "CRESCENT"), ("12", "OCTAGON"), ("13", "CROSS"), ("14", "ARROW"), ("15", "SPIRAL"),
            ("16", "CYLINDER"), ("17", "CUBE"), ("18", "CONE"), ("19", "SPHERE"), ("20", "PYRAMID"),
            ("21", "SHAPE TRAIN"), ("22", "SHAPE CASTLE"), ("23", "SHAPE ROCKET"), ("24", "SHAPE ROBOT"), ("25", "SHAPE CLOCK"),
            ("26", "SHAPE HOUSE"), ("27", "SHAPE CAR"), ("28", "SHAPE FLOWER"), ("29", "SHAPE SUN"), ("30", "SHAPE CATERPILLAR"),
        ],
    },
    "vol_09": {
        "title": "Toys",
        "primary": (2, 132, 199),
        "secondary": (3, 105, 161),
        "accent": (186, 230, 253),
        "subjects": [
            ("01", "TEDDY BEAR"), ("02", "TOY CAR"), ("03", "BUILDING BLOCKS"), ("04", "DOLL"), ("05", "TOY TRAIN"),
            ("06", "DRUM"), ("07", "ROCKING HORSE"), ("08", "YO-YO"), ("09", "KITE"), ("10", "RUBBER DUCK"),
            ("11", "SPINNING TOP"), ("12", "BALLOON"), ("13", "ROBOT TOY"), ("14", "WATER PISTOL"), ("15", "PUZZLE"),
            ("16", "PINWHEEL"), ("17", "XYLOPHONE TOY"), ("18", "TOY PLANE"), ("19", "ACTION FIGURE"), ("20", "JACK IN THE BOX"),
            ("21", "SLINKY"), ("22", "MARBLES"), ("23", "PLUSH BUNNY"), ("24", "TOY BOAT"), ("25", "WIND-UP MOUSE"),
            ("26", "MAGIC WAND"), ("27", "KALEIDOSCOPE"), ("28", "PUPPET"), ("29", "TEA SET"), ("30", "TOY BOX"),
        ],
    },
    "vol_10": {
        "title": "Flowers",
        "primary": (120, 53, 15),
        "secondary": (180, 83, 9),
        "accent": (253, 230, 138),
        "subjects": [
            ("01", "SUNFLOWER"), ("02", "ROSE"), ("03", "TULIP"), ("04", "DAISY"), ("05", "LILY"),
            ("06", "ORCHID"), ("07", "LOTUS"), ("08", "MARIGOLD"), ("09", "HIBISCUS"), ("10", "CARNATION"),
            ("11", "JASMINE"), ("12", "LAVENDER"), ("13", "DAFFODIL"), ("14", "POPPY"), ("15", "CHERRY BLOSSOM"),
            ("16", "BLUEBELL"), ("17", "PANSY"), ("18", "VIOLET"), ("19", "PEONY"), ("20", "CHRYSANTHEMUM"),
            ("21", "MAGNOLIA"), ("22", "IRIS"), ("23", "GARDENIA"), ("24", "CLOVER"), ("25", "DANDELION"),
            ("26", "WATER LILY"), ("27", "SNAPDRAGON"), ("28", "MORNING GLORY"), ("29", "CAMELLIA"), ("30", "FLOWER BOUQUET"),
        ],
    },
    "vol_11": {
        "title": "Transport",
        "primary": (30, 58, 138),
        "secondary": (29, 78, 216),
        "accent": (191, 219, 254),
        "subjects": [
            ("01", "CAR"), ("02", "BUS"), ("03", "BICYCLE"), ("04", "TRAIN"), ("05", "AIRPLANE"),
            ("06", "BOAT"), ("07", "HELICOPTER"), ("08", "MOTORCYCLE"), ("09", "FIRE TRUCK"), ("10", "POLICE CAR"),
            ("11", "AMBULANCE"), ("12", "SCOOTER"), ("13", "SUBMARINE"), ("14", "HOT AIR BALLOON"), ("15", "TRACTOR"),
            ("16", "TAXI"), ("17", "TRUCK"), ("18", "ROCKET"), ("19", "SHIP"), ("20", "SKATEBOARD"),
            ("21", "CABLE CAR"), ("22", "FERRY"), ("23", "BULLDOZER"), ("24", "CEMENT MIXER"), ("25", "CRANE"),
            ("26", "DIRT BIKE"), ("27", "HOVERCRAFT"), ("28", "MONORAIL"), ("29", "TRAM"), ("30", "SPACE SHUTTLE"),
        ],
    },
    "vol_12": {
        "title": "Vegetables",
        "primary": (109, 40, 217),
        "secondary": (124, 58, 237),
        "accent": (221, 214, 254),
        "subjects": [
            ("01", "CARROT"), ("02", "TOMATO"), ("03", "BROCCOLI"), ("04", "POTATO"), ("05", "CORN"),
            ("06", "EGGPLANT"), ("07", "PEAS"), ("08", "PUMPKIN"), ("09", "CUCUMBER"), ("10", "BELL PEPPER"),
            ("11", "ONION"), ("12", "GARLIC"), ("13", "MUSHROOM"), ("14", "CAULIFLOWER"), ("15", "CABBAGE"),
            ("16", "LETTUCE"), ("17", "SPINACH"), ("18", "RADISH"), ("19", "BEETROOT"), ("20", "ZUCCHINI"),
            ("21", "SWEET POTATO"), ("22", "ASPARAGUS"), ("23", "CELERY"), ("24", "GINGER"), ("25", "ARTICHOKE"),
            ("26", "CHILI PEPPER"), ("27", "TURNIP"), ("28", "GREEN BEANS"), ("29", "OKRA"), ("30", "VEGETABLE BASKET"),
        ],
    },
}

# ---------------------------------------------------------------------------
# 3. FONT LOADER HELPER
# ---------------------------------------------------------------------------
def load_font(font_name: str, size: int, fonts_dir: str = "assets/fonts") -> ImageFont.FreeTypeFont:
    """Loads a TrueType font with graceful fallback to system / default."""
    candidates = [
        os.path.join(fonts_dir, font_name),
        os.path.join("assets/fonts", font_name),
        os.path.join(fonts_dir, "Fredoka-Bold.ttf"),
        os.path.join(fonts_dir, "LuckiestGuy-Regular.ttf"),
    ]
    for cand in candidates:
        if os.path.exists(cand):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ---------------------------------------------------------------------------
# 4. ZERO-CREDIT LINE ART EXTRACTION ENGINE
# ---------------------------------------------------------------------------
def color_image_to_clean_lineart(color_img: Image.Image, stroke_boost: int = 3) -> Image.Image:
    """
    Converts a flat/vector colored children's illustration into a crisp, pure
    black-and-white coloring outline with 100% identical geometry.

    Ensures the child's coloring drawing matches the small 'Color Guide' thumbnail line-for-line!
    """
    # Composite transparent images onto solid white so edges of the canvas are not detected
    if color_img.mode in ("RGBA", "LA") or (color_img.mode == "P" and "transparency" in color_img.info):
        bg = Image.new("RGB", color_img.size, (255, 255, 255))
        if color_img.mode == "RGBA":
            bg.paste(color_img, mask=color_img.split()[3])
        else:
            bg.paste(color_img.convert("RGBA"))
        gray = bg.convert("L")
    else:
        gray = color_img.convert("L")

    # Detect edges and invert
    edges = gray.filter(ImageFilter.FIND_EDGES)
    inverted_edges = ImageOps.invert(edges)

    # Combine dark native contours with edge contours
    dark_ink = gray.point(lambda p: 0 if p < 85 else 255)
    edge_ink = inverted_edges.point(lambda p: 0 if p < 180 else 255)
    combined = ImageChops.darker(dark_ink, edge_ink)

    # Thicken lines slightly for preschool coloring friendliness (>= 3 pt contour)
    # MinFilter requires an odd filter size (e.g. 3, 5, 7)
    if stroke_boost > 1:
        filter_size = stroke_boost if (stroke_boost % 2 != 0) else (stroke_boost + 1)
        combined = combined.filter(ImageFilter.MinFilter(filter_size))

    # Threshold to strict binary pure black (0) and pure white (255)
    bw = combined.point(lambda p: 0 if p < 200 else 255)

    # Clean outer edge borders (suppress boundary artifacts)
    bw_draw = ImageDraw.Draw(bw)
    bw_draw.rectangle([0, 0, bw.width - 1, bw.height - 1], outline=255, width=4)

    return bw.convert("RGBA")

# ---------------------------------------------------------------------------
# 5. PROCEDURAL SUBJECT ARTWORK FALLBACK (FOR TESTING / UNGENERATED ASSETS)
# ---------------------------------------------------------------------------
def generate_procedural_subject_pair(code_label: str, word_label: str,
                                     primary_color: tuple) -> tuple[Image.Image, Image.Image]:
    """
    Generates a clean vector-style character/object pair (Color Reference + B&W Outline)
    when external source assets are pending, guaranteeing a print-ready build without crashing.
    Uses multi-animal illustration drawer for all 30 animals in series volume 2.
    """
    if draw_animal_character is not None:
        color_im = draw_animal_character(word_label, primary_color)
    else:
        w, h = 1800, 1800
        color_im = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        d_c = ImageDraw.Draw(color_im)
        cx, cy = w // 2, h // 2
        body_col = primary_color + (255,)
        belly_col = (255, 245, 210, 255)
        eye_col = (20, 20, 25, 255)
        d_c.ellipse([cx - 480, cy - 540, cx - 240, cy - 300], fill=body_col, outline=(30, 30, 30, 255), width=22)
        d_c.ellipse([cx + 240, cy - 540, cx + 480, cy - 300], fill=body_col, outline=(30, 30, 30, 255), width=22)
        d_c.ellipse([cx - 420, cy - 420, cx + 420, cy + 420], fill=body_col, outline=(30, 30, 30, 255), width=24)
        d_c.ellipse([cx - 240, cy - 40, cx + 240, cy + 320], fill=belly_col, outline=(30, 30, 30, 255), width=18)
        d_c.ellipse([cx - 220, cy - 160, cx - 80, cy - 20], fill=eye_col)
        d_c.ellipse([cx - 180, cy - 150, cx - 120, cy - 90], fill=(255, 255, 255, 255))
        d_c.ellipse([cx + 80, cy - 160, cx + 220, cy - 20], fill=eye_col)
        d_c.ellipse([cx + 120, cy - 150, cx + 180, cy - 90], fill=(255, 255, 255, 255))
        d_c.ellipse([cx - 60, cy + 40, cx + 60, cy + 130], fill=(240, 60, 90, 255), outline=(30, 30, 30, 255), width=14)
        d_c.arc([cx - 120, cy + 120, cx + 120, cy + 260], start=20, end=160, fill=(30, 30, 30, 255), width=18)

    # Derive pure B&W lineart with 100% matching geometry
    bw_im = color_image_to_clean_lineart(color_im, stroke_boost=3)
    return color_im, bw_im

# ---------------------------------------------------------------------------
# 6. COPY-TO-COLOR PAGE CHROME RENDERER
# ---------------------------------------------------------------------------
def draw_copy_to_color_chrome(
    canvas: Image.Image,
    header_code: str,
    subject_word: str,
    vol_title: str,
    page_num: int,
    primary_color: tuple = (255, 73, 73),
    secondary_color: tuple = (234, 88, 12),
) -> None:
    """
    Draws the top letter/word banner, Color Guide framing box, and bottom colorful wave
    footer matching commercial retail activity books.
    """
    draw = ImageDraw.Draw(canvas)

    font_code = load_font("Fredoka-Bold.ttf", 200)
    font_footer = load_font("Fredoka-Bold.ttf", 38)
    font_guide_lbl = load_font("Fredoka-Bold.ttf", 28)
    font_color_me = load_font("Fredoka-Bold.ttf", 36)

    # 1. Top-Left Giant Letter / Code (e.g., 'T', 'M', 'E', or 'Aa', 'Bb')
    display_code = header_code
    if header_code.isdigit() and subject_word:
        display_code = subject_word[0].upper()
    draw.text((SAFE_MARGIN + 35, SAFE_MARGIN + 15), display_code, fill=(28, 36, 52, 255), font=font_code)

    # 2. Top-Right Peach/Gold Brushstroke Banner + Educational Name Banner (e.g., 'T is for TIGER')
    bw = 820
    bh = 110
    bx0 = PAGE_W - SAFE_MARGIN - bw - 20
    by0 = SAFE_MARGIN + 60
    bx1 = bx0 + bw
    by1 = by0 + bh

    # Outer peach banner background
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=32, fill=(255, 237, 213, 255), outline=primary_color, width=5)
    # Inner layered pill
    draw.rounded_rectangle([bx0 + 10, by0 + 8, bx1 - 10, by1 - 8], radius=24, fill=(254, 215, 170, 255))

    # Form educational name phrase (e.g., "T is for TIGER")
    clean_subj = subject_word.strip()
    initial_char = display_code[0] if display_code else (clean_subj[0] if clean_subj else "")
    if clean_subj.startswith(f"{initial_char} is for"):
        banner_phrase = clean_subj
    elif initial_char and initial_char.isalpha():
        banner_phrase = f"{initial_char.upper()} is for {clean_subj.upper()}"
    else:
        banner_phrase = clean_subj.upper()

    # Dynamic font sizing to ensure clean fit inside banner
    word_font_size = 60
    font_word = load_font("LuckiestGuy-Regular.ttf", word_font_size)
    bbox = draw.textbbox((0, 0), banner_phrase, font=font_word)
    tw = bbox[2] - bbox[0]
    while tw > (bw - 50) and word_font_size > 36:
        word_font_size -= 4
        font_word = load_font("LuckiestGuy-Regular.ttf", word_font_size)
        bbox = draw.textbbox((0, 0), banner_phrase, font=font_word)
        tw = bbox[2] - bbox[0]

    th = bbox[3] - bbox[1]
    draw.text((bx0 + (bw - tw) // 2, by0 + (bh - th) // 2 - 4), banner_phrase, fill=(45, 25, 15, 255), font=font_word)

    # 3. Framing Container for Top-Right 'Color Guide' Thumbnail
    guide_w, guide_h = 680, 680
    gx0 = PAGE_W - SAFE_MARGIN - guide_w - 30
    gy0 = by1 + 40
    # Card drop shadow
    draw.rounded_rectangle([gx0 + 8, gy0 + 10, gx0 + guide_w + 8, gy0 + guide_h + 10], radius=26, fill=(0, 0, 0, 35))
    # Card white frame
    draw.rounded_rectangle([gx0, gy0, gx0 + guide_w, gy0 + guide_h], radius=26, fill="white", outline="#E2E8F0", width=4)

    # 'COLOR GUIDE' pill badge at top of the preview frame
    g_pill_w, g_pill_h = 240, 48
    g_px = gx0 + (guide_w - g_pill_w) // 2
    g_py = gy0 + 12
    draw.rounded_rectangle([g_px, g_py, g_px + g_pill_w, g_py + g_pill_h], radius=16, fill=primary_color)
    g_txt = "COLOR GUIDE"
    g_bb = draw.textbbox((0, 0), g_txt, font=font_guide_lbl)
    draw.text((g_px + (g_pill_w - (g_bb[2] - g_bb[0])) // 2, g_py + 8), g_txt, fill="white", font=font_guide_lbl)

    # 4. 'COLOR ME!' cheerful instruction badge over main canvas
    draw.text((SAFE_MARGIN + 50, SAFE_MARGIN + 280), "COLOR ME!", fill=primary_color, font=font_color_me)

    # 5. Bottom Double-Layered Colorful Wave Footer
    wave_top = PAGE_H - 220
    # Secondary wave (background curve)
    draw.polygon([
        (0, wave_top + 40),
        (int(PAGE_W * 0.30), wave_top - 10),
        (int(PAGE_W * 0.65), wave_top + 45),
        (PAGE_W, wave_top + 10),
        (PAGE_W, PAGE_H),
        (0, PAGE_H),
    ], fill=secondary_color + (255,))

    # Primary wave (foreground curve)
    draw.polygon([
        (0, wave_top + 80),
        (int(PAGE_W * 0.38), wave_top + 30),
        (int(PAGE_W * 0.72), wave_top + 85),
        (PAGE_W, wave_top + 40),
        (PAGE_W, PAGE_H),
        (0, PAGE_H),
    ], fill=primary_color + (255,))

    # 6. Page Number Badge & Series Title in Footer (Strictly Canonical: 'Copy to Color: <Subject>')
    badge_cx = SAFE_MARGIN + 90
    badge_cy = PAGE_H - 120
    draw.ellipse([badge_cx - 46, badge_cy - 46, badge_cx + 46, badge_cy + 46],
                 fill=(255, 255, 255, 255), outline=secondary_color, width=4)
    p_str = str(page_num)
    p_bb = draw.textbbox((0, 0), p_str, font=font_footer)
    draw.text((badge_cx - (p_bb[2] - p_bb[0]) // 2, badge_cy - (p_bb[3] - p_bb[1]) // 2 - 3),
              p_str, fill=(28, 36, 52, 255), font=font_footer)

    series_label = f"Copy to Color: {vol_title}"
    draw.text((badge_cx + 70, badge_cy - 20), series_label, fill="white", font=font_footer)


# ---------------------------------------------------------------------------
# 7. SPECIAL PAGES (PAGE 1 WELCOME & PAGE 32 COMPLETION CERTIFICATE)
# ---------------------------------------------------------------------------
def render_page_01_welcome(vol_title: str, primary_color: tuple, secondary_color: tuple,
                           logo_path: str | Path | None = None) -> Image.Image:
    """
    Renders Page 1: Belongs-To & Welcome Title Page.
    Enforces Strict Brand & Title Naming Policy: 'Copy to Color: <Subject>'.
    """
    p1 = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(p1)

    # Decorative double-border with rounded corners
    draw.rounded_rectangle(
        [SAFE_MARGIN + 20, SAFE_MARGIN + 20, PAGE_W - SAFE_MARGIN - 20, PAGE_H - SAFE_MARGIN - 20],
        radius=40, outline=primary_color, width=12,
    )
    draw.rounded_rectangle(
        [SAFE_MARGIN + 45, SAFE_MARGIN + 45, PAGE_W - SAFE_MARGIN - 45, PAGE_H - SAFE_MARGIN - 45],
        radius=30, outline=secondary_color, width=4,
    )

    # Fonts
    font_title_main = load_font("LuckiestGuy-Regular.ttf", 120)
    font_title_sub = load_font("LuckiestGuy-Regular.ttf", 145)
    font_belongs = load_font("Fredoka-Bold.ttf", 52)
    font_tagline = load_font("Fredoka-Bold.ttf", 36)

    # 1. Brand Logo
    cx = PAGE_W // 2
    logo_drawn = False
    if logo_path and os.path.exists(str(logo_path)):
        try:
            with Image.open(str(logo_path)) as l_img:
                l_copy = l_img.convert("RGBA")
                l_copy.thumbnail((440, 440), Image.Resampling.LANCZOS)
                p1.paste(l_copy, (cx - l_copy.width // 2, SAFE_MARGIN + 120), l_copy)
                logo_drawn = True
        except Exception:
            pass

    if not logo_drawn:
        font_imprint = load_font("Fredoka-Bold.ttf", 48)
        draw.text((cx - 280, SAFE_MARGIN + 180), "THE PIVOT KIDS", fill=(18, 30, 66), font=font_imprint)
        draw.text((cx - 150, SAFE_MARGIN + 250), "Color & Play", fill=secondary_color, font=font_tagline)

    # 2. Canonical Book Title Stack (Strictly NO 'My First')
    title_y = SAFE_MARGIN + 620
    draw.text((cx - 410, title_y), "Copy to Color", fill=primary_color, font=font_title_main)
    sub_txt = vol_title.upper()
    s_bb = draw.textbbox((0, 0), sub_txt, font=font_title_sub)
    draw.text((cx - (s_bb[2] - s_bb[0]) // 2, title_y + 160), sub_txt, fill=(255, 180, 0), font=font_title_sub)

    # Subtitle blurb
    blurb = "Interactive Coloring & Early Learning Activity Book"
    b_bb = draw.textbbox((0, 0), blurb, font=font_tagline)
    draw.text((cx - (b_bb[2] - b_bb[0]) // 2, title_y + 340), blurb, fill=(75, 85, 99), font=font_tagline)

    # 3. 'THIS BOOK BELONGS TO' Box
    box_w = int(PAGE_W * 0.72)
    box_h = 420
    box_x = cx - box_w // 2
    box_y = SAFE_MARGIN + 1380
    draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=28, fill=(255, 247, 237), outline=primary_color, width=5)

    draw.text((box_x + 80, box_y + 60), "THIS BOOK BELONGS TO:", fill=(30, 41, 59), font=font_belongs)
    # Write-in line
    draw.line([(box_x + 80, box_y + 280), (box_x + box_w - 80, box_y + 280)], fill=(148, 163, 184), width=6)
    draw.text((box_x + 80, box_y + 300), "(Your Name / Little Artist)", fill=(100, 116, 139), font=font_tagline)

    # Bottom notes
    copy_str = "© The Pivot Digital Publication. All rights reserved. • Amazon KDP Edition"
    c_bb = draw.textbbox((0, 0), copy_str, font=font_tagline)
    draw.text((cx - (c_bb[2] - c_bb[0]) // 2, PAGE_H - SAFE_MARGIN - 100), copy_str, fill=(156, 163, 175), font=font_tagline)

    return p1


def render_page_32_certificate(vol_title: str, primary_color: tuple, secondary_color: tuple) -> Image.Image:
    """
    Renders Page 32: Super Colorist Award Completion Certificate.
    Enforces Strict Brand & Title Naming Policy: 'Copy to Color: <Subject>'.
    """
    p32 = Image.new("RGB", (PAGE_W, PAGE_H), "white")
    draw = ImageDraw.Draw(p32)

    # Outer ornate certificate frame
    draw.rounded_rectangle(
        [SAFE_MARGIN + 30, SAFE_MARGIN + 30, PAGE_W - SAFE_MARGIN - 30, PAGE_H - SAFE_MARGIN - 30],
        radius=40, outline=secondary_color, width=16,
    )
    draw.rounded_rectangle(
        [SAFE_MARGIN + 60, SAFE_MARGIN + 60, PAGE_W - SAFE_MARGIN - 60, PAGE_H - SAFE_MARGIN - 60],
        radius=30, outline=primary_color, width=6,
    )

    cx = PAGE_W // 2

    font_award = load_font("LuckiestGuy-Regular.ttf", 95)
    font_cert = load_font("Fredoka-Bold.ttf", 52)
    font_body = load_font("Fredoka-Bold.ttf", 44)
    font_bold = load_font("Fredoka-Bold.ttf", 54)
    font_tagline = load_font("Fredoka-Bold.ttf", 36)

    # Award header
    award_txt = "★ SUPER COLORIST AWARD! ★"
    a_bb = draw.textbbox((0, 0), award_txt, font=font_award)
    draw.text((cx - (a_bb[2] - a_bb[0]) // 2, SAFE_MARGIN + 220), award_txt, fill=primary_color, font=font_award)

    cert_txt = "This Certificate is Proudly Presented to:"
    c_bb = draw.textbbox((0, 0), cert_txt, font=font_cert)
    draw.text((cx - (c_bb[2] - c_bb[0]) // 2, SAFE_MARGIN + 440), cert_txt, fill=(51, 65, 85), font=font_cert)

    # Big name line
    draw.line([(cx - 700, SAFE_MARGIN + 780), (cx + 700, SAFE_MARGIN + 780)], fill=(71, 85, 105), width=6)
    draw.text((cx - 150, SAFE_MARGIN + 800), "Little Artist", fill=(100, 116, 139), font=font_tagline)

    # Body description
    body_txt = "For successfully copying and coloring every page in:"
    b_bb = draw.textbbox((0, 0), body_txt, font=font_body)
    draw.text((cx - (b_bb[2] - b_bb[0]) // 2, SAFE_MARGIN + 1040), body_txt, fill=(51, 65, 85), font=font_body)

    # Canonical Book Title (Strictly NO 'My First')
    book_title = f"Copy to Color: {vol_title}"
    bt_bb = draw.textbbox((0, 0), book_title, font=font_bold)
    draw.text((cx - (bt_bb[2] - bt_bb[0]) // 2, SAFE_MARGIN + 1150), book_title, fill=secondary_color, font=font_bold)

    # Star badge graphic
    badge_cy = SAFE_MARGIN + 1620
    draw.ellipse([cx - 140, badge_cy - 140, cx + 140, badge_cy + 140],
                 fill=(255, 215, 0), outline=(217, 119, 6), width=8)
    draw.ellipse([cx - 110, badge_cy - 110, cx + 110, badge_cy + 110],
                 fill=(254, 243, 199), outline=(245, 158, 11), width=4)
    draw.text((cx - 72, badge_cy - 45), "GREAT\n JOB!", fill=(146, 64, 14), font=font_body, align="center")

    # Date and Signature lines
    draw.line([(SAFE_MARGIN + 220, SAFE_MARGIN + 2150), (SAFE_MARGIN + 750, SAFE_MARGIN + 2150)], fill=(100, 116, 139), width=4)
    draw.text((SAFE_MARGIN + 420, SAFE_MARGIN + 2170), "Date", fill=(100, 116, 139), font=font_tagline)

    draw.line([(PAGE_W - SAFE_MARGIN - 750, SAFE_MARGIN + 2150), (PAGE_W - SAFE_MARGIN - 220, SAFE_MARGIN + 2150)], fill=(100, 116, 139), width=4)
    draw.text((PAGE_W - SAFE_MARGIN - 580, SAFE_MARGIN + 2170), "Signature / Stamp", fill=(100, 116, 139), font=font_tagline)

    # Footer Imprint
    imp_txt = "The Pivot Kids • Color & Play Series"
    i_bb = draw.textbbox((0, 0), imp_txt, font=font_tagline)
    draw.text((cx - (i_bb[2] - i_bb[0]) // 2, PAGE_H - SAFE_MARGIN - 130), imp_txt, fill=(148, 163, 184), font=font_tagline)

    return p32

# ---------------------------------------------------------------------------
# 8. 32-PAGE MASTER COMPILER FUNCTION
# ---------------------------------------------------------------------------
def build_32_page_copy_to_color_book(
    vol_id: str = "vol_02",
    vol_title: str | None = None,
    assets_dir: str | Path | None = None,
    output_pdf_path: str | Path | None = None,
    logo_path: str | Path | None = None,
    primary_color: tuple | None = None,
    secondary_color: tuple | None = None,
) -> Path:
    """
    Compiles a complete 32-page 'Copy to Color' interior PDF at 300 DPI:
      - Page 1: Title & 'This Book Belongs To' Welcome Page
      - Pages 2..31: 30 Interactive 'Copy to Color' Activity Pages
      - Page 32: Super Colorist Award Completion Certificate
    """
    meta = SERIES_CATALOG.get(vol_id, SERIES_CATALOG["vol_02"])
    resolved_title = vol_title or meta["title"]
    p_col = primary_color or meta["primary"]
    s_col = secondary_color or meta["secondary"]

    if output_pdf_path is None:
        output_pdf_path = REPO_ROOT / f"local_builds/{vol_id}_{resolved_title.lower()}_32p_interior.pdf"
    out_pdf = Path(output_pdf_path)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    # Standard fallback logo
    resolved_logo = None
    for cand in [logo_path, REPO_ROOT / "assets/logos/pivot_kids_sticker.png", REPO_ROOT / "assets/logos/pivot_kids.png"]:
        if cand and Path(cand).exists():
            resolved_logo = str(cand)
            break

    pages: list[Image.Image] = []

    print(f"\n[Interior Builder] Compiling 32-page 'Copy to Color: {resolved_title}' ({vol_id})...")

    # --- PAGE 1: WELCOME & BELONGS-TO PAGE ---
    p1 = render_page_01_welcome(resolved_title, p_col, s_col, logo_path=resolved_logo)
    pages.append(p1)

    # --- PAGES 2..31: 30 COPY-TO-COLOR ACTIVITY PAGES ---
    subjects = meta["subjects"][:30]
    for idx, (code_label, word_label) in enumerate(subjects, start=1):
        page_num = idx + 1
        page_canvas = Image.new("RGBA", (PAGE_W, PAGE_H), (255, 255, 255, 255))

        # 1. Render Chrome & Decorative Headers
        draw_copy_to_color_chrome(
            page_canvas,
            header_code=code_label,
            subject_word=word_label,
            vol_title=resolved_title,
            page_num=page_num,
            primary_color=p_col,
            secondary_color=s_col,
        )

        # 2. Resolve Artwork (Color Reference & B&W Outline)
        color_img: Image.Image | None = None
        bw_img: Image.Image | None = None

        # Check disk assets directory if provided
        if assets_dir:
            a_dir = Path(assets_dir)
            c_cand = a_dir / f"subj_{idx:02d}_color.png"
            b_cand = a_dir / f"subj_{idx:02d}_bw.png"
            if c_cand.exists():
                color_img = Image.open(str(c_cand)).convert("RGBA")
                if b_cand.exists():
                    bw_img = Image.open(str(b_cand)).convert("RGBA")
                else:
                    bw_img = color_image_to_clean_lineart(color_img, stroke_boost=3)

        # Special case for animals volume if high-res 1:1 assets exist in local_builds
        if color_img is None and vol_id == "vol_02" and idx == 1:
            t_col = REPO_ROOT / "local_builds/animals/assets/tiger_color_thumb.png"
            t_bw = REPO_ROOT / "local_builds/animals/assets/tiger_outline.png"
            if t_col.exists():
                color_img = Image.open(str(t_col)).convert("RGBA")
                if t_bw.exists():
                    bw_img = Image.open(str(t_bw)).convert("RGBA")
                else:
                    bw_img = color_image_to_clean_lineart(color_img, stroke_boost=3)

        # Fallback to high-quality procedural illustration if no asset is available yet
        if color_img is None or bw_img is None:
            color_img, bw_img = generate_procedural_subject_pair(code_label, word_label, p_col)

        # 3. Composite Small Color Reference Guide (Top-Right inside frame: 680x680 box)
        guide_copy = color_img.copy()
        # Scale to fit inside the 580x580 inner space of the preview frame
        guide_copy.thumbnail((560, 560), Image.Resampling.LANCZOS)
        gx_box = PAGE_W - SAFE_MARGIN - 680 - 30
        gy_box = SAFE_MARGIN + 60 + 110 + 40
        gx = gx_box + (680 - guide_copy.width) // 2
        gy = gy_box + 50 + (630 - 50 - guide_copy.height) // 2
        page_canvas.paste(guide_copy, (gx, gy), guide_copy)

        # 4. Composite Large B&W Coloring Outline (Center-Left main canvas)
        bw_copy = bw_img.copy()
        # Fit prominently inside main drawing canvas (1480 x 2050 px)
        # Main area boundaries: x from SAFE_MARGIN + 50 to SAFE_MARGIN + 50 + 1480 = 1680 (left of gx_box 1690)
        bw_copy.thumbnail((1460, 2050), Image.Resampling.LANCZOS)
        bx = SAFE_MARGIN + 50 + (1460 - bw_copy.width) // 2
        by = SAFE_MARGIN + 360 + (2050 - bw_copy.height) // 2
        page_canvas.paste(bw_copy, (bx, by), bw_copy)

        pages.append(page_canvas.convert("RGB"))

    # --- PAGE 32: COMPLETION CERTIFICATE ---
    p32 = render_page_32_certificate(resolved_title, p_col, s_col)
    pages.append(p32)

    # Save print-ready multi-page PDF
    pages[0].save(
        str(out_pdf),
        "PDF",
        resolution=DPI,
        save_all=True,
        append_images=pages[1:],
    )

    # Render proof contact sheet of sample pages (P1 Welcome, P2 Tiger, P3 Monkey, P4 Elephant, P5 Giraffe, P6 Lion, P7 Zebra, P32 Certificate)
    proof_path = out_pdf.parent / f"{out_pdf.stem}_proof.png"
    proof_w = 400
    proof_h = int(proof_w * (PAGE_H / PAGE_W))
    cols, rows = 4, 2
    sheet = Image.new("RGB", (cols * (proof_w + 15) + 15, rows * (proof_h + 15) + 15), (240, 240, 245))
    sample_indices = [0, 1, 2, 3, 4, 5, 6, 31]
    for s_i, page_idx in enumerate(sample_indices):
        col = s_i % cols
        row = s_i // cols
        thumb = pages[page_idx].copy().resize((proof_w, proof_h), Image.Resampling.LANCZOS)
        sheet.paste(thumb, (15 + col * (proof_w + 15), 15 + row * (proof_h + 15)))
    sheet.save(str(proof_path), "PNG")

    print(f"[OK] 32-page interior PDF compiled successfully: {out_pdf} ({len(pages)} pages)")
    print(f"[OK] Visual Proof Contact Sheet saved: {proof_path}")

    return out_pdf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated 32-Page 'Copy to Color' Interior Compiler")
    parser.add_argument("--vol-id", default="vol_02", help="Series volume ID (e.g., vol_01 to vol_12)")
    parser.add_argument("--vol-title", default=None, help="Volume title override")
    parser.add_argument("--assets-dir", default=None, help="Directory containing subj_XX_color.png and subj_XX_bw.png")
    parser.add_argument("--output", default=None, help="Destination PDF path")
    args = parser.parse_args()

    build_32_page_copy_to_color_book(
        vol_id=args.vol_id,
        vol_title=args.vol_title,
        assets_dir=args.assets_dir,
        output_pdf_path=args.output,
    )
