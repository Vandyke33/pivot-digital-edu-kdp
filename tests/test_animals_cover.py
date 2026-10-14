"""Unit tests for 'Copy to Color: Animals' full-wrap cover spread generator."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pypdf import PdfReader

from scripts.compile_animals_cover import (
    BLEED_IN,
    SERIES_TITLES_12,
    THICKNESS_PER_PAGE_IN,
    calculate_animals_cover_dimensions,
    draw_animals_cover_spread,
)

ROOT = Path(__file__).resolve().parents[1]


class AnimalsCoverSpreadTests(unittest.TestCase):
    def test_dimensions_calculation_32_pages(self) -> None:
        dims = calculate_animals_cover_dimensions(page_count=32)

        # Expected calculations for 8.5 x 11 in trim, 32 pages, 55# white paper
        expected_spine = round(32 * THICKNESS_PER_PAGE_IN, 4)  # ~0.0721 in
        expected_total_w = round(2 * 8.5 + expected_spine + 2 * BLEED_IN, 4)  # ~17.3221 in
        expected_total_h = round(11.0 + 2 * BLEED_IN, 4)  # 11.25 in

        self.assertEqual(dims["trim_width_in"], 8.5)
        self.assertEqual(dims["trim_height_in"], 11.0)
        self.assertEqual(dims["page_count"], 32)
        self.assertEqual(dims["bleed_in"], 0.125)
        self.assertAlmostEqual(dims["spine_width_in"], expected_spine, places=4)
        self.assertAlmostEqual(dims["total_width_in"], expected_total_w, places=4)
        self.assertAlmostEqual(dims["total_height_in"], expected_total_h, places=4)

        # Region boundaries
        self.assertAlmostEqual(dims["back_left_in"], 0.125)
        self.assertAlmostEqual(dims["back_right_in"], 8.625)
        self.assertAlmostEqual(dims["spine_left_in"], dims["back_right_in"])
        self.assertAlmostEqual(dims["spine_right_in"], dims["spine_left_in"] + dims["spine_width_in"])
        self.assertAlmostEqual(dims["front_left_in"], dims["spine_right_in"])
        self.assertAlmostEqual(dims["front_right_in"], dims["total_width_in"] - dims["bleed_in"])

    def test_dimensions_calculation_custom_page_count(self) -> None:
        dims = calculate_animals_cover_dimensions(page_count=64)
        expected_spine = round(64 * THICKNESS_PER_PAGE_IN, 4)
        self.assertAlmostEqual(dims["spine_width_in"], expected_spine, places=4)
        self.assertAlmostEqual(dims["total_width_in"], round(17.0 + expected_spine + 0.25, 4), places=4)

    def test_series_titles_12_registry(self) -> None:
        # Back cover requires a 4x3 grid = exactly 12 miniature titles
        self.assertEqual(len(SERIES_TITLES_12), 12)
        expected_sample_titles = {"Alphabet", "Animals", "Birds", "Sports", "Monsters", "Numbers", "Fruits", "Shapes", "Toys", "Flowers", "Transport", "Vegetables"}
        actual_titles = {item["title"] for item in SERIES_TITLES_12}
        self.assertEqual(actual_titles, expected_sample_titles)

        # Check 1-to-1 volume ordering
        self.assertEqual(SERIES_TITLES_12[0]["title"], "Alphabet")
        self.assertEqual(SERIES_TITLES_12[0]["vol"], 1)
        self.assertEqual(SERIES_TITLES_12[1]["title"], "Animals")
        self.assertEqual(SERIES_TITLES_12[1]["vol"], 2)
        self.assertEqual(SERIES_TITLES_12[2]["title"], "Birds")
        self.assertEqual(SERIES_TITLES_12[2]["vol"], 3)
        self.assertEqual(SERIES_TITLES_12[11]["title"], "Vegetables")
        self.assertEqual(SERIES_TITLES_12[11]["vol"], 12)

        for item in SERIES_TITLES_12:
            self.assertIn("title", item)
            self.assertIn("color", item)
            self.assertIn("accent", item)
            self.assertTrue(item["color"].startswith("#"))
            self.assertTrue(item["accent"].startswith("#"))

    def test_draw_cover_spread_generates_valid_pdf_without_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "test-cover-no-assets.pdf"
            result = draw_animals_cover_spread(
                output_pdf_path=out_pdf,
                page_count=80,
                logo_path=None,
                hero_art_path=None,
                card_color_thumb=None,
                card_bw_outline=None,
            )

            self.assertTrue(result.exists())
            reader = PdfReader(str(result))
            self.assertEqual(len(reader.pages), 1)

            page = reader.pages[0]
            dims = calculate_animals_cover_dimensions(page_count=80)
            expected_w_pt = dims["total_width_in"] * 72.0
            expected_h_pt = dims["total_height_in"] * 72.0

            self.assertAlmostEqual(float(page.mediabox.width), expected_w_pt, places=1)
            self.assertAlmostEqual(float(page.mediabox.height), expected_h_pt, places=1)

    def test_draw_cover_spread_with_existing_assets(self) -> None:
        logo = ROOT / "assets" / "logos" / "pivot_kids.png"
        hero = ROOT / "local_builds" / "animals" / "assets" / "tiger_monkey_transparent.png"
        thumb = ROOT / "local_builds" / "animals" / "assets" / "tiger_color_thumb.png"
        outline = ROOT / "local_builds" / "animals" / "assets" / "tiger_outline.png"

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "test-cover-with-assets.pdf"
            result = draw_animals_cover_spread(
                output_pdf_path=out_pdf,
                page_count=80,
                logo_path=logo if logo.exists() else None,
                hero_art_path=hero if hero.exists() else None,
                card_color_thumb=thumb if thumb.exists() else None,
                card_bw_outline=outline if outline.exists() else None,
            )

            self.assertTrue(result.exists())

    def test_dimensions_calculation_80_pages(self) -> None:
        dims = calculate_animals_cover_dimensions(page_count=80)
        expected_spine = round(80 * THICKNESS_PER_PAGE_IN, 4)  # 0.1802 in
        self.assertAlmostEqual(dims["spine_width_in"], expected_spine, places=4)
        self.assertAlmostEqual(dims["total_width_in"], round(17.0 + expected_spine + 0.25, 4), places=4)
        self.assertGreaterEqual(dims["spine_width_in"], 0.18)

    def test_spine_text_omission_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_under = Path(tmp_dir) / "cover-74p.pdf"
            draw_animals_cover_spread(pdf_under, page_count=74)
            reader_under = PdfReader(str(pdf_under))
            text_under = reader_under.pages[0].extract_text()
            # Under 79 pages: spine text should be suppressed
            self.assertNotIn("My First Copy to Color: Animals", text_under)

            pdf_80 = Path(tmp_dir) / "cover-80p.pdf"
            draw_animals_cover_spread(pdf_80, page_count=80)
            reader_80 = PdfReader(str(pdf_80))
            text_80 = reader_80.pages[0].extract_text()
            # At 80 pages: spine text must be present
            self.assertIn("My First Copy to Color: Animals", text_80)

    def test_corner_floodfill_and_trapped_pocket_extraction(self) -> None:
        from PIL import Image, ImageDraw
        from scripts.utils.alpha_extraction import extract_with_sticker_contour

        # Create 200x200 image with:
        # 1. White background
        # 2. Two brown shapes that form an enclosed white loop of area > 2000 px
        # 3. A small white eye of area ~50 px inside one brown shape
        im = Image.new("RGB", (200, 200), (255, 255, 255))
        d = ImageDraw.Draw(im)

        # Outer thick brown hollow ring that encloses a large white pocket in the center
        d.ellipse([30, 30, 170, 170], fill=(180, 100, 40))
        # Enclosed white pocket in the center (diameter 60 px => area ~2800 px)
        d.ellipse([70, 70, 130, 130], fill=(255, 255, 255))

        # Small white eye inside the brown ring (area ~50 px)
        d.ellipse([45, 95, 55, 105], fill=(255, 255, 255))
        d.ellipse([48, 98, 52, 102], fill=(0, 0, 0))

        res = extract_with_sticker_contour(
            im,
            tolerance=20,
            contour_radius=3,
            blur_radius=1.0,
            remove_trapped_pockets=True,
            min_pocket_area=1500,
        )

        # Corner (exterior bg) must be transparent
        self.assertEqual(res.getpixel((0, 0))[3], 0)

        # Enclosed large center white pocket must also be transparent (alpha 0)
        self.assertEqual(res.getpixel((100, 100))[3], 0)

        # Small white eye sclera must remain fully opaque white (alpha 255)
        eye_pixel = res.getpixel((46, 100))
        self.assertEqual(eye_pixel, (255, 255, 255, 255))

    def test_render_cover_proof(self) -> None:
        from scripts.render_cover_proof import render_pdf_to_image

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "dummy.pdf"
            draw_animals_cover_spread(
                output_pdf_path=out_pdf,
                page_count=80,
                logo_path=None,
                hero_art_path=None,
                card_color_thumb=None,
                card_bw_outline=None,
            )
            out_png = Path(tmp_dir) / "dummy-proof.png"
            render_pdf_to_image(out_pdf, out_png, dpi=100)
            self.assertTrue(out_png.exists())
            self.assertGreater(out_png.stat().st_size, 5000)


if __name__ == "__main__":
    unittest.main()


