"""Independent verification script by reviewer_2_m1."""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.compile_copy_to_color_interior import SERIES_CATALOG

VOLUMES = [
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

def verify_all():
    errors = []
    warnings = []

    # 1. Benchmark manifest
    benchmark_path = REPO_ROOT / "manifests" / "animals-v1.0-core-32p.json"
    if not benchmark_path.exists():
        errors.append(f"Benchmark manifest missing: {benchmark_path}")
        return errors, warnings
    
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    benchmark_keys = set(benchmark.keys())

    print(f"Loaded benchmark {benchmark_path.name} with keys: {sorted(benchmark_keys)}")

    # 2. Check each manifest
    for vol_key, fname, book_id, subject_title in VOLUMES:
        m_path = REPO_ROOT / "manifests" / fname
        if not m_path.exists():
            errors.append(f"Manifest missing: {fname}")
            continue

        raw = m_path.read_text(encoding="utf-8")
        if "my first" in raw.lower():
            errors.append(f"Forbidden phrase 'my first' found in {fname}")

        m = json.loads(raw)
        m_keys = set(m.keys())
        if m_keys != benchmark_keys:
            errors.append(f"Keys mismatch in {fname}: got {sorted(m_keys)}, expected {sorted(benchmark_keys)}")

        if m.get("schema_version") != "1.0.0":
            errors.append(f"{fname}: schema_version is {m.get('schema_version')}, expected '1.0.0'")
        if m.get("book_id") != book_id:
            errors.append(f"{fname}: book_id is {m.get('book_id')}, expected '{book_id}'")
        if m.get("edition_id") != "v1.0-core-32p":
            errors.append(f"{fname}: edition_id is {m.get('edition_id')}, expected 'v1.0-core-32p'")
        if m.get("title") != f"Copy to Color: {subject_title}":
            errors.append(f"{fname}: title is '{m.get('title')}', expected 'Copy to Color: {subject_title}'")
        if m.get("publisher") != "The Pivot Digital Publication":
            errors.append(f"{fname}: publisher is '{m.get('publisher')}', expected 'The Pivot Digital Publication'")
        if m.get("expected_page_count") != 32:
            errors.append(f"{fname}: expected_page_count is {m.get('expected_page_count')}, expected 32")

        trim = m.get("trim", {})
        if trim.get("width_in") != 8.5 or trim.get("height_in") != 11.0:
            errors.append(f"{fname}: trim dimensions mismatch {trim}")
        if trim.get("bleed") != "all":
            errors.append(f"{fname}: trim bleed is '{trim.get('bleed')}', expected 'all'")
        if trim.get("page_width_in_with_bleed") != 8.625 or trim.get("page_height_in_with_bleed") != 11.25:
            errors.append(f"{fname}: bleed dimensions mismatch {trim}")

        if m.get("minimum_dpi") != 300:
            errors.append(f"{fname}: minimum_dpi is {m.get('minimum_dpi')}, expected 300")
        if m.get("minimum_safe_margin_in") != 0.5:
            errors.append(f"{fname}: minimum_safe_margin_in is {m.get('minimum_safe_margin_in')}, expected 0.5")

        # Check subjects against SERIES_CATALOG
        catalog_entry = SERIES_CATALOG.get(vol_key)
        if not catalog_entry:
            errors.append(f"No SERIES_CATALOG entry for {vol_key}")
            continue

        cat_subjects = catalog_entry["subjects"][:30]
        exp_subjects = m.get("expected_subjects", [])
        if len(exp_subjects) != 30:
            errors.append(f"{fname}: expected_subjects length is {len(exp_subjects)}, expected 30")
        if len(set(exp_subjects)) != 30:
            errors.append(f"{fname}: expected_subjects contains duplicates: {len(exp_subjects)} total, {len(set(exp_subjects))} unique")

        # Compare slugs with catalog
        cat_slugs = [w.strip().lower().replace(" ", "_") for _, w in cat_subjects]
        if exp_subjects != cat_slugs:
            errors.append(f"{fname}: expected_subjects does not match SERIES_CATALOG slugs")

        # Check pages
        pages = m.get("pages", [])
        if len(pages) != 32:
            errors.append(f"{fname}: pages count is {len(pages)}, expected 32")

        # Page 1
        p1 = pages[0]
        if p1.get("number") != 1 or p1.get("type") != "welcome" or p1.get("title") != f"Copy to Color: {subject_title}":
            errors.append(f"{fname}: page 1 mismatch {p1}")

        # Pages 2..31
        for idx, p in enumerate(pages[1:31], start=1):
            expected_page_num = idx + 1
            if p.get("number") != expected_page_num:
                errors.append(f"{fname}: page index {idx} has number {p.get('number')}, expected {expected_page_num}")
            if p.get("type") != "copy_to_color":
                errors.append(f"{fname}: page {expected_page_num} has type '{p.get('type')}', expected 'copy_to_color'")
            subj_id = p.get("subject_id")
            if subj_id != exp_subjects[idx - 1]:
                errors.append(f"{fname}: page {expected_page_num} subject_id '{subj_id}' != expected '{exp_subjects[idx - 1]}'")
            if not p.get("letter"):
                errors.append(f"{fname}: page {expected_page_num} missing letter")
            if not p.get("banner"):
                errors.append(f"{fname}: page {expected_page_num} missing banner")
            if "my first" in str(p.get("banner")).lower():
                errors.append(f"{fname}: page {expected_page_num} banner contains 'my first': {p.get('banner')}")

        # Page 32
        p32 = pages[31]
        if p32.get("number") != 32 or p32.get("type") != "certificate" or p32.get("title") != "Super Colorist Award":
            errors.append(f"{fname}: page 32 mismatch {p32}")

    # 3. Check catalog_master.json
    cat_path = REPO_ROOT / "catalogs" / "catalog_master.json"
    cat_raw = cat_path.read_text(encoding="utf-8")
    if "my first" in cat_raw.lower():
        errors.append("Forbidden phrase 'my first' found in catalog_master.json")

    cat_json = json.loads(cat_raw)
    if cat_json.get("publisher_imprint") != "The Pivot Digital Publication":
        errors.append(f"Top-level publisher_imprint is '{cat_json.get('publisher_imprint')}', expected 'The Pivot Digital Publication'")

    editions = {ed["book_id"]: ed for ed in cat_json.get("editions", [])}
    allowed_html_tags = {"b", "i", "h3", "ul", "li", "p", "br"}

    for vol_key, fname, book_id, subject_title in VOLUMES:
        if book_id not in editions:
            errors.append(f"Edition {book_id} missing from catalog_master.json")
            continue
        ed = editions[book_id]
        if ed.get("title") != f"Copy to Color: {subject_title}":
            errors.append(f"Catalog {book_id}: title '{ed.get('title')}' != 'Copy to Color: {subject_title}'")
        if ed.get("subtitle") != f"Interactive Early Learning {subject_title} Coloring Activity Book for Ages 3-5":
            errors.append(f"Catalog {book_id}: subtitle mismatch: '{ed.get('subtitle')}'")
        
        meta = ed.get("metadata")
        if not meta:
            errors.append(f"Catalog {book_id}: missing 'metadata' block")
            continue

        if meta.get("publisher_imprint") != "The Pivot Digital Publication":
            errors.append(f"Catalog {book_id}: meta publisher_imprint '{meta.get('publisher_imprint')}' != 'The Pivot Digital Publication'")

        kws = meta.get("backend_keywords", [])
        if len(kws) != 7:
            errors.append(f"Catalog {book_id}: expected 7 keywords, got {len(kws)}")
        if len(set(kws)) != 7:
            errors.append(f"Catalog {book_id}: duplicate keywords found: {kws}")
        for kw in kws:
            if len(kw) > 50:
                errors.append(f"Catalog {book_id}: keyword '{kw}' exceeds 50 chars ({len(kw)})")
            for b in [",", '"', ";"]:
                if b in kw:
                    errors.append(f"Catalog {book_id}: banned character '{b}' in keyword '{kw}'")
            if "my first" in kw.lower():
                errors.append(f"Catalog {book_id}: 'my first' in keyword '{kw}'")

        cats = meta.get("category_candidates", [])
        if len(cats) != 2:
            errors.append(f"Catalog {book_id}: expected 2 categories, got {len(cats)}")

        desc = meta.get("description_html", "")
        if len(desc) < 100:
            errors.append(f"Catalog {book_id}: description_html too short ({len(desc)})")
        tags = re.findall(r"</?([a-zA-Z0-9]+)[^>]*>", desc)
        for t in tags:
            if t.lower() not in allowed_html_tags:
                errors.append(f"Catalog {book_id}: disallowed HTML tag <{t}> in description")

    # 4. Check compile_copy_to_color_interior.py line 522
    interior_script = REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py"
    interior_code = interior_script.read_text(encoding="utf-8")
    if "© The Pivot Digital Publications" in interior_code:
        errors.append("compile_copy_to_color_interior.py still contains plural 'The Pivot Digital Publications'")
    if "© The Pivot Digital Publication. All rights reserved." not in interior_code:
        errors.append("compile_copy_to_color_interior.py does not contain expected singular copyright string")

    return errors, warnings

if __name__ == "__main__":
    errs, warns = verify_all()
    print(f"\nVerification Results: {len(errs)} errors, {len(warns)} warnings.")
    if errs:
        print("\nERRORS:")
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n[ALL CHECKS PASSED PERFECTLY]")
        sys.exit(0)
