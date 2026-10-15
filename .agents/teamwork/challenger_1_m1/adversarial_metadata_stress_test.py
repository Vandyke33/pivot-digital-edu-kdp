"""
Adversarial Metadata & Governance Stress Test Harness
Challenger: challenger_1_m1 (Adversarial Metadata Challenger)
Target: catalogs/catalog_master.json, scripts/compile_copy_to_color_interior.py, manifests/*.json
"""

import html.parser
import json
import os
import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
CATALOG_PATH = REPO_ROOT / "catalogs" / "catalog_master.json"
INTERIOR_SCRIPT_PATH = REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py"
MANIFESTS_DIR = REPO_ROOT / "manifests"

EXPECTED_SERIES_IDS = [
    "copy_to_color_alphabet",
    "copy_to_color_animals",
    "copy_to_color_birds",
    "copy_to_color_sports",
    "copy_to_color_monsters",
    "copy_to_color_numbers",
    "copy_to_color_fruits",
    "copy_to_color_shapes",
    "copy_to_color_toys",
    "copy_to_color_flowers",
    "copy_to_color_transport",
    "copy_to_color_vegetables",
]

ALLOWED_HTML_TAGS = {"b", "i", "h3", "ul", "li", "p", "br"}
BANNED_KEYWORD_CHARS = {'"', ",", ";", "\n", "\r", "\t", "{", "}", "[", "]", "<", ">", "\\"}

# Explicit Amazon promotional claims that violate KDP policies
PROMOTIONAL_PRICE_CLAIMS = {
    "best seller", "bestseller", "discount", "cheap",
    "kindle unlimited", "sale", "guarantee", "guaranteed", "top rated"
}


