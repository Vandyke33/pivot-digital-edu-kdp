# Test Infrastructure Specification: The Pivot Kids — Copy to Color 12-Volume KDP Pipeline

## 1. Testing Philosophy & Architecture

### 1.1 Opaque-Box, Requirement-Driven Principles
The End-to-End (E2E) testing framework for "The Pivot Kids: Copy to Color" publishing pipeline operates under strict opaque-box, requirement-driven verification standards. Tests treat the production pipeline as an automated publishing engine, asserting observable contracts against Amazon KDP paperback physical specifications, brand governance rules, and reproducible mathematical invariants:
1. **Physical & Geometric Fidelity**: Verification of trim ($8.5 \times 11.0\text{ in}$), bleed mediabox ($8.625 \times 11.250\text{ in}$ / $621.0 \times 810.0\text{ pt}$ / $2588 \times 3375\text{ px}$ @ 300 DPI), full-wrap cover dimensions ($17.322 \times 11.250\text{ in}$ / $5197 \times 3375\text{ px}$ @ 300 DPI), and the $2.0 \times 1.2\text{ in}$ barcode safe area.
2. **Deterministic Output & Reproducibility**: Image hashing (64-bit dHash), pure binary ink thresholding ($\{0, 255\}$), exact page counts (32 pages), and predictable subject sequencing.
3. **Strict Brand Governance**: Zero-tolerance audit for the prohibited phrase `"My First"` (case-insensitive) across typography, back grids, interior pages, manifests, code, and KDP metadata.
4. **Progressive Testability**: Decoupled test tiers allowing validation of metadata, manifests, procedural illustration engines, and layout routines independently of whether all 12 multi-gigabyte release PDFs have completed compilation.

### 1.2 Test Hierarchy & Tier Architecture
The testing suite is structured into four progressive tiers:
- **Tier 1: Feature Coverage**: Comprehensive verification of all 15 discrete pipeline features, enforcing a minimum of $\ge 5$ distinct test cases per feature ($\ge 75$ tests total).
- **Tier 2: Boundary & Corner Cases**: Stress testing mathematical limits, mediabox bleed geometries, spine text suppression thresholds ($<79\text{ pages}$ vs $\ge 80\text{ pages}$), barcode exclusion zones, pure binary ink limits, and edge overflows.
- **Tier 3: Cross-Feature Combinations**: Validating multi-system interactions, including catalog-to-manifest synchronization, back-cover 4x3 collection grid thumbnail embedding, front-cover split activity card matching, and unified brand/imprint governance across all artifacts.
- **Tier 4: Real-World Workload Scenarios**: End-to-end execution of full-volume compilation, automated quality preflight validation, contact sheet proof generation, and submission readiness for Amazon KDP.

---

## 2. Feature Inventory to Test Mapping

The pipeline implements 15 features across 4 milestones as defined in `PROJECT.md § Feature Inventory`:

| Feature ID | Feature Name | Milestone | Scope / Source File | Test File Target | Min Tests |
|---|---|---|---|---|---|
| **F01** | Publisher Imprint Rectification | M1 | `scripts/compile_copy_to_color_interior.py`, `catalogs/catalog_master.json` | `tests/e2e/test_tier1_features.py` | 5 |
| **F02** | KDP Metadata Registry | M1 | `catalogs/catalog_master.json` | `tests/e2e/test_tier1_features.py` | 5 |
| **F03** | 32-Page Manifest Generation | M1 | `manifests/*-v1.0-core-32p.json` | `tests/e2e/test_tier1_features.py` | 5 |
| **F04** | Brand Governance Enforcement | M1 | Codebase, Catalogs, Manifests, Output PDFs | `tests/e2e/test_tier1_features.py` | 5 |
| **F05** | Multi-Domain Illustration Engine | M2 | `scripts/utils/series_illustrations.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F06** | Bleed Mediabox Interior Alignment | M2 | `scripts/compile_copy_to_color_interior.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F07** | Batch Interior Compilation | M2 | `scripts/compile_copy_to_color_interior.py`, `main.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F08** | 12-Volume Interior PDFs & Proofs | M2 | `local_builds/`, Interior Compiler | `tests/e2e/test_tier1_features.py` | 5 |
| **F09** | Missing Glyph (Tofu Box) Fix | M3 | `scripts/compile_cover_pil.py`, `cover_environment.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F10** | 12-Volume Split Activity Cards | M3 | `scripts/compile_cover_pil.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F11** | Two-Pass 4x3 Collection Grid | M3 | `scripts/compile_cover_pil.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F12** | 12-Volume Full-Wrap Covers & Proofs | M3 | `scripts/compile_cover_pil.py`, `compile_animals_cover.py` | `tests/e2e/test_tier1_features.py` | 5 |
| **F13** | Automated Quality Preflight | M4 | `scripts/preflight_kdp.py`, `main.py preflight` | `tests/e2e/test_tier1_features.py` | 5 |
| **F14** | E2E Test Suite (Tiers 1–4) | M4 | `tests/e2e/` test framework | `tests/e2e/test_tier1_features.py` | 5 |
| **F15** | Unit Test Suite 100% Pass | M4 | `tests/` unit test suite | `tests/e2e/test_tier1_features.py` | 5 |

