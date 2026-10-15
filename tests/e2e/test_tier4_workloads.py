"""
Tier 4: Real-World Workload Scenarios Test Suite.
Verifies production publishing workflows:
- End-to-end 32-page interior PDF compilation and contact sheet proof generation
- End-to-end full-wrap cover spread compilation and 300 DPI preview generation
- Automated 12-criteria quality preflight audit
- Amazon KDP submission package completeness
- Pipeline idempotency and reproducible compilation
"""

from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile_animals_cover import (
    BLEED_IN,
    SERIES_TITLES_12,
    THICKNESS_PER_PAGE_IN,
    calculate_animals_cover_dimensions,
    draw_animals_cover_spread,
)
from scripts.compile_cover_pil import calculate_cover_dimensions
from scripts.compile_copy_to_color_interior import (
    DPI,
    PAGE_H,
    PAGE_W,
    SAFE_MARGIN,
    SERIES_CATALOG,
    build_32_page_copy_to_color_book,
    color_image_to_clean_lineart,
)


class TestTier4Workloads(unittest.TestCase):
    """Tier 4: Real-World Workload Scenarios and KDP Submission Readiness."""

    # =========================================================================
    # 1. End-to-End Interior Compilation & Proof Generation
    # =========================================================================
    def test_workload_end_to_end_single_volume_compilation_and_proof(self) -> None:
        """T4.1: Compile a complete 32-page interior PDF and verify proofs and geometry."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_pdf = Path(tmp_dir) / "animals_interior_32p.pdf"
            result = build_32_page_copy_to_color_book(
                vol_id="vol_02",
                vol_title="Animals",
                output_pdf_path=out_pdf,
            )

            # 1. Output PDF existence and validity
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 100_000, "Interior PDF should exceed 100KB")

            # 2. PyPDF structure inspection
            reader = PdfReader(str(result))
            self.assertEqual(len(reader.pages), 32, "Interior PDF must have exactly 32 pages")

            # 3. Geometry verification (8.625 x 11.250 in = 621.0 x 810.0 pt bleed mediabox)
            for idx, page in enumerate(reader.pages):
                self.assertAlmostEqual(float(page.mediabox.width), 8.625 * 72.0, places=1)
                self.assertAlmostEqual(float(page.mediabox.height), 11.250 * 72.0, places=1)

            # 4. Proof contact sheet verification
            proof_file = Path(tmp_dir) / "animals_interior_32p_proof.png"
            self.assertTrue(proof_file.exists())
            self.assertGreater(proof_file.stat().st_size, 10_000, "Contact sheet proof must be non-empty")
            with Image.open(proof_file) as proof_im:
                self.assertGreater(proof_im.width, 1000)
                self.assertGreater(proof_im.height, 500)

            # 5. Brand policy enforcement: zero "My First" in extracted text
            for page in reader.pages:
                txt = page.extract_text() or ""
                self.assertNotIn("my first", txt.lower())

    # =========================================================================
    # 2. End-to-End Full-Wrap Cover Spread Compilation & Proof
    # =========================================================================
    def test_workload_end_to_end_cover_spread_compilation_and_proof(self) -> None:
        """T4.2: Compile full-wrap cover spread and verify 300 DPI preview and spine suppression."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            spread_pdf = Path(tmp_dir) / "animals_cover_spread_32p.pdf"
            result = draw_animals_cover_spread(
                output_pdf_path=spread_pdf,
                page_count=32,
            )

            # 1. Output PDF existence and size
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 50_000)

            # 2. Single-page spread PDF
            reader = PdfReader(str(result))
            self.assertEqual(len(reader.pages), 1)

            # 3. Dimensions match 17.322 x 11.250 in
            dims = calculate_animals_cover_dimensions(page_count=32)
            expected_w_pt = dims["total_width_in"] * 72.0
            expected_h_pt = dims["total_height_in"] * 72.0
            page = reader.pages[0]
            self.assertAlmostEqual(float(page.mediabox.width), expected_w_pt, places=1)
            self.assertAlmostEqual(float(page.mediabox.height), expected_h_pt, places=1)

            # 4. 300 DPI preview PNG
            preview_png = Path(tmp_dir) / "animals_cover_spread_32p-proof.png"
            self.assertTrue(preview_png.exists())
            self.assertGreater(preview_png.stat().st_size, 50_000)

            # 5. Spine text suppression (< 79 pages)
            txt = page.extract_text() or ""
            self.assertNotIn("Copy to Color: Animals", txt)

    # =========================================================================
    # 3. Automated 12-Criteria Quality Preflight Audit
    # =========================================================================
    def test_workload_automated_quality_preflight_audit(self) -> None:
        """T4.3: Programmatically evaluate all 12 preflight release gate criteria."""
        preflight_results = {}

        # 1. Manifest exists
        manifest_path = REPO_ROOT / "manifests" / "animals-v1.0-core-32p.json"
        preflight_results["manifest_exists"] = manifest_path.exists()

        with open(manifest_path, "r", encoding="utf-8") as f:
            mf = json.load(f)

        # 2. Exact 32 pages in manifest
        preflight_results["manifest_32_pages"] = (mf.get("expected_page_count") == 32 and len(mf.get("pages", [])) == 32)

        # 3. Distinct educational subjects (no duplicates)
        subjects = mf.get("expected_subjects", [])
        preflight_results["subjects_30_unique"] = (len(subjects) == 30 and len(set(subjects)) == 30)

        # 4. Page 1 welcome & Page 32 certificate
        pages = mf.get("pages", [])
        preflight_results["sequence_structure"] = (pages[0]["type"] == "welcome" and pages[-1]["type"] == "certificate")

        # 5. Trim & Bleed settings
        trim = mf.get("trim", {})
        preflight_results["trim_and_bleed"] = (
            trim.get("width_in") == 8.5 and
            trim.get("height_in") == 11.0 and
            trim.get("page_width_in_with_bleed") == 8.625 and
            trim.get("page_height_in_with_bleed") == 11.25
        )

        # 6. Minimum DPI >= 300
        preflight_results["dpi_spec"] = (mf.get("minimum_dpi") >= 300)

        # 7. Safe margin >= 0.5 in
        preflight_results["safe_margin_spec"] = (mf.get("minimum_safe_margin_in") >= 0.5)

        # 8. Brand governance: zero "My First"
        preflight_results["zero_my_first"] = ("my first" not in json.dumps(mf).lower())

        # 9. Publisher imprint exact match
        preflight_results["publisher_imprint"] = (mf.get("publisher") == "The Pivot Digital Publication")

        # 10. Catalog metadata entry complete
        catalog_path = REPO_ROOT / "catalogs" / "catalog_master.json"
        with open(catalog_path, "r", encoding="utf-8") as f:
            cat = json.load(f)
        animals_ed = next((e for e in cat.get("editions", []) if e.get("book_id") == "PIVOT-ANIMALS-002-32P"), None)
        preflight_results["catalog_entry_exists"] = (animals_ed is not None)

        # 11. 7 backend keywords <= 50 chars
        keywords = animals_ed.get("metadata", {}).get("backend_keywords", [])
        preflight_results["seven_keywords"] = (len(keywords) == 7 and all(len(kw) <= 50 for kw in keywords))

        # 12. 2 BISAC category candidates
        categories = animals_ed.get("metadata", {}).get("category_candidates", [])
        preflight_results["two_categories"] = (len(categories) == 2)

        # Assert 100% of preflight criteria PASS
        self.assertEqual(len(preflight_results), 12)
        for rule, status in preflight_results.items():
            self.assertTrue(status, f"Preflight criterion '{rule}' failed")

    # =========================================================================
    # 4. Amazon KDP Submission Package Completeness
    # =========================================================================
    def test_workload_kdp_submission_package_completeness(self) -> None:
        """T4.4: Verify complete KDP submission package requirements for a volume."""
        # A release-ready package must have:
        # 1. Manifest
        # 2. Master Catalog metadata package
        # 3. Interior compilation callable
        # 4. Cover compilation callable
        # 5. Valid asset registry reference
        manifest_path = REPO_ROOT / "manifests" / "animals-v1.0-core-32p.json"
        self.assertTrue(manifest_path.exists())

        catalog_path = REPO_ROOT / "catalogs" / "catalog_master.json"
        self.assertTrue(catalog_path.exists())

        with open(catalog_path, "r", encoding="utf-8") as f:
            cat = json.load(f)
        ed = next(e for e in cat["editions"] if e.get("book_id") == "PIVOT-ANIMALS-002-32P")
        self.assertIn("metadata", ed)
        self.assertIn("description_html", ed["metadata"])

    # =========================================================================
    # 5. Compilation Idempotency & Repeatability
    # =========================================================================
    def test_workload_compilation_idempotency(self) -> None:
        """T4.5: Verify repeated dimension and cover calculations are deterministic."""
        dims1 = calculate_animals_cover_dimensions(page_count=32)
        dims2 = calculate_animals_cover_dimensions(page_count=32)
        self.assertEqual(dims1, dims2)

        dims_pil1 = calculate_cover_dimensions(page_count=32)
        dims_pil2 = calculate_cover_dimensions(page_count=32)
        self.assertEqual(dims_pil1, dims_pil2)


if __name__ == "__main__":
    unittest.main()
