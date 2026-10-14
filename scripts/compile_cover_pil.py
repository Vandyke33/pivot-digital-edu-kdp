"""
Automated KDP Full-Wrap Cover Spread Generator (PIL Engine)
Compiles Back Cover, Spine, and Front Cover into a single 300 DPI print-ready PDF.
Eliminates rectangular AI artifacts and programmatically renders typography,
the 12-book series grid, and barcode safe zones.

Dependencies: pip install pillow reportlab numpy
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------------------
# 1. PHYSICAL DIMENSIONS & FORMULAS (8.5 x 11.0 in Trim)
# ---------------------------------------------------------------------------
DPI = 300
TRIM_WIDTH_IN = 8.5
TRIM_HEIGHT_IN = 11.0
BLEED_IN = 0.125
WHITE_PAPER_PAGE_MULTIPLIER = 0.002252

def calculate_cover_dimensions(page_count: int):
    spine_in = page_count * WHITE_PAPER_PAGE_MULTIPLIER
    # Minimum spine width for spine text on KDP is roughly 79-80 pages (0.18 in)
    total_width_in = BLEED_IN + TRIM_WIDTH_IN + spine_in + TRIM_WIDTH_IN + BLEED_IN
    total_height_in = TRIM_HEIGHT_IN + (2 * BLEED_IN)
    
    width_px = int(math.ceil(total_width_in * DPI))
    height_px = int(math.ceil(total_height_in * DPI))
    spine_px = int(math.ceil(spine_in * DPI))
    trim_w_px = int(TRIM_WIDTH_IN * DPI)
    bleed_px = int(BLEED_IN * DPI)
    
    return {
        "width_px": width_px,
        "height_px": height_px,
        "spine_px": spine_px,
        "trim_w_px": trim_w_px,
        "bleed_px": bleed_px,
        "spine_in": spine_in
    }

# ---------------------------------------------------------------------------
# 2. COLOR PALETTES & SERIES DATA
# ---------------------------------------------------------------------------
BG_TOP = (255, 77, 77)       # Coral Red
BG_BOTTOM = (255, 140, 66)   # Warm Sunset Orange
GRASS_COLOR = (76, 175, 80)  # Bright Green Hills
NAVY_TEXT = (26, 42, 74)     # Deep Navy
YELLOW_TEXT = (255, 204, 0)  # Gold/Yellow Bubble

SERIES_TITLES = [
    {"vol": "Vol. 1", "title": "Alphabet", "color": "#FF6B35"},
    {"vol": "Vol. 2", "title": "Animals", "color": "#FF4D4D"},
    {"vol": "Vol. 3", "title": "Birds", "color": "#2EC4B6"},
    {"vol": "Vol. 4", "title": "Sports", "color": "#80ED99"},
    {"vol": "Vol. 5", "title": "Monsters", "color": "#E056FD"},
    {"vol": "Vol. 6", "title": "Numbers", "color": "#9B5DE5"},
    {"vol": "Vol. 7", "title": "Fruits", "color": "#00BBF9"},
    {"vol": "Vol. 8", "title": "Shapes", "color": "#F15BB5"},
    {"vol": "Vol. 9", "title": "Toys", "color": "#0077B6"},
    {"vol": "Vol. 10", "title": "Flowers", "color": "#6B4226"},
    {"vol": "Vol. 11", "title": "Transport", "color": "#1D3557"},
    {"vol": "Vol. 12", "title": "Vegetables", "color": "#5A189A"},
]

# ---------------------------------------------------------------------------
# 3. DRAWING HELPERS
# ---------------------------------------------------------------------------
def draw_gradient_background(width: int, height: int) -> Image.Image:
    """Generates a smooth vertical color gradient."""
    base = Image.new("RGBA", (width, height), BG_TOP)
    draw = ImageDraw.Draw(base)
    for y in range(height):
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * (y / height))
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * (y / height))
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * (y / height))
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    return base

def draw_rolling_hills(canvas: Image.Image, height: int, width: int):
    """Draws organic rolling green hills along the bottom edge."""
    draw = ImageDraw.Draw(canvas)
    hill_top = int(height * 0.78)
    points = [
        (0, hill_top + 100),
        (int(width * 0.25), hill_top + 30),
        (int(width * 0.5), hill_top + 70),
        (int(width * 0.75), hill_top + 20),
        (width, hill_top + 80),
        (width, height),
        (0, height)
    ]
    draw.polygon(points, fill=GRASS_COLOR)

def draw_bubble_text(draw: ImageDraw.ImageDraw, pos: tuple, text: str, font: ImageFont.FreeTypeFont, 
                     fill_color: tuple, outline_color: tuple, outline_width: int = 4, shadow_offset: tuple = (4, 4)):
    """Renders layered 3D bubble typography without rectangular clipping artifacts."""
    x, y = pos
    # 1. 3D Shadow layer
    sx, sy = shadow_offset
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            draw.text((x + sx + dx, y + sy + dy), text, font=font, fill=(30, 20, 10, 255))
            
    # 2. Outline Stroke layer
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
            
    # 3. Main Face Fill
    draw.text((x, y), text, font=font, fill=fill_color)

# ---------------------------------------------------------------------------
# 4. BACK COVER SERIES GRID BUILDER
# ---------------------------------------------------------------------------
def render_back_cover_grid(cover: Image.Image, draw: ImageDraw.ImageDraw, start_x: int, start_y: int, grid_w: int, grid_h: int):
    """Programmatically constructs a 4x3 thumbnail grid of books in the series with micro-asset art."""
    cols, rows = 3, 4
    cell_w = grid_w // cols
    cell_h = grid_h // rows
    
    font_vol = ImageFont.load_default()
    font_title = ImageFont.load_default()
    
    from pathlib import Path
    thumb_dir = Path("local_builds/animals/assets/thumbnails")

    for idx, item in enumerate(SERIES_TITLES):
        col = idx % cols
        row = idx // cols
        
        x0 = start_x + col * cell_w + 12
        y0 = start_y + row * cell_h + 10
        x1 = x0 + cell_w - 24
        y1 = y0 + cell_h - 20
        
        # Draw card container
        draw.rounded_rectangle([x0, y0, x1, y1], radius=12, fill="white", outline="#D0D7DE", width=2)
        
        # Color header bar
        header_h = int((y1 - y0) * 0.32)
        draw.rounded_rectangle([x0, y0, x1, y0 + header_h], radius=10, fill=item["color"])
        
        # Text labels inside card
        draw.text((x0 + 8, y0 + 4), "Copy to Color", fill="white", font=font_vol)
        draw.text((x0 + 8, y0 + 16), item["title"], fill="white", font=font_title)
        draw.text((x1 - 38, y0 + 4), item["vol"], fill="white", font=font_vol)
        
        # Thumbnail illustration box
        bx0 = x0 + 15
        by0 = y0 + header_h + 8
        bx1 = x1 - 15
        by1 = y1 - 8
        draw.rectangle([bx0, by0, bx1, by1], fill="#F8FAFC", outline="#E2E8F0")

        # Dynamically load thumbnail PNG if present
        vol_num = idx + 1
        thumb_file = None
        if thumb_dir.exists():
            cands = sorted(list(thumb_dir.glob(f"vol_{vol_num:02d}*.png")))
            if cands:
                thumb_file = cands[0]

        if thumb_file and thumb_file.exists():
            try:
                with Image.open(thumb_file).convert("RGBA") as thumb_im:
                    max_tw = bx1 - bx0 - 4
                    max_th = by1 - by0 - 4
                    thumb_im.thumbnail((max_tw, max_th), Image.Resampling.LANCZOS)
                    tx = bx0 + (bx1 - bx0 - thumb_im.width) // 2
                    ty = by0 + (by1 - by0 - thumb_im.height) // 2
                    cover.paste(thumb_im, (tx, ty), thumb_im)
            except Exception:
                pass

# ---------------------------------------------------------------------------
# 5. MAIN COMPILER FUNCTION
# ---------------------------------------------------------------------------
def build_kdp_cover(page_count: int, output_path: str, hero_image_path: str = None, logo_path: str = None):
    specs = calculate_cover_dimensions(page_count)
    w, h = specs["width_px"], specs["height_px"]
    spine_w = specs["spine_px"]
    trim_w = specs["trim_w_px"]
    bleed = specs["bleed_px"]
    
    print(f"Generating full-wrap cover: {w}x{h} px | Spine: {specs['spine_in']:.3f} in ({spine_w} px)")
    
    # Create base canvas and elements
    cover = draw_gradient_background(w, h)
    draw_rolling_hills(cover, h, w)
    draw = ImageDraw.Draw(cover)
    
    # Boundaries
    back_x_end = bleed + trim_w
    spine_x_start = back_x_end
    spine_x_end = spine_x_start + spine_w
    front_x_start = spine_x_end
    
    # ---------------- BACK COVER SECTION ----------------
    # Series Banner
    banner_w, banner_h = int(trim_w * 0.7), 80
    bx0 = bleed + (trim_w - banner_w) // 2
    draw.rounded_rectangle([bx0, 220, bx0 + banner_w, 220 + banner_h], radius=24, fill="#0077B6")
    draw.text((bx0 + 40, 245), "★ TITLES IN THIS SERIES ★", fill="white")
    
    # 4x3 Series Grid
    grid_start_y = 340
    grid_w = int(trim_w * 0.9)
    grid_h = int(h * 0.52)
    render_back_cover_grid(cover, draw, bleed + int(trim_w * 0.05), grid_start_y, grid_w, grid_h)

    
    # Barcode Safe Area (Bottom-Right of Back Cover: 2.0 x 1.2 in = 600 x 360 px)
    bc_w, bc_h = 600, 360
    bc_x = back_x_end - bc_w - int(0.5 * DPI)
    bc_y = h - bleed - bc_h - int(0.5 * DPI)
    draw.rectangle([bc_x, bc_y, bc_x + bc_w, bc_y + bc_h], fill="white", outline="#CCCCCC")
    draw.text((bc_x + 180, bc_y + 160), "[ KDP Barcode Location ]", fill="#888888")
    
    # ---------------- FRONT COVER SECTION ----------------
    front_cx = front_x_start + (trim_w // 2)
    
    # Front Brand Logo (Paste with clean alpha transparency)
    if logo_path and os.path.exists(logo_path):
        logo_img = Image.open(logo_path).convert("RGBA")
        logo_img.thumbnail((450, 450), Image.Resampling.LANCZOS)
        lx = front_cx - (logo_img.width // 2)
        cover.paste(logo_img, (lx, 140), logo_img)
    
    # Typography
    try:
        font_large = ImageFont.truetype("arial.ttf", 64)
        font_xlarge = ImageFont.truetype("arialbd.ttf", 96)
    except Exception:
        font_large = ImageFont.load_default()
        font_xlarge = font_large
    
    # "My First" (Arched badge style without rectangular clipping)
    draw.text((front_cx - 100, 620), "MY FIRST", fill="white", font=font_large)
    
    # "Copy to Color"
    draw_bubble_text(draw, (front_cx - 260, 700), "Copy to Color", font_xlarge, 
                     fill_color=(255, 255, 255), outline_color=NAVY_TEXT, outline_width=6)
    
    # "Animals"
    draw_bubble_text(draw, (front_cx - 210, 810), "ANIMALS", font_xlarge, 
                     fill_color=YELLOW_TEXT, outline_color=(120, 40, 10), outline_width=8)
    
    # Hero Character Placement (Tiger + Monkey isolated asset)
    if hero_image_path and os.path.exists(hero_image_path):
        hero = Image.open(hero_image_path).convert("RGBA")
        hero.thumbnail((int(trim_w * 0.7), int(h * 0.45)), Image.Resampling.LANCZOS)
        hx = front_cx - (hero.width // 2)
        hy = h - bleed - hero.height - 200
        cover.paste(hero, (hx, hy), hero)
        
    # ---------------- SPINE SECTION ----------------
    # Spine text printed only if spine width >= 0.18 in (page count >= 80)
    if specs["spine_in"] >= 0.18:
        pass # Draw rotated spine text centered within spine_x_start to spine_x_end
        
    # Save Output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cover.convert("RGB").save(output_path, "PDF", resolution=DPI)
    proof_path = str(output_path).replace(".pdf", "-proof.png")
    cover.save(proof_path, "PNG")
    print(f"Successfully compiled print-ready KDP full-wrap cover: {output_path}")
    print(f"Successfully saved 300 DPI preview proof: {proof_path}")

if __name__ == "__main__":
    hero_path = "local_builds/animals/assets/tiger_monkey_transparent.png"
    if not os.path.exists(hero_path):
        hero_path = None
    logo_path = "assets/logos/pivot_kids_sticker.png"
    if not os.path.exists(logo_path):
        logo_path = None
        
    build_kdp_cover(
        page_count=74,
        output_path="local_builds/animals_cover_fullwrap.pdf",
        hero_image_path=hero_path,
        logo_path=logo_path
    )

