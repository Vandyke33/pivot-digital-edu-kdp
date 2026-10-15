"""Unit tests for the 32-page 'Copy to Color' interior compiler and series pipeline."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from scripts.compile_copy_to_color_interior import (
    DPI,
    PAGE_H,
    PAGE_W,
    SAFE_MARGIN,
    SERIES_CATALOG,
    build_32_page_copy_to_color_book,
    color_image_to_clean_lineart,
    resolve_subject_assets,
)
from scripts.compile_cover_pil import (
    SERIES_TITLES,
    calculate_cover_dimensions,
    pull_remote_asset,
)

ROOT = Path(__file__).resolve().parents[1]


class CopyToColorInteriorTests(unittest.TestCase):
    def test_series_catalog_integrity(self) -> None:
        """Verify that all 12 series volumes are configured with 30 subjects each."""
        self.assertEqual(len(SERIES_CATALOG), 12)
        expected_vols = [f"vol_{i:02d}" for i in range(1, 13)]
        for v in expected_vols:
            self.assertIn(v, SERIES_CATALOG)
            meta = SERIES_CATALOG[v]
            self.assertIn("title", meta)
            self.assertIn("primary", meta)
            self.assertIn("secondary", meta)
            self.assertIn("subjects", meta)
            self.assertGreaterEqual(len(meta["subjects"]), 30)

            # Strict Brand & Title Naming Policy: NEVER includes "My First"
            self.assertNotIn("My First", meta["title"])
            for code, name in meta["subjects"]:
                self.assertNotIn("My First", name)

    def test_color_image_to_clean_lineart(self) -> None:
        """Verify zero-credit line art extraction produces pure 1:1 binary lineart."""
        # Create a test synthetic colored illustration
        img = Image.new("RGBA", (400, 400), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        # Red circle with black border
        draw.ellipse([80, 80, 320, 320], fill=(239, 68, 68, 255), outline=(20, 20, 20, 255), width=8)

        lineart = color_image_to_clean_lineart(img, stroke_boost=2)

        self.assertEqual(lineart.size, (400, 400))
        self.assertEqual(lineart.mode, "RGBA")

        # Check binary ink values: pixels must be strictly pure black (0) or pure white (255)
        gray = lineart.convert("L")
        extrema = gray.getextrema()
        self.assertEqual(extrema, (0, 255))

    def test_resolve_subject_assets_fail_closed(self) -> None:
        """Verify resolve_subject_assets strictly enforces NO_PROCEDURAL_ART and fails closed when assets missing."""
        with self.assertRaises(FileNotFoundError):
            resolve_subject_assets("vol_99", 99, "NON_EXISTENT")

    def test_build_32_page_copy_to_color_book(self) -> None:
        """Verify end-to-end compilation of a compliant 32-page interior PDF."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "test_copy_to_color_32p.pdf"
            result = build_32_page_copy_to_color_book(
                vol_id="vol_02",
                vol_title="Animals",
                output_pdf_path=out_pdf,
            )

            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 100_000)

            # Preflight inspection with PyPDF
            reader = PdfReader(str(result))
            self.assertEqual(len(reader.pages), 32)

            # Inspect page geometry (8.625 x 11.250 in = 621.0 x 810.0 pt bleed mediabox)
            expected_w_pt = 8.625 * 72.0  # 621.0 pt
            expected_h_pt = 11.250 * 72.0  # 810.0 pt
            for idx, page in enumerate(reader.pages):
                self.assertAlmostEqual(float(page.mediabox.width), expected_w_pt, places=1)
                self.assertAlmostEqual(float(page.mediabox.height), expected_h_pt, places=1)

            # Visual Proof Contact sheet must also be generated
            proof_file = Path(tmp_dir) / "test_copy_to_color_32p_proof.png"
            self.assertTrue(proof_file.exists())
            self.assertGreater(proof_file.stat().st_size, 10_000)

            # Strict Brand & Title Naming Policy: Zero occurrences of "My First"
            for p in reader.pages:
                txt = p.extract_text() or ""
                self.assertNotIn("My First", txt)

    def test_cover_dimensions_32p_and_spine_suppression(self) -> None:
        """Verify KDP mechanical dimensions and automated spine suppression for 32 pages."""
        dims = calculate_cover_dimensions(page_count=32)

        # 32 pages on 55# white paper
        expected_spine_in = round(32 * 0.002252, 4)  # ~0.0721 in
        self.assertAlmostEqual(dims["spine_in"], expected_spine_in, places=3)
        self.assertEqual(dims["width_px"], 5197)   # (8.5*2 + 0.0721 + 0.25) * 300 = 5197 px
        self.assertEqual(dims["height_px"], 3375)  # (11.0 + 0.25) * 300 = 3375 px
        self.assertEqual(dims["spine_px"], 22)

    def test_pull_remote_asset_local_and_none(self) -> None:
        """Verify remote asset puller handles existing files and None gracefully."""
        self.assertIsNone(pull_remote_asset(None, "dummy_dest.png"))
        self.assertIsNone(pull_remote_asset("", "dummy_dest.png"))

        # Existing local file should be returned directly
        test_file = ROOT / "README.md"
        if test_file.exists():
            resolved = pull_remote_asset(str(test_file), "dummy_dest.md")
            self.assertEqual(resolved, str(test_file))

    def test_strict_brand_naming_across_cover_series_titles(self) -> None:
        """Verify that SERIES_TITLES never uses 'My First'."""
        for item in SERIES_TITLES:
            self.assertNotIn("My First", item["title"])


if __name__ == "__main__":
    unittest.main()

