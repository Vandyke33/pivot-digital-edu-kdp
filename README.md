# pivot-digital-edu-kdp
Amazon Kindle Direct Publishing books

## Local pipeline

Install Python dependencies with `python -m pip install -r requirements.txt`.

Render the Solar System prompt batch without calling an image provider:

```powershell
python scripts/render_prompts.py --series solar_system_explorers --edition core_coloring --output .\local_builds\solar-system-explorers\v1.0-core\prompts.jsonl
```

Prompt difficulty is selectable independently of age, for example `--skill-level advanced`. Age rules always take precedence over skill-level detail, and the selected skill level is written into prompt and generation provenance.

Prepare auditable per-subject generation records for Google Gemini Enterprise Agent Platform (formerly Vertex AI):

```powershell
python scripts/prepare_generation_batch.py --prompts .\local_builds\solar-system-explorers\v1.0-core\prompts.jsonl --provider google-gemini-agent-platform --model "$env:GOOGLE_IMAGE_MODEL" --model-version "$env:GOOGLE_IMAGE_MODEL" --asset-dir .\local_builds\solar-system-explorers\v1.0-core\raw --output .\local_builds\solar-system-explorers\v1.0-core\generation-manifest.json
```

Generate a one-image pilot locally after `gcloud auth application-default login`, enabling the Gemini Enterprise Agent Platform API, and configuring billing and IAM:

```powershell
python scripts/generate_images_google.py --batch .\local_builds\solar-system-explorers\v1.0-core\generation-manifest.json --output-manifest .\local_builds\solar-system-explorers\v1.0-core\generation-manifest.json --candidate-dir .\local_builds\solar-system-explorers\v1.0-core\candidate-pages --max-assets 1
```

The command sends at most the explicit `--max-assets` count to the configured image model. It stores the provider image separately from a thresholded 2550 x 3300 candidate, records the transformation, and leaves the item `PENDING_QA`. It does not create approved artwork. Optional `--gcs-bucket` uploads provider originals, candidate pages, and the manifest to versioned GCS paths.

For GitHub Actions, manually dispatch `.github/workflows/generate-first-art-batch.yml` from protected `main` with a small `max_images` value. Configure repository **Variables** `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_IMAGE_MODEL`, `GCP_WIF_PROVIDER`, `GCP_GENERATION_SERVICE_ACCOUNT`, and `GCS_ASSET_BUCKET`. Set up Google Workload Identity Federation with a provider condition restricted to your GitHub repository and `refs/heads/main`; grant the federated principal `roles/iam.workloadIdentityUser` on the dedicated service account. Give that service account `roles/aiplatform.user` on the project and `roles/storage.objectCreator` on the private asset bucket. Enable the Gemini Enterprise Agent Platform API and billing. No service-account JSON key or Google API secret is needed; the workflow requests short-lived credentials using GitHub OIDC. These project/provider/service-account identifiers belong in GitHub Variables, not Secrets; only long-lived secrets belong in GitHub Secrets. Keep output files in the GCS bucket and Actions artifact, never in Git.

The pilot uses `gemini-3.1-flash-lite-image` on the `global` endpoint; Google currently lists the 1K image output at approximately $0.034 per image, plus small prompt input charges. Verify current project pricing before dispatch. Imagen 4 is not selected because Google's current model documentation lists its June 30, 2026 discontinuation date, which has passed.

Vectorize raw AI generations into resolution-independent SVG masters and 300-DPI auto-framed previews:

```powershell
python scripts/vectorize_asset.py --input .\local_builds\solar-system-explorers\v1.0-core\raw\sun.png --category solar-system --subject-id sun --asset-id solar_system_explorers.sun.v1 --register --copy-to .\local_builds\solar-system-explorers\v1.0-core\approved-line-art\sun.png
```

The vectorizer auto-detects line-art bounds, crops empty whitespace, traces smooth vector paths via `vtracer`, scales and centers the drawing to fill the 0.5-inch printable safe area at 8.5 x 11 inches, renders a crisp 2550 x 3300 300-DPI preview via `resvg`, and registers hashes in `catalogs/asset_registry.json`.

The tracked edition manifest is `manifests/solar-system-explorers-v1.0-core.json`. Put final-size, QA-approved monochrome artwork under its ignored local `asset_root`, change each corresponding `qa_status` to `PASS` only after review, then build with:

```powershell
python scripts/compile_interior.py --manifest .\manifests\solar-system-explorers-v1.0-core.json --output .\local_builds\solar-system-explorers\v1.0-core\interior-proof.pdf --trim 8.5x11 --bleed all --reverse-page black
```

The builder rejects absent or unapproved art, non-binary grayscale, transparency, insufficient raster dimensions, and visible contours outside the safe margin. It creates a proof PDF, not a publication approval; confirm page geometry and every page in the current KDP Previewer before release. Run unit tests with `python -m unittest discover -s tests`.

Flexible activity layouts use `page_plan_mode: flexible_activity`; an example is in `manifests/activity-layouts-v1-example.json`. Supported page types are single illustrations, 2-4-panel pages, paired color-reference pages, connect-the-dots, and trace paths. Each raster panel must be independently QA-approved. Color-reference pages require `interior_color_mode: color`; connect-the-dots and tracing geometry is stored as ordered normalized vector points. The builder validates composition geometry, age gates, minimum sizes, safe margins, and QA status before PDF creation.

## Asset library and reuse control

Keep editable SVG masters outside Git under `assets/svg/<category>/<asset-id>/v1.svg`; keep the corresponding 2550 x 3300-or-larger QA preview under `assets/previews/<category>/<asset-id>/v1.png`. Categories are `animals`, `flowers`, `trees`, `cartoons`, `solar-system`, `vehicles`, and `other`. The tracked `catalogs/asset_registry.json` stores stable IDs, exact and normalized SVG hashes, preview hashes, a 64-bit visual fingerprint, parent lineage, QA decisions, and published-edition history.

Register only rights-cleared candidate artwork after creating its SVG master and final-size preview. Local paths and hashes are sufficient while the project is local; add the optional versioned GCS URIs when migrating the asset library:

```powershell
python scripts/asset_registry.py register --asset-id solar.sun.v1 --category solar-system --subject-id sun --svg .\assets\svg\solar-system\solar.sun.v1\v1.svg --preview .\assets\previews\solar-system\solar.sun.v1\v1.png
```

After visual and technical QA, record a named reviewer and timestamp with `python scripts/asset_registry.py approve --asset-id solar.sun.v1 --reviewer "Reviewer Name" --reviewed-at-utc 2026-10-13T12:00:00Z`. The production PDF builder checks registered IDs and verifies the supplied page preview hash. It blocks exact reuse from a published edition. It flags dHash distance 6 or less for documented human review; similarity approval identifies the specific prior asset, reviewer, date, and rationale. After KDP publication, record only the assets actually present in the released book with `python scripts/asset_registry.py publish --edition-id v1.0-core --book-id PIVOT-SOLAR-001 --published-at YYYY-MM-DD --asset-id solar.sun.v1` (repeat `--asset-id` for each illustration).

For a derivative, create a new `asset_id`, set `--parent-asset-id`, and provide a concrete `--change-note`; a trivial recolor or resize is not a meaningful new asset. Never overwrite an approved SVG master: create a new versioned object and asset ID. Registration checks exact duplicates; similarity checks compare only assets with published usage.
