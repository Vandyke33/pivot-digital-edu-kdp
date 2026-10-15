"""
AI-First Paired Asset Generation Pipeline for "The Pivot Kids: Copy to Color" Series.

Features:
  - Generates 1:1 paired assets for each subject:
      1. subj_XX_lineart.png: Pure B&W vector outline coloring page (hollow white interior).
      2. subj_XX_color.png: Matched color guide generated via image-to-image referencing the lineart.
  - Strict Ban on Procedural Shape Illustrations (NO_PROCEDURAL_ART).
  - Trap 1 Guardrail: NO "transparent background" in prompts (avoids fake checkerboards).
    Instead prompts for pure solid white (#FFFFFF) background, then performs corner flood-fill +
    white-pocket removal for true RGBA transparency.
  - Trap 2 Guardrail: Pilot mode generates all 30 pairs for vol_02 (Animals) PLUS subj_01 for the other 11 volumes.
  - Trap 3 Guardrail: Automated Black-Blob QA Gate. Retries if lineart black pixels exceed 15%.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.generate_images_google import create_google_client, extract_image_bytes
from scripts.utils.alpha_extraction import isolate_with_sticker_border

# ---------------------------------------------------------------------------
# SERIES VOLUMES & SUBJECT DEFINITIONS
# ---------------------------------------------------------------------------
SERIES_SUBJECTS: dict[str, list[tuple[str, str]]] = {
    "vol_01": [("01", "APPLE"), ("02", "BALL"), ("03", "CAKE"), ("04", "DEER"), ("05", "ELEPHANT"),
               ("06", "FISH"), ("07", "GIRAFFE"), ("08", "HOUSE"), ("09", "ICE CREAM"), ("10", "JEEP"),
               ("11", "KITE"), ("12", "LION"), ("13", "MONKEY"), ("14", "NEST"), ("15", "OWL"),
               ("16", "PARROT"), ("17", "QUEEN BEE"), ("18", "RABBIT"), ("19", "SUN"), ("20", "TIGER"),
               ("21", "UMBRELLA"), ("22", "VAN"), ("23", "WHALE"), ("24", "XYLOPHONE"), ("25", "YACHT"),
               ("26", "ZEBRA"), ("27", "STAR"), ("28", "BELL"), ("29", "TREE"), ("30", "BOAT")],
    "vol_02": [("01", "TIGER"), ("02", "MONKEY"), ("03", "ELEPHANT"), ("04", "GIRAFFE"), ("05", "LION"),
               ("06", "ZEBRA"), ("07", "HIPPO"), ("08", "KOALA"), ("09", "PANDA"), ("10", "KANGAROO"),
               ("11", "RABBIT"), ("12", "PUPPY"), ("13", "KITTEN"), ("14", "COW"), ("15", "HORSE"),
               ("16", "SHEEP"), ("17", "PIGLET"), ("18", "DEER"), ("19", "FOX"), ("20", "BEAR"),
               ("21", "SQUIRREL"), ("22", "HEDGEHOG"), ("23", "SLOTH"), ("24", "CAMEL"), ("25", "CHEETAH"),
               ("26", "RHINO"), ("27", "OTTER"), ("28", "BEAVER"), ("29", "LLAMA"), ("30", "RACCOON")],
    "vol_03": [("01", "PARROT"), ("02", "OWL"), ("03", "PEACOCK"), ("04", "FLAMINGO"), ("05", "EAGLE"),
               ("06", "PENGUIN"), ("07", "TOUCAN"), ("08", "HUMMINGBIRD"), ("09", "SWAN"), ("10", "DUCK"),
               ("11", "ROOSTER"), ("12", "PIGEON"), ("13", "WOODPECKER"), ("14", "ROBIN"), ("15", "BLUE JAY"),
               ("16", "CANARY"), ("17", "SEAGULL"), ("18", "SPARROW"), ("19", "PELICAN"), ("20", "KINGFISHER"),
               ("21", "OSTRICH"), ("22", "HERON"), ("23", "STORK"), ("24", "FALCON"), ("25", "SWALLOW"),
               ("26", "GOOSE"), ("27", "GOLDFINCH"), ("28", "FINCH"), ("29", "DOVE"), ("30", "CARDINAL")],
    "vol_04": [("01", "SOCCER BALL"), ("02", "BASKETBALL"), ("03", "BASEBALL"), ("04", "TENNIS"), ("05", "SWIMMING"),
               ("06", "CYCLING"), ("07", "SKATEBOARD"), ("08", "RUNNING"), ("09", "GYMNASTICS"), ("10", "SKATING"),
               ("11", "KARATE"), ("12", "BOWLING"), ("13", "GOLF"), ("14", "BOXING"), ("15", "BADMINTON"),
               ("16", "VOLLEYBALL"), ("17", "SURFING"), ("18", "SKIING"), ("19", "ARCHERY"), ("20", "TABLE TENNIS"),
               ("21", "RUGBY"), ("22", "ROWING"), ("23", "HOCKEY"), ("24", "CRICKET"), ("25", "ROLLER SKATING"),
               ("26", "MEDAL"), ("27", "TROPHY"), ("28", "WHISTLE"), ("29", "SNEAKERS"), ("30", "SPORTS CAP")],
    "vol_05": [("01", "FUZZY MONSTER"), ("02", "ONE-EYED MONSTER"), ("03", "SPIKY MONSTER"), ("04", "HAPPY MONSTER"),
               ("05", "WINGED MONSTER"), ("06", "HORNED MONSTER"), ("07", "BOUNCY MONSTER"), ("08", "STRIPY MONSTER"),
               ("09", "POLKA-DOT MONSTER"), ("10", "GENTLE GIANT"), ("11", "TINY MONSTER"), ("12", "CANDY MONSTER"),
               ("13", "BOOK MONSTER"), ("14", "MUSIC MONSTER"), ("15", "STAR MONSTER"), ("16", "BUBBLE MONSTER"),
               ("17", "GARDEN MONSTER"), ("18", "SNOW MONSTER"), ("19", "CLOUD MONSTER"), ("20", "RAINBOW MONSTER"),
               ("21", "SLEEPY MONSTER"), ("22", "CHEF MONSTER"), ("23", "DANCING MONSTER"), ("24", "FLYING MONSTER"),
               ("25", "WATER MONSTER"), ("26", "FOREST MONSTER"), ("27", "MAGIC MONSTER"), ("28", "FUNNY MONSTER"),
               ("29", "SPACE MONSTER"), ("30", "SUPER MONSTER")],
    "vol_06": [("01", "ONE GIRAFFE"), ("02", "TWO ELEPHANTS"), ("03", "THREE LIONS"), ("04", "FOUR ZEBRAS"),
               ("05", "FIVE MONKEYS"), ("06", "SIX FROGS"), ("07", "SEVEN BIRDS"), ("08", "EIGHT BUTTERFLIES"),
               ("09", "NINE FISH"), ("10", "TEN STARS"), ("11", "ELEVEN APPLES"), ("12", "TWELVE DUCKS"),
               ("13", "THIRTEEN BALLOONS"), ("14", "FOURTEEN FLOWERS"), ("15", "FIFTEEN HEARTS"),
               ("16", "SIXTEEN CANDIES"), ("17", "SEVENTEEN BEES"), ("18", "EIGHTEEN CHERRIES"),
               ("19", "NINETEEN CRAYONS"), ("20", "TWENTY BUBBLES"), ("21", "NUMBER 1"), ("22", "NUMBER 2"),
               ("23", "NUMBER 3"), ("24", "NUMBER 4"), ("25", "NUMBER 5"), ("26", "NUMBER 6"),
               ("27", "NUMBER 7"), ("28", "NUMBER 8"), ("29", "NUMBER 9"), ("30", "NUMBER 10")],
    "vol_07": [("01", "APPLE"), ("02", "BANANA"), ("03", "ORANGE"), ("04", "STRAWBERRY"), ("05", "MANGO"),
               ("06", "GRAPES"), ("07", "WATERMELON"), ("08", "PINEAPPLE"), ("09", "PEACH"), ("10", "CHERRY"),
               ("11", "PAPAYA"), ("12", "KIWI"), ("13", "PEAR"), ("14", "PLUM"), ("15", "POMEGRANATE"),
               ("16", "LEMON"), ("17", "BLUEBERRY"), ("18", "RASPBERRY"), ("19", "AVOCADO"), ("20", "COCONUT"),
               ("21", "GUAVA"), ("22", "FIG"), ("23", "APRICOT"), ("24", "LIME"), ("25", "MELON"),
               ("26", "BLACKBERRY"), ("27", "DRAGONFRUIT"), ("28", "PASSION FRUIT"), ("29", "LYCHEE"), ("30", "FRUIT BASKET")],
    "vol_08": [("01", "CIRCLE"), ("02", "SQUARE"), ("03", "TRIANGLE"), ("04", "STAR"), ("05", "HEART"),
               ("06", "OVAL"), ("07", "RECTANGLE"), ("08", "DIAMOND"), ("09", "PENTAGON"), ("10", "HEXAGON"),
               ("11", "CRESCENT"), ("12", "CROSS"), ("13", "OCTAGON"), ("14", "TRAPEZOID"), ("15", "ARROW"),
               ("16", "CONE"), ("17", "CYLINDER"), ("18", "CUBE"), ("19", "SPHERE"), ("20", "PYRAMID"),
               ("21", "SHAPE TRAIN"), ("22", "SHAPE HOUSE"), ("23", "SHAPE ROBOT"), ("24", "SHAPE ROCKET"),
               ("25", "SHAPE SUN"), ("26", "SHAPE FLOWER"), ("27", "SHAPE CAR"), ("28", "SHAPE BOAT"),
               ("29", "SHAPE CASTLE"), ("30", "SHAPE TOWN")],
    "vol_09": [("01", "TEDDY BEAR"), ("02", "TOY CAR"), ("03", "BUILDING BLOCKS"), ("04", "DOLL"), ("05", "ROCKET"),
               ("06", "TOY ROBOT"), ("07", "DRUM"), ("08", "TRAIN"), ("09", "YO-YO"), ("10", "SPINNING TOP"),
               ("11", "KITE"), ("12", "RUBBER DUCK"), ("13", "BALLOON"), ("14", "ROCKING HORSE"), ("15", "PINWHEEL"),
               ("16", "XYLOPHONE"), ("17", "WATER GUN"), ("18", "TOY AIRPLANE"), ("19", "PUZZLE"), ("20", "BOAT"),
               ("21", "PLAY DOUGH"), ("22", "JACK-IN-THE-BOX"), ("23", "TOY TRUCK"), ("24", "HELICOPTER"),
               ("25", "SUBMARINE"), ("26", "SAND BUCKET"), ("27", "MAGIC WAND"), ("28", "PUPPET"),
               ("29", "ROLLER SKATES"), ("30", "TOY CHEST")],
    "vol_10": [("01", "SUNFLOWER"), ("02", "ROSE"), ("03", "TULIP"), ("04", "DAISY"), ("05", "LOTUS"),
               ("06", "ORCHID"), ("07", "LILY"), ("08", "HIBISCUS"), ("09", "MARIGOLD"), ("10", "POPPY"),
               ("11", "JASMINE"), ("12", "DAFFODIL"), ("13", "CARNATION"), ("14", "LAVENDER"), ("15", "CHERRY BLOSSOM"),
               ("16", "VIOLET"), ("17", "PEONY"), ("18", "IRIS"), ("19", "BLUEBELL"), ("20", "MAGNOLIA"),
               ("21", "GARDENIA"), ("22", "CHRYSANTHEMUM"), ("23", "BEGONIA"), ("24", "CAMELLIA"),
               ("25", "GERANIUM"), ("26", "WATER LILY"), ("27", "MORNING GLORY"), ("28", "DAHLIA"),
               ("29", "FLOWER POT"), ("30", "FLOWER BOUQUET")],
    "vol_11": [("01", "CAR"), ("02", "BUS"), ("03", "TRAIN"), ("04", "AIRPLANE"), ("05", "BICYCLE"),
               ("06", "BOAT"), ("07", "FIRE TRUCK"), ("08", "POLICE CAR"), ("09", "AMBULANCE"), ("10", "HELICOPTER"),
               ("11", "MOTORCYCLE"), ("12", "TRACTOR"), ("13", "ROCKET"), ("14", "SUBMARINE"), ("15", "SCOOTER"),
               ("16", "TAXI"), ("17", "DUMP TRUCK"), ("18", "HOT AIR BALLOON"), ("19", "SAILBOAT"), ("20", "CABLE CAR"),
               ("21", "SKATEBOARD"), ("22", "YACHT"), ("23", "CEMENT MIXER"), ("24", "FERRY"), ("25", "MONORAIL"),
               ("26", "CRANE TRUCK"), ("27", "GARBAGE TRUCK"), ("28", "TRAM"), ("29", "TOW TRUCK"), ("30", "STEAM ENGINE")],
    "vol_12": [("01", "CARROT"), ("02", "TOMATO"), ("03", "POTATO"), ("04", "BROCCOLI"), ("05", "CORN"),
               ("06", "PEAS"), ("07", "EGGPLANT"), ("08", "CUCUMBER"), ("09", "PUMPKIN"), ("10", "BELL PEPPER"),
               ("11", "ONION"), ("12", "GARLIC"), ("13", "SPINACH"), ("14", "CAULIFLOWER"), ("15", "RADISH"),
               ("16", "LETTUCE"), ("17", "BEETROOT"), ("18", "MUSHROOM"), ("19", "CABBAGE"), ("20", "ZUCCHINI"),
               ("21", "SWEET POTATO"), ("22", "ASPARAGUS"), ("23", "CELERY"), ("24", "GINGER"), ("25", "CHILI"),
               ("26", "OKRA"), ("27", "ARTICHOKE"), ("28", "TURNIP"), ("29", "GREEN BEANS"), ("30", "VEGETABLE BASKET")],
}

VOL_TITLES: dict[str, str] = {
    "vol_01": "Alphabet",
    "vol_02": "Animals",
    "vol_03": "Birds",
    "vol_04": "Sports",
    "vol_05": "Monsters",
    "vol_06": "Numbers",
    "vol_07": "Fruits",
    "vol_08": "Shapes",
    "vol_09": "Toys",
    "vol_10": "Flowers",
    "vol_11": "Transport",
    "vol_12": "Vegetables",
}


# ---------------------------------------------------------------------------
# TRAP 3: BLACK-BLOB QA GATE & LINEART CLEANER
# ---------------------------------------------------------------------------
def audit_lineart_black_blob(im: Image.Image, max_black_ratio: float = 0.15) -> tuple[bool, float]:
    """
    Audits an image to verify it does not contain solid black fills (black blobs).
    Returns (passes_gate, black_ratio).
    """
    gray = im.convert("L")
    w, h = gray.size
    total_pixels = w * h
    # Pixels with L < 80 are considered black outline / dark ink
    black_count = sum(1 for p in gray.getdata() if p < 80)
    ratio = black_count / float(total_pixels)
    passes = (ratio <= max_black_ratio)
    return passes, ratio


def clean_lineart_to_pure_bw(raw_img: Image.Image) -> Image.Image:
    """
    Converts raw Gemini lineart output into strict pure black (0) and pure white (255)
    contours on pure white background with smooth, closed contours.
    """
    if raw_img.mode != "L":
        gray = raw_img.convert("L")
    else:
        gray = raw_img

    # Auto-contrast to maximize dynamic range
    gray = ImageOps.autocontrast(gray, cutoff=2)

    # Threshold: anything brighter than 180 is pure white; darker is black contour
    bw = gray.point(lambda p: 0 if p < 180 else 255)

    # Clean outer edge border
    draw = ImageDraw.Draw(bw)
    draw.rectangle([0, 0, bw.width - 1, bw.height - 1], outline=255, width=6)

    return bw.convert("RGBA")


# ---------------------------------------------------------------------------
# TRAP 1: TRANSPARENT STICKER CONTOUR EXTRACTION (FROM SOLID WHITE)
# ---------------------------------------------------------------------------
def make_pure_white_transparent(img: Image.Image, threshold: int = 240, add_sticker: bool = True) -> Image.Image:
    """
    Safely converts pure white (#FFFFFF) background to true RGBA transparency.
    Avoids checkerboard artifacts by operating only on solid white studio backgrounds.
    """
    rgba = img.convert("RGBA")
    r, g, b, a = rgba.split()

    # Mask of white background: R >= 240, G >= 240, B >= 240
    mask = Image.new("L", rgba.size, 0)
    w, h = rgba.size
    pix = rgba.load()
    mask_pix = mask.load()

    # Flood fill from the 4 corners to only target the outer background
    for seed in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
        ImageDraw.floodfill(rgba, seed, (255, 255, 255, 0), thresh=25)

    # Re-extract alpha
    final_alpha = rgba.split()[3]

    if add_sticker:
        # Add a smooth organic white sticker outline
        return isolate_with_sticker_border(rgba, stroke_size=12, remove_trapped_pockets=True)
    return rgba


# ---------------------------------------------------------------------------
# GEMINI PROMPT FACTORIES
# ---------------------------------------------------------------------------
def build_lineart_prompt(subject_name: str, vol_id: str, is_retry: bool = False) -> str:
    vol_title = VOL_TITLES.get(vol_id, "Animals")

    if is_retry:
        return (
            f"RETRY STRICT OUTLINE ONLY: Extreme minimalist black outline coloring book page for toddlers. "
            f"Adorable cartoon baby {subject_name.lower()}, full body visible. "
            f"Every single body part (head, body, ears, limbs, tail, belly) MUST HAVE A HOLLOW WHITE INTERIOR (#FFFFFF) "
            f"so a child can color it in with crayons. Absolutely zero solid black fills, zero black shading, zero dark gray. "
            f"Only thin closed black contours on a pure solid white (#FFFFFF) background, no drop shadows, no checkerboard pattern, no text."
        )

    if vol_id in ("vol_01", "vol_02", "vol_03"):
        # Animal / Bird / Letter Character
        entity_desc = f"adorable cartoon baby {subject_name.lower()} sitting happily on a small tuft of grass with tiny flowers"
    elif vol_id in ("vol_07", "vol_12"):
        # Fruit / Vegetable
        entity_desc = f"cheerful cute cartoon {subject_name.lower()} with big smiling friendly face and cute eyes"
    elif vol_id == "vol_11":
        # Vehicle
        entity_desc = f"cute cheerful cartoon toy {subject_name.lower()} with smiling headlights and friendly cartoon eyes"
    else:
        entity_desc = f"cheerful cute cartoon {subject_name.lower()}"

    return (
        f"Pure black-and-white outline coloring book page for young kids ages 3-5, {entity_desc}, full body completely visible. "
        f"Hollow white interior regions inside ears, fur, patches, and limbs so every part can be colored with crayons, "
        f"zero solid black fills except tiny eye pupils and nose tip, bold 3-4 pt closed black outlines on a pure solid white (#FFFFFF) background, "
        f"zero gray shading, zero crosshatching, zero texture, zero gradients, zero text, no drop shadows, no checkerboard pattern."
    )


def build_color_guide_prompt(subject_name: str) -> str:
    return (
        f"Color this exact black-and-white line drawing of a {subject_name.lower()} with bright, cheerful, flat children's book colors "
        f"on a pure solid white (#FFFFFF) background. Keep the exact same pose, outlines, and proportions. "
        f"Vibrant preschool palette (clean primary and pastel fills), solid color fills inside all black outlines. "
        f"Zero drop shadows, no checkerboard pattern, no background scenery, no text."
    )


# ---------------------------------------------------------------------------
# CORE GENERATION ENGINE
# ---------------------------------------------------------------------------
def robust_generate_content(client: Any, model: str, contents: Any, config: dict, max_retries: int = 6) -> Any:
    """Calls Gemini API with automatic exponential backoff on 429 / RESOURCE_EXHAUSTED."""
    for attempt in range(max_retries):
        try:
            return client.models.generate_content(model=model, contents=contents, config=config)
        except Exception as exc:
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                wait_time = (attempt + 1) * 20
                print(f"       [429 Quota/Rate Limit] Waiting {wait_time}s before retry (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                if attempt == max_retries - 1:
                    raise
                print(f"       [API Error] {exc}. Retrying in 6s...")
                time.sleep(6)
    raise RuntimeError("Failed to generate content after max retries")


def generate_single_pair(
    client: Any,
    model: str,
    subject_idx: int,
    subject_name: str,
    vol_id: str,
    out_dir: Path,
) -> tuple[Path, Path]:
    """
    Generates one (lineart, color) pair via Gemini API with Black-Blob QA check.
    Saves to:
      out_dir / subj_{idx:02d}_lineart.png
      out_dir / subj_{idx:02d}_color.png
    """
    lineart_path = out_dir / f"subj_{subject_idx:02d}_lineart.png"
    color_path = out_dir / f"subj_{subject_idx:02d}_color.png"

    # Step A: Generate Line-Art Master with Black-Blob QA Gate
    raw_lineart_im = None
    for attempt in range(2):
        is_retry = (attempt > 0)
        prompt = build_lineart_prompt(subject_name, vol_id, is_retry=is_retry)
        print(f"    -> [Gen Line-Art] {vol_id} #{subject_idx:02d} {subject_name} (Attempt {attempt+1})...")

        resp = robust_generate_content(
            client=client,
            model=model,
            contents=prompt,
            config={
                "response_modalities": ["IMAGE"],
                "image_config": {"aspect_ratio": "1:1"},
            },
        )
        raw_bytes = extract_image_bytes(resp)
        from io import BytesIO
        candidate_im = Image.open(BytesIO(raw_bytes)).convert("RGB")

        # QA Check: Audit Black-Blob density
        passes, ratio = audit_lineart_black_blob(candidate_im, max_black_ratio=0.15)
        print(f"       [QA Black-Blob Audit] Ink ratio: {ratio*100:.1f}% (Max 15%) -> {'PASS' if passes else 'FAIL (Too dark, retrying)'}")
        if passes or attempt == 1:
            raw_lineart_im = candidate_im
            break

    # Clean to pure 1:1 binary lineart
    clean_lineart = clean_lineart_to_pure_bw(raw_lineart_im)
    clean_lineart.save(str(lineart_path), "PNG")
    print(f"       [Saved Line-Art] {lineart_path.name}")

    time.sleep(10.0)  # Paced rate limiting between line-art and color-guide calls

    # Step B: Generate Matched Color Guide via Image-to-Image
    print(f"    -> [Gen Color Guide] {vol_id} #{subject_idx:02d} {subject_name} via Image-to-Image...")
    color_prompt = build_color_guide_prompt(subject_name)

    # Pass the clean line-art as reference image
    resp_color = robust_generate_content(
        client=client,
        model=model,
        contents=[clean_lineart.convert("RGB"), color_prompt],
        config={
            "response_modalities": ["IMAGE"],
            "image_config": {"aspect_ratio": "1:1"},
        },
    )
    raw_color_bytes = extract_image_bytes(resp_color)
    color_im = Image.open(BytesIO(raw_color_bytes)).convert("RGBA")
    color_im.save(str(color_path), "PNG")
    print(f"       [Saved Color Guide] {color_path.name}")

    return lineart_path, color_path


# ---------------------------------------------------------------------------
# COVER AI ASSETS GENERATION
# ---------------------------------------------------------------------------
def generate_cover_ai_assets(client: Any, model: str, output_dir: Path) -> dict[str, Path]:
    """
    Generates the 3 essential AI cover assets:
      1. mascot_kid_wand.png: Cartoon boy explorer with backwards cap & magic star wand.
      2. crayons_3d.png: 3 large glossy wax crayons.
      3. jungle_foreground_frame.png: Lush tropical leaves, mushrooms & butterflies.
    Applies pure white isolation + sticker contour for true RGBA transparency (Trap 1 Guardrail).
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    assets_specs = [
        {
            "filename": "mascot_kid_wand.png",
            "prompt": (
                "Cheerful cute cartoon boy explorer wearing a colorful backwards baseball cap (cyan crown, yellow visor, red band) "
                "and purple hoodie, smiling wide, holding up a magic wooden wand with a glowing yellow starburst tip, "
                "chubby rosy cheeks, big anime eyes, thick clean black outlines, storybook vector illustration, "
                "isolated on a pure solid white (#FFFFFF) background, no drop shadows, no checkerboard pattern, full upper body."
            ),
            "sticker": True,
        },
        {
            "filename": "crayons_3d.png",
            "prompt": (
                "Three large vibrant wax crayons (sunny yellow, cherry red, sky blue) grouped together diagonally, "
                "sharp conical wax tips, printed paper wrapper bands, glossy vibrant 3D children's coloring book style, "
                "thick clean contours, isolated on a pure solid white (#FFFFFF) background, no drop shadows, no checkerboard pattern."
            ),
            "sticker": False,
        },
        {
            "filename": "jungle_foreground_frame.png",
            "prompt": (
                "Lush cartoon jungle foliage foreground border for a children's book cover, "
                "oversized green tropical monstera leaves, blooming colorful daisies, red polka-dot fly-agaric toadstool mushrooms, "
                "and cute fluttering butterflies with dotted flight trails, framing the bottom edge and corners, "
                "vibrant children's storybook art, thick clean outlines, isolated on a pure solid white (#FFFFFF) background, "
                "no drop shadows, no checkerboard pattern."
            ),
            "sticker": False,
        },
    ]

    for spec in assets_specs:
        target_path = output_dir / spec["filename"]
        if target_path.exists() and target_path.stat().st_size > 5000:
            print(f"  [Skip Existing Cover Asset] {spec['filename']}")
            results[spec["filename"]] = target_path
            continue

        print(f"  -> [Generating Cover Asset] {spec['filename']}...")
        resp = robust_generate_content(
            client=client,
            model=model,
            contents=spec["prompt"],
            config={
                "response_modalities": ["IMAGE"],
                "image_config": {"aspect_ratio": "1:1"},
            },
        )
        from io import BytesIO
        raw_bytes = extract_image_bytes(resp)
        raw_im = Image.open(BytesIO(raw_bytes))

        # Convert pure white to RGBA transparency with smooth sticker border
        rgba_im = make_pure_white_transparent(raw_im, threshold=240, add_sticker=spec["sticker"])
        rgba_im.save(str(target_path), "PNG")
        print(f"     [Saved & Isolated RGBA] {target_path}")
        results[spec["filename"]] = target_path

    return results


# ---------------------------------------------------------------------------
# BATCH ORCHESTRATOR (PHASE A PILOT)
# ---------------------------------------------------------------------------
def run_phase_a_pilot(
    project: str = "mpe-core",
    location: str = "global",
    model: str = "gemini-3.1-flash-lite-image",
    resume: bool = True,
) -> None:
    """
    Executes Phase A Pilot:
      1. All 30 subject pairs for vol_02 (Animals).
      2. Subject #1 pair for vol_01 and vol_03..vol_12 (11 pairs) so all 12 miniature covers have real cards.
      3. AI cover assets (mascot, crayons, jungle foliage).
    Total: 41 pairs (82 Gemini calls) + 3 cover assets.
    """
    client, proj = create_google_client(project=project, location=location)
    print(f"\n{'='*75}\nAI-FIRST PAIRED ASSET GENERATION PIPELINE — PHASE A PILOT\n{'='*75}")
    print(f"Project: {proj} | Location: {location} | Model: {model}\n")

    # 1. Cover AI Assets
    cover_dir = REPO_ROOT / "assets/cover"
    print("[1/3] Generating AI Cover Assets (Mascot, Crayons, Jungle Frame)...")
    generate_cover_ai_assets(client, model, cover_dir)

    # 2. Volume 2 (Animals) — All 30 Subjects
    vol_02_dir = REPO_ROOT / "assets/series_ai/vol_02"
    vol_02_dir.mkdir(parents=True, exist_ok=True)
    animals = SERIES_SUBJECTS["vol_02"]
    print(f"\n[2/3] Generating Volume 2 (Animals) — All 30 Subjects...")

    for idx, (code, name) in enumerate(animals, start=1):
        l_path = vol_02_dir / f"subj_{idx:02d}_lineart.png"
        c_path = vol_02_dir / f"subj_{idx:02d}_color.png"

        if resume and l_path.exists() and c_path.exists() and l_path.stat().st_size > 5000 and c_path.stat().st_size > 5000:
            print(f"  [Skip Existing] vol_02 #{idx:02d} {name}")
            continue

        print(f"\n  [Subject {idx:02d}/30] Generating {name}...")
        generate_single_pair(client, model, idx, name, "vol_02", vol_02_dir)
        time.sleep(10.0)  # Paced rate limiting

    # Also mirror vol_02 assets to local_builds/animals/assets/ for backwards compatibility
    legacy_dir = REPO_ROOT / "local_builds/animals/assets"
    legacy_dir.mkdir(parents=True, exist_ok=True)
    t_line = vol_02_dir / "subj_01_lineart.png"
    t_col = vol_02_dir / "subj_01_color.png"
    if t_line.exists():
        import shutil
        shutil.copy2(str(t_line), str(legacy_dir / "tiger_outline.png"))
        shutil.copy2(str(t_col), str(legacy_dir / "tiger_color_thumb.png"))

    # 3. Trap 2: Subject #1 for the other 11 volumes (vol_01, vol_03..vol_12)
    print(f"\n[3/3] Generating Subject #1 Pairs for Other 11 Volumes (Back-Cover Grid Completeness)...")
    for vol_id, subj_list in SERIES_SUBJECTS.items():
        if vol_id == "vol_02":
            continue
        code, name = subj_list[0]
        v_dir = REPO_ROOT / f"assets/series_ai/{vol_id}"
        v_dir.mkdir(parents=True, exist_ok=True)
        l_path = v_dir / "subj_01_lineart.png"
        c_path = v_dir / "subj_01_color.png"

        if resume and l_path.exists() and c_path.exists() and l_path.stat().st_size > 5000 and c_path.stat().st_size > 5000:
            print(f"  [Skip Existing] {vol_id} #{code} {name}")
            continue

        print(f"\n  [{vol_id} #01] Generating {name} ({VOL_TITLES[vol_id]})...")
        generate_single_pair(client, model, 1, name, vol_id, v_dir)
        time.sleep(10.0)

    print(f"\n{'='*75}\nPHASE A PILOT GENERATION COMPLETED SUCCESSFULLY!\n{'='*75}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI-First Paired Asset Generator for Copy to Color Series")
    parser.add_argument("--pilot", action="store_true", default=True, help="Run Phase A pilot (vol_02 30 pairs + other 11 subj_01 pairs + cover assets)")
    parser.add_argument("--vol-id", default=None, help="Generate a specific volume (e.g., vol_02)")
    parser.add_argument("--project", default="mpe-core", help="Google Cloud Project ID")
    parser.add_argument("--location", default="global", help="Google Cloud Location")
    parser.add_argument("--model", default="gemini-3.1-flash-lite-image", help="Gemini Image Generation Model")
    parser.add_argument("--batch-size", type=int, default=30, help="Batch size per run (up to 30)")
    parser.add_argument("--no-resume", action="store_true", help="Force regenerate existing assets")
    args = parser.parse_args()

    run_phase_a_pilot(
        project=args.project,
        location=args.location,
        model=args.model,
        resume=(not args.no_resume),
    )

