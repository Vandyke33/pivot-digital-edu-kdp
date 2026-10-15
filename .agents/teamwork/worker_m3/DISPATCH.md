# Dispatch: Worker M3 — 12-Volume Cover Spread Production Pipeline

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m3
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Explorer 2 Report: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2\handoff.md

## Write Ownership (Exclusive)
- `scripts/compile_cover_pil.py`
- `scripts/utils/cover_environment.py`
- `main.py` (for cover CLI dispatch if needed)
- `local_builds/series_fronts/`
- `local_builds/series_covers_32p/`
- `assets/` (for fonts or split activity cards)
- `.agents/teamwork/worker_m3/`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. Read ORIGINAL_REQUEST.md, AGENTS.md, `orchestrator_1/PROJECT.md`, and `explorer_survey_2/handoff.md`.
2. Fix Missing Glyph Box (Tofu `□`) Defect:
   - In `scripts/compile_cover_pil.py` and `scripts/utils/cover_environment.py`, eliminate string-embedded Unicode `★` characters that fail in `Fredoka-Bold.ttf`.
   - Flank ribbons and titles with procedural golden vector stars via `draw_sparkle_star()`.
   - Verify zero tofu boxes (`□`) render on:
     - "TITLES IN THIS SERIES"
     - "CAN YOU COLLECT THEM ALL?"
     - "Collector's Series of 12 Interactive Titles"
3. Split Activity Cards:
   - Provide split color guide + B&W outline activity preview cards for the front cover of each of the 12 volumes (or generate them dynamically from series subject illustrations).
4. Full-Wrap KDP Mechanical Specifications:
   - Verify canvas dimensions: $17.322 \times 11.250\text{ in}$ at 300 DPI ($5197 \times 3375\text{ px}$).
   - PDF Mediabox: $1247.28 \times 810.0\text{ pt}$.
   - Spine width: $0.072\text{ in}$ ($22\text{ px}$ @ 300 DPI). Spine text strictly omitted (<79 pages).
   - Barcode safe area: Unobstructed $2.0 \times 1.2\text{ in}$ at bottom-right of back cover with 0.5 in clearance.
5. Two-Pass 4x3 Collection Back Grid:
   - Pass 1: Render all 12 standalone front covers ($2550 \times 3300\text{ px}$) to `local_builds/series_fronts/`.
   - Pass 2: Embed the 12 authentic miniature front covers into the back cover's 4x3 collection grid on all 12 full-wrap spreads.
6. Batch Compilation:
   - Run compilation generating all 12 full-wrap cover PDFs and 12 300 DPI preview PNG proofs in `local_builds/series_covers_32p/`.
   - Ensure `main.py build-series-covers` executes this batch cleanly.
7. Verify:
   - All 12 cover PDFs and 12 proof PNGs exist.
   - Dimensions are exactly 5197 x 3375 px @ 300 DPI.
   - Barcode safe area is clear.
   - Zero missing glyph boxes.
   - Zero occurrences of "My First".
   - Unit tests pass 100% (`.venv\Scripts\python.exe -m unittest discover -s tests -v`).
8. Execute stage checkpoint git commit:
   `git commit -m "feat(covers): eliminate glyph tofu boxes, generate split activity cards, and batch-compile 12 full-wrap cover spreads with 4x3 back grid"`
9. Write report to `.agents/teamwork/worker_m3/handoff.md` and send completion message to parent.


## 2026-10-14T20:07:14Z
From: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Priority: MESSAGE_PRIORITY_HIGH
Content: You are worker_m3 (Cover Engine Worker).
Your working directory is: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m3
Your parent conversation ID is: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Please read:
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\AGENTS.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2\handoff.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m3\DISPATCH.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your exclusive write ownership:
- scripts/compile_cover_pil.py
- scripts/utils/cover_environment.py
- main.py (for cover CLI dispatch if needed)
- local_builds/series_fronts/
- local_builds/series_covers_32p/
- assets/ (for split activity cards or fonts)
- .agents/teamwork/worker_m3/

Tasks:
1. Fix missing glyph box (tofu □) in `scripts/compile_cover_pil.py` and `scripts/utils/cover_environment.py` by removing string-embedded Unicode ★ in Fredoka-Bold text and rendering procedural golden vector stars via `draw_sparkle_star()`.
2. Provide split color guide + B&W outline activity preview cards for the front cover of each volume.
3. Validate KDP mechanical dimensions for 32 pages ($17.322 \times 11.250$ in, 5197 x 3375 px @ 300 DPI, spine width 22 px, spine text omitted, 2.0 x 1.2 in barcode safe area).
4. Execute two-pass cover compilation:
   - Pass 1: Render 12 standalone front covers ($2550 \times 3300$ px) to `local_builds/series_fronts/`.
   - Pass 2: Render 12 full-wrap spreads with 4x3 collection back grid to `local_builds/series_covers_32p/`.
5. Connect batch compilation in `main.py build-series-covers`.
6. Batch-compile all 12 full-wrap cover PDFs and 12 300 DPI preview PNG proofs.
7. Verify all 12 covers, dimensions, barcode clearance, zero tofu boxes, zero "My First".
8. Run tests (.venv\Scripts\python.exe -m unittest discover -s tests -v).
9. Execute stage checkpoint git commit:
   git commit -m "feat(covers): eliminate glyph tofu boxes, generate split activity cards, and batch-compile 12 full-wrap cover spreads with 4x3 back grid"
10. Write report to `.agents/teamwork/worker_m3/handoff.md` and send completion message to parent.


## 2026-10-14T20:32:31Z
From: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Priority: MESSAGE_PRIORITY_HIGH
Context: Milestone 3 Status Check
Content: Checking on the status of Milestone 3 cover spread implementation. Are you currently waiting on any background task or process? Please provide a progress update on glyph tofu fixes, split activity cards, and batch cover compilation.
Action: Report current status and next steps.
