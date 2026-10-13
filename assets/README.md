# Local Asset Library

Editable artwork masters and preview rasters are local working files and are excluded from Git. Keep a versioned copy in the configured private GCS bucket. Track identity, hashes, QA, derivatives, and edition publication history in `catalogs/asset_registry.json`.

SVG master path convention:

```text
assets/svg/<category>/<asset-id>/v<major>.<minor>.svg
```

Preview path convention:

```text
assets/previews/<category>/<asset-id>/v<major>.<minor>.png
```

Use registry categories exactly: `animals`, `flowers`, `trees`, `cartoons`, `solar-system`, `vehicles`, or `other`. Preserve each approved SVG master; edits create a new version and asset ID, link the parent, and explain the substantive change. Raster previews are required because page proofing and perceptual-reuse checks are based on the actual print candidate.
