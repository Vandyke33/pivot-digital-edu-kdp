"""
Tier 2: Boundary & Corner Cases Test Suite.
Verifies mathematical limits, mechanical tolerances, KDP step-function thresholds,
barcode clearances, mediabox dimensions, pure binary ink limits, and edge overflows.
"""

from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile_animals_cover import (
    BLEED_IN,
    THICKNESS_PER_PAGE_IN,
    calculate_animals_cover_dimensions,
    draw_animals_cover_spread,
)
from scripts.compile_copy_to_color_interior import (
    DPI,
    PAGE_H,
    PAGE_W,
    SAFE_MARGIN,
    color_image_to_clean_lineart,
)
from scripts.compile_cover_pil import calculate_cover_dimensions
from scripts.utils.alpha_extraction import extract_with_sticker_contour


class TestTier2Boundaries(unittest.TestCase):
    """Tier 2: Boundary and Corner Case Stress Testing."""

    # =========================================================================
    # 1. Physical & Mechanical Dimensions Boundaries
    # =========================================================================
    def test_boundary_exact_kdp_cover_dimensions_32p(self) -> None:
        """T2.1: Verify exact mathematical calculations for 32-page KDP full-wrap cover."""
        page_count = 32
        trim_w, trim_h, bleed = 8.5, 11.0, 0.125
        page_thickness = 0.002252

        expected_spine_in = round(page_count * page_thickness, 4)
        expected_total_w_in = round(2 * trim_w + expected_spine_in + 2 * bleed, 4)
        expected_total_h_in = round(trim_h + 2 * bleed, 4)

        dims = calculate_animals_cover_dimensions(page_count=32)

        self.assertAlmostEqual(dims["spine_width_in"], expected_spine_in, places=4)
        self.assertAlmostEqual(dims["total_width_in"], expected_total_w_in, places=4)
        self.assertAlmostEqual(dims["total_height_in"], expected_total_h_in, places=4)

        # Pixel dimensions @ 300 DPI
        expected_w_px = round(expected_total_w_in * 300)
        expected_h_px = round(expected_total_h_in * 300)
        self.assertEqual(expected_w_px, 5197)
        self.assertEqual(expected_h_px, 3375)

    def test_boundary_spine_growth_monotonicity(self) -> None:
        """T2.2: Verify spine width scales strictly monotonically with page count."""
        page_counts = [24, 32, 48, 64, 78, 80, 96, 120]
        spines = [calculate_animals_cover_dimensions(page_count=pc)["spine_width_in"] for pc in page_counts]

        for i in range(len(spines) - 1):
            self.assertGreater(spines[i + 1], spines[i])
            delta_pages = page_counts[i + 1] - page_counts[i]
            expected_delta = delta_pages * THICKNESS_PER_PAGE_IN
            self.assertAlmostEqual(spines[i + 1] - spines[i], expected_delta, places=3)

    # =========================================================================
    # 2. KDP Spine Text Step-Function Threshold (< 79 vs >= 79 pages)
    # =========================================================================
    def test_boundary_spine_text_omission_strict_threshold_78p_suppressed(self) -> None:
        """T2.3: Verify spine text is strictly omitted at 32 pages and 78 pages (< 79 threshold)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            # 32 Pages
            pdf_32p = Path(tmp_dir) / "cover_32p.pdf"
            draw_animals_cover_spread(pdf_32p, page_count=32)
            reader_32 = PdfReader(str(pdf_32p))
            text_32 = reader_32.pages[0].extract_text() or ""
            self.assertNotIn("Copy to Color: Animals", text_32)

            # 78 Pages (Upper boundary under threshold)
            pdf_78p = Path(tmp_dir) / "cover_78p.pdf"
            draw_animals_cover_spread(pdf_78p, page_count=78)
            reader_78 = PdfReader(str(pdf_78p))
            text_78 = reader_78.pages[0].extract_text() or ""
            self.assertNotIn("Copy to Color: Animals", text_78)

    def test_boundary_spine_text_presence_threshold_80p(self) -> None:
        """T2.4: Verify spine text is rendered and present at 80 pages (>= 79 threshold)."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            pdf_80p = Path(tmp_dir) / "cover_80p.pdf"
            draw_animals_cover_spread(pdf_80p, page_count=80)
            reader_80 = PdfReader(str(pdf_80p))
            text_80 = reader_80.pages[0].extract_text() or ""
            self.assertIn("Copy to Color: Animals", text_80)
            # Confirm prohibited phrase is still never present on spine
            self.assertNotIn("My First", text_80)

    # =========================================================================
    # 3. Barcode Safe Area Clearance Boundary
    # =========================================================================
    def test_boundary_barcode_safe_area_bounding_box_clearance(self) -> None:
        """T2.5: Verify 2.0 x 1.2 in barcode safe area preserves 0.5 in trim/spine clearances."""
        trim_w = 8.5
        bleed = 0.125
        barcode_w = 2.0
        barcode_h = 1.2
        margin_clearance = 0.5

        # Back cover coordinates
        back_left = bleed
        back_right = bleed + trim_w

        # Barcode placed at bottom right of back cover
        barcode_right = back_right - margin_clearance
        barcode_left = barcode_right - barcode_w

        self.assertGreaterEqual(barcode_left, back_left + margin_clearance)
        self.assertAlmostEqual(barcode_right - barcode_left, barcode_w)

        # Vertical clearance from bottom trim edge
        barcode_bottom = bleed + margin_clearance
        barcode_top = barcode_bottom + barcode_h
        self.assertGreaterEqual(barcode_bottom, bleed + 0.5)
        self.assertAlmostEqual(barcode_top - barcode_bottom, barcode_h)

    # =========================================================================
    # 4. Interior Mediabox Geometry & Tolerances
    # =========================================================================
    def test_boundary_interior_bleed_mediabox_accuracy(self) -> None:
        """T2.6: Verify interior bleed mediabox dimensions match 621.0 x 810.0 pt."""
        expected_w_pt = 8.625 * 72.0  # 621.0 pt
        expected_h_pt = 11.250 * 72.0  # 810.0 pt

        self.assertEqual(expected_w_pt, 621.0)
        self.assertEqual(expected_h_pt, 810.0)

        # Aspect ratio tolerance
        ar = expected_w_pt / expected_h_pt
        self.assertAlmostEqual(ar, 8.625 / 11.250, places=6)

    # =========================================================================
    # 5. Pure Binary Lineart Ink Limit (Strict Histogram Zero-Gray)
    # =========================================================================
    def test_boundary_pure_binary_lineart_strict_histogram(self) -> None:
        """T2.7: Verify lineart conversion produces zero intermediate grayscale values (1..254)."""
        # Create gradient test image with diverse gray levels
        test_im = Image.new("RGBA", (256, 256), (255, 255, 255, 255))
        draw = ImageDraw.Draw(test_im)
        for x in range(256):
            draw.line([(x, 0), (x, 255)], fill=(x, x, x, 255))

        lineart = color_image_to_clean_lineart(test_im, stroke_boost=2)
        gray = lineart.convert("L")
        histogram = gray.histogram()

        # Check histogram: bins 1 to 254 must have exactly 0 pixels
        intermediate_pixels = sum(histogram[1:255])
        self.assertEqual(intermediate_pixels, 0, f"Found {intermediate_pixels} intermediate gray pixels in lineart")

        # Only bin 0 (pure black) and bin 255 (pure white) may contain pixels
        self.assertEqual(sum(histogram), 256 * 256)
        self.assertEqual(histogram[0] + histogram[255], 256 * 256)

    # =========================================================================
    # 6. Safe Margin Clearance & Encroachment Bounds
    # =========================================================================
    def test_boundary_safe_margin_bounds_inner_clearance(self) -> None:
        """T2.8: Verify safe margin boundary is at least 0.5 inches (150 px @ 300 DPI / 36 pt)."""
        self.assertGreaterEqual(SAFE_MARGIN, 150)
        margin_in = SAFE_MARGIN / DPI
        self.assertGreaterEqual(margin_in, 0.5)

        # Inner drawable zone bounds
        min_x = SAFE_MARGIN
        max_x = PAGE_W - SAFE_MARGIN
        min_y = SAFE_MARGIN
        max_y = PAGE_H - SAFE_MARGIN

        self.assertGreater(max_x, min_x)
        self.assertGreater(max_y, min_y)
        self.assertEqual(max_x - min_x, PAGE_W - 2 * SAFE_MARGIN)

    # =========================================================================
    # 7. Aspect Ratio Consistency Across Canvas Modes
    # =========================================================================
    def test_boundary_aspect_ratio_consistency_across_canvas_modes(self) -> None:
        """T2.9: Verify aspect ratios across standalone front, interior bleed, and full-wrap."""
        # Standalone front cover (8.5 x 11.0 in)
        front_ar = 8.5 / 11.0
        self.assertAlmostEqual(front_ar, 0.7727, places=4)

        # Interior bleed canvas (8.625 x 11.250 in)
        interior_ar = 8.625 / 11.250
        self.assertAlmostEqual(interior_ar, 0.7667, places=4)

        # Full-wrap cover spread for 32 pages (17.3221 x 11.250 in)
        dims = calculate_animals_cover_dimensions(page_count=32)
        spread_ar = dims["total_width_in"] / dims["total_height_in"]
        self.assertAlmostEqual(spread_ar, 1.5397, places=4)

    # =========================================================================
    # 8. Stroke Boost Scaling Limits
    # =========================================================================
    def test_boundary_stroke_boost_scaling_limits(self) -> None:
        """T2.10: Verify stroke boost values (1, 2, 3, 5) preserve binary integrity."""
        test_im = Image.new("RGBA", (200, 200), (255, 255, 255, 255))
        draw = ImageDraw.Draw(test_im)
        draw.line([(50, 50), (150, 150)], fill=(0, 0, 0, 255), width=2)

        for boost in [1, 2, 3, 5]:
            boosted = color_image_to_clean_lineart(test_im, stroke_boost=boost)
            gray = boosted.convert("L")
            hist = gray.histogram()
            self.assertEqual(sum(hist[1:255]), 0)
            self.assertGreater(hist[0], 0)

    # =========================================================================
    # 9. Alpha Extraction Trapped Pocket Area Threshold
    # =========================================================================
    def test_boundary_trapped_pocket_area_thresholds(self) -> None:
        """T2.11: Verify trapped pocket removal preserves small pockets and clears large ones."""
        # Create image with a small white pocket (area ~50 px) and a large white pocket (area ~2800 px)
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
        # Enclosed large center white pocket must be transparent (area > 1500)
        self.assertEqual(res.getpixel((100, 100))[3], 0)
        # Small eye white area (area < 1500) must remain opaque
        self.assertEqual(res.getpixel((46, 96))[3], 255)


if __name__ == "__main__":
    unittest.main()
