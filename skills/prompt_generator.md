# Skill: Prompt Generator for Interiors & Cover Micro-Assets

## Purpose

Generate structured, reproducible prompts for both interior coloring line art and isolated cover visual assets using the root `prompts.yaml` registry. This skill explicitly separates **visual art generation** from **typography and layout execution**.

---

## 1. Prompt Construction Framework

### Interior Line Art Structure
Assemble interior prompts in the following sequence:
```
[Global Style] + [Age-Profile Modifier] + [Skill-Level Modifier] + [Edition Modifier] + [Interpolated Blueprint Template] + [Global Negative Prompt]
```
`scripts/render_prompts.py` enforces and logs this ordering.

### Cover Hero Character Art Structure
Assemble prompts for cover artwork strictly as **isolated character assets**:
```
[Character/Subject Description] + [Art Style & Shading] + [Color Palette & Mood] + [Isolation Background] + [Cover Negative Constraints]
```

---

## 2. Non-Negotiable Constraints by Asset Type

### A. Interior Line-Art Assets
- **Positive Rules:** Pure monochrome black line art, thick crisp outlines, smooth closed paths, pure white background, coloring book page for kids.
- **Negative Rules:** `--no color, shading, gradients, photorealism, crosshatching, texture, gray pixels, shadows, text, captions, frames, borders`.
- **Age Weighting:**
  - *Toddler (Ages 1–3):* Single focal subject, $4\text{–}6\text{ pt}$ outlines, zero background detail, rounded cute shapes.
  - *Preschool (Ages 4–6):* $2\text{–}3\text{ pt}$ outlines, primary subject with 1–2 simple background elements, expressive eyes.
  - *Elementary (Ages 6–8):* $1.5\text{–}2.5\text{ pt}$ outlines, dynamic action scene, moderate scene complexity.

### B. Cover Hero Character Assets (e.g., Animals Cover)
- **Positive Rules:** Richly colored 2D vector animation style, smooth digital cel-shading, vibrant high-contrast lighting, adorable facial expressions, large friendly eyes, bold distinct silhouettes.
- **Isolation Directives:** `isolated on solid white background, clean silhouette edge, character design sheet style, no background scenery, no frames`.
- **Negative Rules (CRITICAL to prevent clunky artifacts):**
  - `--no text, words, titles, labels, badges, banners, rectangular boxes, white borders, watermark, speech bubbles, mockups, books, covers`.

---

## 3. Production Prompt Templates

### Template 1: Cover Hero Art (Tiger & Monkey for "Animals" Book)
```yaml
prompt: >
  Adorable chibi baby tiger sitting playfully beside a cute baby monkey, 
  vibrant 2D vector children's book illustration style, warm inviting smiles, 
  sparkling cartoon eyes, rich cel-shaded warm oranges, golden yellows, and soft browns, 
  crisp bold outlines, high-contrast lighting, completely isolated on a pure solid white background, 
  character sheet art, 8k resolution, Pixar-inspired 2D storybook aesthetic
negative_prompt: >
  text, typography, title, words, banners, frames, boxes, white borders, 
  complex background, trees, sky, ground, realistic fur texture, 3d render, 
  gloomy lighting, watermark, signature
aspect_ratio: "4:5"
```

### Template 2: Inset Activity Card Artwork ("Before & After" Tiger)
```yaml
prompt: >
  A cute cartoon baby tiger sitting cheerfully facing forward. 
  Left half is fully colored in bright cheerful orange with bold black stripes; 
  Right half is clean black and white coloring page line art with pure white fill 
  and bold 3pt outlines. Split-view educational coloring preview, isolated on pure white background
negative_prompt: >
  text, labels, frames, boxes, gray shading, gradients on the line art half, photorealism
aspect_ratio: "1:1"
```

### Template 3: 12 Thumbnail Cover Graphics for Series Grid
For each volume in the series (e.g., Alphabet, Birds, Sports), generate a single square subject illustration:
```yaml
prompt: >
  Cute vibrant cartoon {SUBJECT_NAME} icon for children, bold colorful 2D vector art, 
  bright cheerful colors, thick clean outlines, joyful expression, 
  isolated on a solid bright {THEME_COLOR} background, flat app-icon style
negative_prompt: >
  text, book cover mockup, borders, shadows, realistic details
aspect_ratio: "1:1"
```

---

## 4. Edge Cases and Rejection Behavior

- If requested content cannot be represented without tiny mechanical detail, simplify the silhouette and omit the detail rather than thinning the lines.
- If a subject requires a context scene, reduce it to at most the supporting elements allowed by its age profile.
- If the provider cannot enforce monochrome or a stable seed, record that limitation and send outputs through manual QA; never claim the prompt itself guarantees compliance.
- If the output contains gray antialiasing, pseudo-text, open contours, or trademark-like features, reject or route for documented cleanup and a fresh QA pass.
- If a requested edition needs facts, tracing letters, labels, or search icons, leave a clean reserved area and add reviewed layout elements after image generation.

## 5. Output Contract

Return the assembled prompt, negative prompt, selected profile/modifier, generation settings, asset URI, and batch-manifest record. Mark every image `PENDING_QA` until the visual QA skill issues a decision.