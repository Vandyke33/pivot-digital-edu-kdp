# Project: The Pivot Kids — Copy to Color 12-Volume KDP Pipeline

## Architecture
The production system is an automated, deterministic multi-volume publishing pipeline for Amazon KDP paperbacks. It compiles print-ready 32-page interior PDFs and full-wrap cover spreads for 12 distinct series volumes:
1. `vol_01`: Alphabet (`PIVOT-ALPHABET-001-32P`)
2. `vol_02`: Animals (`PIVOT-ANIMALS-002-32P`)
3. `vol_03`: Birds (`PIVOT-BIRDS-003-32P`)
4. `vol_04`: Sports (`PIVOT-SPORTS-004-32P`)
5. `vol_05`: Monsters (`PIVOT-MONSTERS-005-32P`)
6. `vol_06`: Numbers (`PIVOT-NUMBERS-006-32P`)
7. `vol_07`: Fruits (`PIVOT-FRUITS-007-32P`)
8. `vol_08`: Shapes (`PIVOT-SHAPES-008-32P`)
9. `vol_09`: Toys (`PIVOT-TOYS-009-32P`)
10. `vol_10`: Flowers (`PIVOT-FLOWERS-010-32P`)
11. `vol_11`: Transport (`PIVOT-TRANSPORT-011-32P`)
12. `vol_12`: Vegetables (`PIVOT-VEGETABLES-012-32P`)

### Data Flow & Component Architecture
1. **Catalog & Manifest Registry**:
   - `catalogs/catalog_master.json`: Authoritative metadata registry containing complete KDP listing packages (titles, subtitles, 7 backend keywords <= 50 chars, 2 BISAC categories, allowed HTML descriptions, publisher imprint).
   - `manifests/{series}-v1.0-core-32p.json`: Edition manifests defining exact 32-page sequences and expected subjects.
2. **Procedural Multi-Domain Illustration Engine** (`scripts/utils/series_illustrations.py`):
   - Procedural vector/character rendering for all 360 curated educational subjects across all 12 series volumes.
   - Guarantees distinct visual fingerprints (zero dHash duplicate collisions) across pages 2–31 in every volume.
3. **Interior PDF Compiler** (`scripts/compile_copy_to_color_interior.py`):
   - Page 1: Welcome & Belongs-to page with ornate borders and brand logo.
   - Pages 2–31: 30 Educational activity pages (letter/code badge, custom title banner, full-color reference guide, 1:1 matched pure binary B&W coloring outline, bottom wave footer, page numbers).
   - Page 32: Super Colorist Award Certificate.
   - Dimensions: $8.625 \times 11.250\text{ in}$ at 300 DPI ($2588 \times 3375\text{ px}$ / $621.0 \times 810.0\text{ pt}$ bleed mediabox).
4. **Two-Pass Full-Wrap Cover Engine** (`scripts/compile_cover_pil.py`):
   - Pass 1: Renders 12 standalone front covers ($2550 \times 3300\text{ px}$) featuring official branding ("The Pivot Kids: Color & Play"), 3D display typography ("Copy to Color: <Subject>"), floating activity card, and kid avatars.
   - Pass 2: Renders 12 full-wrap spreads ($5197 \times 3375\text{ px}$ @ 300 DPI, $17.322 \times 11.250\text{ in}$), embedding authentic miniature front covers into the back cover's 4x3 collection grid, vector ribbon ("TITLES IN THIS SERIES") with procedural starbursts (zero tofu boxes), mascot boy with star wand, and unobstructed $2.0 \times 1.2\text{ in}$ barcode safe area.
5. **Quality Preflight Verification Engine** (`scripts/preflight_kdp.py`):
   - Programmatically validates all 12 interior PDFs and 12 cover spreads against 12 mechanical, visual, and governance rules.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Publisher Imprint Rectification | Correct line 522 typo "Publications" -> "The Pivot Digital Publication" in `compile_copy_to_color_interior.py` | M1 | Survey |
