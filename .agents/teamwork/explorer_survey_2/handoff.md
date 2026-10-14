# Handoff Report: Cover Generation Architecture, Typography & 4x3 Collection Grid Engine Survey

**Author**: `explorer_survey_2` (Cover Engine Explorer)  
**Parent Conversation ID**: `ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1`  
**Working Directory**: `d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2`  
**Date**: 2026-10-14  

---

## 1. Observation

### 1.1 Existing Cover Compilation Scripts & Entrypoints
1. `main.py` lines 198–220, 242–256:
   - `cmd_build_animals_cover()` executes `scripts/compile_animals_cover.py --output ... --page-count 32` and then runs `scripts/render_cover_proof.py`.
   - `cmd_build_series_covers()` executes `scripts/compile_cover_pil.py --all --page-count 32`.
   - `cmd_build_cover()` executes `scripts/compile_cover.py` (legacy Solar System Explorers single book).
2. `scripts/compile_cover_pil.py` lines 1–15, 56–69, 75–89, 465–534, 537–603, 608–777, 779–828:
   - Header contains a deprecation note: `"[DEPRECATION NOTICE] compile_cover_pil.py is the experimental PIL-based cover compiler. The canonical production cover engine is compile_animals_cover.py"`.
   - However, `scripts/compile_animals_cover.py` lines 994–1004 directly imports and executes `from scripts.compile_cover_pil import build_kdp_cover`! Thus, `compile_cover_pil.py` is the actual underlying layout and rendering engine.
   - Implements a **Two-Pass Series Architecture**:
     - **Pass 1 (`prebuild_all_series_front_covers`)**: Iterates through all 12 series volumes defined in `SERIES_TITLES` (lines 56–69) and renders standalone front covers (2550 x 3300 px) into `local_builds/series_fronts/{vol_id}_front.png`.
     - **Pass 2 (`build_kdp_cover`)**: Assembles the full-wrap spread ($5197 \times 3375\text{ px}$) by embedding those 12 rendered front covers into the back cover's 4x3 collection grid (`render_back_cover_grid`).
     - Includes `--all` CLI mode (`build_all_12_series_covers`) to batch-render all 12 spreads into `local_builds/series_covers_32p/`.
3. `scripts/compile_animals_cover.py` lines 648–761, 791–975, 985–1023:
   - Contains pure ReportLab drawing routines (`draw_back_cover`, `draw_front_cover`), but `draw_animals_cover_spread` (lines 985–1023) delegates entirely to `scripts.compile_cover_pil.build_kdp_cover`, loads the generated PNG proof onto the canvas, and stamps ReportLab PDF metadata.
   - Hardcoded specifically for Volume 2 ("Animals").
4. `scripts/compile_cover.py` lines 1–495:
   - Dedicated solely to the old single-book project "Solar System Explorers"; not used for the "Copy to Color" series.
5. `scripts/utils/cover_environment.py` lines 26–86, 123–191, 248–302, 303–336, 338–397:
   - Procedural drawing helpers for checkered borders (`draw_checkered_border`), vector pattern collage (`draw_pattern_collage`), jungalow nature elements (`draw_jungalow_elements`), curved ribbon banner (`draw_curved_ribbon_header`), and mascot boy with wand (`draw_mascot_boy_with_wand`).
6. `scripts/generate_cover_microassets.py` lines 34–68, 170–235:
   - Generates and extracts white backgrounds for cover micro-assets via corner flood-fill alpha extraction.
   - Defined 12 volume hero prompts in `manifests/series_thumbnails_batch.json`.

