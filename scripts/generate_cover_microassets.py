"""
Generate Cover Micro-Assets via Google Gemini and Apply Corner Flood-Fill Alpha Extraction.

Generates:
1. 12 Series Thumbnail Icons for the Back Cover 4x3 Grid (Vol. 1 - 12)
2. Hero Character Art (Tiger & Monkey) for Front Cover
3. Inset Activity Card ("Before & After" Tiger) for Front Cover

Applies corner flood-fill alpha extraction with smooth sticker contours so outer white
bounding boxes are 100% transparent while internal whites (eyes, teeth, card areas)
are strictly preserved.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any
from io import BytesIO

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_images_google import extract_image_bytes
from scripts.utils.alpha_extraction import extract_with_sticker_contour


FRONT_COVER_ASSETS = [
    {
        "id": "hero_tiger_monkey",
        "output_raw": "local_builds/animals/assets/raw/hero_tiger_monkey_raw.png",
        "output_final": "local_builds/animals/assets/tiger_monkey_transparent.png",
        "prompt": (
            "Cute cheerful preschool girl wearing a little safari explorer hat happily sitting on green grass "
            "hugging a friendly baby tiger cub and laughing with a playful baby monkey, "
            "vibrant 2D vector children's book illustration style, warm inviting smiles, "
            "sparkling cartoon eyes with white highlights, rich cel-shaded warm oranges, golden yellows, and soft greens, "
            "crisp bold outlines, high-contrast lighting, completely isolated on a pure solid white background, "
            "character sheet art, bright rounded 2D storybook aesthetic with soft cel shading\n\n"
            "--no text, typography, title, words, banners, frames, boxes, white borders, "
            "complex background, trees, sky, ground, realistic fur texture, 3d render, gloomy lighting, watermark, signature"
        ),
        "aspect_ratio": "4:5",
        "contour_radius": 14,
        "tolerance": 20,
    },
    {
        "id": "inset_tiger_split",
        "output_raw": "local_builds/animals/assets/raw/inset_tiger_split_raw.png",
        "output_final": "local_builds/animals/assets/inset_tiger_split.png",
        "prompt": (
            "A cute cartoon baby tiger sitting cheerfully facing forward. "
            "Left half is fully colored in bright cheerful orange with bold black stripes; "
            "Right half is clean black and white coloring page line art with pure white fill "
            "and bold 3pt outlines. Split-view educational coloring preview card, completely isolated on pure solid white background\n\n"
            "--no text, labels, frames, boxes, gray shading, gradients on the line art half, photorealism"
        ),
        "aspect_ratio": "1:1",
        "contour_radius": 10,
        "tolerance": 20,
    }
]


def load_gemini_client():
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return genai.Client(api_key=api_key)

    creds_file = REPO_ROOT / "gcp_credentials.json"
    if creds_file.is_file():
        import google.auth
        credentials, project = google.auth.load_credentials_from_file(
            str(creds_file), scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        return genai.Client(
            enterprise=True,
            project=project,
            location="global",
            credentials=credentials,
        )
    raise FileNotFoundError(f"Missing GEMINI_API_KEY or {creds_file}")


def generate_single_image(
    client,
    prompt: str,
    aspect_ratio: str = "1:1",
    model: str = "gemini-3.1-flash-lite-image",
    max_retries: int = 4,
) -> bytes:
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_modalities": ["IMAGE"],
                    "image_config": {"aspect_ratio": aspect_ratio},
                },
            )
            return extract_image_bytes(response)
        except Exception as e:
            if ("RESOURCE_EXHAUSTED" in str(e) or "429" in str(e)) and attempt < max_retries:
                wait_time = 30 * attempt
                print(f"  [QUOTA] Rate limit hit. Waiting {wait_time}s before retry {attempt}/{max_retries}...")
                time.sleep(wait_time)
                continue
            raise



def run_generation_pipeline(
    skip_existing: bool = True,
    generate_front: bool = True,
    generate_thumbnails: bool = True,
    limit: int | None = None,
):
    print("=" * 70)
    print("KDP Cover Micro-Asset Generation & Alpha Extraction Pipeline")
    print("=" * 70)

    client = load_gemini_client()
    print("[OK] Authenticated Google GenAI client (location: global)")

    generated_count = 0

    # 1. Front Cover Assets
    if generate_front:
        for asset in FRONT_COVER_ASSETS:
            raw_path = REPO_ROOT / asset["output_raw"]
            final_path = REPO_ROOT / asset["output_final"]

            if skip_existing and final_path.exists():
                print(f"[SKIP] Front asset already exists: {final_path.name}")
                continue

            print(f"\n[GEN] Generating front asset: {asset['id']}...")
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            final_path.parent.mkdir(parents=True, exist_ok=True)

            try:
                raw_bytes = generate_single_image(client, asset["prompt"], asset["aspect_ratio"])
                raw_path.write_bytes(raw_bytes)
                print(f"  -> Raw image saved ({len(raw_bytes)} bytes) to {raw_path.relative_to(REPO_ROOT)}")

                with Image.open(BytesIO(raw_bytes)) as img:
                    extracted = extract_with_sticker_contour(
                        img,
                        tolerance=asset["tolerance"],
                        contour_radius=asset["contour_radius"],
                        blur_radius=1.5,
                    )
                    extracted.save(final_path, format="PNG")
                print(f"  -> Alpha extracted with sticker contour saved to {final_path.relative_to(REPO_ROOT)}")
                generated_count += 1
                time.sleep(2)
            except Exception as e:
                print(f"  [ERROR] Failed to generate {asset['id']}: {e}")

    # 2. 12 Series Thumbnail Icons
    if generate_thumbnails:
        batch_file = REPO_ROOT / "manifests" / "series_thumbnails_batch.json"
        batch_data = json.loads(batch_file.read_text(encoding="utf-8"))
        items = batch_data.get("items", [])

        if limit:
            items = items[:limit]

        thumbs_dir = REPO_ROOT / "local_builds" / "animals" / "assets" / "thumbnails"
        raw_thumbs_dir = REPO_ROOT / "local_builds" / "animals" / "assets" / "raw" / "thumbnails"
        thumbs_dir.mkdir(parents=True, exist_ok=True)
        raw_thumbs_dir.mkdir(parents=True, exist_ok=True)

        for item in items:
            vol_num = item["volume_number"]
            subject_id = item["subject_id"]
            title_slug = item["title"].lower().replace(" ", "_")

            raw_path = raw_thumbs_dir / f"{subject_id}_raw.png"
            final_named_path = thumbs_dir / f"vol_{vol_num:02d}_{title_slug}.png"
            final_short_path = thumbs_dir / f"vol_{vol_num:02d}.png"

            if skip_existing and (final_named_path.exists() or final_short_path.exists()):
                print(f"[SKIP] Thumbnail already exists: Vol. {vol_num} ({item['title']})")
                continue

            print(f"\n[GEN] Generating Vol. {vol_num}: {item['title']} ({subject_id})...")
            prompt = item["prompt"] + "\n\nAvoid including: " + item.get("negative_prompt", "")

            try:
                raw_bytes = generate_single_image(client, prompt, aspect_ratio="1:1")
                raw_path.write_bytes(raw_bytes)
                print(f"  -> Raw thumbnail saved to {raw_path.relative_to(REPO_ROOT)}")

                with Image.open(BytesIO(raw_bytes)) as img:
                    # Resize to clean square 512x512 thumbnail
                    img_sq = img.resize((512, 512), Image.Resampling.LANCZOS)
                    # For thumbnails, extract corner white background if present
                    extracted = extract_with_sticker_contour(
                        img_sq,
                        tolerance=20,
                        contour_radius=8,
                        blur_radius=1.2,
                    )
                    extracted.save(final_named_path, format="PNG")
                    extracted.save(final_short_path, format="PNG")

                    global_thumb_dir = REPO_ROOT / "assets" / "cover_thumbnails"
                    global_thumb_dir.mkdir(parents=True, exist_ok=True)
                    extracted.save(global_thumb_dir / f"vol_{vol_num:02d}_{title_slug}.png", format="PNG")
                    extracted.save(global_thumb_dir / f"vol_{vol_num:02d}.png", format="PNG")

                item["review_status"] = "GENERATED_LOCAL"
                item["local_asset_path"] = final_named_path.relative_to(REPO_ROOT).as_posix()
                print(f"  -> Thumbnail saved: {final_named_path.name} & {final_short_path.name}")
                generated_count += 1
                time.sleep(15)
            except Exception as e:
                print(f"  [ERROR] Failed to generate {subject_id}: {e}")

        # Update batch manifest status atomically
        tmp_manifest = batch_file.with_suffix(".tmp")
        tmp_manifest.write_text(json.dumps(batch_data, indent=2) + "\n", encoding="utf-8")
        tmp_manifest.replace(batch_file)

    print(f"\n[DONE] Pipeline completed: {generated_count} asset(s) generated and extracted.")


def main():
    parser = argparse.ArgumentParser(description="Generate KDP Cover Micro-Assets")
    parser.add_argument("--force", action="store_true", help="Force overwrite existing assets")
    parser.add_argument("--front-only", action="store_true", help="Generate only front cover assets")
    parser.add_argument("--thumbnails-only", action="store_true", help="Generate only thumbnails")
    parser.add_argument("--limit", "--max-assets", dest="limit", type=int, default=4, help="Limit number of assets to generate (1-12, default 4)")
    args = parser.parse_args()

    run_generation_pipeline(
        skip_existing=not args.force,
        generate_front=not args.thumbnails_only,
        generate_thumbnails=not args.front_only,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
