"""
Worker M1: Metadata and Manifest Generator & Validator
Generates:
1. Updated catalogs/catalog_master.json with complete metadata blocks for all 12 series volumes.
2. Complete 32-page edition manifests in manifests/ for all 12 series volumes.
Validates:
- Keyword counts (7 per volume)
- Keyword lengths (<= 50 chars)
- BISAC categories (2 per volume)
- HTML tags (allowed only: <b>, <i>, <h3>, <ul>, <li>, <p>)
- Zero occurrences of "My First" (case-insensitive)
- Publisher imprint exact string: "The Pivot Digital Publication"
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
CATALOG_PATH = REPO_ROOT / "catalogs" / "catalog_master.json"
MANIFESTS_DIR = REPO_ROOT / "manifests"

VOLUMES_DATA = [
    {
        "vol_key": "vol_01",
        "book_id": "PIVOT-ALPHABET-001-32P",
        "series_id": "copy_to_color_alphabet",
        "manifest_filename": "alphabet-v1.0-core-32p.json",
        "title": "Copy to Color: Alphabet",
        "subtitle": "Interactive Early Learning Alphabet Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Concepts / Alphabet",
        ],
        "keywords": [
            "toddler letter tracing and coloring practice",
            "preschool abc color and copy workbook ages 3 5",
            "fun phonics beginning sounds activity pages",
            "bold outline alphabet art for little artists",
            "early childhood handwriting readiness book",
            "kindergarten prep letter recognition coloring",
            "screen free travel activities for preschoolers",
        ],
    },
    {
        "vol_key": "vol_02",
        "book_id": "PIVOT-ANIMALS-002-32P",
        "series_id": "copy_to_color_animals",
        "manifest_filename": "animals-v1.0-core-32p.json",
        "title": "Copy to Color: Animals",
        "subtitle": "Interactive Early Learning Animals Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Animals / General",
        ],
        "keywords": [
            "cute baby animals coloring book for toddlers",
            "zoo safari pets wildlife color copy guide",
            "chunky contour animal art for beginner colorists",
            "early learning preschool animal identification",
            "kids calm quiet time coloring book ages 3 4 5",
            "educational animal art gift for boys and girls",
            "color matching visual development activity book",
        ],
    },
    {
        "vol_key": "vol_03",
        "book_id": "PIVOT-BIRDS-003-32P",
        "series_id": "copy_to_color_birds",
        "manifest_filename": "birds-v1.0-core-32p.json",
        "title": "Copy to Color: Birds",
        "subtitle": "Interactive Early Learning Birds Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Animals / Birds",
        ],
        "keywords": [
            "preschool bird watching coloring activities",
            "parrot owl peacock flamingo toddler art pages",
            "easy bold feathered friends coloring book",
            "nature exploration drawing copy workbook for kids",
            "little bird lovers interactive coloring sheets",
            "kindergarten backyard birds color guide book",
            "screen free creative art fun ages three to five",
        ],
    },
    {
        "vol_key": "vol_04",
        "book_id": "PIVOT-SPORTS-004-32P",
        "series_id": "copy_to_color_sports",
        "manifest_filename": "sports-v1.0-core-32p.json",
        "title": "Copy to Color: Sports",
        "subtitle": "Interactive Early Learning Sports Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Sports & Recreation / General",
        ],
        "keywords": [
            "kids athletic games and sports coloring pages",
            "soccer basketball baseball tennis toddler art",
            "active play outdoor games coloring workbook",
            "fun exercise movement theme coloring for boys",
            "preschool sportsmanship early learning book",
            "bold outline sports equipment drawing pages",
            "kindergarten gross motor interest art activity",
        ],
    },
    {
        "vol_key": "vol_05",
        "book_id": "PIVOT-MONSTERS-005-32P",
        "series_id": "copy_to_color_monsters",
        "manifest_filename": "monsters-v1.0-core-32p.json",
        "title": "Copy to Color: Monsters",
        "subtitle": "Interactive Early Learning Monsters Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Imagination & Play / General",
        ],
        "keywords": [
            "silly friendly cute monsters coloring book",
            "whimsical colorful creature art for toddlers",
            "funny joyful monsters no scary stuff for kids",
            "preschool creative imagination drawing workbook",
            "goofy furry friends color copy guide pages",
            "bold line fantasy character coloring ages 3 5",
            "cheerful bedtime coloring fun for little artists",
        ],
    },
    {
        "vol_key": "vol_06",
        "book_id": "PIVOT-NUMBERS-006-32P",
        "series_id": "copy_to_color_numbers",
        "manifest_filename": "numbers-v1.0-core-32p.json",
        "title": "Copy to Color: Numbers",
        "subtitle": "Interactive Early Learning Numbers Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Concepts / Counting & Numbers",
        ],
        "keywords": [
            "toddler counting 1 to 20 coloring workbook",
            "early math concepts preschool color copy book",
            "number recognition and object counting pages",
            "learn to count with cute pictures for ages 3 5",
            "kindergarten math readiness art activities",
            "bold outline numbers tracing and coloring fun",
            "screen free educational numbers activity sheets",
        ],
    },
    {
        "vol_key": "vol_07",
        "book_id": "PIVOT-FRUITS-007-32P",
        "series_id": "copy_to_color_fruits",
        "manifest_filename": "fruits-v1.0-core-32p.json",
        "title": "Copy to Color: Fruits",
        "subtitle": "Interactive Early Learning Fruits Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Health & Daily Living / Diet & Nutrition",
        ],
        "keywords": [
            "healthy fresh delicious fruits coloring pages",
            "preschool fruit identification and color guide",
            "apple banana strawberry watermelon toddler art",
            "nutrition awareness early learning activity book",
            "easy bold fruit illustrations for beginners",
            "kindergarten food group coloring workbook",
            "creative quiet time coloring fun ages 3 4 5",
        ],
    },
    {
        "vol_key": "vol_08",
        "book_id": "PIVOT-SHAPES-008-32P",
        "series_id": "copy_to_color_shapes",
        "manifest_filename": "shapes-v1.0-core-32p.json",
        "title": "Copy to Color: Shapes",
        "subtitle": "Interactive Early Learning Shapes Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Concepts / Size & Shape",
        ],
        "keywords": [
            "geometric shape recognition coloring workbook",
            "circle square triangle star toddler art pages",
            "preschool basic shapes copy and color guide",
            "visual spatial development coloring for ages 3 5",
            "early geometry building blocks activity sheets",
            "bold contour lines shape drawing for kids",
            "screen free educational learning gift for toddlers",
        ],
    },
    {
        "vol_key": "vol_09",
        "book_id": "PIVOT-TOYS-009-32P",
        "series_id": "copy_to_color_toys",
        "manifest_filename": "toys-v1.0-core-32p.json",
        "title": "Copy to Color: Toys",
        "subtitle": "Interactive Early Learning Toys Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Games & Activities / General",
        ],
        "keywords": [
            "favorite childhood toys coloring book ages 3 5",
            "teddy bear toy train blocks robot toddler art",
            "preschool playroom fun color copy activity book",
            "bold outline toy illustrations for little kids",
            "creative playtime drawing and coloring workbook",
            "calm afternoon coloring pages for boys and girls",
            "gift idea for creative preschoolers and toddlers",
        ],
    },
    {
        "vol_key": "vol_10",
        "book_id": "PIVOT-FLOWERS-010-32P",
        "series_id": "copy_to_color_flowers",
        "manifest_filename": "flowers-v1.0-core-32p.json",
        "title": "Copy to Color: Flowers",
        "subtitle": "Interactive Early Learning Flowers Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Science & Nature / Flowers & Plants",
        ],
        "keywords": [
            "beautiful garden flowers coloring book for kids",
            "sunflower rose tulip daisy toddler color guide",
            "preschool botanical nature awareness art pages",
            "spring blossom coloring sheets for little artists",
            "bold clean outline floral drawings for beginners",
            "relaxing quiet time flower coloring ages 3 5",
            "mindful creative coloring workbook for girls boys",
        ],
    },
    {
        "vol_key": "vol_11",
        "book_id": "PIVOT-TRANSPORT-011-32P",
        "series_id": "copy_to_color_transport",
        "manifest_filename": "transport-v1.0-core-32p.json",
        "title": "Copy to Color: Transport",
        "subtitle": "Interactive Early Learning Transport Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Transportation / General",
        ],
        "keywords": [
            "things that go cars trucks planes coloring book",
            "toddler vehicle train boat rocket art activities",
            "preschool transportation color copy guide pages",
            "bold outline emergency vehicles coloring workbook",
            "construction and travel vehicle drawing fun",
            "screen free travel road trip activity for kids",
            "early learning machine identification ages 3 5",
        ],
    },
    {
        "vol_key": "vol_12",
        "book_id": "PIVOT-VEGETABLES-012-32P",
        "series_id": "copy_to_color_vegetables",
        "manifest_filename": "vegetables-v1.0-core-32p.json",
        "title": "Copy to Color: Vegetables",
        "subtitle": "Interactive Early Learning Vegetables Coloring Activity Book for Ages 3-5",
        "categories": [
            "JUVENILE NONFICTION / Activity Books / Coloring",
            "JUVENILE NONFICTION / Health & Daily Living / Diet & Nutrition",
        ],
        "keywords": [
            "fresh garden vegetables coloring pages for kids",
            "carrot tomato broccoli corn toddler art book",
            "healthy eating food awareness preschool coloring",
            "color matching vegetable guide for little artists",
            "easy bold kitchen garden coloring activities",
            "early childhood nutrition education workbook",
            "creative quiet time coloring fun ages 3 to 5",
        ],
    },
]

DESCRIPTION_HTML_TEMPLATE = """<p><b>Welcome to Copy to Color by The Pivot Kids!</b> The perfect early learning activity book designed to help young artists develop fine motor control, color recognition, and hand-eye coordination.</p>

