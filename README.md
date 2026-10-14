# The Pivot Kids — KDP Publishing Pipeline

Amazon Kindle Direct Publishing (KDP) automated pipeline for original, age-appropriate children's coloring and activity books.

---

## 📚 Book Series Portfolio

### 1. Copy to Color Series (Flagship 12-Volume Series)
- **Brand:** `The Pivot Kids` (with tagline `Color & Play`)
- **Format:** 32 pages, $8.5 \times 11\text{ in}$ trim, full-wrap paperback cover with $0.125\text{ in}$ bleed
- **Interior Layout:** Commercial retail layout featuring top brushstroke word banner, 1:1 color guide thumbnail, and bottom wave footer with crayon page badges.
- **12 Titles in Series:**
  1. `Copy to Color: Alphabet` (Warm Orange `#FF6B35`)
  2. `Copy to Color: Animals` (Coral Red `#FF4D4D`)
  3. `Copy to Color: Birds` (Teal `#2EC4B6`)
  4. `Copy to Color: Sports` (Mint Green `#80ED99`)
  5. `Copy to Color: Monsters` (Lavender Pink `#E056FD`)
  6. `Copy to Color: Numbers` (Purple `#9B5DE5`)
  7. `Copy to Color: Fruits` (Bright Cyan `#00BBF9`)
  8. `Copy to Color: Shapes` (Rose Pink `#F15BB5`)
  9. `Copy to Color: Toys` (Royal Blue `#0077B6`)
  10. `Copy to Color: Flowers` (Warm Amber `#6B4226`)
  11. `Copy to Color: Transport` (Deep Blue `#1D3557`)
  12. `Copy to Color: Vegetables` (Deep Violet `#5A189A`)

### 2. Solar System Explorers
- **Format:** 32-80 pages, $8.5 \times 11\text{ in}$ trim, black line art on white paper with bleed-stop reverse pages.

---

## 🚀 Quick Start with `main.py`

The unified CLI runner `main.py` provides easy commands for all pipeline tasks:

```powershell
# 1. Check pipeline and asset status
python main.py status

# 2. Run full unit test suite (46+ tests)
python main.py test

# 3. Compile 'Copy to Color: Animals' 32-page full-wrap cover spread
python main.py build-animals-cover --page-count 32

# 4. Compile 'Copy to Color: Animals' 32-page interior PDF + proof sheet
python main.py build-copy-to-color-interior --vol-id vol_02

# 5. Compile full spreads or standalone front covers for all 12 series volumes
python main.py build-series-covers --page-count 32

# 6. Build both cover and interior in a single command
python main.py build-all --series copy_to_color_animals
```

---

## 🎨 Cover Engine Architecture

- **Component-First Rule:** AI models generate isolated visual components only; headless Python engines programmatically assemble typography, spine, barcode zone, and back-cover thumbnail grid.
- **Strict Brand & Naming Policy:**
  - Official Brand: `The Pivot Kids`
  - Canonical Title Format: `Copy to Color: <Subject>`
  - **Permanently Banned:** The phrase `"My First"` is strictly prohibited across all front covers, spines, back cover grids, interiors, and metadata.
- **Display Typography Stack:**
  | Usage | Font Family | Font Asset File |
  |---|---|---|
  | Series Title ("Copy to Color") | Luckiest Guy | `LuckiestGuy-Regular.ttf` |
  | Subject Title ("Animals", etc.) | Luckiest Guy | `LuckiestGuy-Regular.ttf` |
  | Brand Header & Subtitles | Fredoka Bold | `Fredoka-Bold.ttf` |
  | Ribbon Banners & Badges | Bungee Regular | `Bungee-Regular.ttf` |
- **Spine Omission Guard:** Per Amazon KDP rules, books with fewer than 79 pages cannot have printed spine text. Spines are automatically left clean of text when `page_count < 79`.
- **Barcode Safe Zone:** Strictly reserves an unobstructed $2.0 \times 1.2\text{ in}$ white box at the bottom right of the back cover spread ($0.5\text{ in}$ clearance from trim margins).

---

## 🧪 Testing & Verification

Run the comprehensive unit test suite:

```powershell
python -m unittest discover -s tests -v
```

Tests cover:
- KDP mechanical dimensions (32-page and 80-page cover spreads)
- Spine text suppression below 79 pages
- 12-volume series catalog integrity and naming policy compliance
- Zero-credit 1:1 binary lineart extraction engine
- Asset reuse and visual fingerprinting (64-bit dHash)
- Prompt rendering and seed management
