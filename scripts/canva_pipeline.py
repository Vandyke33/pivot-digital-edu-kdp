"""
scripts/canva_pipeline.py
=========================
Canva MCP Cover Pipeline Manager & Dispatcher for "The Pivot Kids: Copy to Color"

Automates:
1. Standardized Canva prompt briefs for all 12 series volumes.
2. Ingestion of exported Canva front covers into assets/external_fronts/
3. Mechanical compilation of KDP full-wrap paperback cover spreads (300 DPI, dynamic spine, barcode safe zone).
4. Automated KDP preflight verification.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTERNAL_FRONTS_DIR = REPO_ROOT / "assets" / "external_fronts"
EXTERNAL_FRONTS_DIR.mkdir(parents=True, exist_ok=True)

# Series Volumes & Optimized Canva Generation Briefs
CANVA_SERIES_BRIEFS = {
    "vol_01": {
        "title": "Alphabet",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Alphabet'. A cheerful cartoon kid avatar joyfully sitting on colorful "
            "oversized 3D ABC letter blocks with a giant crayon in a bright sunny playroom. 3D extruded colorful "
            "typography, coral and sunny yellow palette, playful stickers, sparkles, professional book cover."
        ),
    },
    "vol_02": {
        "title": "Animals",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Animals'. A cheerful cartoon kid avatar joyfully playing with an "
            "adorable friendly baby tiger in a colorful lush tropical meadow. 3D extruded colorful bubbly typography, "
            "warm coral and sunny yellow palette, playful stickers, sparkles, professional and eye-catching children's book cover."
        ),
    },
    "vol_03": {
        "title": "Birds",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Birds'. A cheerful cartoon kid avatar with colorful friendly tropical parakeets "
            "and toucans perched nearby in an enchanted treehouse. 3D extruded colorful bubbly typography, warm palette, "
            "playful stickers, sparkles, professional children's book cover."
        ),
    },
    "vol_04": {
        "title": "Sports",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Sports'. A cheerful cartoon kid athlete avatar holding a gleaming gold trophy "
            "surrounded by soccer, basketball, and tennis balls on a sunny green field. 3D extruded typography, professional cover."
        ),
    },
    "vol_05": {
        "title": "Monsters",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Monsters'. A cheerful cartoon kid avatar joyfully hugging friendly, cute, "
            "fluffy pastel monsters in a whimsical dreamland. 3D extruded bubbly typography, sparkling stars, vibrant cover."
        ),
    },
    "vol_06": {
        "title": "Numbers",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Numbers'. A cheerful cartoon kid avatar joyfully stacking giant glowing "
            "1-2-3 number blocks with confetti and stars in a sunny room. 3D extruded typography, playful stickers, bright cover."
        ),
    },
    "vol_07": {
        "title": "Fruits",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Fruits'. A cheerful little kid chef avatar surrounded by smiling giant juicy "
            "strawberries, oranges, and apples in an orchard. 3D extruded colorful typography, warm sunny palette, professional cover."
        ),
    },
    "vol_08": {
        "title": "Shapes",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Shapes'. A cheerful cartoon kid avatar building a whimsical castle with colorful "
            "3D geometric shapes (cubes, spheres, cones) in a creative studio. 3D extruded typography, vibrant cover."
        ),
    },
    "vol_09": {
        "title": "Toys",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Toys'. A cheerful cartoon kid avatar playing with classic toys, a friendly "
            "teddy bear, building bricks, and toy airplanes in a warm colorful playroom. 3D extruded typography, professional cover."
        ),
    },
    "vol_10": {
        "title": "Flowers",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Flowers'. A cheerful cartoon kid avatar holding a colorful watering can in a "
            "blooming meadow with smiling sunflowers and fluttering butterflies. 3D extruded typography, bright floral palette."
        ),
    },
    "vol_11": {
        "title": "Transport",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Transport'. A cheerful cartoon kid driver avatar in a cute vintage toy car "
            "with airplanes flying in the sky and friendly trains in the background. 3D extruded typography, vibrant cover."
        ),
    },
    "vol_12": {
        "title": "Vegetables",
        "brief": (
            "A vibrant, premium children's activity book front cover for 'The Pivot Kids: Color & Play'. "
            "Series title 'Copy to Color: Vegetables'. A cheerful little kid gardener avatar holding an oversized smiling "
            "carrot in a lush sunny farm garden with pumpkins and tomatoes. 3D extruded typography, fresh garden palette."
        ),
    },
}


def ingest_canva_export(download_url: str, vol_id: str) -> Path:
    """Downloads an exported Canva cover image and saves it to assets/external_fronts/."""
    if vol_id not in CANVA_SERIES_BRIEFS:
        raise ValueError(f"Unknown volume ID '{vol_id}'. Valid IDs: {list(CANVA_SERIES_BRIEFS.keys())}")
    
    dest_path = EXTERNAL_FRONTS_DIR / f"{vol_id}_front.png"
    print(f"[Canva Pipeline] Downloading exported cover for {vol_id} ({CANVA_SERIES_BRIEFS[vol_id]['title']})...")
    urllib.request.urlretrieve(download_url, str(dest_path))
    
    with Image.open(dest_path) as im:
        print(f"[Canva Pipeline] Successfully saved {dest_path} ({im.size[0]}x{im.size[1]} px, mode={im.mode})")
    return dest_path


def list_briefs() -> None:
    """Prints all series volumes and their Canva generation briefs."""
    print("=" * 80)
    print("CANVA GENERATION BRIEFS FOR 'THE PIVOT KIDS: COPY TO COLOR' (12 VOLUMES)")
    print("=" * 80)
    for vol_id, data in CANVA_SERIES_BRIEFS.items():
        print(f"\n[{vol_id.upper()}] Copy to Color: {data['title']}")
        print(f"Brief: {data['brief']}")


def main():
    parser = argparse.ArgumentParser(description="Canva MCP Cover Pipeline Manager")
    subparsers = parser.add_subparsers(dest="command")

    # List briefs
    subparsers.add_parser("list-briefs", help="List Canva generation briefs for all 12 series volumes")

    # Ingest
    ingest_p = subparsers.add_parser("ingest", help="Ingest a Canva export URL into assets/external_fronts/")
    ingest_p.add_argument("--vol", required=True, help="Volume ID (e.g. vol_01 to vol_12)")
    ingest_p.add_argument("--url", required=True, help="Download URL from canva.export-design")

    # Compile spread
    compile_p = subparsers.add_parser("compile", help="Compile KDP full-wrap spread using external front")
    compile_p.add_argument("--vol", default="vol_02", help="Volume ID (default: vol_02)")

    args = parser.parse_args()

    if args.command == "list-briefs":
        list_briefs()
    elif args.command == "ingest":
        path = ingest_canva_export(args.url, args.vol)
        print(f"[Canva Pipeline] Ready for assembly: {path}")
    elif args.command == "compile":
        vol_file = EXTERNAL_FRONTS_DIR / f"{args.vol}_front.png"
        if not vol_file.exists():
            print(f"[Error] External front not found at {vol_file}. Ingest it first.")
            sys.exit(1)
        import subprocess
        cmd = [sys.executable, "main.py", "build-animals-cover", "--external-front", str(vol_file)]
        subprocess.run(cmd, check=True)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