| 2 | KDP Metadata Registry | Inject complete metadata blocks into `catalogs/catalog_master.json` for all 12 volumes | M1 | Survey |
| 3 | 32-Page Manifest Generation | Create 12 edition manifests in `manifests/` (`alphabet-v1.0-core-32p.json` .. `vegetables-v1.0-core-32p.json`) | M1 | Survey |
| 4 | Brand Governance Enforcement | Strict elimination of "My First" (case-insensitive) across all files, code, and metadata | M1 | Survey |
| 5 | Multi-Domain Illustration Engine | Implement `scripts/utils/series_illustrations.py` with 360 distinct procedural subjects across all 12 series volumes | M2 | Survey |
| 6 | Bleed Mediabox Interior Alignment | Update interior canvas to 2588x3375 px (621.0 x 810.0 pt mediabox) at 300 DPI | M2 | Survey |
| 7 | Batch Interior Compilation | Add `--all` to `compile_copy_to_color_interior.py` and `main.py build-copy-to-color-interior` | M2 | Survey |
| 8 | 12-Volume Interior PDFs & Proofs | Generate all 12 32-page interior PDFs and 300 DPI contact sheet proofs | M2 | Survey |
| 9 | Missing Glyph (Tofu Box) Fix | Replace text Unicode `★` with procedural vector `draw_sparkle_star()` in cover ribbons | M3 | Survey |
| 10 | 12-Volume Split Activity Cards | Provide split color/B&W activity preview cards for front covers of all 12 volumes | M3 | Survey |
| 11 | Two-Pass 4x3 Collection Grid | Embed 12 authentic miniature front covers into back cover grid without circular dependency | M3 | Survey |
| 12 | 12-Volume Full-Wrap Covers & Proofs | Generate all 12 full-wrap cover PDFs ($17.322 \times 11.250\text{ in}$) and 300 DPI preview PNGs | M3 | Survey |
| 13 | Automated Quality Preflight | Implement `scripts/preflight_kdp.py` and `main.py preflight` checking all 12 criteria | M4 | Survey |
| 14 | E2E Test Suite (Tiers 1–4) | Build and pass comprehensive E2E test suite covering feature, boundary, cross-feature, and workload tests | M4 | Survey |
| 15 | Unit Test Suite 100% Pass | Ensure existing test suite (`python -m unittest discover -s tests`) passes with 0 errors | M4 | Survey |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Governance, Catalogs & KDP Metadata | Imprint fix, 12-volume metadata in `catalog_master.json`, manifests in `manifests/`, brand verification | none | PLANNED |
| M2 | 12-Volume Interior Production Pipeline | Multi-domain illustration engine (`series_illustrations.py`), 8.625x11.25 in bleed mediabox, batch interior compiler, generate 12 interior PDFs & proofs | M1 | PLANNED |
| M3 | 12-Volume Cover Spread Production Pipeline | Vector star tofu fix, split activity cards, 4x3 collection grid, batch cover compiler, generate 12 full-wrap cover spreads & proofs | M1 | PLANNED |
| M4 | Final Milestone: E2E Quality Preflight & Test Verification | Build `scripts/preflight_kdp.py`, pass 100% of E2E tests (Tiers 1-4) and unit tests, verify all 12 release packages | M2, M3 | PLANNED |

---

## Interface Contracts

### `scripts/utils/series_illustrations.py` ↔ `scripts/compile_copy_to_color_interior.py`
- `get_series_illustration(vol_id: str, subject_name: str, primary_color: tuple, secondary_color: tuple) -> PIL.Image.Image`:
  - Returns: $1800 \times 1800\text{ px}$ RGBA image with transparent background.
  - Geometry: Closed, clean contours suitable for `color_image_to_clean_lineart()`.
  - Uniqueness: Distinct dHash per subject within the volume.

### `scripts/compile_cover_pil.py` ↔ CLI & Main
- `prebuild_all_series_front_covers(output_dir: Path) -> dict[str, Path]`:
  - Generates 12 standalone front cover PNGs ($2550 \times 3300\text{ px}$) in `local_builds/series_fronts/`.
- `build_kdp_cover(vol_id: str, page_count: int = 32, ...) -> tuple[Path, Path]`:
  - Generates full-wrap spread PDF ($17.322 \times 11.250\text{ in}$) and 300 DPI preview PNG ($5197 \times 3375\text{ px}$) in `local_builds/series_covers_32p/`.

### `scripts/preflight_kdp.py` ↔ Release Gate
- `preflight_volume(vol_id: str) -> dict[str, bool]`:
  - Returns dictionary of 12 checklist verification statuses. Exit code 0 if and only if all 12 volumes pass 100%.

---

## Code Layout
- `catalogs/catalog_master.json`: Master catalog and KDP metadata
- `manifests/`: Edition manifests for all 12 volumes
- `scripts/compile_copy_to_color_interior.py`: Interior PDF generator
- `scripts/utils/series_illustrations.py`: Procedural illustration engine for 360 subjects
- `scripts/compile_cover_pil.py`: Two-pass full-wrap cover engine
- `scripts/utils/cover_environment.py`: Cover vector graphics and environment helpers
- `scripts/preflight_kdp.py`: Automated quality preflight runner
- `main.py`: Unified CLI dispatch
- `tests/`: Unit and E2E test suites
- `local_builds/`: Release output artifacts (interiors, covers, proofs)