---

## 3. Detailed Test Tier Specifications

### Tier 1: Feature Coverage (>=5 Tests per Feature, >=75 Tests Total)
Every feature has dedicated, isolated test cases asserting its explicit functional contract:
1. **F01 (Publisher Imprint Rectification)**:
   - `test_f01_imprint_constant_exact_match`: Asserts string `"The Pivot Digital Publication"`.
   - `test_f01_imprint_singular_not_plural`: Rejects `"Publications"` (plural).
   - `test_f01_catalog_imprint_consistency`: Inspects imprint attribute in catalog records.
   - `test_f01_interior_welcome_page_imprint`: Asserts imprint text formatting on Page 1 welcome canvas.
   - `test_f01_imprint_case_sensitive_check`: Rejects casing mutations (e.g., `"the pivot digital publication"`).
2. **F02 (KDP Metadata Registry)**:
   - `test_f02_metadata_all_12_volumes_present`: Verifies all 12 series volumes (`vol_01`–`vol_12`) are defined.
   - `test_f02_metadata_seven_keywords_per_volume`: Verifies exactly 7 backend keywords per volume.
   - `test_f02_metadata_keyword_length_under_50_chars`: Enforces KDP limit of $\le 50$ characters per keyword phrase.
   - `test_f02_metadata_two_bisac_categories`: Verifies 2 valid BISAC category paths per volume.
   - `test_f02_metadata_html_description_allowed_tags_only`: Asserts only KDP-supported tags (`<b>`, `<i>`, `<h3>`, `<ul>`, `<li>`, `<p>`).
3. **F03 (32-Page Manifest Generation)**:
   - `test_f03_manifest_page_count_32`: Validates total page count is exactly 32.
   - `test_f03_manifest_page1_welcome_page32_certificate`: Validates Page 1 is `welcome`/`title` and Page 32 is `certificate`.
   - `test_f03_manifest_pages_2_to_31_thirty_unique_subjects`: Validates 30 distinct educational activity pages.
   - `test_f03_manifest_zero_duplicate_subjects`: Asserts zero subject duplication within any volume manifest.
   - `test_f03_manifest_geometry_and_bleed_settings`: Validates trim, bleed, and safe margin specifications.
4. **F04 (Brand Governance Enforcement)**:
   - `test_f04_zero_my_first_in_catalog`: Scans `catalog_master.json` for zero `"My First"` occurrences.
   - `test_f04_zero_my_first_in_manifests`: Scans all `manifests/*.json` for zero `"My First"` occurrences.
   - `test_f04_zero_my_first_in_scripts`: Scans cover and interior compilers for banned string literals.
   - `test_f04_brand_name_the_pivot_kids`: Verifies canonical brand `"The Pivot Kids"`.
   - `test_f04_series_title_copy_to_color`: Verifies canonical series title `"Copy to Color"`.
