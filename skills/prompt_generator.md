# Skill: Children's Coloring-Page Prompt Generator

## Purpose

Create versioned, age-calibrated prompts for original children's coloring-book line art using the root `prompts.yaml` registry. This skill creates source-art instructions only; it does not certify generated images as print-ready.

## Required inputs

- Series blueprint ID and subject ID from `prompts.yaml`
- Age profile and edition modifier
- Image provider/model/version and supported aspect ratio/seed options
- Output asset path and target edition version

If a requested subject is not in the registry, request a reviewed registry change before generating it. Do not silently add subjects or relax requirements.

## Prompt construction

1. Load the exact blueprint `prompt_template` and fill every declared subject parameter.
2. Assemble sections in this exact order: global style, age-profile modifier, selected edition modifier, interpolated blueprint template, and global negative prompt. `scripts/render_prompts.py` enforces and logs this ordering.
3. Preserve all negative constraints; provider-specific syntax may be adapted only if the resulting exclusions remain explicit and logged.
4. Use a portrait 4:5 source by default, or 1:1 for a centered single object. Fit to the portrait print safe area without stretching or cropping identifying features.
5. Use the stable subject seed policy when supported. Store prompt, seed, provider/model/version, generation date, and source asset URI in the batch manifest.
6. Generate images without text. Leave tracing and STEM footer bands empty for later typesetting. Never request named commercial characters, brand logos, trademarked vehicle liveries, or imitation of a living artist's style.

## Non-negotiable visual constraints

- Black contours on a pure white background; no color, shading, grayscale, gradients, photorealism, crosshatching, or complex texture.
- Closed, unambiguous regions for intended coloring areas; no broken loops or tangled line intersections.
- Final-size line weights must satisfy the selected age profile: 4-6 pt for toddlers, 2-3 pt for preschool, and 1.5-2.5 pt for early elementary. QA applies a 2 pt general floor; toddler requirements supersede it.
- One focal object for ages 1-3 with no background clutter. Keep scenes simple for ages 4-6. Use moderate, readable storytelling detail for ages 6-8.
- No text, letters, pseudo-lettering, numbers, captions, labels, signatures, watermarks, or logos.
- Keep artwork and all meaningful contours within 0.5 inch of the trim edge for no-bleed pages.

## Edge cases and rejection behavior

- If requested content cannot be represented without tiny mechanical detail, simplify the silhouette and omit the detail rather than thinning the lines.
- If a subject requires a context scene, reduce it to at most the supporting elements allowed by its age profile.
- If the provider cannot enforce monochrome or a stable seed, record that limitation and send outputs through manual QA; never claim the prompt itself guarantees compliance.
- If the output contains gray antialiasing, pseudo-text, open contours, or trademark-like features, reject or route for documented cleanup and a fresh QA pass. Do not pass it based on prompt wording alone.
- If a requested edition needs facts, tracing letters, labels, or search icons, leave a clean reserved area and add reviewed layout elements after image generation.

## Output contract

Return the assembled prompt, negative prompt, selected profile/modifier, generation settings, asset URI, and batch-manifest record. Mark every image `PENDING_QA` until the visual QA skill issues a decision.