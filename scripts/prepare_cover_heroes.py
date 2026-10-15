"""
Extract 12 High-Resolution Kid Avatar Hero Stickers for Series Front Covers.

Processes raw 1024x1024 RGB AI generations from local_builds/animals/assets/raw/thumbnails/
into clean, transparent RGBA stickers with smooth 14px white die-cut contours.
Saves outputs to assets/cover_heroes/vol_01_hero.png .. vol_12_hero.png.
"""

from __future__ import annotations

import glob
import os
import sys
from pathlib import Path
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.utils.alpha_extraction import extract_with_sticker_contour

RAW_DIR = REPO_ROOT / "local_builds" / "animals" / "assets" / "raw" / "thumbnails"
OUTPUT_DIR = REPO_ROOT / "assets" / "cover_heroes"


def extract_all_heroes(force: bool = False) -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated = []

    print("=" * 70)
    print("Preparing 12 High-Resolution Kid Avatar Hero Stickers (1024x1024)")
    print("=" * 70)

    for vol_num in range(1, 13):
        vol_id = f"vol_{vol_num:02d}"
        target_path = OUTPUT_DIR / f"{vol_id}_hero.png"

        if target_path.exists() and not force and target_path.stat().st_size > 20_000:
            print(f"[SKIP] {vol_id} hero already exists: {target_path.name}")
            generated.append(target_path)
            continue

        # Find matching raw file
        pattern = str(RAW_DIR / f"{vol_id}_*_raw.png")
        matches = glob.glob(pattern)
        if not matches:
            print(f"[WARN] No raw file found for {vol_id} with pattern {pattern}")
            continue

        raw_path = Path(matches[0])
        print(f"[PROCESS] Extracting sticker for {vol_id} from {raw_path.name}...")

        with Image.open(raw_path) as raw_img:
            # Extract transparent alpha with clean sticker contour
            sticker = extract_with_sticker_contour(
                image=raw_img,
                tolerance=22,
                contour_radius=14,
                blur_radius=1.5,
                remove_trapped_pockets=True,
                min_pocket_area=1500,
            )
            sticker.save(target_path, "PNG")
            print(f"  -> Saved {sticker.size} RGBA sticker to {target_path.relative_to(REPO_ROOT)} ({target_path.stat().st_size} bytes)")
            generated.append(target_path)

    print(f"\n[OK] Successfully prepared {len(generated)}/12 Kid Avatar Hero Stickers in {OUTPUT_DIR.relative_to(REPO_ROOT)}")
    return generated


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract Kid Avatar Hero Stickers")
    parser.add_argument("--force", action="store_true", help="Force re-extraction of all heroes")
    args = parser.parse_args()

    extract_all_heroes(force=args.force)

