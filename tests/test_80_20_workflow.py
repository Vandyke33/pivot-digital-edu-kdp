"""
Unit test suite for the 80/20 Visual Studio Publishing Workflow.
Validates external front cover ingestion, dimensions normalization,
zero-occlusion invariants, and full-wrap KDP spread assembly.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from scripts.compile_cover_pil import (
    calculate_cover_dimensions,
    build_kdp_cover,
    load_and_normalize_front_cover,
    prebuild_all_series_front_covers,
)
import main


class Test8020Workflow(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_load_and_normalize_front_cover_exact_bleed(self) -> None:
        """Exact 2588 x 3375 px bleed image is returned as RGBA with matching dimensions."""
        im = Image.new("RGB", (2588, 3375), (255, 100, 50))
        img_path = self.tmp_path / "exact_bleed.png"
        im.save(img_path)

        norm = load_and_normalize_front_cover(img_path, target_w_px=2588, target_h_px=3375)
        self.assertEqual(norm.size, (2588, 3375))
        self.assertEqual(norm.mode, "RGBA")

    def test_load_and_normalize_front_cover_trim_only(self) -> None:
        """Trim-only 2550 x 3300 px artwork is normalized to 2588 x 3375 px full bleed."""
        im = Image.new("RGB", (2550, 3300), (40, 180, 100))
        img_path = self.tmp_path / "trim_only.png"
        im.save(img_path)

        norm = load_and_normalize_front_cover(img_path, target_w_px=2588, target_h_px=3375)
        self.assertEqual(norm.size, (2588, 3375))
        self.assertEqual(norm.mode, "RGBA")

    def test_load_and_normalize_front_cover_arbitrary_res(self) -> None:
        """Arbitrary resolution is scaled proportionally and center-cropped to target dimensions."""
        im = Image.new("RGBA", (1200, 1600), (80, 90, 200, 255))
        img_path = self.tmp_path / "arbitrary.png"
        im.save(img_path)

        norm = load_and_normalize_front_cover(img_path, target_w_px=2588, target_h_px=3375)
        self.assertEqual(norm.size, (2588, 3375))
        self.assertEqual(norm.mode, "RGBA")

    def test_load_and_normalize_front_cover_file_not_found(self) -> None:
        """Non-existent external front path raises FileNotFoundError (fails closed)."""
        non_existent = self.tmp_path / "does_not_exist.png"
        with self.assertRaises(FileNotFoundError):
            load_and_normalize_front_cover(non_existent)

    def test_build_kdp_cover_with_external_front(self) -> None:
        """build_kdp_cover successfully ingests an external front cover and reflects it in the spread."""
        # Create a distinct external front image with a unique marker color
        unique_color = (123, 234, 56, 255)
        ext_front = Image.new("RGBA", (2588, 3375), unique_color)
        ext_front_path = self.tmp_path / "vol_02_studio_front.png"
        ext_front.save(ext_front_path)

        out_pdf = self.tmp_path / "animals_fullwrap_external.pdf"

        result = build_kdp_cover(
            page_count=32,
            output_path=str(out_pdf),
            active_vol_id="vol_02",
            external_front=ext_front_path,
        )

        self.assertTrue(result.exists())
        self.assertGreater(result.stat().st_size, 50_000)

        proof_path = self.tmp_path / "animals_fullwrap_external-proof.png"
        self.assertTrue(proof_path.exists())

        # Inspect proof image dimensions and front cover zone color
        with Image.open(proof_path) as proof_im:
            self.assertEqual(proof_im.size, (5197, 3375))
            # Sample a pixel in the front cover area (e.g. center of front cover)
            # Front cover starts around x = 2609
            sample_pixel = proof_im.getpixel((3900, 1680))
            # Proof is RGB, compare R, G, B channels
            self.assertEqual(sample_pixel[:3], (123, 234, 56))

    def test_prebuild_all_series_front_covers_with_external_dir(self) -> None:
        """prebuild_all_series_front_covers ingests matching files from external_fronts_dir."""
        ext_dir = self.tmp_path / "external_fronts"
        ext_dir.mkdir(parents=True, exist_ok=True)

        # Create external front for vol_01 (Alphabet) and vol_02 (Animals)
        color_01 = (210, 45, 60, 255)
        color_02 = (30, 140, 220, 255)
        Image.new("RGBA", (2550, 3300), color_01).save(ext_dir / "vol_01_front.png")
        Image.new("RGBA", (2550, 3300), color_02).save(ext_dir / "vol_02_front.png")

        rendered = prebuild_all_series_front_covers(
            trim_w_px=2550,
            trim_h_px=3300,
            output_fronts_dir=str(self.tmp_path / "out_fronts"),
            force=True,
            external_fronts_dir=str(ext_dir),
        )

        self.assertIn("vol_01", rendered)
        self.assertIn("vol_02", rendered)
        self.assertEqual(len(rendered), 12)

        # Verify pixel colors match external fronts
        px_01 = rendered["vol_01"].getpixel((100, 100))
        px_02 = rendered["vol_02"].getpixel((100, 100))
        self.assertEqual(px_01[:3], (210, 45, 60))
        self.assertEqual(px_02[:3], (30, 140, 220))

    @patch("main.run_cmd")
    def test_cli_build_animals_cover_external_front_flag(self, mock_run: MagicMock) -> None:
        """CLI main wires --external-front flag to compile_animals_cover.py."""
        dummy_front = self.tmp_path / "my_front.png"
        dummy_front.touch()

        with patch("sys.argv", ["main.py", "build-animals-cover", "--external-front", str(dummy_front)]):
            exit_code = main.main()
            self.assertEqual(exit_code, 0)
            self.assertTrue(mock_run.called)
            call_cmd = mock_run.call_args_list[0][0][0]
            self.assertIn("--external-front", call_cmd)
            idx = call_cmd.index("--external-front")
            self.assertEqual(call_cmd[idx + 1], str(dummy_front))

    @patch("main.run_cmd")
    def test_cli_build_series_covers_external_fronts_dir_flag(self, mock_run: MagicMock) -> None:
        """CLI main wires --external-fronts-dir flag to compile_cover_pil.py."""
        dummy_dir = self.tmp_path / "my_fronts_dir"
        dummy_dir.mkdir()

        with patch("sys.argv", ["main.py", "build-series-covers", "--external-fronts-dir", str(dummy_dir)]):
            exit_code = main.main()
            self.assertEqual(exit_code, 0)
            self.assertTrue(mock_run.called)
            call_cmd = mock_run.call_args_list[0][0][0]
            self.assertIn("--external-fronts-dir", call_cmd)
            idx = call_cmd.index("--external-fronts-dir")
            self.assertEqual(call_cmd[idx + 1], str(dummy_dir))


if __name__ == "__main__":
    unittest.main()
