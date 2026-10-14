# Dispatch: Explorer Survey 2 — Cover Architecture & 4x3 Collection Grid Engine

- Working Directory: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2
- Parent Conversation ID: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
- Original Request: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- Project Root: d:\pivot-edu-kdp\pivot-digital-edu-kdp

## Mission
You are Explorer 2 for the Survey Phase. Your focus is Cover Generation Architecture, Typography, and the 4x3 Collection Grid Engine for all 12 series volumes.
Read ORIGINAL_REQUEST.md and AGENTS.md before beginning.

Investigate:
1. Cover compilation scripts (`main.py`, `scripts/compile_cover.py`, `scripts/compile_animals_cover.py`, or any new cover scripts).
2. KDP mechanical specs for 32-page full-wrap covers:
   - Width: 17.322 in (17.25 + 32 * 0.002252 = 17.322064 in)
   - Height: 11.250 in
   - Resolution: 300 DPI (5197 x 3375 px)
   - Spine text: strictly omitted (<79 pages)
   - Barcode safe area: 2.0 x 1.2 in at bottom-right of back cover with 0.5 in margin clearance.
3. Front cover elements:
   - Official series branding: "The Pivot Kids: Color & Play" (clean sticker contour, no white box)
   - 3D extruded display typography: "Copy to Color: <Subject>" using Google Fonts (`LuckiestGuy-Regular.ttf`)
   - Floating activity card and cheerful kid avatars actively engaged with theme items
4. Back cover elements:
   - Curved ribbon header: "TITLES IN THIS SERIES" (using `Bungee-Regular.ttf` or ReportLab vector)
   - Mascot character waving magic star wand next to "CAN YOU COLLECT THEM ALL?" banner
   - 4x3 collection grid embedding authentic miniature replicas of all 12 series front covers with no missing glyph boxes (`□`)
   - Collector blurb
5. Font availability (`assets/fonts/` or similar), missing glyph handling, cover asset caching/ordering (how thumbnail front covers are rendered for the back grid without circular dependencies).

Write your comprehensive findings and recommendations to:
`d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2\handoff.md`
and send a completion message back to your parent.

## 2026-10-14T19:27:47Z
You are explorer_survey_2 (Cover Engine Explorer).
Your working directory is: d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2
Your parent conversation ID is: ed41e1b9-d5a2-4203-ba58-c83ae4e2cef1
Please read:
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\ORIGINAL_REQUEST.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\AGENTS.md
- d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2\DISPATCH.md

Investigate the Cover generation architecture, typography, and 4x3 collection grid engine for all 12 series volumes.
Inspect `main.py`, `scripts/compile_cover.py`, `scripts/compile_animals_cover.py`, cover generation scripts, fonts, and assets.
Examine KDP 32-page full-wrap dimensions (17.322 x 11.250 in, 5197 x 3375 px @ 300 DPI, spine text omitted, 2.0 x 1.2 in barcode safe zone), branding, 3D extruded typography, floating activity card, kid avatars, back ribbon header, wand mascot, and 4x3 miniature front cover grid with no missing glyph boxes.
Determine what exists, what is functional, and what needs to be created or refactored.
Write a comprehensive report to:
d:\pivot-edu-kdp\pivot-digital-edu-kdp\.agents\teamwork\explorer_survey_2\handoff.md
And send a completion message to your parent.