class KDPHTMLValidator(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags_found = []
        self.disallowed_tags = []
        self.attributes_found = []
        self.tag_stack = []
        self.mismatched_tags = []

    def handle_starttag(self, tag, attrs):
        self.tags_found.append(tag)
        if tag.lower() not in ALLOWED_HTML_TAGS:
            self.disallowed_tags.append(tag)
        if attrs:
            # Amazon KDP description HTML strictly forbids attributes (e.g. style, class, onclick)
            self.attributes_found.append((tag, attrs))
        if tag.lower() != "br":
            self.tag_stack.append(tag.lower())

    def handle_endtag(self, tag):
        if tag.lower() == "br":
            return
        if self.tag_stack and self.tag_stack[-1] == tag.lower():
            self.tag_stack.pop()
        else:
            self.mismatched_tags.append((tag, list(self.tag_stack)))


class AdversarialMetadataStressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        self = cls
        self.assertTrue(CATALOG_PATH.exists(), f"Missing catalog file: {CATALOG_PATH}")
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            self.catalog_data = json.load(f)
            self.catalog_raw_text = CATALOG_PATH.read_text(encoding="utf-8")

        self.c2c_editions = [
            ed for ed in self.catalog_data.get("editions", [])
            if ed.get("series_id") in EXPECTED_SERIES_IDS
        ]

    def test_01_all_12_volumes_present_in_catalog(self):
        """Stress Test 1: Verify exactly 12 Copy to Color series editions exist in catalog."""
        found_series_ids = [ed.get("series_id") for ed in self.c2c_editions]
        self.assertEqual(
            len(self.c2c_editions), 12,
            f"Expected exactly 12 Copy to Color editions, found {len(self.c2c_editions)}"
        )
        self.assertEqual(
            sorted(found_series_ids), sorted(EXPECTED_SERIES_IDS),
            f"Mismatch in series_ids: {set(EXPECTED_SERIES_IDS) ^ set(found_series_ids)}"
        )

    def test_02_backend_keywords_count_and_length(self):
        """Stress Test 2: Assert all 84 backend keywords are <= 50 chars and <= 50 bytes."""
        total_keywords = 0
        violations = []
        kw_lengths = []

        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            meta = ed.get("metadata", {})
            keywords = meta.get("backend_keywords", [])

            self.assertEqual(
                len(keywords), 7,
                f"Volume {series_id} has {len(keywords)} keywords, expected exactly 7."
            )

            for i, kw in enumerate(keywords, 1):
                total_keywords += 1
                char_len = len(kw)
                byte_len = len(kw.encode("utf-8"))
                kw_lengths.append(char_len)

                # Amazon KDP imposes a strict 50 character limit per keyword field
                if char_len > 50:
                    violations.append(
                        f"[{series_id}] Keyword #{i} length EXCEEDS 50 chars ({char_len}): '{kw}'"
                    )
                if byte_len > 50:
                    violations.append(
                        f"[{series_id}] Keyword #{i} UTF-8 byte size EXCEEDS 50 bytes ({byte_len}): '{kw}'"
                    )
                if char_len < 3:
                    violations.append(f"[{series_id}] Keyword #{i} is suspiciously short ({char_len}): '{kw}'")
                if kw.strip() != kw:
                    violations.append(f"[{series_id}] Keyword #{i} has unstripped whitespace: '{kw}'")
                if "  " in kw:
                    violations.append(f"[{series_id}] Keyword #{i} contains consecutive double spaces: '{kw}'")

        print(f"\n[Keyword Stats] Total: {total_keywords}, Min: {min(kw_lengths)}, Max: {max(kw_lengths)}, Avg: {sum(kw_lengths)/len(kw_lengths):.1f}")
        self.assertEqual(total_keywords, 84, f"Expected 84 total keywords, checked {total_keywords}")
        self.assertFalse(violations, f"Keyword length violations found:\n" + "\n".join(violations))

    def test_03_keyword_banned_punctuation_and_uniqueness(self):
        """Stress Test 3: Assert no keyword contains banned punctuation or duplicate within volume."""
        violations = []
        advisory_flags = []

        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            keywords = ed.get("metadata", {}).get("backend_keywords", [])
            seen_kws = set()

            for i, kw in enumerate(keywords, 1):
                # Check for banned punctuation characters
                for char in BANNED_KEYWORD_CHARS:
                    if char in kw:
                        violations.append(
                            f"[{series_id}] Keyword #{i} contains banned char {repr(char)}: '{kw}'"
                        )

                # Check for forbidden promotional/marketing claims
                kw_lower = kw.lower()
                for claim in PROMOTIONAL_PRICE_CLAIMS:
                    if claim in kw_lower:
                        violations.append(
                            f"[{series_id}] Keyword #{i} contains prohibited KDP claim '{claim}': '{kw}'"
                        )

                # Check duplicate keywords in same volume
                kw_norm = kw.lower().strip()
                if kw_norm in seen_kws:
                    violations.append(f"[{series_id}] Duplicate keyword in volume: '{kw}'")
                seen_kws.add(kw_norm)

                # Advisory check for 'screen free' containing 'free'
                if "screen free" in kw_lower:
                    advisory_flags.append(f"[{series_id}] '{kw}' contains 'screen free'")

        if advisory_flags:
            print(f"\n[Advisory Note] Found {len(advisory_flags)} keywords using educational 'screen free':")
            for flag in advisory_flags:
                print("  - " + flag)

        self.assertFalse(violations, f"Keyword content violations found:\n" + "\n".join(violations))

    def test_04_html_description_tag_whitelist_and_syntax(self):
        """Stress Test 4: Parse all HTML descriptions with HTMLParser, asserting ONLY allowed tags and zero attributes."""
        tag_violations = []
        attr_violations = []
        parse_errors = []
        length_violations = []

        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            meta = ed.get("metadata", {})
            html_desc = meta.get("description_html")

            self.assertIsNotNone(html_desc, f"Missing description_html in {series_id}")

            # KDP allows up to 4000 characters
            desc_len = len(html_desc)
            if desc_len < 100 or desc_len > 4000:
                length_violations.append(f"[{series_id}] Description length {desc_len} outside [100, 4000] range")

            parser = KDPHTMLValidator()
            try:
                parser.feed(html_desc)
                parser.close()
            except Exception as e:
                parse_errors.append(f"[{series_id}] HTML parser error: {e}")

            if parser.disallowed_tags:
                tag_violations.append(
                    f"[{series_id}] Disallowed tags {parser.disallowed_tags} in: {html_desc[:80]}..."
                )

            if parser.attributes_found:
                attr_violations.append(
                    f"[{series_id}] Disallowed attributes {parser.attributes_found} in description."
                )

            # Check that tag stack is empty (all non-void tags properly closed)
            if parser.tag_stack:
                tag_violations.append(
                    f"[{series_id}] Unclosed tags remaining in stack: {parser.tag_stack}"
                )

            # Check required descriptive sections
            self.assertIn("8.5 x 11", html_desc, f"[{series_id}] Missing trim specification in HTML description")
            self.assertIn("32 pages", html_desc, f"[{series_id}] Missing 32-page specification in HTML description")
            self.assertIn("The Pivot Digital Publication", html_desc, f"[{series_id}] Missing publisher imprint in HTML description")
            self.assertIn("Copy to Color", html_desc, f"[{series_id}] Missing series name in HTML description")

        self.assertFalse(length_violations, f"Description length violations:\n" + "\n".join(length_violations))
        self.assertFalse(parse_errors, f"HTML parsing errors:\n" + "\n".join(parse_errors))
        self.assertFalse(tag_violations, f"HTML tag whitelist violations:\n" + "\n".join(tag_violations))
        self.assertFalse(attr_violations, f"HTML attribute violations:\n" + "\n".join(attr_violations))

    def test_05_publisher_imprint_zero_publications(self):
        """Stress Test 5: Verify zero occurrences of plural 'Publications' across catalog and interior code."""
        # Check raw catalog text
        catalog_matches = re.findall(r'["\'].*?publications.*?["\']', self.catalog_raw_text, re.IGNORECASE)
        self.assertEqual(
            catalog_matches, [],
            f"Found 'Publications' plural in catalog_master.json: {catalog_matches}"
        )

        # Check top-level catalog imprint
        top_imprint = self.catalog_data.get("publisher_imprint")
        self.assertEqual(
            top_imprint, "The Pivot Digital Publication",
            f"Unexpected top-level publisher imprint: '{top_imprint}'"
        )

        # Check each edition's publisher_imprint
        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            imprint = ed.get("metadata", {}).get("publisher_imprint")
            self.assertEqual(
                imprint, "The Pivot Digital Publication",
                f"Mismatch in edition {series_id} imprint: '{imprint}'"
            )

        # Check compile_copy_to_color_interior.py
        interior_code = INTERIOR_SCRIPT_PATH.read_text(encoding="utf-8")
        interior_matches = re.findall(r'["\'].*?publications.*?["\']', interior_code, re.IGNORECASE)
        self.assertEqual(
            interior_matches, [],
            f"Found 'Publications' plural in compile_copy_to_color_interior.py: {interior_matches}"
        )

        # Specifically check line 522 area in compile_copy_to_color_interior.py
        lines = interior_code.splitlines()
        line_522_area = "\n".join(lines[515:530])
        self.assertNotIn(
            "Publications", line_522_area,
            f"Line 522 area still contains 'Publications':\n{line_522_area}"
        )
        self.assertIn(
            "© The Pivot Digital Publication. All rights reserved.", line_522_area,
            "Line 522 does not contain expected singular copyright string."
        )

    def test_06_brand_governance_zero_my_first(self):
        """Stress Test 6: Verify zero occurrences of 'My First' case-insensitively across metadata and manifests."""
        # 1. Search raw catalog_master.json text
        self.assertNotIn(
            "my first", self.catalog_raw_text.lower(),
            "Found 'my first' in catalog_master.json!"
        )

        # 2. Search all 12 manifests
        manifest_files = list(MANIFESTS_DIR.glob("*-v1.0-core-32p.json"))
        self.assertEqual(
            len(manifest_files), 12,
            f"Expected 12 32p manifests, found {len(manifest_files)}"
        )
        for mf in manifest_files:
            content = mf.read_text(encoding="utf-8")
            self.assertNotIn(
                "my first", content.lower(),
                f"Forbidden phrase 'my first' found in manifest {mf.name}"
            )

        # 3. Check parsed titles and subtitles in catalog
        for ed in self.c2c_editions:
            title = ed.get("title", "")
            subtitle = ed.get("subtitle", "")
            meta = ed.get("metadata", {})
            meta_title = meta.get("title", "")
            meta_subtitle = meta.get("subtitle", "")
            desc = meta.get("description_html", "")

            for field_name, val in [
                ("title", title),
                ("subtitle", subtitle),
                ("meta_title", meta_title),
                ("meta_subtitle", meta_subtitle),
                ("description_html", desc)
            ]:
                self.assertNotIn(
                    "my first", val.lower(),
                    f"Forbidden phrase 'my first' in {ed.get('series_id')} field {field_name}"
                )

    def test_07_manifest_schema_and_page_structure(self):
        """Stress Test 7: Assert all 12 manifests have exact 32-page structure and 30 unique subjects."""
        for expected_id in EXPECTED_SERIES_IDS:
            vol_name = expected_id.replace("copy_to_color_", "")
            manifest_path = MANIFESTS_DIR / f"{vol_name}-v1.0-core-32p.json"
            self.assertTrue(manifest_path.exists(), f"Manifest missing: {manifest_path}")

            with open(manifest_path, "r", encoding="utf-8") as f:
                mf = json.load(f)

            self.assertEqual(mf.get("expected_page_count"), 32, f"Expected 32 pages in {manifest_path}")
            self.assertEqual(mf.get("publisher"), "The Pivot Digital Publication")
            self.assertNotIn("Publications", mf.get("publisher", ""))

            pages = mf.get("pages", [])
            self.assertEqual(len(pages), 32, f"Manifest {manifest_path} pages count != 32")

            # Page 1: welcome
            self.assertEqual(pages[0].get("type"), "welcome")

            # Pages 2 to 31: 30 copy_to_color pages
            subjects_in_pages = []
            for p_num in range(2, 32):
                p = pages[p_num - 1]
                self.assertEqual(p.get("number"), p_num, f"Page number mismatch on page {p_num} in {manifest_path}")
                self.assertEqual(p.get("type"), "copy_to_color")
                sub_id = p.get("subject_id")
                self.assertTrue(sub_id, f"Missing subject_id on page {p_num} in {manifest_path}")
                subjects_in_pages.append(sub_id)

            # Check for uniqueness: exactly 30 unique subjects
            self.assertEqual(
                len(set(subjects_in_pages)), 30,
                f"Duplicate subjects detected in {manifest_path}: {subjects_in_pages}"
            )

            # Check expected_subjects field matches
            expected_subjects = mf.get("expected_subjects", [])
            self.assertEqual(
                subjects_in_pages, expected_subjects,
                f"Mismatch between pages subjects and expected_subjects in {manifest_path}"
            )

            # Page 32: certificate
            self.assertEqual(pages[31].get("type"), "certificate")

    def test_08_category_candidates_validity(self):
        """Stress Test 8: Assert every volume has exactly 2 valid BISAC category paths."""
        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            cats = ed.get("metadata", {}).get("category_candidates", [])
            self.assertEqual(
                len(cats), 2,
                f"Volume {series_id} has {len(cats)} categories, expected 2"
            )
            for cat in cats:
                self.assertTrue(isinstance(cat, str) and len(cat.strip()) > 5)
                self.assertTrue("/" in cat, f"Invalid BISAC format: '{cat}' in {series_id}")

    def test_09_catalog_and_manifest_synchronization(self):
        """Stress Test 9: Assert 100% synchronization between catalog_master.json and manifests/*.json."""
        for ed in self.c2c_editions:
            series_id = ed.get("series_id")
            vol_name = series_id.replace("copy_to_color_", "")
            manifest_path = MANIFESTS_DIR / f"{vol_name}-v1.0-core-32p.json"

            with open(manifest_path, "r", encoding="utf-8") as f:
                mf = json.load(f)

            # Verify synchronization of key attributes
            self.assertEqual(ed.get("book_id"), mf.get("book_id"), f"Mismatch in book_id for {series_id}")
            self.assertEqual(ed.get("title"), mf.get("title"), f"Mismatch in title for {series_id}")
            self.assertEqual(ed.get("subtitle"), mf.get("subtitle"), f"Mismatch in subtitle for {series_id}")
            self.assertEqual(
                ed.get("metadata", {}).get("publisher_imprint"),
                mf.get("publisher"),
                f"Mismatch in publisher for {series_id}"
            )
            self.assertEqual(
                ed.get("print_specifications", {}).get("planned_page_count"),
                mf.get("expected_page_count"),
                f"Mismatch in page count for {series_id}"
            )


if __name__ == "__main__":
    unittest.main()
