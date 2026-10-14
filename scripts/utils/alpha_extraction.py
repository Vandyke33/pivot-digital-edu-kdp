"""
Corner Flood-Fill Alpha Extraction with Smooth Sticker Contour.

Extracts foreground characters from solid or near-white backgrounds using connected
perimeter floodfill, strictly preserving all interior whites (eyes, teeth, card areas),
and optionally wrapping the silhouette in a silky smooth, die-cut white sticker contour.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageOps


def extract_with_sticker_contour(
    image: Image.Image,
    tolerance: int = 18,
    contour_radius: int = 16,
    blur_radius: float = 1.5,
    contour_color: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    Extract foreground subject from a white background using connected corner flood-fill.
    
    1. Only near-white pixels connected to outer corners/edges are classified as exterior background.
    2. Interior white details (eyes, teeth, bellies, pages) enclosed by dark contours are 100% preserved.
    3. The character boundary is smoothly dilated to form an organic sticker contour.
    4. Subpixel Gaussian antialiasing is applied to the outer alpha boundary.
    """
    img = image.convert("RGB")
    w, h = img.size

    # Build grayscale intensity map
    gray = ImageOps.grayscale(img)

    # Clone grayscale to perform connected flood-fill on background
    # Background seed pixels will be flood-filled to 0
    bg_canvas = gray.copy()

    # Seed flood-fill strictly from perimeter corners and edge midpoints
    seeds = [
        (0, 0),
        (w - 1, 0),
        (0, h - 1),
        (w - 1, h - 1),
        (w // 2, 0),
        (w // 2, h - 1),
        (0, h // 2),
        (w - 1, h // 2),
    ]

    for sx, sy in seeds:
        seed_val = bg_canvas.getpixel((sx, sy))
        if seed_val >= (255 - tolerance - 15):
            # Floodfill connected pixels that match seed within tolerance
            ImageDraw.floodfill(bg_canvas, (sx, sy), 0, thresh=tolerance)

    # Connected exterior background pixels now have value 0.
    # Subject pixels (and interior whites) have value > 0.
    # Create binary subject mask: 255 for subject, 0 for background
    subject_mask = bg_canvas.point(lambda p: 255 if p > 0 else 0, mode="L")

    # Create dilated contour mask if requested
    if contour_radius > 0:
        filter_size = max(3, contour_radius * 2 + 1)
        dilated_mask = subject_mask.filter(ImageFilter.MaxFilter(filter_size))
    else:
        dilated_mask = subject_mask

    # Apply subtle anti-aliasing to the outer boundary
    if blur_radius > 0:
        smooth_alpha = dilated_mask.filter(ImageFilter.GaussianBlur(blur_radius))
    else:
        smooth_alpha = dilated_mask

    # Assemble composite: white sticker base + original character pixels
    r, g, b = contour_color
    sticker_base = Image.new("RGBA", (w, h), (r, g, b, 255))
    img_rgba = img.convert("RGBA")

    result = sticker_base.copy()
    result.paste(img_rgba, (0, 0), subject_mask)
    result.putalpha(smooth_alpha)

    return result


def process_image_file(
    input_path: str | Path,
    output_path: str | Path,
    tolerance: int = 18,
    contour_radius: int = 16,
    blur_radius: float = 1.5,
) -> Path:
    """Read an image file, process it with corner flood-fill sticker contour, and save as RGBA PNG."""
    in_p = Path(input_path)
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(in_p) as src:
        processed = extract_with_sticker_contour(
            src,
            tolerance=tolerance,
            contour_radius=contour_radius,
            blur_radius=blur_radius,
        )
        processed.save(out_p, format="PNG")

    return out_p