### 1.2 KDP Mechanical Dimensions (32-Page Full-Wrap Cover)
- Interior Trim: $8.5 \times 11.0\text{ in}$
- Outer Bleed: $0.125\text{ in}$ on all 4 edges
- 55# White Paper Spine Multiplier: $0.002252\text{ in/page}$
- Exact Formulas:
  - $\text{Spine Width} = 32 \times 0.002252 = 0.072064\text{ in}$ ($21.6 \rightarrow 22\text{ px}$ @ 300 DPI)
  - $\text{Total Width} = 8.5 + 8.5 + 0.072064 + (2 \times 0.125) = 17.322064\text{ in}$ ($5196.6 \rightarrow 5197\text{ px}$ @ 300 DPI)
  - $\text{Total Height} = 11.0 + (2 \times 0.125) = 11.250\text{ in}$ ($3375\text{ px}$ @ 300 DPI)
  - Canvas Resolution @ 300 DPI: $5197 \times 3375\text{ px}$
  - PDF Mediabox: $1247.28 \times 810.0\text{ pt}$ ($17.3233 \times 11.250\text{ in}$)
- Spine text suppression:
  - Both `compile_cover_pil.py` (line 748) and `compile_animals_cover.py` (line 775) guard spine text: strictly suppressed when `page_count < 79`.
- Barcode safe area:
  - $2.0 \times 1.2\text{ in}$ ($600 \times 360\text{ px}$ @ 300 DPI) located at bottom right of back cover (`bc_x = back_x_end - bc_w - int(0.5 * DPI)`, `bc_y = h - bleed - bc_h - int(0.5 * DPI)`), maintaining $0.5\text{ in}$ clearance from bottom trim and spine margin.

### 1.3 Front Cover Visual Elements
- **Brand Logo**: `assets/logos/pivot_kids_sticker.png` (or `pivot_kids.png` with automatic sticker contour extraction). Anchored top center, no rectangular white box.
- **Display Typography**:
  - Series Title: "Copy to Color" rendered in `LuckiestGuy-Regular.ttf` with white fill, dark navy outline, 3D block extrusion, neon glow aura, top highlight, and 4-point vector sparkles.
  - Subject Title: e.g. "ANIMALS" rendered in `LuckiestGuy-Regular.ttf` in golden-yellow (`YELLOW_TEXT = (255, 230, 80, 255)`) with dark outline, 3D extrusion, and corner sparkle stars.
- **Tilted Wax Crayons**: Cluster of 3 tilted crayons (yellow, red, blue) on the left margin.
- **Kid Avatar & Activity Standard**:
  - High-contrast, expressive kid character artwork actively interacting with theme objects (e.g., toddler on ABC blocks, safari girl hugging tiger cub/monkey, kid with parrot, etc.).
  - All 12 character images exist in `assets/cover_thumbnails/vol_01.png` through `vol_12.png`.
- **Floating Activity Card ("Before & After")**:
  - Located at right-middle of front cover with drop shadow and pill badge.
  - Observed Gap: Only Volume 2 has `local_builds/animals/assets/inset_tiger_split.png` (split color guide + B&W outline). Volumes 1 and 3–12 fall back to displaying the color hero artwork inside the card (line 520 in `compile_cover_pil.py`).

### 1.4 Back Cover Visual Elements & 4x3 Collection Grid
- **Curved Ribbon Header**:
  - Parchment ribbon banner centered at top with folded triangular notch tails and drop shadow.
  - Text rendered: `"★ TITLES IN THIS SERIES ★"` using `Fredoka-Bold.ttf`.
- **Mascot Boy with Star Wand**:
  - Boy wearing backwards cyan/yellow baseball cap, anime eyes, smile, and purple hoodie, holding magic wand with glowing 4-point starburst.
  - Next to banner pill: `"★ CAN YOU COLLECT THEM ALL? ★"`.
- **4x3 Collection Grid**:
  - Warm ivory container card embedding 12 miniature books (4 columns $\times$ 3 rows).
  - Each miniature book is a scaled replica of the actual rendered Front Cover, framed with a white border, 3D drop shadow, and a "Vol. #" star pill badge at top right.
- **Collector Hook Box & Blurb**:
  - Green rounded pill at bottom left: `"★ Collector's Series of 12 Interactive Titles ★"`.
  - Marketing blurb below it: `"A playful, easy coloring series designed for early learners to copy, color, and play!"`.
- **Barcode Safe Area**:
  - Unobstructed white box with barcode lines, "2.0 x 1.2 in" notation, and copyright text: `"© The Pivot Digital Publication. All rights reserved."`.