5. **F05 (Multi-Domain Illustration Engine)**:
   - `test_f05_illustration_dimensions_1800x1800`: Asserts generated artwork is $1800 \times 1800\text{ px}$.
   - `test_f05_illustration_alpha_transparency`: Verifies background transparency (corner $\alpha = 0$, center $\alpha > 0$).
   - `test_f05_illustration_all_12_domains_supported`: Verifies support across all 12 series themes.
   - `test_f05_illustration_distinct_visual_dhash`: Asserts distinct 64-bit dHash fingerprints per subject.
   - `test_f05_clean_lineart_conversion_pure_binary`: Asserts lineart conversion produces pure binary ink ($\{0, 255\}$).
6. **F06 (Bleed Mediabox Interior Alignment)**:
   - `test_f06_interior_mediabox_points_621x810`: Asserts PDF mediabox is $621.0 \times 810.0\text{ pt}$.
   - `test_f06_interior_pixel_dimensions_2588x3375`: Asserts 300 DPI canvas is $2588 \times 3375\text{ px}$.
   - `test_f06_interior_aspect_ratio_accuracy`: Asserts aspect ratio equals $8.625 / 11.250 = 0.7667$.
   - `test_f06_interior_safe_margins_half_inch`: Asserts safe margins $\ge 0.5\text{ in}$ ($36\text{ pt}$ / $150\text{ px}$).
   - `test_f06_interior_trim_box_vs_mediabox`: Asserts trim box ($8.5 \times 11.0\text{ in}$) centered inside bleed box.
7. **F07 (Batch Interior Compilation)**:
   - `test_f07_cli_argument_parsing_vol_and_all`: Verifies CLI parser accepts `--vol` and `--all`.
   - `test_f07_compile_single_volume_function`: Validates programmatic entry point for single volume.
   - `test_f07_batch_compilation_registry_dispatch`: Validates batch compilation dispatch logic.
   - `test_f07_invalid_volume_id_error_handling`: Validates failure handling on invalid volume requests.
   - `test_f07_output_path_handling`: Asserts directory creation and path resolution for output PDFs.
8. **F08 (12-Volume Interior PDFs & Proofs)**:
   - `test_f08_interior_pdf_page_count_32`: Validates compiled PDFs contain exactly 32 pages.
   - `test_f08_interior_pdf_valid_streams`: Asserts PDF page streams parse without corruption.
   - `test_f08_interior_contact_sheet_dimensions`: Validates 300 DPI contact sheet proof generation.
   - `test_f08_interior_contact_sheet_grid_layout`: Validates contact sheet layout of 32 page thumbnails.
   - `test_f08_interior_pdf_filesize_reasonable`: Validates interior PDF file size is non-empty and uncorrupted.
9. **F09 (Missing Glyph / Tofu Box Fix)**:
   - `test_f09_ribbon_text_contains_no_unicode_star`: Asserts absence of Unicode `'★'` in banner text strings.
   - `test_f09_vector_star_draw_function_callable`: Asserts vector star drawing function executes without error.
   - `test_f09_rendered_ribbon_has_no_missing_glyphs`: Asserts rendered banner contains no tofu box (`□`) glyphs.
   - `test_f09_back_cover_sparkle_placement`: Asserts sparkle stars surround banner and mascot wand.
   - `test_f09_text_rendering_fallback_robustness`: Asserts custom fonts render all title characters without glyph drops.
10. **F10 (12-Volume Split Activity Cards)**:
    - `test_f10_card_split_geometry_aspect_ratio`: Validates color reference thumb and B&W outline card dimensions.
    - `test_f10_card_border_and_drop_shadow`: Validates card styling with white rounded border and drop shadow.
    - `test_f10_card_subject_matches_volume`: Asserts card subject matches volume theme.
    - `test_f10_card_color_reference_fidelity`: Asserts color card preserves vivid reference art.
    - `test_f10_card_bw_outline_fidelity`: Asserts B&W outline card preserves pure black contour lineart.
