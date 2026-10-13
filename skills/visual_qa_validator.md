# Skill: Coloring-Page Visual and Print QA

## Purpose

Audit generated line art before page layout and again after final-size rendering. This skill issues a documented PASS or FAIL; it does not replace KDP's official preview or human release approval.

## Required evidence

- Asset ID, series/edition/subject IDs, source URI, and prompt-registry version
- Provider, model/version, seed, generation date, and any cleanup steps
- Pixel dimensions, color mode, placed dimensions, effective DPI, and a final-size proof
- Intended age profile, edition modifier, safe-area specification, and reviewer/date

## Visual checklist

### Composition and developmental fit

- [ ] Subject is recognizable, friendly, age-appropriate, and consistent with the manifest.
- [ ] Toddler pages contain one large focal object and no background clutter.
- [ ] Preschool pages contain a clear focal object and no more than two simple supporting elements.
- [ ] Elementary pages have readable visual hierarchy and moderate detail, not dense micro-texture.
- [ ] Main subject and meaningful contours remain at least 0.5 inch from trim for no-bleed pages.
- [ ] Required tracing/STEM reserve band is clear and large enough for the planned typeset overlay.

### Contours and printability

- [ ] Intended coloring regions have closed, continuous boundaries.
- [ ] No broken loops, tangled intersections, accidental doubled contours, stray marks, or ambiguous overlaps.
- [ ] Thinnest meaningful line is at least 2 pt at final trim size.
- [ ] Toddler artwork meets its stricter 4-6 pt profile target; preschool artwork targets 2-3 pt; elementary artwork targets 1.5-2.5 pt, subject to the 2 pt general minimum.
- [ ] Details and enclosed regions are large enough to survive printing and be colored with crayons or markers.
- [ ] No gray fills, shading, gradients, crosshatching, halftones, paper texture, or non-white background.

### Content and rights

- [ ] No readable or pseudo-text, letters, numbers, signatures, watermarks, or logos are present.
- [ ] No identifiable copyrighted character, protected brand mark, or trademarked vehicle livery is present.
- [ ] No unsafe, frightening, misleading, or developmentally inappropriate content is present.
- [ ] STEM facts and search-and-find counts, if included in the page plan, are independently checked by a human editor; image generation is not a source of scientific authority.

## Technical checklist

- [ ] Asset opens without corruption and has the expected orientation.
- [ ] Full-page raster artwork is at least 2550 x 3300 px for an 8.5 x 11 inch page at 300 DPI, or vector source has valid geometry and passes a 300 DPI raster proof.
- [ ] Effective resolution is calculated at actual placed size, not inferred from metadata alone.
- [ ] Color mode and pixel inspection confirm black line work on white. Any thresholding or cleanup is documented and rechecked for broken contours and changed line weight.
- [ ] Artwork is fitted proportionally; no stretching, unintended crop, clipping, or transparency artifacts.
- [ ] Final-size proof is inspected at 100 percent and at normal print viewing distance.

## Decision rules

- Mark `FAIL` if any required checklist item fails, if evidence is missing, or if the line weight cannot be verified at final trim.
- Mark `PASS` only when all applicable items pass and measurements/evidence are recorded.
- Record specific defect locations and remediation. A cleaned/re-generated file receives a new asset version and a complete new review.
- Do not promote a failed asset into the assembly manifest. Do not waive a failure because a prompt contained the correct wording.

## QA record format

```yaml
asset_id: "series.subject.version"
review_status: "PASS or FAIL"
reviewer: "reviewer identifier"
reviewed_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
pixel_dimensions: "2550x3300 or actual dimensions"
effective_dpi: 300
minimum_line_weight_pt: 2.0
safe_margin_in: 0.5
defects: []
remediation: []
proof_uri: "local path or gs:// URI"
```