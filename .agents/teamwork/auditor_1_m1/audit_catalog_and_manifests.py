import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path("d:/pivot-edu-kdp/pivot-digital-edu-kdp")

def audit_catalog():
    print("=== AUDITING CATALOG MASTER ===")
    catalog_path = REPO_ROOT / "catalogs" / "catalog_master.json"
    if not catalog_path.exists():
        print(f"FAIL: {catalog_path} does not exist!")
        return False

    with open(catalog_path, "r", encoding="utf-8") as f:
        content = f.read()
        data = json.loads(content)

    violations = []

    # Check top-level imprint
    imprint = data.get("publisher_imprint")
    if imprint != "The Pivot Digital Publication":
        violations.append(f"Invalid top-level imprint: '{imprint}' (expected 'The Pivot Digital Publication')")

    # Check for prohibited phrase 'my first'
    my_first_matches = re.findall(r"my first", content, re.IGNORECASE)
    if my_first_matches:
        violations.append(f"Found {len(my_first_matches)} occurrences of 'my first' in catalog_master.json")

    # Check for placeholder strings in content (excluding valid words)
    placeholder_patterns = [r"\bTODO\b", r"\bTBD\b", r"\bdummy\b", r"\bplaceholder\b", r"\blorem ipsum\b"]
    for pat in placeholder_patterns:
        matches = re.findall(pat, content, re.IGNORECASE)
        if matches:
            violations.append(f"Found placeholder pattern '{pat}' in catalog_master.json: {matches}")

    expected_editions = [
        ("PIVOT-ALPHABET-001-32P", "Alphabet"),
        ("PIVOT-ANIMALS-002-32P", "Animals"),
        ("PIVOT-BIRDS-003-32P", "Birds"),
        ("PIVOT-SPORTS-004-32P", "Sports"),
        ("PIVOT-MONSTERS-005-32P", "Monsters"),
        ("PIVOT-NUMBERS-006-32P", "Numbers"),
        ("PIVOT-FRUITS-007-32P", "Fruits"),
        ("PIVOT-SHAPES-008-32P", "Shapes"),
        ("PIVOT-TOYS-009-32P", "Toys"),
        ("PIVOT-FLOWERS-010-32P", "Flowers"),
        ("PIVOT-TRANSPORT-011-32P", "Transport"),
        ("PIVOT-VEGETABLES-012-32P", "Vegetables"),
    ]

    raw_editions = data.get("editions", [])
    if isinstance(raw_editions, list):
        editions = {ed.get("book_id"): ed for ed in raw_editions if isinstance(ed, dict)}
    else:
        editions = raw_editions

    allowed_html_tags = {"b", "i", "h3", "ul", "li", "p", "br"}

    for eid, subj in expected_editions:
        if eid not in editions:
            violations.append(f"Missing edition in catalog: {eid}")
            continue

        ed = editions[eid]
        meta = ed.get("metadata", {})
        if not meta:
            violations.append(f"Missing metadata block for {eid}")
            continue

        title = meta.get("title", "")
        expected_title = f"Copy to Color: {subj}"
        if title != expected_title:
            violations.append(f"{eid} title mismatch: '{title}' != '{expected_title}'")

        subtitle = meta.get("subtitle", "")
        if not subtitle or len(subtitle) < 10:
            violations.append(f"{eid} subtitle missing or too short: '{subtitle}'")

        keywords = meta.get("backend_keywords", [])
        if len(keywords) != 7:
            violations.append(f"{eid} has {len(keywords)} keywords (expected 7)")
        if len(set(keywords)) != len(keywords):
            violations.append(f"{eid} has duplicate keywords: {keywords}")

        for ki, kw in enumerate(keywords):
            if len(kw) > 50:
                violations.append(f"{eid} keyword {ki} exceeds 50 chars ({len(kw)}): '{kw}'")
            if any(char in kw for char in ['"', ',', ';']):
                violations.append(f"{eid} keyword {ki} contains punctuation: '{kw}'")
            if len(kw.strip()) < 5:
                violations.append(f"{eid} keyword {ki} suspiciously short: '{kw}'")

        categories = meta.get("category_candidates", [])
        if len(categories) != 2:
            violations.append(f"{eid} has {len(categories)} categories (expected 2)")
        for cat in categories:
            if not cat.startswith("JUVENILE NONFICTION /") and not cat.startswith("JUVENILE FICTION /") and not cat.startswith("GAMES & ACTIVITIES /"):
                violations.append(f"{eid} unusual category: '{cat}'")

        desc = meta.get("description_html", "")
        if not desc or len(desc) < 100:
            violations.append(f"{eid} description too short or missing ({len(desc)} chars)")

        # Validate HTML tags
        tags = re.findall(r"</?([a-zA-Z0-9]+)[^>]*>", desc)
        for tag in tags:
            tag_name = tag.lower().strip()
            if tag_name not in allowed_html_tags:
                violations.append(f"{eid} description contains unapproved HTML tag '<{tag}>'")

    if violations:
        print(f"FAILED with {len(violations)} violations:")
        for v in violations:
            print(f"  - {v}")
        return False
    else:
        print(f"PASS: catalog_master.json metadata is complete, authentic, and compliant across all 12 volumes.")
        return True

