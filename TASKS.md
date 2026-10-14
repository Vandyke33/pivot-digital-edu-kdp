# TASKS: 'My First Copy to Colour: Animals' Cover Spread & Volume 2 Edition

## Overview
Implementation tracking for the flat, print-ready full paperback cover spread and 74-page interior edition for **"My First Copy to Color: Animals"** (8.5 x 11 in trim, full-wrap KDP spread with bleed and spine).

---

## Task Progress

- [x] **Phase 0: Planning & Approval**
  - [x] Analyze user reference images (GoWoo 16-book series, back-cover 4x3 grid, front cover title hierarchy)
  - [x] Create detailed implementation plan (`animals_cover_spread_plan.md`)
  - [x] Obtain user approval to proceed

- [x] **Phase 1: Asset Preparation & Character Art**
  - [x] Extract and verify pristine logo (`assets/logos/pivot_kids.png`)
  - [x] Prepare cute cartoon tiger and monkey character artwork for front cover (`local_builds/animals/assets/tiger_monkey_transparent.png`)
  - [x] Prepare before-and-after "TIGER" activity card assets (`tiger_color_thumb.png` + `tiger_outline.png`)
  - [x] Prepare 12 thumbnail cover theme data for back-cover 4x3 grid (`SERIES_TITLES_12`)

- [x] **Phase 2: Full-Spread Cover Compiler (`scripts/compile_animals_cover.py`)**
  - [x] Step 2.1: KDP spread geometry calculations ($17.322 \times 11.250\text{ in}$ at 300+ DPI)
  - [x] Step 2.2: Global background (Vivid Coral-Red `#FF4C4C` gradient, starbursts, paint splatters, continuous rolling green hills, daisies, ladybugs)
  - [x] Step 2.3: Back cover layout:
    - [x] "The Pivot Kids" emblem badge
    - [x] Cyan-blue ribbon banner `"TITLES IN THIS SERIES"`
    - [x] Procedural **4x3 grid of 12 miniature book cover cards** with titles and theme colors
    - [x] Early-learner marketing blurb
    - [x] Amazon KDP Barcode zone ($2.0 \times 1.2\text{ in}$) with copyright
  - [x] Step 2.4: Spine layout:
    - [x] Vertical white & yellow lettering: `"THE PIVOT KIDS"` | `"My First Copy to Colour: Animals"`
    - [x] Miniature brand "P" logo at base
  - [x] Step 2.5: Front cover layout:
    - [x] Arched stitched ribbon header with "The Pivot Kids" logo
    - [x] Curved `"My First"` badge
    - [x] Huge white rounded lettering with dark blue outline: `"Copy to Colour"`
    - [x] Giant yellow bubble lettering with dark outline: `"Animals"`
    - [x] 3 angled large wax crayons (yellow, red, orange)
    - [x] Inset `"TIGER"` before-and-after card (color thumbnail + B&W line art)
    - [x] Child-friendly cartoon tiger and monkey characters on grass

- [x] **Phase 3: CLI Integration (`main.py`)**
  - [x] Add `build-animals-cover` subcommand to `main.py`
  - [x] Auto-detect virtual environment Python for cross-environment robustness
  - [x] Support `--output` and `--page-count` options

- [x] **Phase 4: Automated Testing (`tests/test_animals_cover.py`)**
  - [x] Add test cases verifying KDP dimensions, barcode clearance, and 4x3 grid rendering
  - [x] Run full 35 test suite with 100% test pass

- [x] **Phase 5: Verification & Delivery**
  - [x] Compile full-spread PDF to `local_builds/animals/v1.0-core/animals-cover-spread.pdf`
  - [x] Visual verification of front, spine, and back cover
  - [x] Document final release artifacts and walkthrough

- [x] **Phase 6: Component-Based Architecture & Governance Integration**
  - [x] Update [`AGENTS.md`](file:///d:/pivot-edu-kdp/pivot-digital-edu-kdp/AGENTS.md) with `Cover_Designer_Agent` & the Component-First Rule
  - [x] Create [`skills/cover_engine.md`](file:///d:/pivot-edu-kdp/pivot-digital-edu-kdp/skills/cover_engine.md) defining mechanical dimensioning, spine math, and grid specifications
  - [x] Update [`skills/prompt_generator.md`](file:///d:/pivot-edu-kdp/pivot-digital-edu-kdp/skills/prompt_generator.md) with isolated micro-asset prompt templates
  - [x] Implement reference PIL cover compiler [`scripts/compile_cover_pil.py`](file:///d:/pivot-edu-kdp/pivot-digital-edu-kdp/scripts/compile_cover_pil.py)
  - [x] Generate complete 12-subject prompt batch manifest [`manifests/series_thumbnails_batch.json`](file:///d:/pivot-edu-kdp/pivot-digital-edu-kdp/manifests/series_thumbnails_batch.json)
  - [x] Execute test compilations for both ReportLab vector compiler and PIL compiler
  - [x] Validate all 35 test cases pass

- [x] **Phase 7: Micro-Asset Generation, Alpha Extraction, & Animals 74-Page Interior Blueprint**
  - [x] Implement Corner Flood-Fill Alpha Extraction (`scripts/utils/alpha_extraction.py`) with die-cut sticker contour dilation
  - [x] Generate 12 Series Thumbnail Icons (Vol. 1 - 12) via Google Gemini with rate-limit pacing and automatic backoff
  - [x] Generate Front Cover activity inset card (`inset_tiger_split.png`)
  - [x] Wire all 12 thumbnail PNGs dynamically into ReportLab vector engine (`scripts/compile_animals_cover.py`) and PIL engine (`scripts/compile_cover_pil.py`)
  - [x] Build 300 DPI proof renderer (`scripts/render_cover_proof.py`) using PyMuPDF
  - [x] Re-compile 74-page cover spread (`5225 x 3375 px` @ 300 DPI) and visually inspect proofs
  - [x] Add `copy_to_color_animals` blueprint to `prompts.yaml` with 35 calibrated animal subjects
  - [x] Prepare 74-page production interior manifest `manifests/animals-v1.0-core.json`
  - [x] Add unit tests for 74-page spine math, alpha extraction, and proof rendering (38/38 tests passing)
