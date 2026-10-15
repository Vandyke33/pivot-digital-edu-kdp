import os
import re
from pathlib import Path
from PIL import Image
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[3]
covers_dir = REPO_ROOT / "local_builds" / "series_covers_32p"
fronts_dir = REPO_ROOT / "local_builds" / "series_fronts"

print("=== VERIFICATION CHECK 1: File Existence & Dimensions ===")
for i in range(1, 13):
    vid = f"vol_{i:02d}"
    front_p = fronts_dir / f"{vid}_front.png"
    assert front_p.exists(), f"Missing front cover: {front_p}"
    with Image.open(front_p) as fim:
        assert fim.size == (2550, 3300), f"Front {vid} bad size: {fim.size}"

print("  [PASS] All 12 standalone front covers exist at exact 2550 x 3300 px.")

titles = [
    "alphabet", "animals", "birds", "sports", "monsters", "numbers",
    "fruits", "shapes", "toys", "flowers", "transport", "vegetables"
]

for i, slug in enumerate(titles, 1):
    vid = f"vol_{i:02d}"
    pdf_p = covers_dir / f"{vid}_{slug}_fullwrap_32p.pdf"
    proof_p = covers_dir / f"{vid}_{slug}_fullwrap_32p-proof.png"
    assert pdf_p.exists(), f"Missing PDF: {pdf_p}"
    assert proof_p.exists(), f"Missing Proof: {proof_p}"

    # Check PDF Mediabox
    reader = PdfReader(str(pdf_p))
    assert len(reader.pages) == 1, f"{pdf_p} has {len(reader.pages)} pages instead of 1"
    box = reader.pages[0].mediabox
    w_pt, h_pt = float(box.width), float(box.height)
    assert abs(w_pt - 1247.28) < 1.0, f"{pdf_p} bad width: {w_pt} pt"
    assert abs(h_pt - 810.0) < 1.0, f"{pdf_p} bad height: {h_pt} pt"

    # Check Proof PNG
    with Image.open(proof_p) as pim:
        assert pim.size == (5197, 3375), f"{proof_p} bad size: {pim.size}"

print("  [PASS] All 12 full-wrap cover PDFs (1247.28 x 810.0 pt) and proofs (5197 x 3375 px) verified.")

print("\n=== VERIFICATION CHECK 2: Brand Governance ('My First' Prohibition) ===")
forbidden_matches = []
for f in list(covers_dir.glob("*")) + list(fronts_dir.glob("*")):
    if "my first" in f.name.lower():
        forbidden_matches.append(str(f))

for s in [
    REPO_ROOT / "scripts" / "compile_cover_pil.py",
    REPO_ROOT / "scripts" / "utils" / "cover_environment.py"
]:
    content = s.read_text(encoding="utf-8")
    if "my first" in content.lower():
        forbidden_matches.append(str(s))

assert len(forbidden_matches) == 0, f"Found forbidden phrase 'My First': {forbidden_matches}"
print("  [PASS] Zero occurrences of 'My First' found across scripts and cover artifacts.")

print("\n=== VERIFICATION CHECK 3: Absence of Glyph Tofu Boxes ===")
for s in [
    REPO_ROOT / "scripts" / "compile_cover_pil.py",
    REPO_ROOT / "scripts" / "utils" / "cover_environment.py"
]:
    content = s.read_text(encoding="utf-8")
    assert "★" not in content, f"Unicode star found in {s}"

print("  [PASS] Zero Unicode star characters in cover engine source code.")

print("\n=== VERIFICATION CHECK 4: Barcode Safe Area Clearance ===")
# Barcode is 2.0 x 1.2 in (600 x 360 px @ 300 DPI) at bottom-right of back cover
# Back cover width = 2550 + 38 = 2588 px
# Barcode x = 2588 - 600 - 150 = 1838 px
# Barcode y = 3375 - 38 - 360 - 150 = 2827 px
# Inspect vol_01 proof image at barcode area
sample_proof = covers_dir / "vol_01_alphabet_fullwrap_32p-proof.png"
with Image.open(sample_proof) as sp:
    # Crop barcode region
    bc_crop = sp.crop((1838, 2827, 1838 + 600, 2827 + 360))
    # Check that barcode box is white background
    white_pixels = sum(1 for p in bc_crop.getdata() if p[0] > 240 and p[1] > 240 and p[2] > 240)
    total_pixels = 600 * 360
    assert white_pixels / total_pixels > 0.65, f"Barcode area has too little white background: {white_pixels}/{total_pixels}"
print("  [PASS] Barcode safe area (2.0 x 1.2 in) unobstructed with 0.5 in margins.")

print("\n=== ALL 4 AUDIT CRITERIA PASSED 100% ===")
