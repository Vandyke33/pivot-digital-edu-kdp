"""Comprehensive verification script for Worker M1 deliverables."""

import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile_copy_to_color_interior import SERIES_CATALOG


class WorkerM1VerificationTests(unittest.TestCase):
    def test_line_522_imprint_typo_fixed(self):
        """Verify line 522 has 'The Pivot Digital Publication' (singular)."""
        script_path = REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py"
        content = script_path.read_text(encoding="utf-8")
        self.assertNotIn("The Pivot Digital Publications", content)
        self.assertIn("© The Pivot Digital Publication. All rights reserved. • Amazon KDP Edition", content)

    def test_catalog_master_top_level_imprint(self):
        """Verify top-level imprint in catalog_master.json."""
        cat_path = REPO_ROOT / "catalogs" / "catalog_master.json"
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        self.assertEqual(cat.get("publisher_imprint"), "The Pivot Digital Publication")

    def test_catalog_master_12_volumes_metadata(self):
        """Verify all 12 Copy to Color editions have complete, valid metadata."""
        cat_path = REPO_ROOT / "catalogs" / "catalog_master.json"
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        editions = {ed["book_id"]: ed for ed in cat["editions"]}

        expected_ids = [
            ("vol_01", "PIVOT-ALPHABET-001-32P", "Alphabet"),
            ("vol_02", "PIVOT-ANIMALS-002-32P", "Animals"),
            ("vol_03", "PIVOT-BIRDS-003-32P", "Birds"),
            ("vol_04", "PIVOT-SPORTS-004-32P", "Sports"),
            ("vol_05", "PIVOT-MONSTERS-005-32P", "Monsters"),
            ("vol_06", "PIVOT-NUMBERS-006-32P", "Numbers"),
            ("vol_07", "PIVOT-FRUITS-007-32P", "Fruits"),
            ("vol_08", "PIVOT-SHAPES-008-32P", "Shapes"),
            ("vol_09", "PIVOT-TOYS-009-32P", "Toys"),
            ("vol_10", "PIVOT-FLOWERS-010-32P", "Flowers"),
            ("vol_11", "PIVOT-TRANSPORT-011-32P", "Transport"),
            ("vol_12", "PIVOT-VEGETABLES-012-32P", "Vegetables"),
        ]

        allowed_html_tags = {"b", "i", "h3", "ul", "li", "p", "br"}

        for vol_key, book_id, subject in expected_ids:
            self.assertIn(book_id, editions, f"Missing edition {book_id}")
            ed = editions[book_id]
            self.assertEqual(ed["title"], f"Copy to Color: {subject}")
            self.assertEqual(ed["subtitle"], f"Interactive Early Learning {subject} Coloring Activity Book for Ages 3-5")
            self.assertIn("metadata", ed, f"Missing metadata for {book_id}")

            meta = ed["metadata"]
            self.assertEqual(meta["title"], f"Copy to Color: {subject}")
            self.assertEqual(meta["subtitle"], f"Interactive Early Learning {subject} Coloring Activity Book for Ages 3-5")
            self.assertEqual(meta["publisher_imprint"], "The Pivot Digital Publication")

            # 7 distinct keywords <= 50 chars each
            keywords = meta["backend_keywords"]
            self.assertEqual(len(keywords), 7, f"Expected 7 keywords for {book_id}")
            self.assertEqual(len(set(keywords)), 7, f"Duplicate keywords in {book_id}")
            for kw in keywords:
                self.assertLessEqual(len(kw), 50, f"Keyword > 50 chars in {book_id}: '{kw}' ({len(kw)})")
                self.assertNotIn("my first", kw.lower(), f"'My First' in keyword: {kw}")
                for banned in [",", '"', ";"]:
                    self.assertNotIn(banned, kw, f"Banned char '{banned}' in keyword: {kw}")

            # 2 BISAC category candidates
            categories = meta["category_candidates"]
            self.assertEqual(len(categories), 2, f"Expected 2 categories for {book_id}")
            self.assertTrue(categories[0].startswith("JUVENILE NONFICTION / Activity Books / Coloring"))

            # HTML description
            html = meta["description_html"]
            self.assertTrue(len(html) > 100, f"HTML description too short for {book_id}")
            self.assertNotIn("my first", html.lower(), f"'My First' in description for {book_id}")
            tags = re.findall(r"</?([a-zA-Z0-9]+)[^>]*>", html)
            for t in tags:
                self.assertIn(t.lower(), allowed_html_tags, f"Disallowed HTML tag <{t}> in {book_id}")

    def test_all_12_manifests_exist_and_valid(self):
        """Verify all 12 32-page edition manifests exist in manifests/ and are valid."""
        manifest_files = [
            ("vol_01", "alphabet-v1.0-core-32p.json", "PIVOT-ALPHABET-001-32P", "Alphabet"),
            ("vol_02", "animals-v1.0-core-32p.json", "PIVOT-ANIMALS-002-32P", "Animals"),
            ("vol_03", "birds-v1.0-core-32p.json", "PIVOT-BIRDS-003-32P", "Birds"),
            ("vol_04", "sports-v1.0-core-32p.json", "PIVOT-SPORTS-004-32P", "Sports"),
            ("vol_05", "monsters-v1.0-core-32p.json", "PIVOT-MONSTERS-005-32P", "Monsters"),
            ("vol_06", "numbers-v1.0-core-32p.json", "PIVOT-NUMBERS-006-32P", "Numbers"),
            ("vol_07", "fruits-v1.0-core-32p.json", "PIVOT-FRUITS-007-32P", "Fruits"),
            ("vol_08", "shapes-v1.0-core-32p.json", "PIVOT-SHAPES-008-32P", "Shapes"),
            ("vol_09", "toys-v1.0-core-32p.json", "PIVOT-TOYS-009-32P", "Toys"),
            ("vol_10", "flowers-v1.0-core-32p.json", "PIVOT-FLOWERS-010-32P", "Flowers"),
            ("vol_11", "transport-v1.0-core-32p.json", "PIVOT-TRANSPORT-011-32P", "Transport"),
            ("vol_12", "vegetables-v1.0-core-32p.json", "PIVOT-VEGETABLES-012-32P", "Vegetables"),
        ]

        for vol_key, fname, book_id, subject in manifest_files:
            m_path = REPO_ROOT / "manifests" / fname
            self.assertTrue(m_path.exists(), f"Manifest file missing: {fname}")
            m = json.loads(m_path.read_text(encoding="utf-8"))

            self.assertEqual(m["schema_version"], "1.0.0")
            self.assertEqual(m["book_id"], book_id)
            self.assertEqual(m["edition_id"], "v1.0-core-32p")
            self.assertEqual(m["title"], f"Copy to Color: {subject}")
            self.assertEqual(m["publisher"], "The Pivot Digital Publication")
            self.assertEqual(m["expected_page_count"], 32)
            self.assertEqual(m["trim"]["width_in"], 8.5)
            self.assertEqual(m["trim"]["height_in"], 11.0)
            self.assertEqual(m["trim"]["bleed"], "all")
            self.assertEqual(m["trim"]["page_width_in_with_bleed"], 8.625)
            self.assertEqual(m["trim"]["page_height_in_with_bleed"], 11.25)
            self.assertEqual(m["minimum_dpi"], 300)
            self.assertEqual(m["minimum_safe_margin_in"], 0.5)

            # Expected subjects
            exp_subj = m["expected_subjects"]
            self.assertEqual(len(exp_subj), 30, f"Expected 30 subjects in {fname}")
            self.assertEqual(len(set(exp_subj)), 30, f"Duplicate subjects in {fname}")

            # Pages
            pages = m["pages"]
            self.assertEqual(len(pages), 32, f"Expected 32 pages in {fname}")
            self.assertEqual(pages[0]["number"], 1)
            self.assertEqual(pages[0]["type"], "welcome")
            self.assertEqual(pages[0]["title"], f"Copy to Color: {subject}")

            for p in pages[1:31]:
                self.assertEqual(p["type"], "copy_to_color")
                self.assertIn("subject_id", p)
                self.assertIn("letter", p)
                self.assertIn("banner", p)
                self.assertNotIn("my first", p["banner"].lower())

            self.assertEqual(pages[31]["number"], 32)
            self.assertEqual(pages[31]["type"], "certificate")
            self.assertEqual(pages[31]["title"], "Super Colorist Award")

            # Check raw json text for forbidden phrase
            raw_text = m_path.read_text(encoding="utf-8")
            self.assertNotIn("my first", raw_text.lower())

    def test_zero_occurrences_of_my_first_in_catalog_and_manifests(self):
        """Verify zero occurrences of 'My First' in catalog_master.json and all manifests."""
        cat_text = (REPO_ROOT / "catalogs" / "catalog_master.json").read_text(encoding="utf-8")
        self.assertNotIn("my first", cat_text.lower())

        for p in (REPO_ROOT / "manifests").glob("*-32p.json"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("my first", text.lower(), f"Found 'My First' in {p.name}")


if __name__ == "__main__":
    unittest.main()
