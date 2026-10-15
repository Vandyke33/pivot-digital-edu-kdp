"""
Adversarial Manifest Schema & Page Sequence Stress Test Harness
Challenger 2 (M1) — Empirical Validation Suite

Validates all 12 32-page edition manifests in manifests/:
1. Existence & valid JSON syntax across all 12 manifests.
2. Page count exactness: len(pages) == 32 and expected_page_count == 32.
3. Page structure integrity:
   - Page 1: type == 'welcome', canonical title
   - Pages 2-31: type == 'copy_to_color', non-empty subject_id, letter, banner
   - Page 32: type == 'certificate', title == 'Super Colorist Award'
4. Subject uniqueness and exact 1:1 synchronization with SERIES_CATALOG:
   - 30 unique subjects per manifest
   - Exact alignment with SERIES_CATALOG in compile_copy_to_color_interior.py
   - Zero missing, swapped, or misspelled subjects
5. Publisher imprint consistency: strictly 'The Pivot Digital Publication'.
6. Brand governance: zero occurrences of 'My First' (case-insensitive).
7. Mechanical specification compliance: 8.5x11 in trim, 8.625x11.25 in bleed, 300 DPI, 0.5 in safe margin.
8. Cross-manifest consistency: unique book_ids, series_ids, titles across all 12 volumes.
9. Mutation / Negative stress-testing: proving tests fail on corrupted inputs.
"""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile_copy_to_color_interior import SERIES_CATALOG

# Curated registry of the 12 volumes under test
EXPECTED_VOLUMES = [
    {
        "vol_key": "vol_01",
        "book_id": "PIVOT-ALPHABET-001-32P",
        "series_id": "copy_to_color_alphabet",
        "filename": "alphabet-v1.0-core-32p.json",
        "title": "Copy to Color: Alphabet",
        "subject_domain": "Alphabet",
    },
    {
        "vol_key": "vol_02",
        "book_id": "PIVOT-ANIMALS-002-32P",
        "series_id": "copy_to_color_animals",
        "filename": "animals-v1.0-core-32p.json",
        "title": "Copy to Color: Animals",
        "subject_domain": "Animals",
    },
    {
        "vol_key": "vol_03",
        "book_id": "PIVOT-BIRDS-003-32P",
        "series_id": "copy_to_color_birds",
        "filename": "birds-v1.0-core-32p.json",
        "title": "Copy to Color: Birds",
        "subject_domain": "Birds",
    },
    {
        "vol_key": "vol_04",
        "book_id": "PIVOT-SPORTS-004-32P",
        "series_id": "copy_to_color_sports",
        "filename": "sports-v1.0-core-32p.json",
        "title": "Copy to Color: Sports",
        "subject_domain": "Sports",
    },
    {
        "vol_key": "vol_05",
        "book_id": "PIVOT-MONSTERS-005-32P",
        "series_id": "copy_to_color_monsters",
        "filename": "monsters-v1.0-core-32p.json",
        "title": "Copy to Color: Monsters",
        "subject_domain": "Monsters",
    },
    {
        "vol_key": "vol_06",
        "book_id": "PIVOT-NUMBERS-006-32P",
        "series_id": "copy_to_color_numbers",
        "filename": "numbers-v1.0-core-32p.json",
        "title": "Copy to Color: Numbers",
        "subject_domain": "Numbers",
    },
    {
        "vol_key": "vol_07",
        "book_id": "PIVOT-FRUITS-007-32P",
        "series_id": "copy_to_color_fruits",
        "filename": "fruits-v1.0-core-32p.json",
        "title": "Copy to Color: Fruits",
        "subject_domain": "Fruits",
    },
    {
        "vol_key": "vol_08",
        "book_id": "PIVOT-SHAPES-008-32P",
        "series_id": "copy_to_color_shapes",
        "filename": "shapes-v1.0-core-32p.json",
        "title": "Copy to Color: Shapes",
        "subject_domain": "Shapes",
    },
    {
        "vol_key": "vol_09",
        "book_id": "PIVOT-TOYS-009-32P",
        "series_id": "copy_to_color_toys",
        "filename": "toys-v1.0-core-32p.json",
        "title": "Copy to Color: Toys",
        "subject_domain": "Toys",
    },
    {
        "vol_key": "vol_10",
        "book_id": "PIVOT-FLOWERS-010-32P",
        "series_id": "copy_to_color_flowers",
        "filename": "flowers-v1.0-core-32p.json",
        "title": "Copy to Color: Flowers",
        "subject_domain": "Flowers",
    },
    {
        "vol_key": "vol_11",
        "book_id": "PIVOT-TRANSPORT-011-32P",
        "series_id": "copy_to_color_transport",
        "filename": "transport-v1.0-core-32p.json",
        "title": "Copy to Color: Transport",
        "subject_domain": "Transport",
    },
    {
        "vol_key": "vol_12",
        "book_id": "PIVOT-VEGETABLES-012-32P",
        "series_id": "copy_to_color_vegetables",
        "filename": "vegetables-v1.0-core-32p.json",
        "title": "Copy to Color: Vegetables",
        "subject_domain": "Vegetables",
    },
]


