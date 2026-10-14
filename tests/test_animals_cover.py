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
        expected_sample_titles = {"Alphabet", "Birds", "Sports", "Monsters", "Numbers", "Fruits", "Shapes", "Toys"}
        actual_titles = {item["title"] for item in SERIES_TITLES_12}
        self.assertTrue(expected_sample_titles.issubset(actual_titles))

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
                page_count=32,
                logo_path=None,
                hero_art_path=None,
                card_color_thumb=None,
                card_bw_outline=None,
            )

            self.assertTrue(result.exists())
            reader = PdfReader(str(result))
            self.assertEqual(len(reader.pages), 1)

            page = reader.pages[0]
            dims = calculate_animals_cover_dimensions(page_count=32)
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
                page_count=32,
                logo_path=logo if logo.exists() else None,
                hero_art_path=hero if hero.exists() else None,
                card_color_thumb=thumb if thumb.exists() else None,
                card_bw_outline=outline if outline.exists() else None,
            )

            self.assertTrue(result.exists())
    def test_dimensions_calculation_74_pages(self) -> None:
        dims = calculate_animals_cover_dimensions(page_count=74)
        expected_spine = round(74 * THICKNESS_PER_PAGE_IN, 4)
        self.assertAlmostEqual(dims["spine_width_in"], expected_spine, places=4)
        self.assertAlmostEqual(dims["total_width_in"], round(17.0 + expected_spine + 0.25, 4), places=4)

    def test_corner_floodfill_alpha_extraction(self) -> None:
        from PIL import Image, ImageDraw
        from scripts.utils.alpha_extraction import extract_with_sticker_contour

        # Create dummy image with white background, brown character circle, and white eye inside
        im = Image.new("RGB", (100, 100), (255, 255, 255))
        d = ImageDraw.Draw(im)
        d.ellipse([20, 20, 80, 80], fill=(180, 100, 40), outline=(50, 20, 10), width=3)
        # White eye inside
        d.ellipse([35, 35, 55, 55], fill=(255, 255, 255), outline=(0, 0, 0), width=1)
        # Black pupil
        d.ellipse([45, 45, 50, 50], fill=(0, 0, 0))

        res = extract_with_sticker_contour(im, tolerance=20, contour_radius=4, blur_radius=1.0)
        # Corner must be transparent
        self.assertEqual(res.getpixel((0, 0))[3], 0)
        # White eye sclera must remain fully opaque white (255, 255, 255, 255)
        eye_pixel = res.getpixel((38, 40))
        self.assertEqual(eye_pixel, (255, 255, 255, 255))

    def test_render_cover_proof(self) -> None:
        from scripts.render_cover_proof import render_pdf_to_image

        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "dummy.pdf"
            draw_animals_cover_spread(
                output_pdf_path=out_pdf,
                page_count=74,
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