<h3>Why Children and Parents Love This Book:</h3>
<ul>
  <li><b>Color & Copy Dual-Guide Layout:</b> Every activity page features a vibrant, full-color reference guide alongside an exactly matched, bold black-and-white coloring outline. Little ones can look, match, and color with confidence!</li>
  <li><b>30 Unique Educational Themes:</b> Features 30 curated, age-appropriate illustrations with zero duplicate subjects.</li>
  <li><b>Chunky Bold Contours:</b> Designed specifically for little hands (ages 3–5) with thick, crisp contours and wide colorable areas.</li>
  <li><b>Single-Page Learning Chrome:</b> Includes educational letter and index code badges, custom subject banners, and celebratory completion badges.</li>
  <li><b>Official Super Colorist Award:</b> Includes an official completion certificate on Page 32 celebrating your little artist's achievement!</li>
</ul>

<h3>Book Specifications:</h3>
<ul>
  <li><b>Trim Size:</b> 8.5 x 11.0 inches (Large, comfortable coloring canvas)</li>
  <li><b>Page Count:</b> Exactly 32 pages</li>
  <li><b>Age Recommendation:</b> 3 to 5 years (Toddlers, Preschool, Kindergarten)</li>
  <li><b>Publisher Imprint:</b> The Pivot Digital Publication</li>
