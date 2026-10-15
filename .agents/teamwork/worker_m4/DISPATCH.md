# Dispatch: Worker M4 — Quality Preflight Runner & 12-Volume Integration

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m4
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Test Infrastructure: d:\pivot-edu-kdp\pivot-digital-edu-kdp\TEST_INFRA.md
- Test Readiness: d:\pivot-edu-kdp\pivot-digital-edu-kdp\TEST_READY.md

## Write Ownership (Exclusive)
- `scripts/preflight_kdp.py`
- `main.py` (for `preflight` subcommand)
- `local_builds/interiors/`
- `.agents/teamwork/worker_m4/`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. Read ORIGINAL_REQUEST.md, AGENTS.md, `orchestrator_1/PROJECT.md`, `TEST_INFRA.md`, and `TEST_READY.md`.
2. Batch-compile all 12 32-page interior PDFs and 300 DPI contact sheet proofs using `scripts/compile_copy_to_color_interior.py --all` into `local_builds/interiors/` (or run volume by volume).
3. Implement `scripts/preflight_kdp.py` and register the `preflight` subcommand in `main.py` (`python main.py preflight`):
   - Programmatically audits all 12 series volumes across the 12 criteria:
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
4. Execute `python main.py preflight` or `scripts/preflight_kdp.py` and verify 100% PASS on all 12 volumes with exit code 0.
5. Execute full test suites:
   - `.venv\Scripts\python.exe -m unittest discover -s tests -v`
   - `.venv\Scripts\python.exe tests/e2e/run_all_e2e.py`
6. Execute stage checkpoint git commit:
   `git commit -m "feat(preflight): implement automated 12-volume KDP preflight verification runner and compile 12-volume 32p interiors"`
7. Write report to `.agents/teamwork/worker_m4/handoff.md` and send completion message to parent.


## 2026-10-14T20:34:47Z
You are worker_m4 (Preflight & Integration Worker).
Your working directory is: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m4
Your parent conversation ID is: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Please read:
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\AGENTS.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\TEST_INFRA.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\TEST_READY.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m4\DISPATCH.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your exclusive write ownership:
- scripts/preflight_kdp.py
- main.py (for preflight CLI dispatch)
- local_builds/interiors/
- .agents/teamwork/worker_m4/

Tasks:
1. Batch-compile all 12 32-page interior PDFs and contact sheet proofs to `local_builds/interiors/` using `scripts/compile_copy_to_color_interior.py --all` (or by importing and calling `build_all_series_interiors()`).
2. Verify all 12 interior PDFs and 12 full-wrap cover PDFs exist and match specifications (32 pages, 8.625x11.25 in bleed mediabox, 5197x3375 px covers, zero "My First", exact imprint "The Pivot Digital Publication").
3. Implement `scripts/preflight_kdp.py` and connect `python main.py preflight` to run programmatic verification of all 12 volumes against the 12 preflight checklist criteria.
4. Run `python main.py preflight` and ensure 100% PASS with exit code 0.
5. Run full test suites: `.venv\Scripts\python.exe -m unittest discover -s tests -v` and `.venv\Scripts\python.exe tests/e2e/run_all_e2e.py`.
6. Execute stage checkpoint git commit:
   git commit -m "feat(preflight): implement automated 12-volume KDP preflight verification runner and compile 12-volume 32p interiors"
7. Write report to `.agents/teamwork/worker_m4/handoff.md` and send completion message to parent.
