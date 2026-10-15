# Dispatch: Challenger 2 (M1) — Adversarial Manifest Schema & Page Sequence Stress Test

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_2_m1
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Worker Report: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1\handoff.md

## Mission
Adversarially challenge and stress-test all 12 manifests in `manifests/`.
Write an automated adversarial test harness in your working directory to verify:
1. Manifest Existence: Assert all 12 expected 32-page manifests exist:
   `alphabet-v1.0-core-32p.json` through `vegetables-v1.0-core-32p.json`.
2. Exact Page Count: For each manifest, assert `len(manifest["pages"]) == 32` and `manifest["expected_page_count"] == 32`.
3. Page Structure Integrity:
   - Page 1 must have `type == "welcome"`.
   - Pages 2–31 (30 pages) must have `type == "copy_to_color"`.
   - Page 32 must have `type == "certificate"`.
4. Subject Uniqueness & Alignment:
   - Assert `len(set(manifest["expected_subjects"])) == 30`.
   - Cross-check each subject against `SERIES_CATALOG` in `scripts/compile_copy_to_color_interior.py` to ensure exact matching and zero missing or swapped subjects.
5. Imprint Consistency:
   - Assert `manifest["publisher"] == "The Pivot Digital Publication"`.

Deliver your confirmation of correctness and empirical findings in:
`d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_2_m1\handoff.md`
and send a completion message to your parent.

## 2026-10-14T19:53:47Z

Adversarially challenge and stress-test all 12 manifests in `manifests/`:
Write a Python script to assert:
- All 12 manifests exist and parse.
- Exactly 32 pages per manifest.
- Page 1 welcome, pages 2-31 copy_to_color, page 32 certificate.
- Exactly 30 unique subjects matching SERIES_CATALOG in `compile_copy_to_color_interior.py`.
- Publisher equals "The Pivot Digital Publication".
Deliver confirmation of correctness in handoff.md and send completion message to parent.