def validate_single_manifest_data(data: dict, vol_meta: dict, series_catalog: dict) -> None:
    """Rigorous validator function asserting all rules on a single parsed manifest dict."""
    # Top-level required keys
    required_keys = {
        "schema_version", "book_id", "series_id", "edition_id", "title",
        "subtitle", "publisher", "trim", "reverse_page", "minimum_dpi",
        "minimum_safe_margin_in", "asset_registry", "expected_page_count",
        "expected_subjects", "pages",
    }
    missing_keys = required_keys - set(data.keys())
    if missing_keys:
        raise AssertionError(f"Manifest missing required keys: {missing_keys}")

    # Schema & Identifiers
    if data["schema_version"] != "1.0.0":
        raise AssertionError(f"Invalid schema_version: {data['schema_version']}")
    if data["book_id"] != vol_meta["book_id"]:
        raise AssertionError(f"Book ID mismatch: expected {vol_meta['book_id']}, got {data['book_id']}")
    if data["series_id"] != vol_meta["series_id"]:
        raise AssertionError(f"Series ID mismatch: expected {vol_meta['series_id']}, got {data['series_id']}")
    if data["edition_id"] != "v1.0-core-32p":
        raise AssertionError(f"Edition ID mismatch: expected 'v1.0-core-32p', got {data['edition_id']}")
    if data["title"] != vol_meta["title"]:
        raise AssertionError(f"Title mismatch: expected {vol_meta['title']}, got {data['title']}")

    # Publisher imprint exactness
    if data["publisher"] != "The Pivot Digital Publication":
        raise AssertionError(f"Publisher imprint violation: expected 'The Pivot Digital Publication', got '{data['publisher']}'")

    # Physical trim & bleed specifications
    trim = data["trim"]
    if trim.get("width_in") != 8.5:
        raise AssertionError(f"Trim width_in != 8.5: {trim.get('width_in')}")
    if trim.get("height_in") != 11.0:
        raise AssertionError(f"Trim height_in != 11.0: {trim.get('height_in')}")
    if trim.get("bleed") != "all":
        raise AssertionError(f"Trim bleed != 'all': {trim.get('bleed')}")
    if trim.get("page_width_in_with_bleed") != 8.625:
        raise AssertionError(f"Bleed page_width_in != 8.625: {trim.get('page_width_in_with_bleed')}")
    if trim.get("page_height_in_with_bleed") != 11.25:
        raise AssertionError(f"Bleed page_height_in != 11.25: {trim.get('page_height_in_with_bleed')}")

    if data.get("minimum_dpi") != 300:
        raise AssertionError(f"minimum_dpi != 300: {data.get('minimum_dpi')}")
    if data.get("minimum_safe_margin_in") != 0.5:
        raise AssertionError(f"minimum_safe_margin_in != 0.5: {data.get('minimum_safe_margin_in')}")
    if data.get("reverse_page") != "activity_chrome":
        raise AssertionError(f"reverse_page != 'activity_chrome': {data.get('reverse_page')}")

    # Page count assertion
    if data.get("expected_page_count") != 32:
        raise AssertionError(f"expected_page_count != 32: {data.get('expected_page_count')}")
    pages = data.get("pages", [])
    if len(pages) != 32:
        raise AssertionError(f"Page array length != 32: {len(pages)}")

    # Strict sequential page numbering 1..32
    page_numbers = [p.get("number") for p in pages]
    if page_numbers != list(range(1, 33)):
        raise AssertionError(f"Page numbering not strictly 1..32: {page_numbers}")

    # Page 1: welcome
    p1 = pages[0]
    if p1.get("type") != "welcome":
        raise AssertionError(f"Page 1 type != 'welcome': {p1.get('type')}")
    if p1.get("title") != vol_meta["title"]:
        raise AssertionError(f"Page 1 title mismatch: expected '{vol_meta['title']}', got '{p1.get('title')}'")

    # Pages 2..31: copy_to_color (30 activity pages)
    activity_pages = pages[1:31]
    if len(activity_pages) != 30:
        raise AssertionError(f"Expected 30 activity pages (pages 2-31), got {len(activity_pages)}")

    # Cross-reference with SERIES_CATALOG
    vol_key = vol_meta["vol_key"]
    if vol_key not in series_catalog:
        raise AssertionError(f"Volume key {vol_key} not in SERIES_CATALOG")
    catalog_subjects = series_catalog[vol_key]["subjects"]
    if len(catalog_subjects) < 30:
        raise AssertionError(f"SERIES_CATALOG has fewer than 30 subjects for {vol_key}: {len(catalog_subjects)}")

    expected_subjects = data.get("expected_subjects", [])
    if len(expected_subjects) != 30:
        raise AssertionError(f"expected_subjects length != 30: {len(expected_subjects)}")
    if len(set(expected_subjects)) != 30:
        raise AssertionError(f"Duplicate expected_subjects detected in {vol_meta['filename']}: {expected_subjects}")

    # Validate each page 2..31 against SERIES_CATALOG subject
    for idx, (p, (cat_code, cat_word)) in enumerate(zip(activity_pages, catalog_subjects[:30])):
        page_num = idx + 2
        if p.get("number") != page_num:
            raise AssertionError(f"Page number mismatch at index {idx}: expected {page_num}, got {p.get('number')}")
        if p.get("type") != "copy_to_color":
            raise AssertionError(f"Page {page_num} type != 'copy_to_color': {p.get('type')}")

        expected_slug = cat_word.strip().lower().replace(" ", "_")
        if p.get("subject_id") != expected_slug:
            raise AssertionError(f"Page {page_num} subject_id mismatch: expected '{expected_slug}', got '{p.get('subject_id')}'")
        if expected_subjects[idx] != expected_slug:
            raise AssertionError(f"expected_subjects[{idx}] mismatch: expected '{expected_slug}', got '{expected_subjects[idx]}'")

        # Expected letter & banner calculation matching compile_copy_to_color_interior.py
        expected_display_code = cat_code
        if cat_code.isdigit() and cat_word:
            expected_display_code = cat_word.strip()[0].upper()

        if p.get("letter") != expected_display_code:
            raise AssertionError(f"Page {page_num} letter mismatch: expected '{expected_display_code}', got '{p.get('letter')}'")

        clean_subj = cat_word.strip()
        initial_char = expected_display_code[0] if expected_display_code else (clean_subj[0] if clean_subj else "")
        if clean_subj.startswith(f"{initial_char} is for"):
            expected_banner = clean_subj
        elif initial_char and initial_char.isalpha():
            expected_banner = f"{initial_char.upper()} is for {clean_subj.upper()}"
        else:
            expected_banner = clean_subj.upper()

        if p.get("banner") != expected_banner:
            raise AssertionError(f"Page {page_num} banner mismatch: expected '{expected_banner}', got '{p.get('banner')}'")

    # Page 32: certificate
    p32 = pages[31]
    if p32.get("type") != "certificate":
        raise AssertionError(f"Page 32 type != 'certificate': {p32.get('type')}")
    if p32.get("title") != "Super Colorist Award":
        raise AssertionError(f"Page 32 title mismatch: expected 'Super Colorist Award', got '{p32.get('title')}'")

    # Case-insensitive brand rule: zero 'My First'
    raw_json_str = json.dumps(data)
    if "my first" in raw_json_str.lower():
        raise AssertionError(f"Strict brand violation: 'My First' detected in manifest {vol_meta['filename']}")