11. **F11 (Two-Pass 4x3 Collection Grid)**:
    - `test_f11_standalone_front_covers_generation`: Validates Pass 1 standalone front cover generation ($2550 \times 3300\text{ px}$).
    - `test_f11_collection_grid_4x3_twelve_cells`: Asserts back cover grid contains 4 rows $\times$ 3 cols = 12 cells.
    - `test_f11_collection_grid_ordering_vol1_to_12`: Asserts strict ordering from `vol_01` to `vol_12`.
    - `test_f11_thumbnail_vol_badges_present`: Asserts `"Vol. #"` badges on every miniature thumbnail.
    - `test_f11_thumbnails_visually_distinct`: Asserts all 12 miniature thumbnails are visually distinct.
12. **F12 (12-Volume Full-Wrap Covers & Proofs)**:
    - `test_f12_cover_spread_dimensions_5197x3375`: Asserts cover dimensions equal $5197 \times 3375\text{ px}$ @ 300 DPI.
    - `test_f12_spine_width_formula`: Asserts spine formula: $\text{Pages} \times 0.002252\text{ in}$.
    - `test_f12_spine_text_omission_32p`: Asserts spine text is strictly omitted for 32-page books ($<79\text{ pages}$).
    - `test_f12_barcode_safe_area_clearance`: Asserts $2.0 \times 1.2\text{ in}$ barcode safe zone has 0.5 in margin clearance.
    - `test_f12_cover_spread_proof_generation`: Validates 300 DPI preview PNG and spread PDF generation.
13. **F13 (Automated Quality Preflight)**:
    - `test_f13_preflight_interface_callable`: Validates `preflight_volume()` interface and return contract.
    - `test_f13_preflight_checks_all_twelve_criteria`: Asserts preflight dictionary contains all 12 checklist items.
    - `test_f13_preflight_detects_bad_dimensions`: Verifies preflight fails if dimensions are invalid.
    - `test_f13_preflight_detects_forbidden_phrase`: Verifies preflight fails if `"My First"` is present.
    - `test_f13_preflight_cli_all_execution`: Verifies CLI batch runner exit code behavior.
14. **F14 (E2E Test Suite Tiers 1–4)**:
    - `test_f14_test_suite_runner_discoverable`: Validates discovery of all test modules under `tests/e2e/`.
    - `test_f14_tier1_feature_coverage_breadth`: Asserts Tier 1 covers all 15 features.
    - `test_f14_tier2_boundary_coverage`: Asserts Tier 2 contains boundary stress test cases.
    - `test_f14_tier3_cross_feature_coverage`: Asserts Tier 3 contains integration test cases.
    - `test_f14_tier4_workload_coverage`: Asserts Tier 4 contains workload test cases.
15. **F15 (Unit Test Suite 100% Pass)**:
    - `test_f15_animals_cover_unit_tests_pass`: Asserts `test_animals_cover.py` passes 100%.
    - `test_f15_cli_dispatch_unit_tests_pass`: Asserts `test_cli_dispatch.py` passes 100%.
    - `test_f15_copy_to_color_interior_unit_tests_pass`: Asserts `test_copy_to_color_interior.py` passes 100%.
    - `test_f15_pipeline_unit_tests_pass`: Asserts `test_pipeline.py` passes 100%.
    - `test_f15_publicity_kit_unit_tests_pass`: Asserts `test_publicity_kit.py` passes 100%.

---

### Tier 2: Boundary & Corner Cases
Stress tests verifying mathematical limits, mechanical tolerances, and error guards:
1. **Geometric Tolerances**:
   - Total cover width for 32 pages: $2 \times 8.5 + 32 \times 0.002252 + 2 \times 0.125 = 17.3221\text{ in} \pm 0.005\text{ in}$.
   - Spine width at 32 pages: $0.0721\text{ in} \approx 22\text{ px}$ at 300 DPI.
   - Bleed mediabox: exactly $621.0 \times 810.0\text{ pt}$ ($8.625 \times 11.250\text{ in}$).
2. **KDP Spine Text Step-Function Threshold**:
   - $74\text{ pages}$: Spine text strictly suppressed (empty spine zone).
   - $78\text{ pages}$: Spine text strictly suppressed.
   - $79\text{ pages}$: Spine text allowed.
   - $80\text{ pages}$: Spine text rendered and centered along vertical spine axis.
