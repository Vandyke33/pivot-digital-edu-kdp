"""
Unit tests for compile_publicity_kit.py
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from PIL import Image

from scripts.compile_publicity_kit import draw_poster_gradient, generate_series_poster


class PublicityKitTests(unittest.TestCase):
    def test_draw_poster_gradient_dimensions_and_mode(self):
        """Verify that poster backdrop gradient produces correct dimensions and RGBA mode."""
        width, height = 400, 600
        grad = draw_poster_gradient(width, height)
        self.assertEqual(grad.size, (width, height))
        self.assertEqual(grad.mode, "RGBA")

    def test_generate_series_poster_end_to_end(self):
        """Verify that generate_series_poster runs and writes a high-res PNG."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_png = Path(tmp_dir) / "test_poster.png"
            fronts_dir = Path(tmp_dir) / "fronts"
            fronts_dir.mkdir()

            # Create dummy mini fronts for testing
            for i in range(1, 13):
                dummy_front = Image.new("RGBA", (300, 400), (255, 100, 50, 255))
                dummy_front.save(fronts_dir / f"vol_{i:02d}_front.png")

            result = generate_series_poster(
                output_path=out_png,
                fronts_dir=fronts_dir,
                logo_path=None,
            )

            self.assertTrue(result.exists())
            with Image.open(result) as img:
                self.assertEqual(img.size, (2400, 3600))
                self.assertEqual(img.format, "PNG")


if __name__ == "__main__":
    unittest.main()