### 1.5 Typography, Glyphs & Font Availability
1. Font directory contents (`assets/fonts/`):
   - `Fredoka-Bold.ttf`
   - `LuckiestGuy-Regular.ttf`
   - `LuckiestGuy.ttf`
   - Missing: `Bungee-Regular.ttf` (listed in AGENTS.md Cover_Designer_Agent rules).
2. **Critical Defect — Missing Glyph Box (`□`)**:
   - In `scripts/compile_cover_pil.py` and `scripts/utils/cover_environment.py`, strings contain Unicode character `★` (U+2605):
     - Line 689: `"★ TITLES IN THIS SERIES ★"`
     - Line 698: `"★ CAN YOU COLLECT THEM ALL? ★"`
     - Line 721: `"★ Collector's Series of 12 Interactive Titles ★"`
   - Direct execution of `inspect_glyphs.py` and inspection of `local_builds/animals/v1.0-core/animals-cover-spread-32p-proof.png` revealed:
     - `Fredoka-Bold.ttf` does **NOT** contain glyph U+2605 (`★`).
     - FreeType substitutes the font's `.notdef` glyph, which renders as a hollow rectangular box (`□`)!
     - In `animals-cover-spread-32p-proof.png`, the ribbons verbatim display:
       - `□ TITLES IN THIS SERIES □`
       - `□ CAN YOU COLLECT THEM ALL? □`
       - `□ Collector's Series of 12 Interactive Titles □`

---

## 2. Logic Chain

1. **Premise**: Dispatch and Acceptance Criteria require:
   - "Back cover displays a 4x3 collection grid embedding all 12 authentic miniature front covers with no missing glyph boxes (`□`)."
   - KDP 32-page mechanical dimensions ($17.322 \times 11.250\text{ in}$, 5197 x 3375 px @ 300 DPI).
   - Zero occurrences of "My First".
   - Cheerful kid avatars actively engaged with theme items.
2. **Analysis of Missing Glyph Box**:
   - The string `"★ TITLES IN THIS SERIES ★"` relies on the font file to render `★`.
   - FreeType inspects `Fredoka-Bold.ttf` for code point 0x2605, finds no glyph definition, and falls back to `.notdef` (a rectangle `□`).
   - `compile_cover_pil.py` and `cover_environment.py` already define a procedural vector function: `draw_sparkle_star(draw, cx, cy, outer_r, inner_r)`.
   - Modifying the text to remove `★` (`"TITLES IN THIS SERIES"`, `"CAN YOU COLLECT THEM ALL?"`, `"Collector's Series of 12 Interactive Titles"`) and calling `draw_sparkle_star()` to render crisp golden vector stars on the left and right of the text completely eliminates the `□` tofu box (empirically confirmed in `test_clean_ribbon.py` and `clean_ribbon.png`).
3. **Analysis of 12-Volume Series Workflow & Circular Dependency**:
   - To show all 12 covers on the back cover of every volume without circular dependency:
     - Step 1 (Pass 1): Render all 12 standalone front covers ($2550 \times 3300\text{ px}$) to `local_builds/series_fronts/vol_XX_front.png`. Front covers do not depend on back covers.
     - Step 2 (Pass 2): When assembling the full spread ($5197 \times 3375\text{ px}$) for any volume $i \in \{1..12\}$, load the 12 pre-rendered front covers from disk and paste scaled thumbnails into the back cover's 4x3 grid.
     - This forms a strict Directed Acyclic Graph (DAG) with zero circular recursion.
   - `compile_cover_pil.py` already implements this exact two-pass logic in `prebuild_all_series_front_covers()` and `build_all_12_series_covers()`.
4. **Analysis of Floating Activity Cards**:
   - Front covers require a floating activity card with a color guide and B&W coloring outline.
   - In `compile_cover_pil.py`, Volume 2 uses `local_builds/animals/assets/inset_tiger_split.png` (split color/outline preview).
   - Volumes 1 and 3–12 currently fall back to duplicating `hero_candidate` (the full-color character sticker) inside the activity card.
   - To achieve full parity across all 12 volumes, each volume's activity card should display either:
     - A split preview image (left half color guide, right half clean B&W outline) of a subject from that volume, OR
     - The interior color guide + B&W outline from that volume's interior assets.

