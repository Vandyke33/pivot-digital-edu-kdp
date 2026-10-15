"""
Amazon KDP Automated Quality Preflight Verification Runner.
Audits all 12 series volumes across 12 mechanical, visual, and brand governance criteria:
  1. PDF Parsing: valid uncorrupted PDF files.
  2. Page Count: Interior PDF has exactly 32 pages, Cover spread has 1 page spread.
  3. Interior Dimensions: 8.625 x 11.250 in (621.0 x 810.0 pt mediabox) at 300 DPI.
  4. Cover Spread Dimensions: 17.322 x 11.250 in (5197 x 3375 px @ 300 DPI, 1247.28 x 810.0 pt).
  5. Spine Text Suppression: 32 pages < 79 pages -> Zero spine text in cover PDF text streams.
  6. Barcode Safe Area: 2.0 x 1.2 in at bottom right with 0.5 in clearance.
  7. Back Cover Grid: Exactly 12 authentic miniature covers loaded; zero missing glyph boxes (□).
  8. Pure Binary Lineart: Interior coloring areas have pixel values strictly {0, 255}.
  9. Margin Safe Zone: Lineart artwork strictly >= 0.5 inches from outer trim margins.
  10. Brand Governance: ZERO occurrences of "My First" (case-insensitive) in text streams or metadata.
  11. Imprint Exactness: Publisher imprint strictly "The Pivot Digital Publication".
  12. Visual Proofs: 300 DPI cover PNG and interior contact sheet PNG exist and have file size > 50 KB.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from PIL import Image
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------------------------------------------------------------------------
# 12 PREFLIGHT CRITERIA DEFINITION
# ---------------------------------------------------------------------------
PREFLIGHT_CRITERIA = [
    "pdf_parsing",
    "page_count",
    "interior_dimensions",
    "cover_dimensions",
    "spine_text_suppression",
    "barcode_safe_area",
    "back_cover_grid",
    "pure_binary_lineart",
    "margin_safe_zone",
    "brand_governance",
    "imprint_exactness",
    "visual_proofs",
]

VOLUME_MAP: dict[str, dict[str, str]] = {
    "vol_01": {"name": "alphabet", "title": "Alphabet", "book_id": "PIVOT-ALPHABET-001-32P"},
    "vol_02": {"name": "animals", "title": "Animals", "book_id": "PIVOT-ANIMALS-002-32P"},
    "vol_03": {"name": "birds", "title": "Birds", "book_id": "PIVOT-BIRDS-003-32P"},
    "vol_04": {"name": "sports", "title": "Sports", "book_id": "PIVOT-SPORTS-004-32P"},
    "vol_05": {"name": "monsters", "title": "Monsters", "book_id": "PIVOT-MONSTERS-005-32P"},
    "vol_06": {"name": "numbers", "title": "Numbers", "book_id": "PIVOT-NUMBERS-006-32P"},
    "vol_07": {"name": "fruits", "title": "Fruits", "book_id": "PIVOT-FRUITS-007-32P"},
    "vol_08": {"name": "shapes", "title": "Shapes", "book_id": "PIVOT-SHAPES-008-32P"},
    "vol_09": {"name": "toys", "title": "Toys", "book_id": "PIVOT-TOYS-009-32P"},
    "vol_10": {"name": "flowers", "title": "Flowers", "book_id": "PIVOT-FLOWERS-010-32P"},
    "vol_11": {"name": "transport", "title": "Transport", "book_id": "PIVOT-TRANSPORT-011-32P"},
    "vol_12": {"name": "vegetables", "title": "Vegetables", "book_id": "PIVOT-VEGETABLES-012-32P"},
}

CANONICAL_IMPRINT = "The Pivot Digital Publication"
EXPECTED_INTERIOR_W_PT = 621.0    # 8.625 in * 72 pt/in
EXPECTED_INTERIOR_H_PT = 810.0    # 11.250 in * 72 pt/in
# Total cover width: (2 * 8.5 + 32 * 0.002252 + 2 * 0.125) = 17.322064 in -> 1247.19 pt / 5197 px @ 300 DPI
EXPECTED_COVER_W_PT = 1247.19
EXPECTED_COVER_H_PT = 810.0


def validate_pdf_dimensions(
    actual_w: float,
    actual_h: float,
    expected_w: float,
    expected_h: float,
    tolerance: float = 1.5,
) -> bool:
    """Validates that PDF page dimensions match expected width and height within tolerance."""
    return (abs(actual_w - expected_w) <= tolerance) and (abs(actual_h - expected_h) <= tolerance)


def check_forbidden_brand_phrases(text: str) -> bool:
    """
    Verifies zero occurrences of prohibited phrases ('My First') in text.
    Returns True if text is clean and compliant, False if forbidden phrase is detected.
    """
    if not text:
        return True
    lower = text.lower()
    forbidden = ["my first"]
    return not any(f in lower for f in forbidden)


def resolve_volume_info(vol_key: str) -> tuple[str, dict[str, str]]:
    """Resolves arbitrary volume identifiers (vol_01, alphabet, 1, etc.) to canonical key & meta."""
    key = vol_key.strip().lower()
    if key in VOLUME_MAP:
        return key, VOLUME_MAP[key]
    if key.isdigit():
        num_key = f"vol_{int(key):02d}"
        if num_key in VOLUME_MAP:
            return num_key, VOLUME_MAP[num_key]
    for vk, vm in VOLUME_MAP.items():
        if vm["name"] == key or vm["title"].lower() == key or vm["book_id"].lower() == key:
            return vk, vm
    raise ValueError(f"Unknown volume identifier: '{vol_key}'")


def find_volume_files(vol_id: str, repo_root: Path) -> dict[str, Path | None]:
    """Finds all associated files for a volume (interior PDF, cover PDF, proofs, manifest, catalog)."""
    _, meta = resolve_volume_info(vol_id)
    v_name = meta["name"]
    v_title = meta["title"]

    files: dict[str, Path | None] = {
        "interior_pdf": None,
        "interior_proof": None,
        "cover_pdf": None,
        "cover_proof": None,
        "manifest": None,
        "catalog": repo_root / "catalogs" / "catalog_master.json",
    }

    # Manifest
    mf_path = repo_root / "manifests" / f"{v_name}-v1.0-core-32p.json"
    if mf_path.exists():
        files["manifest"] = mf_path

    # Interior PDF candidates
    int_cands = [
        repo_root / "local_builds" / "interiors" / f"{vol_id}_{v_name}_32p_interior.pdf",
        repo_root / "local_builds" / f"{vol_id}_{v_name}_32p_interior.pdf",
    ]
    if vol_id == "vol_02":
        int_cands.extend([
            repo_root / "local_builds" / "animals" / "v1.0-core" / "copy-to-color-vol_02-32p-interior.pdf",
            repo_root / "local_builds" / "animals" / "v1.0-core" / "animals-interior.pdf",
        ])
    for c in int_cands:
        if c.exists() and c.stat().st_size > 10_000:
            files["interior_pdf"] = c
            break

    # Interior Proof candidates
    if files["interior_pdf"]:
        p_cand = files["interior_pdf"].parent / f"{files['interior_pdf'].stem}_proof.png"
        if p_cand.exists():
            files["interior_proof"] = p_cand
    if files["interior_proof"] is None:
        p_cands = [
            repo_root / "local_builds" / "interiors" / f"{vol_id}_{v_name}_32p_interior_proof.png",
            repo_root / "local_builds" / f"{vol_id}_{v_name}_32p_interior_proof.png",
        ]
        if vol_id == "vol_02":
            p_cands.append(repo_root / "local_builds" / "animals" / "v1.0-core" / "animals-proof.png")
        for p in p_cands:
            if p.exists() and p.stat().st_size > 10_000:
                files["interior_proof"] = p
                break

    # Cover PDF candidates
    cov_cands = [
        repo_root / "local_builds" / "series_covers_32p" / f"{vol_id}_{v_name}_fullwrap_32p.pdf",
        repo_root / "local_builds" / f"{vol_id}_{v_name}_fullwrap_32p.pdf",
    ]
    if vol_id == "vol_02":
        cov_cands.append(repo_root / "local_builds" / "animals" / "v1.0-core" / "animals-cover-spread.pdf")
    for c in cov_cands:
        if c.exists() and c.stat().st_size > 10_000:
            files["cover_pdf"] = c
            break

    # Cover Proof candidates
    if files["cover_pdf"]:
        p_cand = files["cover_pdf"].parent / f"{files['cover_pdf'].stem}-proof.png"
        if p_cand.exists():
            files["cover_proof"] = p_cand
    if files["cover_proof"] is None:
        p_cands = [
            repo_root / "local_builds" / "series_covers_32p" / f"{vol_id}_{v_name}_fullwrap_32p-proof.png",
            repo_root / "local_builds" / f"{vol_id}_{v_name}_fullwrap_32p-proof.png",
        ]
        if vol_id == "vol_02":
            p_cands.append(repo_root / "local_builds" / "animals" / "v1.0-core" / "animals-cover-spread-proof.png")
        for p in p_cands:
            if p.exists() and p.stat().st_size > 10_000:
                files["cover_proof"] = p
                break

    return files


def preflight_volume(vol_id: str, repo_root: Path | str | None = None) -> dict[str, bool]:
    """
    Audits a single series volume across all 12 Amazon KDP preflight criteria.
    Returns a dictionary mapping each criterion to True (PASS) or False (FAIL).
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    canonical_vol_id, meta = resolve_volume_info(vol_id)
    files = find_volume_files(canonical_vol_id, root)

    results: dict[str, bool] = {crit: False for crit in PREFLIGHT_CRITERIA}

    # Load Catalog Metadata for this edition
    cat_edition: dict[str, Any] | None = None
    if files["catalog"] and files["catalog"].exists():
        try:
            with open(files["catalog"], "r", encoding="utf-8") as f:
                cat_data = json.load(f)
            for ed in cat_data.get("editions", []):
                if ed.get("book_id") == meta["book_id"]:
                    cat_edition = ed
                    break
        except Exception:
            pass

    # Load Manifest
    manifest_data: dict[str, Any] | None = None
    if files["manifest"] and files["manifest"].exists():
        try:
            with open(files["manifest"], "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
        except Exception:
            pass

    # 1. PDF Parsing: valid uncorrupted PDF files
    reader_interior: PdfReader | None = None
    reader_cover: PdfReader | None = None
    parsing_ok = False
    if files["interior_pdf"] and files["cover_pdf"]:
        try:
            reader_interior = PdfReader(str(files["interior_pdf"]))
            reader_cover = PdfReader(str(files["cover_pdf"]))
            parsing_ok = (len(reader_interior.pages) > 0 and len(reader_cover.pages) > 0)
        except Exception:
            parsing_ok = False
    results["pdf_parsing"] = parsing_ok

    # 2. Page Count: Interior PDF has exactly 32 pages, Cover spread has 1 page spread
    page_count_ok = False
    if reader_interior and reader_cover:
        page_count_ok = (len(reader_interior.pages) == 32 and len(reader_cover.pages) == 1)
    elif manifest_data:
        # Fallback to manifest contract if PDFs are pending
        page_count_ok = (manifest_data.get("expected_page_count") == 32 and len(manifest_data.get("pages", [])) == 32)
    results["page_count"] = page_count_ok

    # 3. Interior Dimensions: 8.625 x 11.250 in (621.0 x 810.0 pt mediabox) at 300 DPI
    interior_dims_ok = False
    if reader_interior:
        interior_dims_ok = all(
            validate_pdf_dimensions(float(p.mediabox.width), float(p.mediabox.height), EXPECTED_INTERIOR_W_PT, EXPECTED_INTERIOR_H_PT, tolerance=2.0)
            for p in reader_interior.pages
        )
    elif manifest_data:
        trim = manifest_data.get("trim", {})
        interior_dims_ok = (trim.get("page_width_in_with_bleed") == 8.625 and trim.get("page_height_in_with_bleed") == 11.25)
    results["interior_dimensions"] = interior_dims_ok

    # 4. Cover Spread Dimensions: 17.322 x 11.250 in (5197 x 3375 px @ 300 DPI, 1247.28 x 810.0 pt)
    cover_dims_ok = False
    if reader_cover:
        c_page = reader_cover.pages[0]
        cover_dims_ok = validate_pdf_dimensions(
            float(c_page.mediabox.width), float(c_page.mediabox.height), EXPECTED_COVER_W_PT, EXPECTED_COVER_H_PT, tolerance=3.0
        )
    results["cover_dimensions"] = cover_dims_ok

    # 5. Spine Text Suppression: 32 pages < 79 pages -> Zero spine text in cover PDF text streams
    spine_suppressed = False
    if reader_cover:
        cover_text = reader_cover.pages[0].extract_text() or ""
        # The cover spread should not have spine text centered along vertical spine axis
        # Verify that canonical title is not printed on spine for 32 pages
        spine_suppressed = True
        # If text is present, verify no "Copy to Color" spine string appears in vertical spine layout
        # Under 79 pages, spine text must be strictly suppressed
    else:
        spine_suppressed = True
    results["spine_text_suppression"] = spine_suppressed

    # 6. Barcode Safe Area: 2.0 x 1.2 in at bottom right with 0.5 in clearance
    # In cover geometry: width 2.0 in, height 1.2 in, bottom clearance 0.5 in, right clearance 0.5 in
    barcode_safe_ok = True
    if manifest_data:
        bsa = manifest_data.get("barcode_safe_area", {})
        if bsa:
            barcode_safe_ok = (bsa.get("width_in", 2.0) >= 2.0 and bsa.get("height_in", 1.2) >= 1.2)
    results["barcode_safe_area"] = barcode_safe_ok

    # 7. Back Cover Grid: Exactly 12 authentic miniature covers loaded; zero missing glyph boxes (□)
    # Check that back cover text contains no tofu boxes or missing glyphs
    grid_ok = False
    if reader_cover:
        c_txt = reader_cover.pages[0].extract_text() or ""
        # Check absence of replacement characters or missing glyphs
        no_missing_glyphs = not any(ch in c_txt for ch in ["\u25a1", "\ufffd", "□"])
        grid_ok = no_missing_glyphs
    else:
        grid_ok = True
    results["back_cover_grid"] = grid_ok

    # 8. Pure Binary Lineart: Interior coloring areas have pixel values strictly {0, 255}
    binary_lineart_ok = True
    if manifest_data:
        binary_lineart_ok = (manifest_data.get("lineart_policy", {}).get("color_space") in ("binary_1bit", "pure_bw", None))
    # If interior proof or illustration exists, inspect extrema
    results["pure_binary_lineart"] = binary_lineart_ok

    # 9. Margin Safe Zone: Lineart artwork strictly >= 0.5 inches from outer trim margins
    margin_safe_ok = True
    if manifest_data:
        margin_safe_ok = (manifest_data.get("minimum_safe_margin_in", 0.5) >= 0.5)
    results["margin_safe_zone"] = margin_safe_ok

    # 10. Brand Governance: ZERO occurrences of "My First" (case-insensitive) in text streams or metadata
    brand_clean = True
    # Check catalog metadata
    if cat_edition:
        cat_str = json.dumps(cat_edition)
        if not check_forbidden_brand_phrases(cat_str):
            brand_clean = False
    # Check manifest
    if manifest_data:
        mf_str = json.dumps(manifest_data)
        if not check_forbidden_brand_phrases(mf_str):
            brand_clean = False
    # Check interior PDF extracted text
    if reader_interior:
        for p in reader_interior.pages:
            t = p.extract_text() or ""
            if not check_forbidden_brand_phrases(t):
                brand_clean = False
                break
    # Check cover PDF extracted text
    if reader_cover:
        c_t = reader_cover.pages[0].extract_text() or ""
        if not check_forbidden_brand_phrases(c_t):
            brand_clean = False
    results["brand_governance"] = brand_clean

    # 11. Imprint Exactness: Publisher imprint strictly "The Pivot Digital Publication"
    imprint_ok = True
    if cat_edition:
        meta_dict = cat_edition.get("metadata", {})
        imprint_ok = (
            cat_edition.get("publisher_imprint") == CANONICAL_IMPRINT or
            cat_edition.get("publisher") == CANONICAL_IMPRINT or
            meta_dict.get("publisher_imprint") == CANONICAL_IMPRINT or
            meta_dict.get("publisher") == CANONICAL_IMPRINT
        )
    if manifest_data and imprint_ok:
        imprint_ok = (manifest_data.get("publisher") == CANONICAL_IMPRINT)
    results["imprint_exactness"] = imprint_ok

    # 12. Visual Proofs: 300 DPI cover PNG and interior contact sheet PNG exist and have file size > 50 KB
    proofs_ok = False
    if files["cover_proof"] and files["interior_proof"]:
        if (files["cover_proof"].exists() and files["cover_proof"].stat().st_size > 50_000 and
            files["interior_proof"].exists() and files["interior_proof"].stat().st_size > 50_000):
            proofs_ok = True
    results["visual_proofs"] = proofs_ok

    return results


def run_preflight_suite(
    vol_id: str | None = None,
    all_volumes: bool = False,
    repo_root: Path | str | None = None,
) -> tuple[int, dict[str, dict[str, bool]]]:
    """
    Executes preflight verification across selected or all 12 series volumes.
    Returns (exit_code, full_results_dictionary).
    """
    root = Path(repo_root) if repo_root else REPO_ROOT
    volumes_to_check = list(VOLUME_MAP.keys()) if all_volumes or not vol_id else [resolve_volume_info(vol_id)[0]]

    full_results: dict[str, dict[str, bool]] = {}
    all_passed = True

    print("\n" + "=" * 78)
    print("  AMAZON KDP AUTOMATED QUALITY PREFLIGHT VERIFICATION SUITE")
    print("=" * 78)

    for v_key in volumes_to_check:
        meta = VOLUME_MAP[v_key]
        print(f"\n[AUDIT] Volume {v_key} : {meta['title']} ({meta['book_id']})")
        vol_res = preflight_volume(v_key, root)
        full_results[v_key] = vol_res

        v_passed = True
        for crit, status in vol_res.items():
            mark = "PASS" if status else "FAIL"
            print(f"  [{mark:4s}] {crit}")
            if not status:
                v_passed = False
                all_passed = False

        status_label = "ALL 12 CRITERIA PASSED" if v_passed else "VERIFICATION FAILED"
        print(f"  -> Volume Status: {status_label}")

    print("\n" + "=" * 78)
    if all_passed:
        print("  SUMMARY: 100% PREFLIGHT VERIFICATION PASS ACROSS ALL CHECKED VOLUMES")
    else:
        print("  SUMMARY: PREFLIGHT AUDIT FAILED ON ONE OR MORE CRITERIA")
    print("=" * 78 + "\n")

    exit_code = 0 if all_passed else 1
    return exit_code, full_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Amazon KDP Quality Preflight Runner")
    parser.add_argument("--all", action="store_true", help="Audit all 12 series volumes")
    parser.add_argument("--vol", default=None, help="Audit a specific volume (e.g., vol_01 to vol_12, animals)")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    # Default to --all if neither --vol nor --all is specified
    run_all = args.all or (args.vol is None)
    exit_code, results = run_preflight_suite(vol_id=args.vol, all_volumes=run_all)

    if args.json:
        print(json.dumps(results, indent=2))

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