3. **Barcode Safe Area Clearance**:
   - Barcode zone rectangle: $[14.825, 16.825]\text{ in}$ horizontally, $[0.500, 1.700]\text{ in}$ vertically from bottom edge.
   - Assert zero text, graphic, or decorative element overlaps within this region.
4. **Pure Binary Lineart Thresholding Extremes**:
   - Grayscale histograms must contain pixel counts only at $0$ (black ink) and $255$ (paper white).
   - Reject any intermediate gray values ($1 \dots 254$).
5. **Page Limit Violations**:
   - Enforce rejection or error on invalid page counts: $0\text{ pages}$, odd page counts (e.g. $31\text{ pages}$), or counts exceeding maximum.
6. **Safe Margin Clamping**:
   - Content bounds must remain inside $\ge 0.5\text{ in}$ inner margin.

---

### Tier 3: Cross-Feature Combinations
End-to-end integration tests verifying cross-module contracts:
1. **Catalog ↔ Manifest Synchronization**:
   - Volume IDs, volume titles, and volume subjects in `catalogs/catalog_master.json` match `manifests/*-v1.0-core-32p.json` 1:1.
2. **Back Cover Grid ↔ Series Catalog Alignment**:
   - The 12 thumbnail cells in the 4x3 back grid match the exact titles, volume numbers, and colors registered in the catalog master.
3. **Front Cover Activity Card ↔ Interior Page Subject Alignment**:
   - The featured split-card subject on the front cover corresponds to the lead activity subject in the volume manifest.
4. **Global Brand Governance Integrity**:
   - Cross-file text search ensures zero occurrences of `"My First"` across all front covers, spines, back cover grids, interior title pages, certificate pages, manifests, and metadata JSON records.
5. **Publisher Imprint Synchronization**:
   - Imprint string `"The Pivot Digital Publication"` is verified identical across Python code, catalog metadata, and interior PDF text.

---

### Tier 4: Real-World Workload Scenarios
Production-grade scenario testing:
1. **Multi-Volume Full Compilation Pipeline**:
   - Exercises end-to-end compilation of a 32-page interior PDF, contact sheet proof, standalone front cover, full-wrap cover spread, and cover proof.
2. **Automated Quality Preflight Verification**:
   - Executes preflight verification against compiled volume artifacts and verifies 100% PASS on all 12 inspection criteria.
3. **Amazon KDP Submission Package Readiness**:
   - Confirms complete set of submission artifacts exists in `local_builds/`:
     - Interior PDF ($8.625 \times 11.250\text{ in}$, 32 pages)
     - Full-Wrap Cover PDF ($17.322 \times 11.250\text{ in}$)
     - Cover Proof PNG (300 DPI)
     - Interior Proof PNG (300 DPI contact sheet)
     - Listing Metadata Package (Title, Subtitle, 7 Keywords, 2 BISACs, HTML description)
4. **Pipeline Idempotency & Repeatability**:
   - Verifies that compiling a volume multiple times produces identical byte-level or structural output without file corruption or race conditions.

---

## 4. Test Execution & Coverage Thresholds

### Execution Command
The test suite is executable via standard Python `unittest`:
```powershell
.venv\Scripts\python.exe -m unittest discover -s tests/e2e -v
```
Or via the unified test runner:
```powershell
.venv\Scripts\python.exe tests/e2e/run_all_e2e.py
```

### Coverage & Quality Thresholds
- **Tier 1**: $\ge 75$ tests ($15\text{ features} \times \ge 5\text{ tests}$). Target: 100% PASS.
- **Tier 2**: $\ge 10$ boundary/corner cases. Target: 100% PASS.
- **Tier 3**: $\ge 6$ cross-feature combinations. Target: 100% PASS.
- **Tier 4**: $\ge 4$ real-world workload scenarios. Target: 100% PASS.
- **Unit Test Baseline**: 55 existing unit tests. Target: 100% PASS, 0 failures, 0 errors.
