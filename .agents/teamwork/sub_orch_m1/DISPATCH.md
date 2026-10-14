# Dispatch: Milestone 1 Sub-Orchestrator — Governance, Catalogs, Metadata & Manifests

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\sub_orch_m1
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Explorer 3 Survey: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_3\handoff.md

## Scope & Deliverables
You are the Sub-Orchestrator for Milestone 1. Manage the Explorer -> Worker -> Reviewer -> Challenger -> Auditor cycle to implement and verify:
1. **Publisher Imprint Typo Rectification**:
   - In `scripts/compile_copy_to_color_interior.py` line 522, fix `"© The Pivot Digital Publications. All rights reserved. • Amazon KDP Edition"` -> `"© The Pivot Digital Publication. All rights reserved. • Amazon KDP Edition"`.
2. **KDP Metadata Injection in `catalogs/catalog_master.json`**:
   - Inject complete `"metadata"` blocks for all 12 series volumes (`PIVOT-ALPHABET-001-32P` through `PIVOT-VEGETABLES-012-32P`).
   - Use Explorer 3's verified specifications: exact title, subtitle, 7 backend keywords (all <= 50 chars, no banned punctuation, zero competitor terms), 2 verified BISAC categories per volume, and clean HTML descriptions using exclusively allowed KDP tags (`<b>`, `<i>`, `<h3>`, `<ul>`, `<li>`, `<p>`).
   - Ensure `"publisher_imprint": "The Pivot Digital Publication"`.
3. **32-Page Edition Manifests in `manifests/`**:
   - Generate all 12 32-page edition manifests: `alphabet-v1.0-core-32p.json` through `vegetables-v1.0-core-32p.json`.
   - Each manifest must specify `expected_page_count: 32`, the exact 30 curated subjects from `SERIES_CATALOG`, and the page structure (1 welcome, 30 copy_to_color, 1 certificate).
4. **Brand Governance Audit**:
   - Assert zero occurrences of "My First" (case-insensitive) across all manifests, catalog entries, and code files.
5. **Gate Verification**:
   - Run Worker, Reviewers, Challengers, and Forensic Auditor.
   - Record verdicts in `GATE_STATUS.md`. All must pass before delivering handoff.

