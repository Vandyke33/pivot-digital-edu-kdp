# Dispatch: Worker M1 — Governance, Catalogs, Metadata & Manifests

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Explorer 3 Survey: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_3\handoff.md

## Write Ownership (Exclusive)
- `scripts/compile_copy_to_color_interior.py` (Line 522 typo fix only)
- `catalogs/catalog_master.json`
- `manifests/alphabet-v1.0-core-32p.json` through `manifests/vegetables-v1.0-core-32p.json`
- `.agents/teamwork/worker_m1/`

## Mandatory Integrity Warning
DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A teamwork_preview_auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

## Detailed Tasks
1. Read ORIGINAL_REQUEST.md, AGENTS.md, and `explorer_survey_3/handoff.md`.
2. Fix Publisher Imprint in `scripts/compile_copy_to_color_interior.py`:
   - Line 522: Change `"© The Pivot Digital Publications. All rights reserved. • Amazon KDP Edition"` to `"© The Pivot Digital Publication. All rights reserved. • Amazon KDP Edition"`.
3. In `catalogs/catalog_master.json`:
   - Inject complete, verified `"metadata"` blocks into all 12 series volumes (`PIVOT-ALPHABET-001-32P` through `PIVOT-VEGETABLES-012-32P`) using the exact table in `explorer_survey_3/handoff.md`:
     - Exact title and subtitle
     - 7 distinct backend keyword phrases per volume (all <= 50 chars, no banned punctuation, zero competitor terms)
     - 2 verified BISAC category paths per volume
     - Formatted HTML description using only KDP-supported tags (`<b>`, `<i>`, `<h3>`, `<ul>`, `<li>`, `<p>`)
     - Ensure top-level `"publisher_imprint": "The Pivot Digital Publication"`.
4. In `manifests/`:
   - Create 32-page edition manifests for all 12 series volumes (`alphabet-v1.0-core-32p.json` through `vegetables-v1.0-core-32p.json`).
   - Match the schema and structure of `manifests/animals-v1.0-core-32p.json`:
     - `"expected_page_count": 32`
     - `"expected_subjects"`: the 30 curated subjects from `SERIES_CATALOG` in `compile_copy_to_color_interior.py`
     - `"pages"`: 1 welcome page, 30 copy_to_color pages, 1 certificate page.
     - `"publisher": "The Pivot Digital Publication"`.
5. Verify zero occurrences of "My First" (case-insensitive) across all edited and created files.
6. Verify unit tests: execute `.venv\Scripts\python.exe -m unittest discover -s tests -v` to ensure 0 failures and 0 errors.
7. Write your report to `.agents/teamwork/worker_m1/handoff.md` and send a completion message to your parent.


## 2026-10-14T19:42:16Z
[Message] timestamp=2026-10-14T19:42:16Z sender=ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1 priority=MESSAGE_PRIORITY_HIGH content=You are worker_m1 (Metadata & Manifest Worker).
Your working directory is: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1
Your parent conversation ID is: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Please read:
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\AGENTS.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_3\handoff.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1\DISPATCH.md

DO NOT CHEAT. All implementations must be genuine. DO NOT hardcode test results, create dummy/facade implementations, or circumvent the intended task. A auditor will independently verify your work. Integrity violations WILL be detected and your work WILL be rejected.

Your exclusive write ownership:
- scripts/compile_copy_to_color_interior.py (Line 522 typo fix only: change "Publications" to "The Pivot Digital Publication")
- catalogs/catalog_master.json (inject metadata blocks for all 12 series volumes)
- manifests/ (create 32-page manifests for all 12 series volumes)
- .agents/teamwork/worker_m1/

Tasks:
1. Fix line 522 in `scripts/compile_copy_to_color_interior.py` ("The Pivot Digital Publication").
2. Inject complete, policy-compliant metadata blocks in `catalogs/catalog_master.json` for all 12 series volumes using Explorer 3's exact table (exact titles, subtitles, 7 backend keywords <= 50 chars, 2 verified BISAC categories, clean HTML descriptions with <b>, <i>, <h3>, <ul>, <li>, <p>, imprint "The Pivot Digital Publication").
3. Create all 12 32-page edition manifests in `manifests/` matching `animals-v1.0-core-32p.json`.
4. Ensure zero occurrences of "My First" (case-insensitive) across all files.
5. Verify with unit tests (`.venv\Scripts\python.exe -m unittest discover -s tests -v`).
6. Write your report to `.agents/teamwork/worker_m1/handoff.md` and send a completion message to your parent.


## 2026-10-14T19:47:17Z
[Message] timestamp=2026-10-14T19:47:17Z sender=ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1 priority=MESSAGE_PRIORITY_HIGH content=**Context**: Stage Checkpoint Git Commit Directive
**Content**: User directive received: "commit changes as stages are achieved to track progress and checkpoint code". Once you have verified your changes (imprint fix, metadata injection in catalog_master.json, 12 manifests), please stage and commit them with a clean git commit message, e.g. "feat(metadata): inject 12-volume KDP metadata, fix publisher imprint, and create 32p manifests".
**Action**: Execute git checkpoint commit upon passing verification.
