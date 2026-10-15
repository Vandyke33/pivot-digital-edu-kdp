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
    remove_trapped_pockets: bool = True,
    min_pocket_area: int = 1800,
    stroke_size: int | None = None,
) -> Image.Image:
    if stroke_size is not None:
        contour_radius = stroke_size
    """
    Extract foreground subject from a white background using connected corner flood-fill.
    
    1. Only near-white pixels connected to outer corners/edges are classified as exterior background.
    2. Enclosed large white pockets (>= min_pocket_area) trapped between foreground limbs are cleared.
    3. Interior white details (eyes, teeth, bellies, pages) < min_pocket_area are 100% preserved.
    4. The character boundary is smoothly dilated to form an organic sticker contour.
    5. Subpixel Gaussian antialiasing is applied to the outer alpha boundary.
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

    # Detect and remove trapped white pockets (e.g. between character limbs)
    if remove_trapped_pockets:
        try:
            import numpy as np
            from scipy import ndimage

            sub_arr = np.array(subject_mask) > 0
            img_arr = np.array(img)
            # Find near-white pixels still marked as subject
            near_white = sub_arr & (img_arr[:, :, 0] >= 235) & (img_arr[:, :, 1] >= 235) & (img_arr[:, :, 2] >= 235)
            labeled, num_features = ndimage.label(near_white)
            if num_features > 0:
                sizes = ndimage.sum(near_white, labeled, range(num_features + 1))
                for comp_idx, sz in enumerate(sizes):
                    if sz >= min_pocket_area:
                        # Clear large trapped pocket
                        sub_arr[labeled == comp_idx] = False

                subject_mask = Image.fromarray((sub_arr * 255).astype(np.uint8), mode="L")
        except ImportError:
            pass  # Fall back to corner floodfill if scipy not available

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


def isolate_thumbnail_icon(
    image: Image.Image | str | Path,
    output_path: str | Path | None = None,
    tolerance: float = 40.0,
    contour_radius: int = 6,
    blur_radius: float = 1.0,
    pad: int = 16,
) -> Image.Image:
    """
    Isolate a thumbnail subject from its solid or gradient background color,
    tight-crop to the subject bounding box, and wrap with a soft white sticker contour.
    """
    import numpy as np
    from scipy import ndimage

    if isinstance(image, (str, Path)):
        img = Image.open(image).convert("RGB")
    else:
        img = image.convert("RGB")

    w, h = img.size
    arr = np.array(img, dtype=float)

    # Detect background color from 4 corners
    corner_colors = [arr[0, 0], arr[0, -1], arr[-1, 0], arr[-1, -1]]
    bg_color = np.median(corner_colors, axis=0)

    # Euclidean color distance to background color
    diff = np.sqrt(np.sum((arr - bg_color) ** 2, axis=2))
    bg_mask = diff < tolerance

    # Connected components of background touching any corner
    labeled, _ = ndimage.label(bg_mask)
    corner_labels = {labeled[0, 0], labeled[0, -1], labeled[-1, 0], labeled[-1, -1]}
    is_corner_bg = np.isin(labeled, list(corner_labels))

    subject_mask = ~is_corner_bg
    coords = np.where(subject_mask)

    if len(coords[0]) == 0:
        # Fallback if isolation fails
        res = img.convert("RGBA")
        if output_path:
            res.save(output_path, format="PNG")
        return res

    ymin, ymax = int(np.min(coords[0])), int(np.max(coords[0]))
    xmin, xmax = int(np.min(coords[1])), int(np.max(coords[1]))

    # Expand box slightly for padding
    ymin = max(0, ymin - pad)
    ymax = min(h, ymax + pad)
    xmin = max(0, xmin - pad)
    xmax = min(w, xmax + pad)

    # Crop image and mask to bounding box
    cropped_img = img.crop((xmin, ymin, xmax, ymax))
    cropped_sub_arr = subject_mask[ymin:ymax, xmin:xmax]
    sub_l = Image.fromarray((cropped_sub_arr * 255).astype(np.uint8), mode="L")

    # Create white sticker contour
    if contour_radius > 0:
        filter_size = max(3, contour_radius * 2 + 1)
        dilated = sub_l.filter(ImageFilter.MaxFilter(filter_size))
    else:
        dilated = sub_l

    if blur_radius > 0:
        alpha = dilated.filter(ImageFilter.GaussianBlur(blur_radius))
    else:
        alpha = dilated

    cw, ch = cropped_img.size
    sticker = Image.new("RGBA", (cw, ch), (255, 255, 255, 255))
    res = sticker.copy()
    res.paste(cropped_img.convert("RGBA"), (0, 0), sub_l)
    res.putalpha(alpha)

    if output_path:
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        res.save(out_p, format="PNG")

    return res


def process_image_file(
    input_path: str | Path,
    output_path: str | Path,
    tolerance: int = 18,
    contour_radius: int = 16,
    blur_radius: float = 1.5,
    remove_trapped_pockets: bool = True,
    min_pocket_area: int = 1800,
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
            remove_trapped_pockets=remove_trapped_pockets,
            min_pocket_area=min_pocket_area,
        )
        processed.save(out_p, format="PNG")

    return out_p


# Export alias for convenience and backward compatibility
isolate_with_sticker_border = extract_with_sticker_contour