class AdversarialManifestTestSuite(unittest.TestCase):
    """Automated adversarial stress tests across all 12 series manifests."""

    @classmethod
    def setUpClass(cls):
        cls.manifests_dir = REPO_ROOT / "manifests"
        cls.manifest_data = {}
        for vol in EXPECTED_VOLUMES:
            path = cls.manifests_dir / vol["filename"]
            if path.exists():
                cls.manifest_data[vol["vol_key"]] = json.loads(path.read_text(encoding="utf-8"))

    def test_01_all_12_manifest_files_exist_on_disk(self):
        """Assert all 12 expected manifest files exist on disk with valid file size."""
        for vol in EXPECTED_VOLUMES:
            p = self.manifests_dir / vol["filename"]
            self.assertTrue(p.exists(), f"Missing manifest file: {vol['filename']}")
            self.assertGreater(p.stat().st_size, 1000, f"Manifest file unusually small: {vol['filename']}")

    def test_02_all_12_manifests_parse_valid_json(self):
        """Assert all 12 manifests parse as valid, well-formed JSON without error."""
        for vol in EXPECTED_VOLUMES:
            p = self.manifests_dir / vol["filename"]
            raw_bytes = p.read_bytes()
            # Assert no UTF-8 BOM
            self.assertFalse(raw_bytes.startswith(b"\xef\xbb\xbf"), f"UTF-8 BOM detected in {vol['filename']}")
            try:
                parsed = json.loads(raw_bytes.decode("utf-8"))
            except Exception as e:
                self.fail(f"Failed to parse {vol['filename']} as JSON: {e}")
            self.assertIsInstance(parsed, dict)

    def test_03_exact_32_page_count_contract(self):
        """Assert expected_page_count is exactly 32 and pages list has length 32."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            self.assertEqual(data.get("expected_page_count"), 32, f"expected_page_count != 32 in {vol['filename']}")
            self.assertIsInstance(data.get("expected_page_count"), int)
            self.assertEqual(len(data.get("pages", [])), 32, f"pages list len != 32 in {vol['filename']}")

    def test_04_strictly_sequential_page_numbering(self):
        """Assert page numbers are strictly [1, 2, ..., 32] without gaps, swaps, or duplicates."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            numbers = [p["number"] for p in data["pages"]]
            self.assertEqual(numbers, list(range(1, 33)), f"Page numbering irregular in {vol['filename']}")

    def test_05_page_1_is_welcome_with_canonical_title(self):
        """Assert Page 1 is strictly type 'welcome' with canonical title 'Copy to Color: <Subject>'."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            p1 = data["pages"][0]
            self.assertEqual(p1["number"], 1)
            self.assertEqual(p1["type"], "welcome")
            self.assertEqual(p1["title"], f"Copy to Color: {vol['subject_domain']}")
            self.assertNotIn("my first", p1["title"].lower())

    def test_06_pages_2_to_31_are_copy_to_color_activities(self):
        """Assert Pages 2-31 are strictly type 'copy_to_color' with required non-empty fields."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            activity_pages = data["pages"][1:31]
            self.assertEqual(len(activity_pages), 30)
            for p in activity_pages:
                self.assertEqual(p["type"], "copy_to_color", f"Non-copy_to_color page in {vol['filename']}: {p}")
                self.assertTrue(p.get("subject_id"), f"Empty subject_id in {vol['filename']}: {p}")
                self.assertTrue(p.get("letter"), f"Empty letter in {vol['filename']}: {p}")
                self.assertTrue(p.get("banner"), f"Empty banner in {vol['filename']}: {p}")
                self.assertNotIn("my first", p["banner"].lower())

    def test_07_page_32_is_certificate_super_colorist_award(self):
        """Assert Page 32 is strictly type 'certificate' with title 'Super Colorist Award'."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            p32 = data["pages"][31]
            self.assertEqual(p32["number"], 32)
            self.assertEqual(p32["type"], "certificate")
            self.assertEqual(p32["title"], "Super Colorist Award")

    def test_08_exactly_30_unique_subjects_matching_series_catalog(self):
        """Assert exactly 30 unique subjects matching SERIES_CATALOG in compile_copy_to_color_interior.py."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            vol_key = vol["vol_key"]
            cat_subjects = SERIES_CATALOG[vol_key]["subjects"]
            exp_subjects = data["expected_subjects"]

            self.assertEqual(len(exp_subjects), 30, f"Expected 30 subjects in {vol['filename']}")
            self.assertEqual(len(set(exp_subjects)), 30, f"Duplicate subjects in {vol['filename']}")

            page_subjects = [p["subject_id"] for p in data["pages"][1:31]]
            self.assertEqual(exp_subjects, page_subjects, f"expected_subjects does not match pages 2-31 in {vol['filename']}")

            # Verify exact slug mapping with SERIES_CATALOG
            for idx, (code, word) in enumerate(cat_subjects[:30]):
                expected_slug = word.strip().lower().replace(" ", "_")
                self.assertEqual(exp_subjects[idx], expected_slug,
                                 f"Subject mismatch in {vol['filename']} at index {idx}: expected '{expected_slug}', got '{exp_subjects[idx]}'")

    def test_09_publisher_imprint_strictly_singular(self):
        """Assert publisher imprint is strictly 'The Pivot Digital Publication' with zero trailing whitespace."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            self.assertEqual(data.get("publisher"), "The Pivot Digital Publication",
                             f"Publisher imprint discrepancy in {vol['filename']}")
            self.assertNotIn("Publications", data.get("publisher"))

    def test_10_strict_brand_policy_zero_my_first(self):
        """Assert zero occurrences of 'My First' (case-insensitive) across entire manifest file content."""
        for vol in EXPECTED_VOLUMES:
            p = self.manifests_dir / vol["filename"]
            raw_text = p.read_text(encoding="utf-8")
            self.assertNotIn("my first", raw_text.lower(), f"Forbidden phrase 'My First' found in {vol['filename']}")

    def test_11_cross_manifest_uniqueness(self):
        """Assert all 12 book_ids, series_ids, and titles are distinct across the 12 volumes."""
        book_ids = [self.manifest_data[v["vol_key"]]["book_id"] for v in EXPECTED_VOLUMES]
        series_ids = [self.manifest_data[v["vol_key"]]["series_id"] for v in EXPECTED_VOLUMES]
        titles = [self.manifest_data[v["vol_key"]]["title"] for v in EXPECTED_VOLUMES]

        self.assertEqual(len(set(book_ids)), 12, "Duplicate book_ids found across manifests")
        self.assertEqual(len(set(series_ids)), 12, "Duplicate series_ids found across manifests")
        self.assertEqual(len(set(titles)), 12, "Duplicate titles found across manifests")

    def test_12_kdp_bleed_and_margins_specification(self):
        """Assert physical trim (8.5x11), bleed (8.625x11.25), safe margin (0.5 in), and 300 DPI."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            trim = data["trim"]
            self.assertEqual(trim["width_in"], 8.5)
            self.assertEqual(trim["height_in"], 11.0)
            self.assertEqual(trim["bleed"], "all")
            self.assertEqual(trim["page_width_in_with_bleed"], 8.625)
            self.assertEqual(trim["page_height_in_with_bleed"], 11.25)
            self.assertEqual(data["minimum_dpi"], 300)
            self.assertEqual(data["minimum_safe_margin_in"], 0.5)

    def test_13_validator_function_passes_all_12_manifests(self):
        """Assert validate_single_manifest_data passes cleanly for all 12 manifests."""
        for vol in EXPECTED_VOLUMES:
            data = self.manifest_data[vol["vol_key"]]
            try:
                validate_single_manifest_data(data, vol, SERIES_CATALOG)
            except AssertionError as e:
                self.fail(f"Validation failed for {vol['filename']}: {e}")

    # =========================================================================
    # NEGATIVE / ADVERSARIAL STRESS TESTS (ORACLE VERIFICATION)
    # Proves that our validator actively detects and rejects malformed manifests
    # =========================================================================
    def test_14_adversarial_oracle_detects_wrong_page_count(self):
        """Adversarial Oracle: Test harness must reject manifest with 31 or 33 pages."""
        base_data = copy.deepcopy(self.manifest_data["vol_01"])
        base_vol = EXPECTED_VOLUMES[0]

        # Mutate to 31 pages
        bad_data_31 = copy.deepcopy(base_data)
        bad_data_31["pages"] = bad_data_31["pages"][:31]
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_data_31, base_vol, SERIES_CATALOG)
        self.assertIn("Page array length != 32", str(ctx.exception))

        # Mutate expected_page_count to 31
        bad_data_exp = copy.deepcopy(base_data)
        bad_data_exp["expected_page_count"] = 31
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_data_exp, base_vol, SERIES_CATALOG)
        self.assertIn("expected_page_count != 32", str(ctx.exception))

    def test_15_adversarial_oracle_detects_swapped_or_invalid_page_types(self):
        """Adversarial Oracle: Test harness must reject corrupt Page 1, Page 2, or Page 32 types."""
        base_data = copy.deepcopy(self.manifest_data["vol_02"])
        base_vol = EXPECTED_VOLUMES[1]

        # Mutate Page 1 type from welcome to copy_to_color
        bad_p1 = copy.deepcopy(base_data)
        bad_p1["pages"][0]["type"] = "copy_to_color"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_p1, base_vol, SERIES_CATALOG)
        self.assertIn("Page 1 type != 'welcome'", str(ctx.exception))

        # Mutate Page 2 type from copy_to_color to illustration
        bad_p2 = copy.deepcopy(base_data)
        bad_p2["pages"][1]["type"] = "illustration"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_p2, base_vol, SERIES_CATALOG)
        self.assertIn("Page 2 type != 'copy_to_color'", str(ctx.exception))

        # Mutate Page 32 type from certificate to blank
        bad_p32 = copy.deepcopy(base_data)
        bad_p32["pages"][31]["type"] = "blank"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_p32, base_vol, SERIES_CATALOG)
        self.assertIn("Page 32 type != 'certificate'", str(ctx.exception))

    def test_16_adversarial_oracle_detects_duplicate_or_swapped_subjects(self):
        """Adversarial Oracle: Test harness must reject duplicate or out-of-order subjects."""
        base_data = copy.deepcopy(self.manifest_data["vol_03"])
        base_vol = EXPECTED_VOLUMES[2]

        # Injected duplicate in expected_subjects
        bad_subj = copy.deepcopy(base_data)
        bad_subj["expected_subjects"][1] = bad_subj["expected_subjects"][0]
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_subj, base_vol, SERIES_CATALOG)
        self.assertIn("Duplicate expected_subjects detected", str(ctx.exception))

        # Injected subject mismatch between manifest and SERIES_CATALOG
        bad_page_subj = copy.deepcopy(base_data)
        bad_page_subj["pages"][1]["subject_id"] = "wrong_bird"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_page_subj, base_vol, SERIES_CATALOG)
        self.assertIn("subject_id mismatch", str(ctx.exception))

    def test_17_adversarial_oracle_detects_publisher_imprint_typo(self):
        """Adversarial Oracle: Test harness must reject plural 'Publications' or other typos."""
        base_data = copy.deepcopy(self.manifest_data["vol_04"])
        base_vol = EXPECTED_VOLUMES[3]

        bad_pub = copy.deepcopy(base_data)
        bad_pub["publisher"] = "The Pivot Digital Publications"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_pub, base_vol, SERIES_CATALOG)
        self.assertIn("Publisher imprint violation", str(ctx.exception))

    def test_18_adversarial_oracle_detects_forbidden_phrase_my_first(self):
        """Adversarial Oracle: Test harness must reject any occurrence of 'My First'."""
        base_data = copy.deepcopy(self.manifest_data["vol_05"])
        base_vol = EXPECTED_VOLUMES[4]

        # Injected into title
        bad_title = copy.deepcopy(base_data)
        bad_title["title"] = "My First Copy to Color: Monsters"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_title, base_vol, SERIES_CATALOG)
        self.assertIn("'My First' detected", str(ctx.exception))

        # Injected into banner
        bad_banner = copy.deepcopy(base_data)
        bad_banner["pages"][1]["banner"] = "My First Monster"
        with self.assertRaises(AssertionError) as ctx:
            validate_single_manifest_data(bad_banner, base_vol, SERIES_CATALOG)
        self.assertIn("'My First' detected", str(ctx.exception))


if __name__ == "__main__":
    unittest.main(verbosity=2)
