# Dispatch: Challenger 1 (M1) — Adversarial Metadata & Brand Governance Stress Test

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_1_m1
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Scope: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- Worker Report: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1\handoff.md

## Mission
Adversarially challenge and stress-test the metadata, keywords, HTML descriptions, and brand governance.
Write an automated adversarial test harness in your working directory to verify:
1. Keyword Length Stress Test: Assert that every single backend keyword in `catalogs/catalog_master.json` is <= 50 characters (and <= 50 bytes). Fail if even 1 keyword exceeds 50 chars.
2. Character/Punctuation Test: Assert no keyword contains banned punctuation (`"`, `,`, `;`).
3. Tag Whitelist Test: Parse all HTML descriptions with an HTML parser (e.g. `html.parser`) and verify that ONLY allowed tags (`<b>`, `<i>`, `<h3>`, `<ul>`, `<li>`, `<p>`, `<br>`) are used.
4. Publisher Imprint Test: Search for "Publications" (plural) across `compile_copy_to_color_interior.py` and `catalogs/catalog_master.json`. Fail if found.
5. Brand Governance Test: Search case-insensitively for "My First" across all 12 manifests and `catalog_master.json`. Fail if found.

Deliver your confirmation of correctness and empirical findings in:
`d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_1_m1\handoff.md`
and send a completion message to your parent.
## 2026-10-14T19:53:47Z
You are challenger_1_m1 (Adversarial Metadata Challenger).
Your working directory is: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_1_m1
Your parent conversation ID is: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Please read:
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\AGENTS.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\PROJECT.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\worker_m1\handoff.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\challenger_1_m1\DISPATCH.md

Adversarially challenge and stress-test metadata in `catalogs/catalog_master.json`:
Write a Python script to assert:
- All 84 backend keywords <= 50 chars.
- No banned punctuation in keywords.
- Only allowed HTML tags in descriptions.
- Zero occurrences of "Publications" in imprint fields or line 522.
- Zero occurrences of "My First" (case-insensitive) in metadata and manifests.
Deliver confirmation of correctness in handoff.md and send completion message to parent.
