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

## 2. Front Cover Composition Hierarchy

To match commercial bestsellers without rectangular AI artifacts:

1. **Background Canvas:** Procedural warm coral/orange gradient with rolling green vector hills along the bottom third and subtle starbursts/dotted paths.
2. **Brand Header:** Transparent PNG of "The Pivot Kids (Color & Play)" logo with a smooth sticker-like drop shadow or white outer contour, anchored at the top-center.
3. **Typography Stack (Programmatic Vector Layers):**
   - **"My First"**: Arched or straight text rendered using a Google Font (*Baloo 2* or *Fredoka* Bold) in dark navy or deep red with a soft glowing border. **Never enclosed in a hard rectangular white box.**
   - **"Copy to Color"**: Arched vector bubble lettering in bright white with a $4\text{ px}$ dark navy border and an extruded 3D drop-shadow.
   - **"Animals"**: Giant golden-yellow/orange bubble letters with light-yellow highlight glares and dark-brown 3D depth shadows.
4. **Hero Artwork:** Isolated AI-generated character graphic (Baby Tiger & Monkey) scaled proportionally and layered so their paws naturally overlap the green rolling hills.
5. **Interactive Preview Inset:** A rounded, white floating card displaying the color guide thumbnail and black-and-white coloring outline with drop-shadow styling.

---

## 3. Back Cover & "Titles in this Series" Grid Specification

The back cover acts as an automated cross-selling engine:

1. **Series Header:** Pill-shaped blue ribbon centered near the top: `★ TITLES IN THIS SERIES ★`.
2. **Automated $4 \times 3$ Thumbnail Grid:**
   - 12 equal-sized rounded-corner rectangles.
   - Each card displays the volume's specific theme color header, the title name, a `Vol. #` badge, and the miniature icon art.
   - Grid layout coordinates are mathematically computed by the Python engine, guaranteeing sub-millimeter alignment across all 15 editions.
3. **Marketing Hook Box:** Green rounded pill at bottom-left:
   - `★ Collector's Series of 15 Interactive Titles ★`
   - Blurb: *"A playful, easy coloring series designed for early learners to copy, color, and play!"*
4. **KDP Barcode Exclusion Zone:**
   - Leave an unobstructed white rectangular area of exactly $2.0\text{ inches wide} \times 1.2\text{ inches high}$ located at the bottom right corner ($0.5\text{ inches}$ from the bottom and right trim margins).

