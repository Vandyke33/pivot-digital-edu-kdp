"""
scripts/canva_pipeline.py
=========================
Unified Brand-Governed Cover Production Pipeline & Canva Manager
for "The Pivot Kids: Copy to Color" (12 Volumes)

Enforces:
1. Component-First Architecture: Isolated 3D character hero briefs for Canva generation.
2. Background Transparency & Sticker Contours: 100% transparent RGBA with smooth white die-cut contours.
3. Floor Shadow Elimination: Clean removal of floor contact shadows while preserving shoe/paw details.
4. Non-Idempotency Protection: Automatically archives raw AI generations in assets/cover_heroes/raw/.
5. 100% Brand Mark Consistency: Official 'The Pivot Kids (Color & Play)' vector logo.
6. 100% Typography Consistency: Native 300 DPI 3D neon sparkle display fonts ('Copy to Color' + '<SUBJECT>').
7. Exact Series Palettes & Mechanical Alignment: Strict volume hex codes and locked coordinates.
8. KDP Compliance: Dynamic spine width formula, barcode safe zone (2.0 x 1.2 in), 4x3 series back grid.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_FRONTS_DIR = REPO_ROOT / "assets" / "external_fronts"
HERO_ASSETS_DIR = REPO_ROOT / "assets" / "cover_heroes"
HERO_RAW_DIR = HERO_ASSETS_DIR / "raw"
SERIES_FRONTS_DIR = REPO_ROOT / "local_builds" / "series_fronts"

EXTERNAL_FRONTS_DIR.mkdir(parents=True, exist_ok=True)
HERO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
HERO_RAW_DIR.mkdir(parents=True, exist_ok=True)
SERIES_FRONTS_DIR.mkdir(parents=True, exist_ok=True)

# Standardized Isolated 3D Character Hero Briefs (Component-First Standard)
# Strict negative prompt: no text, no letters, no words, no banners, clean solid white background
CANVA_HERO_BRIEFS = {
    "vol_01": {
        "title": "Alphabet",
        "brief": (
            "A cheerful cartoon toddler kid avatar joyfully sitting on oversized colorful 3D ABC alphabet blocks "
            "holding a giant colorful crayon, 3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters on background, no words, no frame"
        ),
    },
    "vol_02": {
        "title": "Animals",
        "brief": (
            "A cheerful cartoon kid avatar joyfully hugging an adorable friendly baby tiger cub, "
            "3D Pixar Disney animation style, isolated on a clean pure solid white background, "
            "full body view, vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_03": {
        "title": "Birds",
        "brief": (
            "A cheerful cartoon kid avatar with a colorful friendly tropical parrot perched gently on their hand, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "full body, playful, vibrant colors, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_04": {
        "title": "Sports",
        "brief": (
            "A cheerful sporty cartoon kid athlete avatar holding a gleaming gold winner trophy and a colorful soccer ball, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_05": {
        "title": "Monsters",
        "brief": (
            "A cheerful cartoon kid avatar hugging an adorable fluffy pastel friendly mini monster with tiny horns, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_06": {
        "title": "Numbers",
        "brief": (
            "A cheerful cartoon kid avatar joyfully stacking giant colorful 1-2-3 number blocks, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "full body, vibrant colors, playful, high detail, no text, no words, no frame"
        ),
    },
    "vol_07": {
        "title": "Fruits",
        "brief": (
            "A cheerful little kid chef avatar in a cute chef hat holding a giant smiling juicy strawberry, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_08": {
        "title": "Shapes",
        "brief": (
            "A cheerful cartoon kid avatar holding colorful 3D building blocks in sphere, cube, and pyramid shapes, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_09": {
        "title": "Toys",
        "brief": (
            "A cheerful cartoon kid avatar playing with an adorable classic teddy bear and a colorful toy wooden train, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_10": {
        "title": "Flowers",
        "brief": (
            "A cheerful cartoon kid avatar holding a sunny yellow smiling sunflower and a cute colorful watering can, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_11": {
        "title": "Transport",
        "brief": (
            "A cheerful cartoon kid avatar sitting proudly in a bright red vintage toy roadster pedal car, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
    "vol_12": {
        "title": "Vegetables",
        "brief": (
            "A cheerful little kid gardener avatar wearing cute overalls and holding an oversized smiling orange carrot, "
            "3D Pixar Disney animation style, isolated on a clean solid white background, "
            "vibrant colors, playful, high detail, no text, no letters, no words, no frame"
        ),
    },
}


def extract_clean_transparent_sticker(
    raw_image_path: Path,
    output_sticker_path: Path,
    contour_radius: int = 16,
) -> Path:
    """
    Converts a solid white RGB character generation into a true transparent RGBA
    sticker with smooth die-cut white contour, floor shadow elimination, and preserved shoe/paw details.
    """
    with Image.open(raw_image_path) as im:
        img_rgb = im.convert("RGB")

    arr = np.array(img_rgb, dtype=float)
    h, w, _ = arr.shape

    color_spread = np.maximum(
        np.maximum(np.abs(arr[:, :, 0] - arr[:, :, 1]), np.abs(arr[:, :, 1] - arr[:, :, 2])),
        np.abs(arr[:, :, 0] - arr[:, :, 2]),
    )
    brightness = arr.mean(axis=2)

    # Pure white canvas background
    is_white_bg = (color_spread < 10) & (brightness > 248)

    # Floor shadow: in the bottom 7.5% of image where soles meet floor
    is_floor_region = np.zeros((h, w), dtype=bool)
    is_floor_region[int(h * 0.925):, :] = True
    is_floor_shadow = is_floor_region & (color_spread < 14) & (brightness > 150)

    candidate_bg = is_white_bg | is_floor_shadow

    # Connected background from canvas borders
    labeled, _ = ndimage.label(candidate_bg)
    perimeter_mask = np.zeros((h, w), dtype=bool)
    perimeter_mask[0, :] = True
    perimeter_mask[-1, :] = True
    perimeter_mask[:, 0] = True
    perimeter_mask[:, -1] = True

    bg_labels = np.unique(labeled[perimeter_mask & candidate_bg])
    bg_labels = bg_labels[bg_labels > 0]
    is_connected_bg = np.isin(labeled, bg_labels)

    subject_mask = ~is_connected_bg

    # Clear large trapped white pockets strictly between upper limbs (never shoes/feet)
    near_white_pockets = np.zeros((h, w), dtype=bool)
    upper_limit = int(h * 0.75)
    near_white_pockets[:upper_limit, :] = (
        subject_mask[:upper_limit, :]
        & (arr[:upper_limit, :, 0] >= 238)
        & (arr[:upper_limit, :, 1] >= 238)
        & (arr[:upper_limit, :, 2] >= 238)
    )

    labeled_pockets, num_pockets = ndimage.label(near_white_pockets)
    if num_pockets > 0:
        sizes = ndimage.sum(near_white_pockets, labeled_pockets, range(num_pockets + 1))
        for idx, sz in enumerate(sizes):
            if sz >= 2000:
                subject_mask[labeled_pockets == idx] = False

    # Smooth die-cut white contour
    subject_pil = Image.fromarray((subject_mask * 255).astype(np.uint8), mode="L")
    dilated = subject_pil.filter(ImageFilter.MaxFilter(contour_radius * 2 + 1))
    smooth_alpha = dilated.filter(ImageFilter.GaussianBlur(1.2))

    sticker_base = Image.new("RGBA", (w, h), (255, 255, 255, 255))
    img_rgba = img_rgb.convert("RGBA")

    result = sticker_base.copy()
    result.paste(img_rgba, (0, 0), subject_pil)
    result.putalpha(smooth_alpha)

    # Tight crop with 20px padding
    bbox = result.getbbox()
    if bbox:
        pad = 20
        crop_box = (max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(w, bbox[2] + pad), min(h, bbox[3] + pad))
        cropped = result.crop(crop_box)
    else:
        cropped = result

    output_sticker_path.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(output_sticker_path, "PNG")
    return output_sticker_path


def ingest_canva_hero(url_or_path: str, vol_id: str) -> Path:
    """
    Downloads or copies an isolated Canva 3D hero character into assets/cover_heroes/raw/,
    then converts it into a true transparent RGBA sticker in assets/cover_heroes/{vol_id}_hero.png.
    """
    if vol_id not in CANVA_HERO_BRIEFS:
        raise ValueError(f"Unknown volume ID '{vol_id}'. Valid IDs: {list(CANVA_HERO_BRIEFS.keys())}")
    
    raw_dest = HERO_RAW_DIR / f"{vol_id}_raw.png"
    sticker_dest = HERO_ASSETS_DIR / f"{vol_id}_hero.png"
    p_str = str(url_or_path).strip()
    
    if p_str.startswith(("http://", "https://")):
        print(f"[Canva Pipeline] Downloading 3D hero raw for {vol_id} ({CANVA_HERO_BRIEFS[vol_id]['title']})...")
        urllib.request.urlretrieve(p_str, str(raw_dest))
    elif os.path.exists(p_str):
        print(f"[Canva Pipeline] Copying local 3D hero to raw backup: {p_str} -> {raw_dest}...")
        shutil.copy(p_str, str(raw_dest))
    else:
        raise FileNotFoundError(f"Could not find or reach hero source: {p_str}")

    print(f"[Canva Pipeline] Extracting transparent RGBA sticker with white die-cut contour...")
    extract_clean_transparent_sticker(raw_dest, sticker_dest)
        
    with Image.open(sticker_dest) as im:
        extrema = im.getextrema()
        is_transparent = (im.mode == "RGBA") and (len(extrema) == 4 and extrema[3][0] == 0)
        print(f"[Canva Pipeline] Successfully prepared: {sticker_dest} ({im.size[0]}x{im.size[1]} px, {im.mode}, Transparent={is_transparent})")
    return sticker_dest


def audit_heroes_transparency() -> bool:
    """Audits all 12 heroes in assets/cover_heroes/ to guarantee 100% transparent RGBA format."""
    print("=" * 80)
    print("AUDITING COVER HERO BACKGROUND TRANSPARENCY & STICKER CONTOURS")
    print("=" * 80)
    all_pass = True
    for vol_num in range(1, 13):
        vol_id = f"vol_{vol_num:02d}"
        fp = HERO_ASSETS_DIR / f"{vol_id}_hero.png"
        if not fp.exists():
            print(f"[FAIL] {vol_id:6s} | MISSING on disk: {fp}")
            all_pass = False
            continue
        with Image.open(fp) as im:
            extrema = im.getextrema()
            is_transparent = (im.mode == "RGBA") and (len(extrema) == 4 and extrema[3][0] == 0)
            status = "PASS" if is_transparent else "FAIL"
            if not is_transparent:
                all_pass = False
            print(f"[{status}] {vol_id:6s} | Mode: {im.mode:4s} | Size: {im.size} | Transparent RGBA: {is_transparent}")

    if all_pass:
        print("\n[PASS] 100% COVER HERO AUDIT PASS: All 12 heroes have transparent RGBA backgrounds.")
    else:
        print("\n[FAIL] Some hero assets lack transparent RGBA backgrounds. Re-run extraction.")
    return all_pass


def list_hero_briefs() -> None:
    """Prints all 12 series volumes and their standardized isolated 3D character hero briefs."""
    print("=" * 80)
    print("CANVA ISOLATED 3D CHARACTER HERO BRIEFS (COMPONENT-FIRST STANDARD)")
    print("=" * 80)
    for vol_id, data in CANVA_HERO_BRIEFS.items():
        print(f"\n[{vol_id.upper()}] Copy to Color: {data['title']}")
        print(f"Prompt: {data['brief']}")


def build_unified_cover(vol_id: str, page_count: int = 32) -> Path:
    """
    Compiles a brand-governed cover spread for the specified volume using:
    - Native 300 DPI vector layout (LuckiestGuy 3D neon sparkle title stack)
    - Official 'The Pivot Kids' brand mark
    - Volume theme color gradient
    - Ingested 3D hero character from assets/cover_heroes/{vol_id}_hero.png
    - Two-panel activity card with wax crayons
    - Full-wrap spread with 4x3 back grid and barcode safe zone
    """
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "compile_cover_pil.py"),
        "--vol", vol_id,
        "--page-count", str(page_count),
    ]
    print(f"\n[Canva Pipeline] Compiling brand-governed cover spread for {vol_id}...")
    subprocess.run(cmd, check=True)
    out_pdf = REPO_ROOT / "local_builds" / vol_id / "v1.0-core" / f"{vol_id}-cover-spread-{page_count}p.pdf"
    if not out_pdf.exists():
        # Check animals default
        if vol_id == "vol_02":
            out_pdf = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / f"animals-cover-spread-{page_count}p.pdf"
    return out_pdf


def build_all_unified_covers(page_count: int = 32) -> None:
    """Batch-compiles all 12 series covers with 100% brand consistency and 4x3 grid synchronization."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "compile_cover_pil.py"),
        "--build-all-series",
        "--page-count", str(page_count),
    ]
    print("\n[Canva Pipeline] Batch-compiling all 12 unified series covers...")
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(description="Unified Brand-Governed Cover Production Pipeline")
    subparsers = parser.add_subparsers(dest="command")

    # List briefs
    subparsers.add_parser("list-briefs", help="List isolated 3D character hero briefs for all 12 series volumes")

    # Audit transparency
    subparsers.add_parser("audit-transparency", help="Audit all 12 heroes for transparent RGBA and sticker borders")

    # Ingest Hero
    ingest_hero_p = subparsers.add_parser("ingest-hero", help="Ingest a Canva 3D character hero into assets/cover_heroes/")
    ingest_hero_p.add_argument("--vol", required=True, help="Volume ID (e.g. vol_01 to vol_12)")
    ingest_hero_p.add_argument("--source", required=True, help="Download URL or local file path of the hero image")

    # Build Single Volume
    build_p = subparsers.add_parser("build", help="Build unified brand-governed cover spread for a volume")
    build_p.add_argument("--vol", default="vol_02", help="Volume ID (default: vol_02)")
    build_p.add_argument("--page-count", type=int, default=32, help="Page count (default: 32)")

    # Build All 12 Volumes
    subparsers.add_parser("build-all", help="Build all 12 unified brand-governed series cover spreads")

    args = parser.parse_args()

    if args.command == "list-briefs":
        list_hero_briefs()
    elif args.command == "audit-transparency":
        ok = audit_heroes_transparency()
        sys.exit(0 if ok else 1)
    elif args.command == "ingest-hero":
        path = ingest_canva_hero(args.source, args.vol)
        print(f"[Canva Pipeline] Ready for assembly: {path}")
    elif args.command == "build":
        out = build_unified_cover(args.vol, args.page_count)
        print(f"[Canva Pipeline] Successfully compiled: {out}")
    elif args.command == "build-all":
        build_all_unified_covers()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
