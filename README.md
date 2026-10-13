# pivot-digital-edu-kdp
Amazon Kindle Direct Publishing books

## Local pipeline

Install Python dependencies with `python -m pip install -r requirements.txt`.

Render the Solar System prompt batch without calling an image provider:

```powershell
python scripts/render_prompts.py --series solar_system_explorers --edition core_coloring --output .\local_builds\solar-system-explorers\v1.0-core\prompts.jsonl
```

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

The default model placeholder is `gemini-3.1-flash-lite-image`; verify model availability and pricing for your project and location before dispatch. Imagen 4 is not selected because Google's current model documentation lists its June 30, 2026 discontinuation date, which has passed.

The tracked edition manifest is `manifests/solar-system-explorers-v1.0-core.json`. Put final-size, QA-approved monochrome artwork under its ignored local `asset_root`, change each corresponding `qa_status` to `PASS` only after review, then build with:

```powershell
python scripts/compile_interior.py --manifest .\manifests\solar-system-explorers-v1.0-core.json --output .\local_builds\solar-system-explorers\v1.0-core\interior-proof.pdf --trim 8.5x11 --bleed all --reverse-page black
```

The builder rejects absent or unapproved art, non-binary grayscale, transparency, insufficient raster dimensions, and visible contours outside the safe margin. It creates a proof PDF, not a publication approval; confirm page geometry and every page in the current KDP Previewer before release. Run unit tests with `python -m unittest discover -s tests`.
