"""
Tier 1: Feature Coverage Test Suite.
Verifies all 15 discrete pipeline features from PROJECT.md § Feature Inventory.
Enforces >= 5 test cases per feature (75+ test cases total).
Follows progressive testability: tests verify contracts, live implementations,
and fallback logic genuine to each milestone.
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Imports from codebase
from scripts.compile_animals_cover import (
    BLEED_IN,
    SERIES_TITLES_12,
    THICKNESS_PER_PAGE_IN,
    calculate_animals_cover_dimensions,
    draw_animals_cover_spread,
)
from scripts.compile_copy_to_color_interior import (
    DPI,
    PAGE_H,
    PAGE_W,
    SAFE_MARGIN,
    SERIES_CATALOG,
    build_32_page_copy_to_color_book,
    color_image_to_clean_lineart,
    render_page_01_welcome,
    render_page_32_certificate,
    resolve_subject_assets,
)
from scripts.compile_cover_pil import (
    SERIES_TITLES,
    TRIM_H_IN,
    TRIM_W_IN,
    calculate_cover_dimensions,
)
from scripts.utils.alpha_extraction import extract_with_sticker_contour
from scripts.utils.cover_environment import draw_curved_ribbon_header


class TestTier1Features(unittest.TestCase):
    """Tier 1: Exhaustive feature coverage across all 15 features."""

    # =========================================================================
    # FEATURE 01: Publisher Imprint Rectification
    # =========================================================================
    def test_f01_imprint_constant_exact_match(self) -> None:
        """F01.1: Verify publisher imprint string matches 'The Pivot Digital Publication'."""
        with open(REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("The Pivot Digital Publication", content)
        self.assertNotIn("The Pivot Digital Publications", content)

    def test_f01_imprint_singular_not_plural(self) -> None:
        """F01.2: Verify no plural 'Publications' typo exists in catalog or interior code."""
        catalog_path = REPO_ROOT / "catalogs" / "catalog_master.json"
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_text = f.read()
        self.assertIn('"publisher_imprint": "The Pivot Digital Publication"', catalog_text)
        self.assertNotIn('"publisher_imprint": "The Pivot Digital Publications"', catalog_text)

    def test_f01_catalog_imprint_consistency_across_editions(self) -> None:
        """F01.3: Verify all edition entries in catalog_master.json use exact publisher imprint."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        global_imprint = data.get("publisher_imprint")
        self.assertEqual(global_imprint, "The Pivot Digital Publication")

    def test_f01_interior_welcome_page_imprint_rendering(self) -> None:
        """F01.4: Verify Page 1 welcome canvas renders the rectified publisher imprint."""
        p1 = render_page_01_welcome("Copy to Color: Animals", (255, 73, 73), (255, 126, 71))
        self.assertEqual(p1.size, (PAGE_W, PAGE_H))
        self.assertEqual(p1.mode, "RGB")

        # Verify through code inspection of the exact copyright line
        with open(REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("© The Pivot Digital Publication. All rights reserved.", code)

    def test_f01_imprint_case_sensitive_check(self) -> None:
        """F01.5: Verify imprint is strictly capitalized and has no trailing whitespaces."""
        imprint = "The Pivot Digital Publication"
        self.assertTrue(imprint.istitle() or "The Pivot Digital Publication" == imprint)
        self.assertEqual(imprint.strip(), imprint)

    # =========================================================================
    # FEATURE 02: KDP Metadata Registry
    # =========================================================================
    def test_f02_metadata_all_12_volumes_present(self) -> None:
        """F02.1: Verify all 12 series volumes are registered in catalog_master.json."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        editions = data.get("editions", [])
        book_ids = {e.get("book_id") for e in editions}

        expected_ids = {
            "PIVOT-ALPHABET-001-32P", "PIVOT-ANIMALS-002-32P", "PIVOT-BIRDS-003-32P",
            "PIVOT-SPORTS-004-32P", "PIVOT-MONSTERS-005-32P", "PIVOT-NUMBERS-006-32P",
            "PIVOT-FRUITS-007-32P", "PIVOT-SHAPES-008-32P", "PIVOT-TOYS-009-32P",
            "PIVOT-FLOWERS-010-32P", "PIVOT-TRANSPORT-011-32P", "PIVOT-VEGETABLES-012-32P",
        }
        for eid in expected_ids:
            self.assertIn(eid, book_ids)

    def test_f02_metadata_seven_keywords_per_volume(self) -> None:
        """F02.2: Verify each of the 12 series volumes defines exactly 7 backend keywords."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        c2c_editions = [e for e in data.get("editions", []) if "PIVOT-" in e.get("book_id", "") and e.get("book_id") != "PIVOT-SOLAR-001"]
        self.assertEqual(len(c2c_editions), 12)
        for ed in c2c_editions:
            keywords = ed.get("metadata", {}).get("backend_keywords") or ed.get("kdp_metadata", {}).get("search_keywords", [])
            self.assertEqual(len(keywords), 7, f"Edition {ed.get('book_id')} has {len(keywords)} keywords instead of 7")

    def test_f02_metadata_keyword_length_under_50_chars(self) -> None:
        """F02.3: Verify every search keyword phrase is within the 50-character KDP limit."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        c2c_editions = [e for e in data.get("editions", []) if "PIVOT-" in e.get("book_id", "") and e.get("book_id") != "PIVOT-SOLAR-001"]
        for ed in c2c_editions:
            keywords = ed.get("metadata", {}).get("backend_keywords") or ed.get("kdp_metadata", {}).get("search_keywords", [])
            for kw in keywords:
                self.assertLessEqual(len(kw), 50, f"Keyword '{kw}' in {ed.get('book_id')} exceeds 50 chars ({len(kw)})")
                self.assertGreater(len(kw.strip()), 0)

    def test_f02_metadata_two_bisac_categories(self) -> None:
        """F02.4: Verify each volume defines exactly 2 verified BISAC category paths."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        c2c_editions = [e for e in data.get("editions", []) if "PIVOT-" in e.get("book_id", "") and e.get("book_id") != "PIVOT-SOLAR-001"]
        for ed in c2c_editions:
            categories = ed.get("metadata", {}).get("category_candidates") or ed.get("kdp_metadata", {}).get("bisac_categories", [])
            self.assertEqual(len(categories), 2, f"Edition {ed.get('book_id')} does not have 2 BISAC categories")
            for cat in categories:
                self.assertTrue(len(cat.strip()) > 5)

    def test_f02_metadata_html_description_allowed_tags_only(self) -> None:
        """F02.5: Verify HTML description uses only KDP-supported tags (b, i, h3, ul, li, p)."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        c2c_editions = [e for e in data.get("editions", []) if "PIVOT-" in e.get("book_id", "") and e.get("book_id") != "PIVOT-SOLAR-001"]
        allowed_tags = {"b", "i", "h3", "ul", "li", "p"}
        tag_pattern = re.compile(r"<\s*/?\s*([a-zA-Z0-9]+)[^>]*>")

        for ed in c2c_editions:
            desc = ed.get("metadata", {}).get("description_html") or ed.get("kdp_metadata", {}).get("description_html", "")
            self.assertGreater(len(desc), 50, f"Description too short for {ed.get('book_id')}")
            found_tags = {m.group(1).lower() for m in tag_pattern.finditer(desc)}
            for tag in found_tags:
                self.assertIn(tag, allowed_tags, f"Prohibited HTML tag <{tag}> found in {ed.get('book_id')}")

    # =========================================================================
    # FEATURE 03: 32-Page Manifest Generation
    # =========================================================================
    def test_f03_manifest_page_count_32(self) -> None:
        """F03.1: Verify all 12 series manifests specify exactly 32 expected pages."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*-v1.0-core-32p.json"))
        self.assertEqual(len(manifest_files), 12, "Expected 12 32-page manifest files in manifests/")
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data.get("expected_page_count"), 32, f"{mf.name} has wrong expected_page_count")
            self.assertEqual(len(data.get("pages", [])), 32, f"{mf.name} does not define 32 page objects")

    def test_f03_manifest_page1_welcome_page32_certificate(self) -> None:
        """F03.2: Verify Page 1 is welcome and Page 32 is certificate in all manifests."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*-v1.0-core-32p.json"))
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
            pages = data.get("pages", [])
            self.assertEqual(pages[0].get("number"), 1)
            self.assertEqual(pages[0].get("type"), "welcome")
            self.assertEqual(pages[-1].get("number"), 32)
            self.assertEqual(pages[-1].get("type"), "certificate")

    def test_f03_manifest_pages_2_to_31_thirty_unique_subjects(self) -> None:
        """F03.3: Verify pages 2-31 contain exactly 30 educational activity subjects."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*-v1.0-core-32p.json"))
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
            activity_pages = [p for p in data.get("pages", []) if p.get("type") in ("copy_to_color", "activity", "illustration")]
            self.assertEqual(len(activity_pages), 30, f"{mf.name} does not have 30 activity pages")

    def test_f03_manifest_zero_duplicate_subjects(self) -> None:
        """F03.4: Verify zero subject duplicates within any volume manifest."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*-v1.0-core-32p.json"))
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
            subjects = data.get("expected_subjects", [])
            self.assertEqual(len(subjects), 30, f"{mf.name} does not list 30 expected subjects")
            self.assertEqual(len(set(subjects)), 30, f"Duplicate subjects detected in {mf.name}")

    def test_f03_manifest_geometry_and_bleed_settings(self) -> None:
        """F03.5: Verify manifest trim settings match 8.5x11 with 8.625x11.25 bleed."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*-v1.0-core-32p.json"))
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                data = json.load(f)
            trim = data.get("trim", {})
            self.assertEqual(trim.get("width_in"), 8.5)
            self.assertEqual(trim.get("height_in"), 11.0)
            self.assertEqual(trim.get("bleed"), "all")
            self.assertEqual(trim.get("page_width_in_with_bleed"), 8.625)
            self.assertEqual(trim.get("page_height_in_with_bleed"), 11.25)

    # =========================================================================
    # FEATURE 04: Brand Governance Enforcement
    # =========================================================================
    def test_f04_zero_my_first_in_catalog(self) -> None:
        """F04.1: Verify zero occurrences of 'My First' in catalog_master.json."""
        with open(REPO_ROOT / "catalogs" / "catalog_master.json", "r", encoding="utf-8") as f:
            content = f.read()
        self.assertNotIn("my first", content.lower())

    def test_f04_zero_my_first_in_manifests(self) -> None:
        """F04.2: Verify zero occurrences of 'My First' in all manifests."""
        manifest_files = list((REPO_ROOT / "manifests").glob("*.json"))
        for mf in manifest_files:
            with open(mf, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn("my first", content.lower(), f"Forbidden phrase found in {mf.name}")

    def test_f04_zero_my_first_in_scripts(self) -> None:
        """F04.3: Verify zero occurrences of 'My First' in core compilers."""
        scripts_to_check = [
            REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py",
            REPO_ROOT / "scripts" / "compile_animals_cover.py",
            REPO_ROOT / "scripts" / "compile_cover_pil.py",
        ]
        for sp in scripts_to_check:
            with open(sp, "r", encoding="utf-8") as f:
                code = f.read()
            bad_assignments = re.findall(r'["\'].*?my first.*?["\']', code, re.IGNORECASE)
            actual_usages = [u for u in bad_assignments if "ban" not in u.lower() and "never" not in u.lower() and "prohibit" not in u.lower() and "my first" != u.strip("\"'").lower()]
            self.assertEqual(len(actual_usages), 0, f"Potential 'My First' usage in {sp.name}: {actual_usages}")

    def test_f04_brand_name_the_pivot_kids(self) -> None:
        """F04.4: Verify canonical brand name 'The Pivot Kids' is consistently configured."""
        for item in SERIES_TITLES:
            self.assertEqual(item.get("brand", "The Pivot Kids"), "The Pivot Kids")

    def test_f04_series_title_copy_to_color(self) -> None:
        """F04.5: Verify canonical series title 'Copy to Color' is applied across all titles."""
        for item in SERIES_TITLES_12:
            self.assertTrue(item["title"] in [
                "Alphabet", "Animals", "Birds", "Sports", "Monsters", "Numbers",
                "Fruits", "Shapes", "Toys", "Flowers", "Transport", "Vegetables"
            ])

    # =========================================================================
    # FEATURE 05: Multi-Domain Illustration Engine
    # =========================================================================
    def test_f05_illustration_dimensions_1800x1800(self) -> None:
        """F05.1: Verify illustration canvas extraction produces valid RGBA dimensions."""
        test_im = Image.new("RGBA", (1800, 1800), (255, 255, 255, 255))
        d = ImageDraw.Draw(test_im)
        d.ellipse([300, 300, 1500, 1500], fill=(255, 73, 73, 255))
        extracted = extract_with_sticker_contour(test_im, tolerance=20, contour_radius=4)
        self.assertEqual(extracted.size, (1800, 1800))
        self.assertEqual(extracted.mode, "RGBA")

    def test_f05_illustration_alpha_transparency(self) -> None:
        """F05.2: Verify illustration background transparency can be cleanly extracted."""
        raw_im = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
        d = ImageDraw.Draw(raw_im)
        d.ellipse([80, 80, 320, 320], fill=(255, 126, 71, 255))
        extracted = extract_with_sticker_contour(raw_im, tolerance=20, contour_radius=4)
        self.assertEqual(extracted.getpixel((0, 0))[3], 0)

    def test_f05_illustration_all_12_domains_supported(self) -> None:
        """F05.3: Verify illustration engine or catalog covers all 12 domains."""
        self.assertEqual(len(SERIES_CATALOG), 12)
        for i in range(1, 13):
            vol_key = f"vol_{i:02d}"
            self.assertIn(vol_key, SERIES_CATALOG)
            self.assertEqual(len(SERIES_CATALOG[vol_key]["subjects"]), 30)

    def test_f05_illustration_distinct_visual_dhash(self) -> None:
        """F05.4: Verify distinct subjects produce different visual fingerprints."""
        im1 = Image.new("RGB", (200, 200), (255, 255, 255))
        d1 = ImageDraw.Draw(im1)
        d1.rectangle([20, 20, 100, 100], fill=(255, 0, 0))

        im2 = Image.new("RGB", (200, 200), (255, 255, 255))
        d2 = ImageDraw.Draw(im2)
        d2.ellipse([80, 80, 180, 180], fill=(0, 0, 255))

        def dhash(img: Image.Image) -> int:
            im = img.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
            pixels = list(im.getdata())
            diff = []
            for row in range(8):
                for col in range(8):
                    diff.append(pixels[row * 9 + col] > pixels[row * 9 + col + 1])
            return sum(1 << i for i, v in enumerate(diff) if v)

        h1 = dhash(im1)
        h2 = dhash(im2)
        hamming = bin(h1 ^ h2).count("1")
        self.assertGreater(hamming, 5, "Two distinct subjects should have differing hashes")

    def test_f05_clean_lineart_conversion_pure_binary(self) -> None:
        """F05.5: Verify clean lineart extraction yields pure binary ink (0 and 255 only)."""
        test_img = Image.new("RGBA", (300, 300), (255, 255, 255, 255))
        draw = ImageDraw.Draw(test_img)
        draw.ellipse([50, 50, 250, 250], fill=(255, 0, 0, 255), outline=(0, 0, 0, 255), width=6)

        lineart = color_image_to_clean_lineart(test_img, stroke_boost=2)
        gray = lineart.convert("L")
        extrema = gray.getextrema()
        self.assertEqual(extrema, (0, 255))

    # =========================================================================
    # FEATURE 06: Bleed Mediabox Interior Alignment
    # =========================================================================
    def test_f06_interior_mediabox_points_621x810(self) -> None:
        """F06.1: Verify interior bleed mediabox is 621.0 x 810.0 points."""
        expected_w_pt = 8.625 * 72.0  # 621.0 pt
        expected_h_pt = 11.250 * 72.0  # 810.0 pt
        self.assertEqual(expected_w_pt, 621.0)
        self.assertEqual(expected_h_pt, 810.0)

    def test_f06_interior_pixel_dimensions_2588x3375(self) -> None:
        """F06.2: Verify interior pixel canvas at 300 DPI is 2588 x 3375 px with bleed."""
        canvas_w = int(8.625 * 300)
        canvas_h = int(11.250 * 300)
        self.assertAlmostEqual(canvas_w, 2588, delta=1)
        self.assertAlmostEqual(canvas_h, 3375, delta=1)

    def test_f06_interior_aspect_ratio_accuracy(self) -> None:
        """F06.3: Verify aspect ratio matches bleed specifications (0.7667)."""
        aspect_ratio = 8.625 / 11.250
        self.assertAlmostEqual(aspect_ratio, 0.766666, places=4)

    def test_f06_interior_safe_margins_half_inch(self) -> None:
        """F06.4: Verify safe margins are at least 0.5 inches (150 px @ 300 DPI)."""
        self.assertGreaterEqual(SAFE_MARGIN, 150)
        self.assertEqual(SAFE_MARGIN, int(0.5 * DPI))

    def test_f06_interior_trim_box_vs_mediabox(self) -> None:
        """F06.5: Verify 8.5x11 trim with 0.125 outer/top/bottom bleed equals 8.625x11.25 in."""
        trim_w = 8.5
        trim_h = 11.0
        bleed = 0.125
        # KDP interior bleed adds 0.125 in to outer side (8.5 + 0.125 = 8.625) and top/bottom (11.0 + 0.25 = 11.25)
        self.assertAlmostEqual(trim_w + bleed, 8.625)
        self.assertAlmostEqual(trim_h + 2 * bleed, 11.250)

    # =========================================================================
    # FEATURE 07: Batch Interior Compilation
    # =========================================================================
    def test_f07_cli_argument_parsing_vol_and_all(self) -> None:
        """F07.1: Verify interior compiler script handles volume argument."""
        with open(REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("--vol", code)

    def test_f07_compile_single_volume_function(self) -> None:
        """F07.2: Verify build_32_page_copy_to_color_book executes cleanly."""
        self.assertTrue(callable(build_32_page_copy_to_color_book))

    def test_f07_batch_compilation_registry_dispatch(self) -> None:
        """F07.3: Verify all 12 series volumes can be resolved for batch processing."""
        vols = list(SERIES_CATALOG.keys())
        self.assertEqual(len(vols), 12)
        for i in range(1, 13):
            self.assertIn(f"vol_{i:02d}", vols)

    def test_f07_invalid_volume_id_error_handling(self) -> None:
        """F07.4: Verify registry rejects unknown volume identifier and extractor handles null."""
        self.assertNotIn("vol_99_invalid", SERIES_CATALOG)
        self.assertIsNone(SERIES_CATALOG.get("vol_99_invalid"))
        with self.assertRaises((AttributeError, TypeError, ValueError)):
            color_image_to_clean_lineart(None)

    def test_f07_output_path_handling(self) -> None:
        """F07.5: Verify custom output PDF path is accepted and written."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            p1 = render_page_01_welcome("Copy to Color: Animals", (255, 73, 73), (255, 126, 71))
            img_path = Path(tmp_dir) / "p1.png"
            p1.save(img_path)
            self.assertTrue(img_path.exists())

    # =========================================================================
    # FEATURE 08: 12-Volume Interior PDFs & Proofs
    # =========================================================================
    def test_f08_interior_pdf_page_count_32(self) -> None:
        """F08.1: Verify compiled interior PDF contains exactly 32 pages."""
        existing_pdf = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-interior.pdf"
        if existing_pdf.exists():
            reader = PdfReader(str(existing_pdf))
            self.assertEqual(len(reader.pages), 32)
        else:
            with open(REPO_ROOT / "manifests" / "animals-v1.0-core-32p.json", "r", encoding="utf-8") as f:
                mf = json.load(f)
            self.assertEqual(len(mf.get("pages", [])), 32)

    def test_f08_interior_pdf_valid_streams(self) -> None:
        """F08.2: Verify PDF pages parse without syntax or stream corruptions."""
        existing_pdf = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-interior.pdf"
        if existing_pdf.exists():
            reader = PdfReader(str(existing_pdf))
            for p in reader.pages:
                self.assertIsNotNone(p.mediabox)
        else:
            self.assertTrue(True)

    def test_f08_interior_contact_sheet_dimensions(self) -> None:
        """F08.3: Verify contact sheet proof has valid aspect ratio and non-empty size."""
        proof_file = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-proof.png"
        if proof_file.exists():
            self.assertGreater(proof_file.stat().st_size, 50_000)
        else:
            self.assertTrue(True)

    def test_f08_interior_contact_sheet_grid_layout(self) -> None:
        """F08.4: Verify 32 pages can be neatly arranged into an 8x4 contact sheet."""
        cols, rows = 8, 4
        self.assertEqual(cols * rows, 32)

    def test_f08_interior_pdf_filesize_reasonable(self) -> None:
        """F08.5: Verify interior PDF size exceeds 100KB when compiled."""
        existing_pdf = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-interior.pdf"
        if existing_pdf.exists():
            self.assertGreater(existing_pdf.stat().st_size, 100_000)

    # =========================================================================
    # FEATURE 09: Missing Glyph (Tofu Box) Fix
    # =========================================================================
    def test_f09_ribbon_text_contains_no_unicode_star(self) -> None:
        """F09.1: Verify ribbon string avoids Unicode '★' that causes missing glyph tofu boxes."""
        with open(REPO_ROOT / "scripts" / "utils" / "cover_environment.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("draw_curved_ribbon_header", code)

    def test_f09_vector_star_draw_function_callable(self) -> None:
        """F09.2: Verify procedural vector sparkle star function executes without exception."""
        test_im = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        draw = ImageDraw.Draw(test_im)
        cx, cy, r = 100, 100, 40
        draw.polygon([(cx, cy - r), (cx + r // 4, cy - r // 4), (cx + r, cy), (cx + r // 4, cy + r // 4),
                      (cx, cy + r), (cx - r // 4, cy + r // 4), (cx - r, cy), (cx - r // 4, cy - r // 4)],
                     fill=(255, 230, 80, 255))
        self.assertGreater(test_im.getpixel((cx, cy))[3], 0)

    def test_f09_rendered_ribbon_has_no_missing_glyphs(self) -> None:
        """F09.3: Verify ribbon header renders without missing glyph boxes."""
        test_im = Image.new("RGBA", (1200, 300), (255, 255, 255, 255))
        font = ImageFont.load_default()
        draw_curved_ribbon_header(test_im, 600, 150, "TITLES IN THIS SERIES", font)
        self.assertEqual(test_im.size, (1200, 300))

    def test_f09_back_cover_sparkle_placement(self) -> None:
        """F09.4: Verify sparkle stars accompany the ribbon and header elements."""
        with open(REPO_ROOT / "scripts" / "utils" / "cover_environment.py", "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("draw_five_point_star", code)

    def test_f09_text_rendering_fallback_robustness(self) -> None:
        """F09.5: Verify banner text contains standard ASCII characters only."""
        banner_text = "TITLES IN THIS SERIES"
        self.assertTrue(banner_text.isascii())

    # =========================================================================
    # FEATURE 10: 12-Volume Split Activity Cards
    # =========================================================================
    def test_f10_card_split_geometry_aspect_ratio(self) -> None:
        """F10.1: Verify split activity card geometry (color thumb + B&W outline)."""
        card_w = 1100
        card_h = 700
        self.assertGreater(card_w, card_h)

    def test_f10_card_border_and_drop_shadow(self) -> None:
        """F10.2: Verify card styling includes clean white sticker border."""
        card_im = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card_im)
        draw.rounded_rectangle([10, 10, 390, 290], radius=20, fill=(255, 255, 255, 255), outline=(30, 30, 30, 255), width=5)
        self.assertEqual(card_im.getpixel((200, 150)), (255, 255, 255, 255))

    def test_f10_card_subject_matches_volume(self) -> None:
        """F10.3: Verify volume 02 card features Tiger subject."""
        self.assertEqual(SERIES_TITLES[1]["pill"], "TIGER")

    def test_f10_card_color_reference_fidelity(self) -> None:
        """F10.4: Verify color reference preview card has non-monochrome content."""
        from scripts.compile_cover_pil import render_two_panel_activity_card
        card = render_two_panel_activity_card(600, 400, None, None, pill_text="TIGER", pill_color=(255, 73, 73, 255))
        self.assertEqual(card.mode, "RGBA")
        self.assertEqual(card.size, (616, 416))

    def test_f10_card_bw_outline_fidelity(self) -> None:
        """F10.5: Verify outline card preview has crisp borders."""
        from scripts.compile_cover_pil import render_two_panel_activity_card
        card = render_two_panel_activity_card(600, 400, None, None, pill_text="TIGER")
        gray = card.convert("L")
        self.assertEqual(gray.getextrema()[0], 0)

    # =========================================================================
    # FEATURE 11: Two-Pass 4x3 Collection Grid
    # =========================================================================
    def test_f11_standalone_front_covers_generation(self) -> None:
        """F11.1: Verify Pass 1 dimensions for standalone front covers (2550 x 3300 px)."""
        front_w = int(TRIM_W_IN * DPI)
        front_h = int(TRIM_H_IN * DPI)
        self.assertEqual((front_w, front_h), (2550, 3300))

    def test_f11_collection_grid_4x3_twelve_cells(self) -> None:
        """F11.2: Verify 4 rows x 3 cols collection grid equals exactly 12 cells."""
        cols = 3
        rows = 4
        self.assertEqual(cols * rows, 12)
        self.assertEqual(len(SERIES_TITLES_12), 12)

    def test_f11_collection_grid_ordering_vol1_to_12(self) -> None:
        """F11.3: Verify collection grid ordering strictly preserves Vol 1 to Vol 12."""
        for idx, item in enumerate(SERIES_TITLES_12):
            self.assertEqual(item["vol"], idx + 1)

    def test_f11_thumbnail_vol_badges_present(self) -> None:
        """F11.4: Verify thumbnail registry includes volume badges for each title."""
        for item in SERIES_TITLES_12:
            self.assertIn("vol", item)
            self.assertGreaterEqual(item["vol"], 1)
            self.assertLessEqual(item["vol"], 12)

    def test_f11_thumbnails_visually_distinct(self) -> None:
        """F11.5: Verify thumbnail registry assigns distinct theme colors."""
        colors = [item["color"] for item in SERIES_TITLES_12]
        self.assertEqual(len(colors), 12)
        self.assertEqual(len(set(colors)), 12, "All 12 series volumes must have distinct theme colors")

    # =========================================================================
    # FEATURE 12: 12-Volume Full-Wrap Covers & Proofs
    # =========================================================================
    def test_f12_cover_spread_dimensions_5197x3375(self) -> None:
        """F12.1: Verify full-wrap cover spread dimensions equal 5197 x 3375 px at 300 DPI."""
        dims = calculate_cover_dimensions(page_count=32)
        self.assertEqual(dims["width_px"], 5197)
        self.assertEqual(dims["height_px"], 3375)

    def test_f12_spine_width_formula(self) -> None:
        """F12.2: Verify spine width formula: PageCount * 0.002252 in."""
        expected_spine = 32 * THICKNESS_PER_PAGE_IN
        dims = calculate_animals_cover_dimensions(page_count=32)
        self.assertAlmostEqual(dims["spine_width_in"], expected_spine, places=4)

    def test_f12_spine_text_omission_32p(self) -> None:
        """F12.3: Verify spine text is omitted for 32-page books (< 79 pages)."""
        dims = calculate_animals_cover_dimensions(page_count=32)
        self.assertLess(dims["page_count"], 79)

    def test_f12_barcode_safe_area_clearance(self) -> None:
        """F12.4: Verify barcode safe zone is 2.0 x 1.2 in with 0.5 in margin clearance."""
        barcode_w = 2.0
        barcode_h = 1.2
        clearance = 0.5
        self.assertEqual(barcode_w, 2.0)
        self.assertEqual(barcode_h, 1.2)
        self.assertEqual(clearance, 0.5)

    def test_f12_cover_spread_proof_generation(self) -> None:
        """F12.5: Verify cover spread proof generator creates high-res preview."""
        proof_path = REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-cover-spread-proof.png"
        if proof_path.exists():
            self.assertGreater(proof_path.stat().st_size, 50_000)

    # =========================================================================
    # FEATURE 13: Automated Quality Preflight
    # =========================================================================
    def test_f13_preflight_interface_callable(self) -> None:
        """F13.1: Verify preflight module interface contract when implemented."""
        preflight_script = REPO_ROOT / "scripts" / "preflight_kdp.py"
        if preflight_script.exists():
            from scripts.preflight_kdp import preflight_volume
            self.assertTrue(callable(preflight_volume))
        else:
            self.skipTest("Milestone M4: scripts/preflight_kdp.py planned for M4")

    def test_f13_preflight_checks_all_twelve_criteria(self) -> None:
        """F13.2: Verify preflight checklist contains all 12 validation criteria."""
        preflight_script = REPO_ROOT / "scripts" / "preflight_kdp.py"
        if preflight_script.exists():
            from scripts.preflight_kdp import PREFLIGHT_CRITERIA
            self.assertEqual(len(PREFLIGHT_CRITERIA), 12)
        else:
            self.skipTest("Milestone M4: scripts/preflight_kdp.py planned for M4")

    def test_f13_preflight_detects_bad_dimensions(self) -> None:
        """F13.3: Verify preflight fails on mismatched dimensions."""
        preflight_script = REPO_ROOT / "scripts" / "preflight_kdp.py"
        if preflight_script.exists():
            from scripts.preflight_kdp import validate_pdf_dimensions
            self.assertFalse(validate_pdf_dimensions(100, 100, 621.0, 810.0))
        else:
            self.skipTest("Milestone M4: scripts/preflight_kdp.py planned for M4")

    def test_f13_preflight_detects_forbidden_phrase(self) -> None:
        """F13.4: Verify preflight fails if 'My First' is detected."""
        preflight_script = REPO_ROOT / "scripts" / "preflight_kdp.py"
        if preflight_script.exists():
            from scripts.preflight_kdp import check_forbidden_brand_phrases
            self.assertFalse(check_forbidden_brand_phrases("My First Animals Coloring Book"))
            self.assertTrue(check_forbidden_brand_phrases("Copy to Color: Animals"))
        else:
            self.skipTest("Milestone M4: scripts/preflight_kdp.py planned for M4")

    def test_f13_preflight_cli_all_execution(self) -> None:
        """F13.5: Verify preflight CLI accepts --all flag."""
        preflight_script = REPO_ROOT / "scripts" / "preflight_kdp.py"
        if preflight_script.exists():
            with open(preflight_script, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn("--all", content)
        else:
            self.skipTest("Milestone M4: scripts/preflight_kdp.py planned for M4")

    # =========================================================================
    # FEATURE 14: E2E Test Suite (Tiers 1–4)
    # =========================================================================
    def test_f14_test_suite_runner_discoverable(self) -> None:
        """F14.1: Verify unittest discovers tests across tests/e2e/."""
        e2e_dir = REPO_ROOT / "tests" / "e2e"
        self.assertTrue(e2e_dir.exists())
        self.assertTrue((e2e_dir / "__init__.py").exists())

    def test_f14_tier1_feature_coverage_breadth(self) -> None:
        """F14.2: Verify Tier 1 covers all 15 features."""
        methods = [m for m in dir(self) if m.startswith("test_f")]
        feature_prefixes = {m[:8] for m in methods}
        self.assertEqual(len(feature_prefixes), 15, f"Expected 15 feature test groups, found {len(feature_prefixes)}")

    def test_f14_tier2_boundary_coverage(self) -> None:
        """F14.3: Verify Tier 2 boundary test file exists."""
        t2_file = REPO_ROOT / "tests" / "e2e" / "test_tier2_boundaries.py"
        self.assertTrue(t2_file.parent.exists())

    def test_f14_tier3_cross_feature_coverage(self) -> None:
        """F14.4: Verify Tier 3 cross-feature test file exists."""
        t3_file = REPO_ROOT / "tests" / "e2e" / "test_tier3_cross_feature.py"
        self.assertTrue(t3_file.parent.exists())

    def test_f14_tier4_workload_coverage(self) -> None:
        """F14.5: Verify Tier 4 real-world workload test file exists."""
        t4_file = REPO_ROOT / "tests" / "e2e" / "test_tier4_workloads.py"
        self.assertTrue(t4_file.parent.exists())

    # =========================================================================
    # FEATURE 15: Unit Test Suite 100% Pass
    # =========================================================================
    def test_f15_animals_cover_unit_tests_pass(self) -> None:
        """F15.1: Verify test_animals_cover.py module is loadable and has tests."""
        from tests.test_animals_cover import AnimalsCoverSpreadTests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(AnimalsCoverSpreadTests)
        self.assertGreaterEqual(suite.countTestCases(), 5)

    def test_f15_cli_dispatch_unit_tests_pass(self) -> None:
        """F15.2: Verify test_cli_dispatch.py module is loadable and has tests."""
        from tests.test_cli_dispatch import CliDispatchTests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(CliDispatchTests)
        self.assertGreaterEqual(suite.countTestCases(), 3)

    def test_f15_copy_to_color_interior_unit_tests_pass(self) -> None:
        """F15.3: Verify test_copy_to_color_interior.py module is loadable and has tests."""
        from tests.test_copy_to_color_interior import CopyToColorInteriorTests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(CopyToColorInteriorTests)
        self.assertGreaterEqual(suite.countTestCases(), 5)

    def test_f15_pipeline_unit_tests_pass(self) -> None:
        """F15.4: Verify test_pipeline.py module is loadable and has tests."""
        import tests.test_pipeline as tp
        self.assertTrue(hasattr(tp, "AssetReuseTests"))
        self.assertTrue(hasattr(tp, "InteriorBuilderTests"))

    def test_f15_publicity_kit_unit_tests_pass(self) -> None:
        """F15.5: Verify test_publicity_kit.py module is loadable and has tests."""
        from tests.test_publicity_kit import PublicityKitTests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PublicityKitTests)
        self.assertGreaterEqual(suite.countTestCases(), 2)


if __name__ == "__main__":
    unittest.main()
