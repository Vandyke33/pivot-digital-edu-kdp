## 2026-10-14T19:26:27Z
Sender: 6e10828b-c6e8-4375-b65e-e873a5a892e8 (Sentinel)
Priority: MESSAGE_PRIORITY_HIGH

You are the Project Orchestrator (teamwork_preview_orchestrator).

Your working directory is:
d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1

The project root is:
d:\pivot-edu-kdp\pivot-digital-edu-kdp

The original user request is recorded in:
d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md

Please read ORIGINAL_REQUEST.md, AGENTS.md, and project files carefully.

## Core Objective
Build and automate an end-to-end production pipeline for the 12-volume children's activity book series "The Pivot Kids: Copy to Color", generating:
1. Print-ready 32-page interior PDFs (8.625 x 11.25 in bleed mediabox, 300 DPI) for all 12 planned series volumes (Alphabet, Animals, Birds, Sports, Monsters, Numbers, Fruits, Shapes, Toys, Flowers, Transport, Vegetables). Page 1: welcome page, Pages 2-31: 30 unique themed educational activity pages (educational badge, custom title banner, full-color reference guide, matching crisp B&W coloring outline with zero duplicate subjects within the book), Page 32: completion certificate.
2. Full-wrap KDP paperback cover spreads for 32 pages (17.322 x 11.250 in at 300 DPI, 5197 x 3375 px) with spine text omitted (< 79 pages), official branding "The Pivot Kids: Color & Play", 3D display typography ("Copy to Color: <Subject>"), floating activity card, cheerful kid avatars, back cover curved ribbon header ("TITLES IN THIS SERIES"), mascot waving magic star wand next to "CAN YOU COLLECT THEM ALL?" banner, 4x3 collection grid embedding authentic miniature front covers without missing glyph boxes, collector blurb, and unobstructed 2.0 x 1.2 in barcode safe area at bottom-right (0.5 in clearance).
3. Strict Brand & Naming Governance: zero occurrences of "My First" (case-insensitive) across all covers, spines, back grids, interior pages, manifests, and metadata. Publisher imprint is strictly "The Pivot Digital Publication".
4. Amazon KDP Metadata packages for each volume (title, subtitle, formatted HTML description using only KDP tags <b>, <i>, <h3>, <ul>, <li>, <p>, 7 distinct validated backend keyword phrases within limits, 2 verified BISAC categories).
5. Automated quality preflight scripts and ensure existing test suite (`python -m unittest discover -s tests`) passes 100% with 0 failures or errors.

## Coordination & Lifecycle
- Create your BRIEFING.md, plan.md, and maintain progress.md in your working directory (`d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\orchestrator_1\progress.md`).
- Update progress.md regularly so Sentinel's monitoring crons track your health and progress.
- Decompose the work, dispatch specialist subagents as needed, and manage the team according to Teamwork rules.
- When all tasks are completed and verified, send your final completion report back to Sentinel. Sentinel will conduct an independent Victory Audit before final acceptance.

