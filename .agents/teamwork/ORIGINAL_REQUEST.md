# Original User Request

## 2026-10-14T19:25:15Z

Build and automate an end-to-end production pipeline for the 12-volume children's activity book series "The Pivot Kids: Copy to Color", generating print-ready 32-page interior PDFs with unique subjects, matching full-wrap KDP paperback cover spreads (with 4x3 collection back grids), contact sheet proofs, and validated Amazon KDP metadata packages.

Working directory: d:/pivot-edu-kdp/pivot-digital-edu-kdp
Integrity mode: development

## Requirements

### R1. 12-Volume 32-Page Interior Compilation
Produce 12 distinct 32-page children's activity book interior PDFs corresponding to the 12 planned series volumes (Alphabet, Animals, Birds, Sports, Monsters, Numbers, Fruits, Shapes, Toys, Flowers, Transport, Vegetables). Each volume must have Page 1 as a welcome page, Pages 2–31 as 30 unique themed educational activity pages (featuring an educational initial letter badge, custom title banner, full-color reference guide, and an exactly matched crisp black-and-white coloring outline with zero duplicate subjects within the book), and Page 32 as a completion certificate. All interior pages must conform to 8.5 x 11 inch trim with bleed (8.625 x 11.25 inches) and 300 DPI resolution.

### R2. Full-Wrap KDP Paperback Cover Spreads
Generate 12 print-ready full-wrap paperback cover spreads formatted to Amazon KDP mechanical specifications for 32 pages ($17.322 \times 11.250\text{ in}$ at 300 DPI, 5197 x 3375 px) with spine text omitted per KDP rules for books under 79 pages. Each front cover must feature official series branding ("The Pivot Kids: Color & Play"), 3D extruded display typography ("Copy to Color: <Subject>"), floating activity card, and cheerful kid avatars actively engaged with the theme items. Each back cover must feature an ornate curved ribbon header ("TITLES IN THIS SERIES"), a mascot character waving a magic star wand next to a "CAN YOU COLLECT THEM ALL?" banner, a 4x3 collection grid embedding authentic miniature replicas of all 12 series front covers, collector blurb, and an unobstructed $2.0 \times 1.2\text{ in}$ barcode safe area at the bottom-right.

### R3. Strict Brand & Naming Governance
Enforce brand policy across all 12 volumes: the phrase "My First" (and any pill box, ribbon, or badge containing it) is strictly prohibited from all front covers, spines, back cover grids, interior pages, and metadata. The official series title is "Copy to Color" and the publisher imprint is strictly "The Pivot Digital Publication".

### R4. Amazon KDP Metadata Packages
Generate a complete, policy-compliant metadata package for each of the 12 volumes, including exact title, subtitle, formatted HTML description using only KDP-supported tags (`<b>`, `<i>`, `<h3>`, `<ul>`, `<li>`, `<p>`), 7 distinct validated backend keyword phrases within character limits, and 2 verified BISAC category paths.

### R5. Verification Resources & Automated Quality Preflight
Utilize the existing unit test suite in `tests/` and provide automated preflight verification scripts to programmatically validate page counts, dimensional accuracy, DPI, margin safe areas, absence of forbidden phrases, and visual proof contact sheets for all release artifacts.

## Acceptance Criteria

### Interior PDF Quality & Integrity
- [ ] All 12 interior PDFs exist, are valid uncorrupted PDF files, and have exactly 32 pages each.
- [ ] Every interior PDF has page dimensions of 8.625 x 11.25 inches (bleed mediabox).
- [ ] In each volume, pages 2 through 31 contain 30 distinct educational subjects with non-identical lineart outlines.
- [ ] Coloring lineart regions are crisp pure black lines on pure white paper with no grayscale artifacts or color bleed.

### Full-Wrap Cover Spread Compliance
- [ ] All 12 full-wrap cover spread PDFs and 300 DPI preview PNGs exist.
- [ ] Dimensions for every cover spread equal $17.322 \times 11.250\text{ in}$ (5197 x 3375 px) at 300 DPI.
- [ ] Spine text is omitted on all spreads per KDP rules for < 79 pages.
- [ ] An unobstructed $2.0 \times 1.2\text{ in}$ barcode safe area is preserved at bottom-right of the back cover with 0.5 in clearance.
- [ ] Back cover displays a 4x3 collection grid embedding all 12 authentic miniature front covers with no missing glyph boxes (`□`).

### Brand Governance & Zero "My First"
- [ ] Zero occurrences of the phrase "My First" (case-insensitive) across all 12 front covers, spines, back cover grids, interior pages, manifests, and metadata files.
- [ ] Imprint is consistently recorded as "The Pivot Digital Publication".

### Automated Verification Suite
- [ ] Automated preflight script executes and passes 100% on all 12 volumes.
- [ ] Existing test suite (`unittest discover -s tests`) passes with 0 failures or errors.
