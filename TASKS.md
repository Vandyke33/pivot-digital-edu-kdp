# TASKS: 'My First Copy to Colour: Animals' Cover Spread

## Overview
Implementation tracking for the flat, print-ready full paperback cover spread for **"My First Copy to Colour: Animals"** (8.5 x 11 in trim, full-wrap KDP spread with bleed and spine).

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
