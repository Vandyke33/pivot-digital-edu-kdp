# Execution Plan: The Pivot Kids "Copy to Color" 12-Volume Production Pipeline

## Overview
Automate and build the production pipeline across 4 milestones, operating in dual track with an independent E2E Testing track.

---

## Dual Track Structure

### Track 1: Implementation Track
- **Milestone 1**: Governance, Catalogs & KDP Metadata
  - Fix publisher imprint typo in `scripts/compile_copy_to_color_interior.py:522`.
  - Populate `catalogs/catalog_master.json` with complete metadata packages for all 12 series volumes.
  - Generate 32-page edition manifests in `manifests/` for all 12 volumes.
  - Verify zero "My First" brand violations.
- **Milestone 2**: 12-Volume Interior Production Pipeline
  - Implement `scripts/utils/series_illustrations.py` with 360 distinct procedural educational subjects.
  - Update interior canvas in `scripts/compile_copy_to_color_interior.py` to $2588 \times 3375$ px @ 300 DPI with exact $621.0 \times 810.0$ pt bleed mediabox.
  - Add `--all` batch compilation to interior script and `main.py`.
  - Generate and verify all 12 32-page interior PDFs and contact sheet proofs.
- **Milestone 3**: 12-Volume Cover Spread Production Pipeline
  - Fix missing glyph box (tofu `□`) by replacing string `★` with procedural vector `draw_sparkle_star()`.
  - Generate split activity card assets (color + B&W outline) for all 12 volumes.
  - Compile 12 standalone front covers and 12 full-wrap spreads ($17.322 \times 11.250$ in, 5197 x 3375 px @ 300 DPI) with 4x3 back grids.
  - Add `--all` batch compilation to `main.py build-series-covers`.
- **Milestone 4**: Final Milestone: Quality Preflight & Test Verification
  - Implement automated quality preflight runner `scripts/preflight_kdp.py` and CLI command `main.py preflight`.
  - Execute full unit test suite (`python -m unittest discover -s tests`) and ensure 100% pass.
  - Execute automated preflight across all 12 volumes and ensure 100% pass with 0 warnings or errors.

### Track 2: E2E Testing Track (Independent & Concurrent)
- Spawn E2E Testing Orchestrator / Test Writer to create `TEST_INFRA.md`.
- Build comprehensive 4-tier test suite:
  - Tier 1: Feature Coverage (5 tests per feature).
  - Tier 2: Boundary & Corner Cases (dimensions, margins, bleed, page count limits).
  - Tier 3: Cross-Feature Combinations (cover-grid sync, interior-manifest sync, brand governance).
  - Tier 4: Real-World Workload Scenarios (end-to-end multi-volume build and preflight).
- Publish `TEST_READY.md` upon completion.

---

## Dispatch Sequence
1. Dispatch M1 Sub-Orchestrator (Governance, Catalogs, Metadata & Manifests) + E2E Testing Track concurrently.
2. Upon M1 completion, dispatch M2 Sub-Orchestrator (Interiors) and M3 Sub-Orchestrator (Covers) in parallel (independent file boundaries!).
3. Upon M2 and M3 completion and receipt of `TEST_READY.md`, dispatch M4 Sub-Orchestrator (Final Preflight & Test Verification).
4. Run Forensic Audit gate on release artifacts.
5. Deliver comprehensive Victory Report to Sentinel.

