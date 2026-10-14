# Skill: Programmatic KDP Cover Engineering & Layout Specification

## Purpose

Govern the programmatic generation of physical full-wrap paperback book covers (Back Cover + Spine + Front Cover) for Amazon KDP. This skill replaces manual drag-and-drop design tools with an automated Python layout pipeline that guarantees dimensional precision, vector-sharp typography, and print compliance.

---

## 1. Mechanical Dimensioning & Spine Calculation

Amazon KDP requires a single flat PDF spread encompassing the front, spine, back, and full $0.125\text{ inch}$ cutting bleeds.

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│  BLEED (L)   │  BACK COVER  │    SPINE     │ FRONT COVER  │  BLEED (R)   │
│  0.125 in    │  8.500 in    │ Calculated W │  8.500 in    │  0.125 in    │
└──────────────┴──────────────┴──────────────┴──────────────┘
◄────────────────────────────── TOTAL COVER WIDTH ──────────────────────────►
```

### Exact Mathematical Formulas
- **Interior Trim Size:** $8.5 \times 11.0\text{ inches}$
- **Bleed Allowance:** $0.125\text{ inches}$ on all four outer edges
- **White Paper Spine Multiplier:** $0.002252\text{ inches per page}$
- **Total Cover Width:**
  $$\text{Width} = 0.125 + 8.5 + \text{Spine Width} + 8.5 + 0.125 = 17.25 + (\text{Page Count} \times 0.002252)\text{ inches}$$
- **Total Cover Height:**
  $$\text{Height} = 11.0 + (2 \times 0.125) = 11.25\text{ inches}$$
- **Canvas Resolution at $300\text{ DPI}$:**
  $$\text{Width (px)} = \text{Width (in)} \times 300, \quad \text{Height (px)} = 11.25 \times 300 = 3375\text{ pixels}$$

---

## Strict Brand & Title Naming Policy (No "My First" Prefix)

- **Official Brand:** `The Pivot Kids` (with tagline `Color & Play`).
- **Official Series Title:** `Copy to Color`
- **Canonical Book Title Format:** `Copy to Color: <Subject>` (e.g., `Copy to Color: Animals`, `Copy to Color: Alphabet`).
- **Prohibited Phrase (`"My First"`):** NEVER include the words `"My First"` (nor any pill box, ribbon, or banner for it) on the Front Cover, Spine, Back Cover miniature grid, Interior Title Page, or KDP Metadata.
- **Front Cover Title Stack (Top-to-Bottom):**
  1. Top Center: `The Pivot Kids (Color & Play)` logo with a clean, organic white sticker contour (no rectangular box).
  2. Directly Below Logo: `"Copy to Color"` in large, 3D-extruded, neon-glow, sparkle display typography (`LuckiestGuy-Regular.ttf`).
  3. Directly Below Series Title: `"<SUBJECT>"` (e.g., `"Animals"`) in oversized golden-yellow 3D-extruded, neon-glow, sparkle display typography.
- **Kid Avatar & Activity Standard (Cover Hero Art):** Front cover hero artwork MUST feature cheerful, playful kid characters / avatars actively engaged in fun activities with the theme items (e.g., kid hugging a baby tiger, kid chef with giant fruit, kid on ABC blocks with giant crayon). NEVER use isolated, inanimate object clipart alone without expressive child avatars.

---

## 2. Front Cover Composition Hierarchy

To match commercial bestsellers without rectangular AI artifacts:

1. **Background Canvas:** Procedural warm coral/orange gradient with rolling green vector hills along the bottom third and subtle starbursts/dotted paths.
2. **Brand Header:** Transparent PNG of "The Pivot Kids (Color & Play)" logo with a smooth sticker-like drop shadow or white outer contour, anchored at the top-center.
3. **Typography Stack (Programmatic Vector Layers):**
   - **"Copy to Color"**: Arched or floating display bubble lettering in bright white with 3D block extrusion, neon outer glow aura, and vector diamond sparkles (`LuckiestGuy-Regular.ttf`).
   - **"<SUBJECT>" (e.g., "Animals")**: Giant golden-yellow/orange bubble letters with light-yellow highlight glares, 3D depth extrusion, and sparkles (`LuckiestGuy-Regular.ttf`).
   - **Prohibited:** NEVER render the words `"My First"` or any pill badge/ribbon for it.
4. **Hero Artwork:** Isolated AI-generated character graphic (volume-specific cheerful kid avatar actively interacting with theme objects) scaled proportionally and layered so their feet/paws naturally overlap the green rolling hills.
5. **Interactive Preview Inset:** A rounded, white floating card displaying the color guide thumbnail and black-and-white coloring outline with drop-shadow styling.

---

## 3. Back Cover & "Titles in this Series" Grid Specification

The back cover acts as an automated cross-selling engine:

1. **Series Header:** Pill-shaped blue ribbon centered near the top: `★ TITLES IN THIS SERIES ★`.
2. **Automated $4 \times 3$ Thumbnail Grid:**
   - 12 equal-sized rounded-corner rectangles.
   - Each card displays the volume's specific theme color header, the title name, a `Vol. #` badge, and the miniature icon art (or miniature front cover replica).
   - Grid layout coordinates are mathematically computed by the Python engine, guaranteeing sub-millimeter alignment across all 12 series volumes.
3. **Marketing Hook Box:** Green rounded pill at bottom-left:
   - `★ Collector's Series of 12 Interactive Titles ★`
   - Blurb: *"A playful, easy coloring series designed for early learners to copy, color, and play!"*
4. **KDP Barcode Exclusion Zone:**
   - Leave an unobstructed white rectangular area of exactly $2.0\text{ inches wide} \times 1.2\text{ inches high}$ located at the bottom right corner ($0.5\text{ inches}$ from the bottom and right trim margins).