---

## 3. Caveats

1. **Cover Asset Resolution**:
   - The 12 hero character images in `assets/cover_thumbnails/` are $512 \times 512\text{ px}$ or $1024 \times 1024\text{ px}$. When placed on the front cover hero area ($1400 \times 1400\text{ px}$), they look sharp and clean, but for ultra-high commercial fidelity, generating dedicated high-res hero/inset pairs ($1024 \times 1024\text{ px}$ or vector) per volume is an enhancement for the Art Director agent.
2. **Missing Font Asset**:
   - `Bungee-Regular.ttf` is referenced in `AGENTS.md` but is not present in `assets/fonts/`. Currently, `Fredoka-Bold.ttf` is used for ribbons and headers. If strict font mapping is enforced, `Bungee-Regular.ttf` must be downloaded from Google Fonts or vendored.
3. **Output File Location**:
   - `compile_cover_pil.py --all` currently outputs to `local_builds/series_covers_32p/`. If pipeline conventions require per-series folders (e.g., `local_builds/<series>/v1.0-core/`), the output path argument must be parameterized accordingly.

---

## 4. Conclusion

1. **Cover Engine Viability**:
   - The Two-Pass PIL cover engine in `scripts/compile_cover_pil.py` is functional, robust, and mathematically compliant with Amazon KDP 32-page paperback mechanical specifications ($17.322 \times 11.250\text{ in}$, 5197 x 3375 px @ 300 DPI, spine width = 0.072 in, spine text omitted, 2.0 x 1.2 in barcode safe zone).
   - The deprecation notice on `scripts/compile_cover_pil.py` should be removed because `scripts/compile_animals_cover.py` delegates directly to it.
2. **Required Refactoring & Fixes**:
   - **Tofu Box Bug**: Replace string-embedded Unicode `★` characters with procedural vector `draw_sparkle_star()` calls in `scripts/compile_cover_pil.py` and `scripts/utils/cover_environment.py`.
   - **Bungee Font**: Add `Bungee-Regular.ttf` to `assets/fonts/` (or update font loader in `compile_cover_pil.py`).
   - **Activity Cards**: Provide split-view preview microassets or interior subject pairs for Volumes 1 and 3–12.
   - **CLI Unification**: Ensure `main.py build-series-covers` executes cleanly and outputs all 12 spreads and 300 DPI preview PNGs.

---

## 5. Verification Method

### 5.1 Automated Unit Tests
Run the test suite using the project virtual environment:
```powershell
.venv\Scripts\python.exe -m unittest tests/test_animals_cover.py -v
```
**Expected Result**: All 11 tests pass with 0 failures, verifying 32-page dimensions, 80-page spine text logic, 32-page spine text suppression, barcode safe area, and alpha extraction.

### 5.2 Missing Glyph Box Tofu Elimination Verification
Run the verification test script:
```powershell
.venv\Scripts\python.exe .agents/teamwork/explorer_survey_2/test_clean_ribbon.py
```
Inspect `.agents/teamwork/explorer_survey_2/clean_ribbon.png`:
- Confirm that the ribbon header displays `"TITLES IN THIS SERIES"` flanked by sharp, 4-point golden vector stars with **zero** hollow rectangles or missing glyph boxes (`□`).

### 5.3 Batch Series Cover Compilation
Run the 12-volume compilation command:
```powershell
.venv\Scripts\python.exe scripts/compile_cover_pil.py --all --page-count 32
```
Verify generated artifacts in `local_builds/series_covers_32p/`:
- Exactly 12 PDF files (`vol_01_alphabet_fullwrap_32p.pdf` ... `vol_12_vegetables_fullwrap_32p.pdf`).
- Exactly 12 preview PNGs (`vol_01_alphabet_fullwrap_32p-proof.png` ... `vol_12_vegetables_fullwrap_32p-proof.png`).
- Validate image dimensions: `(5197, 3375)` at 300 DPI.
- Validate PDF Mediabox: `1247.28 x 810.0 pt`.