def audit_manifests():
    print("\n=== AUDITING MANIFESTS ===")
    manifests_dir = REPO_ROOT / "manifests"
    manifest_files = [
        "alphabet-v1.0-core-32p.json",
        "animals-v1.0-core-32p.json",
        "birds-v1.0-core-32p.json",
        "sports-v1.0-core-32p.json",
        "monsters-v1.0-core-32p.json",
        "numbers-v1.0-core-32p.json",
        "fruits-v1.0-core-32p.json",
        "shapes-v1.0-core-32p.json",
        "toys-v1.0-core-32p.json",
        "flowers-v1.0-core-32p.json",
        "transport-v1.0-core-32p.json",
        "vegetables-v1.0-core-32p.json",
    ]

    violations = []

    for fname in manifest_files:
        fpath = manifests_dir / fname
        if not fpath.exists():
            violations.append(f"Manifest missing: {fname}")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Check 'my first'
        if re.search(r"my first", raw_text, re.IGNORECASE):
            violations.append(f"{fname} contains 'my first'")

        try:
            m = json.loads(raw_text)
        except Exception as e:
            violations.append(f"{fname} invalid JSON: {e}")
            continue

        if m.get("schema_version") != "1.0.0":
            violations.append(f"{fname} schema_version is {m.get('schema_version')} (expected 1.0.0)")

        if m.get("expected_page_count") != 32:
            violations.append(f"{fname} expected_page_count is {m.get('expected_page_count')} (expected 32)")

        pages = m.get("pages", [])
        if len(pages) != 32:
            violations.append(f"{fname} has {len(pages)} pages (expected 32)")

        expected_subjects = m.get("expected_subjects", [])
        if len(expected_subjects) != 30:
            violations.append(f"{fname} has {len(expected_subjects)} expected_subjects (expected 30)")
        if len(set(expected_subjects)) != 30:
            violations.append(f"{fname} has duplicate expected_subjects")

        # Check page 1
        p1 = pages[0] if pages else {}
        if p1.get("number") != 1 or p1.get("type") != "welcome":
            violations.append(f"{fname} page 1 invalid: {p1}")

        # Check page 32
        p32 = pages[31] if len(pages) >= 32 else {}
        if p32.get("number") != 32 or p32.get("type") != "certificate":
            violations.append(f"{fname} page 32 invalid: {p32}")

        # Check pages 2-31
        seen_subjects = set()
        for p_idx, p in enumerate(pages[1:31], start=2):
            if p.get("number") != p_idx:
                violations.append(f"{fname} page {p_idx} has mismatched number: {p.get('number')}")
            if p.get("type") != "copy_to_color":
                violations.append(f"{fname} page {p_idx} has invalid type: {p.get('type')}")
            s_id = p.get("subject_id")
            if not s_id or s_id in seen_subjects:
                violations.append(f"{fname} page {p_idx} has missing or duplicate subject_id: {s_id}")
            seen_subjects.add(s_id)
            if not p.get("letter") or not p.get("banner"):
                violations.append(f"{fname} page {p_idx} missing letter or banner: {p}")

        # Check publisher imprint
        pub = m.get("publisher")
        if pub != "The Pivot Digital Publication":
            violations.append(f"{fname} publisher is '{pub}' (expected 'The Pivot Digital Publication')")

    if violations:
        print(f"FAILED with {len(violations)} violations:")
        for v in violations:
            print(f"  - {v}")
        return False
    else:
        print(f"PASS: all 12 manifests are authentic, complete (32 pages, 30 distinct subjects), and compliant.")
        return True

def audit_compile_script():
    print("\n=== AUDITING COMPILE SCRIPT LINE 522 ===")
    script_path = REPO_ROOT / "scripts" / "compile_copy_to_color_interior.py"
    with open(script_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    line_522 = lines[521] # 0-indexed
    print(f"Line 522: {line_522.strip()}")
    expected = 'copy_str = "© The Pivot Digital Publication. All rights reserved. • Amazon KDP Edition"'
    if line_522.strip() != expected:
        print(f"FAIL: Line 522 does not match expected!\nFound:    {line_522.strip()}\nExpected: {expected}")
        return False

    # Check that 'Publications' (plural) is not used in copyright notice
    if "The Pivot Digital Publications" in "".join(lines):
        print("FAIL: 'The Pivot Digital Publications' found in compile_copy_to_color_interior.py")
        return False

    print("PASS: compile_copy_to_color_interior.py line 522 is genuine and clean.")
    return True

if __name__ == "__main__":
    c_ok = audit_catalog()
    m_ok = audit_manifests()
    s_ok = audit_compile_script()
    if not (c_ok and m_ok and s_ok):
        sys.exit(1)
    print("\nALL FORENSIC CHECKS PASSED.")
    sys.exit(0)

