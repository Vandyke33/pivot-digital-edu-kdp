"""
scripts/canva_pipeline.py
=========================
Unified Brand-Governed Cover Production Pipeline & Canva Manager
for "The Pivot Kids: Copy to Color" (12 Volumes)

Enforces:
1. Component-First Architecture: Isolated 3D character hero briefs for Canva generation.
2. 100% Brand Mark Consistency: Official 'The Pivot Kids (Color & Play)' vector logo.
3. 100% Typography Consistency: Native 300 DPI 3D neon sparkle display fonts ('Copy to Color' + '<SUBJECT>').
4. Exact Series Palettes & Mechanical Alignment: Strict volume hex codes and locked coordinates.
5. Non-Destructive Scaling: Native 300 DPI layout with zero pixel corruption or fuzzy upscale.
6. KDP Compliance: Dynamic spine width formula, barcode safe zone (2.0 x 1.2 in), 4x3 series back grid.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_FRONTS_DIR = REPO_ROOT / "assets" / "external_fronts"
HERO_ASSETS_DIR = REPO_ROOT / "assets" / "cover_heroes"
SERIES_FRONTS_DIR = REPO_ROOT / "local_builds" / "series_fronts"
EXTERNAL_FRONTS_DIR.mkdir(parents=True, exist_ok=True)
HERO_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
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


def ingest_canva_hero(url_or_path: str, vol_id: str) -> Path:
    """
    Downloads or copies an isolated Canva 3D hero character into assets/cover_heroes/{vol_id}_hero.png
    so the 300 DPI native vector layout engine can layer it into the cover.
    """
    if vol_id not in CANVA_HERO_BRIEFS:
        raise ValueError(f"Unknown volume ID '{vol_id}'. Valid IDs: {list(CANVA_HERO_BRIEFS.keys())}")
    
    dest_path = HERO_ASSETS_DIR / f"{vol_id}_hero.png"
    p_str = str(url_or_path).strip()
    
    if p_str.startswith(("http://", "https://")):
        print(f"[Canva Pipeline] Downloading 3D hero for {vol_id} ({CANVA_HERO_BRIEFS[vol_id]['title']})...")
        urllib.request.urlretrieve(p_str, str(dest_path))
    elif os.path.exists(p_str):
        import shutil
        print(f"[Canva Pipeline] Copying local 3D hero from {p_str} -> {dest_path}...")
        shutil.copy(p_str, str(dest_path))
    else:
        raise FileNotFoundError(f"Could not find or reach hero source: {p_str}")
        
    with Image.open(dest_path) as im:
        print(f"[Canva Pipeline] Successfully ingested 3D hero: {dest_path} ({im.size[0]}x{im.size[1]} px, {im.mode})")
    return dest_path


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