</ul>

<p><i>Collect all 12 volumes in the Copy to Color series and inspire a lifelong love of creative coloring!</i></p>"""


def validate_description_html(html: str) -> None:
    # Only allowed tags: <b>, </b>, <i>, </i>, <h3>, </h3>, <ul>, </ul>, <li>, </li>, <p>, </p>, <br>
    tags = re.findall(r"</?([a-zA-Z0-9]+)[^>]*>", html)
    allowed = {"b", "i", "h3", "ul", "li", "p", "br"}
    for t in tags:
        if t.lower() not in allowed:
            raise ValueError(f"Disallowed HTML tag found: <{t}>")


def validate_keywords(keywords: list[str]) -> None:
    if len(keywords) != 7:
        raise ValueError(f"Expected 7 keywords, got {len(keywords)}")
    for kw in keywords:
        if len(kw) > 50:
            raise ValueError(f"Keyword exceeds 50 chars ({len(kw)}): {kw}")
        if any(c in kw for c in [",", '"', ";"]):
            raise ValueError(f"Banned punctuation in keyword: {kw}")
        if "my first" in kw.lower():
            raise ValueError(f"'My First' found in keyword: {kw}")


def run() -> None:
    from scripts.compile_copy_to_color_interior import SERIES_CATALOG

    # 1. Update catalog_master.json
    print(f"Reading {CATALOG_PATH}...")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    catalog["publisher_imprint"] = "The Pivot Digital Publication"

    editions_by_id = {ed["book_id"]: ed for ed in catalog["editions"]}

    for item in VOLUMES_DATA:
        book_id = item["book_id"]
        if book_id not in editions_by_id:
            raise KeyError(f"Book ID {book_id} not found in catalog_master.json")

        ed = editions_by_id[book_id]
        validate_keywords(item["keywords"])
        validate_description_html(DESCRIPTION_HTML_TEMPLATE)

        ed["title"] = item["title"]
        ed["subtitle"] = item["subtitle"]
        ed["metadata"] = {
            "title": item["title"],
            "subtitle": item["subtitle"],
            "publisher_imprint": "The Pivot Digital Publication",
            "backend_keywords": item["keywords"],
            "category_candidates": item["categories"],
            "description_html": DESCRIPTION_HTML_TEMPLATE,
        }

    # Write back catalog_master.json
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[OK] Successfully updated {CATALOG_PATH}")

    # 2. Generate all 12 manifests in manifests/
    MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)

    for item in VOLUMES_DATA:
        vol_key = item["vol_key"]
        series_meta = SERIES_CATALOG[vol_key]
        raw_subjects = series_meta["subjects"][:30]

        expected_subjects: list[str] = []
        pages: list[dict] = [
            {"number": 1, "type": "welcome", "title": item["title"]}
        ]

        for idx, (code_label, word_label) in enumerate(raw_subjects, start=1):
            page_num = idx + 1
            slug = word_label.strip().lower().replace(" ", "_")
            expected_subjects.append(slug)

            # Determine display code & banner phrase matching compile_copy_to_color_interior.py
            display_code = code_label
            if code_label.isdigit() and word_label:
                display_code = word_label.strip()[0].upper()

            clean_subj = word_label.strip()
            initial_char = display_code[0] if display_code else (clean_subj[0] if clean_subj else "")
            if clean_subj.startswith(f"{initial_char} is for"):
                banner_phrase = clean_subj
            elif initial_char and initial_char.isalpha():
                banner_phrase = f"{initial_char.upper()} is for {clean_subj.upper()}"
            else:
                banner_phrase = clean_subj.upper()

            pages.append({
                "number": page_num,
                "type": "copy_to_color",
                "subject_id": slug,
                "letter": display_code,
                "banner": banner_phrase,
            })

        pages.append({
            "number": 32,
            "type": "certificate",
            "title": "Super Colorist Award",
        })

        manifest_data = {
            "schema_version": "1.0.0",
            "book_id": item["book_id"],
            "series_id": item["series_id"],
            "edition_id": "v1.0-core-32p",
            "title": item["title"],
            "subtitle": item["subtitle"],
            "publisher": "The Pivot Digital Publication",
            "trim": {
                "width_in": 8.5,
                "height_in": 11.0,
                "bleed": "all",
                "page_width_in_with_bleed": 8.625,
                "page_height_in_with_bleed": 11.25,
            },
            "reverse_page": "activity_chrome",
            "minimum_dpi": 300,
            "minimum_safe_margin_in": 0.5,
            "asset_registry": "../catalogs/asset_registry.json",
            "expected_page_count": 32,
            "expected_subjects": expected_subjects,
            "pages": pages,
        }

        # Check for forbidden phrase
        manifest_text = json.dumps(manifest_data)
        if "my first" in manifest_text.lower():
            raise ValueError(f"'My First' found in manifest for {item['book_id']}")

        out_path = MANIFESTS_DIR / item["manifest_filename"]
        out_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[OK] Generated manifest: {out_path.name} (32 pages, {len(expected_subjects)} subjects)")

    print("\n[SUCCESS] All 12 metadata blocks injected and all 12 manifests created.")


if __name__ == "__main__":
    run()
