import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from scripts.compile_interior import _validate_raster, build_pdf, load_and_validate_manifest, validate_page_plan
from scripts.asset_reuse import (
    approve_asset_record,
    check_manifest_reuse,
    empty_registry,
    normalized_svg_sha256,
    register_asset_record,
    visual_fingerprint,
)
from scripts.generate_images_google import generate_batch, google_image_prompt, normalize_candidate
from scripts.prepare_generation_batch import build_batch_manifest, load_prompt_batch
from scripts.render_prompts import render_registry
import yaml


ROOT = Path(__file__).resolve().parents[1]


class PromptRendererTests(unittest.TestCase):
    def test_renders_all_solar_subjects_in_stable_order(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))

        rendered = render_registry(registry, "solar_system_explorers", "core_coloring")

        self.assertEqual(len(rendered), 15)
        self.assertEqual(rendered[0]["subject_id"], "sun")
        self.assertEqual(rendered[0]["seed"], 41001)
        self.assertIn("pure white", rendered[0]["prompt"])
        self.assertIn("--no color", rendered[0]["prompt"])

    def test_rejects_unknown_subject_series(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))

        with self.assertRaisesRegex(ValueError, "Unknown series_id"):
            render_registry(registry, "not-a-series", "core_coloring")

    def test_skill_level_changes_prompt_modifier(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))

        beginner = render_registry(registry, "solar_system_explorers", "core_coloring", "beginner")[0]
        advanced = render_registry(registry, "solar_system_explorers", "core_coloring", "advanced")[0]

        self.assertIn("broad open regions", beginner["prompt"])
        self.assertIn("nested regions", advanced["prompt"])
        self.assertEqual(advanced["skill_level_id"], "advanced")

    def test_batch_manifest_carries_provider_and_subject_provenance(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))
        prompts = render_registry(registry, "solar_system_explorers", "core_coloring")

        batch = build_batch_manifest(prompts, "test-provider", "test-model", "v1", Path("assets"))

        self.assertEqual(len(batch["assets"]), 15)
        self.assertEqual(batch["assets"][0]["subject_id"], "sun")
        self.assertEqual(batch["assets"][0]["asset_id"], "solar_system_explorers.sun.v1")
        self.assertEqual(batch["assets"][0]["review_status"], "PENDING_GENERATION")
        self.assertIsNone(batch["assets"][0]["generated_at_utc"])

    def test_batch_separates_book_edition_from_prompt_modifier(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))
        prompts = render_registry(registry, "solar_system_explorers", "core_coloring")

        batch = build_batch_manifest(
            prompts, "test-provider", "test-model", "v1", Path("assets"), edition_id="v1.0-core"
        )

        self.assertEqual(batch["edition_id"], "v1.0-core")
        self.assertEqual(batch["prompt_edition_modifier_id"], "core_coloring")
        self.assertEqual(batch["assets"][0]["edition_id"], "v1.0-core")
        self.assertEqual(batch["assets"][0]["prompt_edition_modifier_id"], "core_coloring")

    def test_rejects_duplicate_subjects_in_prompt_batch(self):
        prompt = {
            "registry_version": "1.0.0",
            "series_id": "series",
            "edition_id": "edition",
            "age_profile_id": "age",
            "skill_level_id": "beginner",
            "subject_id": "same",
            "seed": 1,
            "prompt": "test prompt",
        }
        with tempfile.TemporaryDirectory() as directory:
            prompts_path = Path(directory) / "duplicate-prompts.jsonl"
            prompts_path.write_text(json.dumps(prompt) + "\n" + json.dumps(prompt) + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "duplicate subject_id"):
                load_prompt_batch(prompts_path)


class GoogleImageGenerationTests(unittest.TestCase):
    class FakeImageClient:
        def __init__(self, image_bytes):
            self.models = self
            self.image_bytes = image_bytes
            self.calls = []

        def generate_content(self, **kwargs):
            self.calls.append(kwargs)
            return type(
                "Response",
                (),
                {"parts": [type("Part", (), {"inline_data": type("InlineData", (), {"data": self.image_bytes})()})()]},
            )()

    def test_imagen_prompt_converts_provider_flags_to_text(self):
        prompt = "bold clean outlines\n\n--no color, shading, gray"

        rendered = google_image_prompt(prompt)

        self.assertIn("Avoid including: color, shading, gray.", rendered)
        self.assertNotIn("--no", rendered)

    def test_candidate_generation_normalizes_image_and_keeps_qa_pending(self):
        source = BytesIO()
        Image.new("RGB", (768, 1024), "white").save(source, format="PNG")
        image_client = self.FakeImageClient(source.getvalue())
        batch = {
            "batch_id": "test-batch",
            "series_id": "test-series",
            "edition_id": "v1-core",
            "assets": [
                {
                    "subject_id": "sun",
                    "prompt_text": "clean line art\n\n--no shading",
                    "output_path": "raw/sun.png",
                    "seed": 101,
                    "generation_status": "PENDING_GENERATION",
                    "review_status": "PENDING_GENERATION",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "generation-manifest.json"
            candidate_dir = root / "candidate-pages"
            batch["assets"][0]["output_path"] = str(root / "raw/sun.png")

            count = generate_batch(
                batch,
                manifest_path,
                candidate_dir,
                "project-123",
                "us-central1",
                "gemini-image-model",
                "3:4",
                200,
                1,
                image_client,
            )

            self.assertEqual(count, 1)
            with Image.open(candidate_dir / "sun.png") as candidate:
                self.assertEqual(candidate.size, (2550, 3300))
            self.assertEqual(batch["assets"][0]["review_status"], "PENDING_QA")
            self.assertEqual(batch["assets"][0]["generation_status"], "GENERATED_LOCAL")
            self.assertTrue(batch["assets"][0]["generation_settings"]["seed_recorded_but_not_sent"])
            self.assertEqual(len(image_client.calls), 1)

    def test_upscaled_candidate_is_not_accepted_as_native_300_dpi_art(self):
        source = BytesIO()
        Image.new("RGB", (896, 1200), "white").save(source, format="PNG")

        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "candidate.png"
            details = normalize_candidate(source.getvalue(), candidate)

            self.assertTrue(details["requires_vectorization_or_native_300dpi_replacement"])
            with self.assertRaisesRegex(ValueError, "only .* native DPI"):
                _validate_raster(
                    candidate,
                    {"width_in": 8.5, "height_in": 11.0},
                    300,
                    0.5,
                )

    def test_gcs_archive_updates_recorded_uris(self):
        source = BytesIO()
        Image.new("RGB", (768, 1024), "white").save(source, format="PNG")
        image_client = self.FakeImageClient(source.getvalue())
        uploaded = []

        def fake_uploader(bucket, object_name, local_path):
            uploaded.append((bucket, object_name, local_path))
            return f"gs://{bucket}/{object_name}"

        batch = {
            "batch_id": "test-batch",
            "series_id": "test-series",
            "edition_id": "v1-core",
            "assets": [
                {
                    "subject_id": "sun",
                    "prompt_text": "clean line art",
                    "output_path": "raw/sun.png",
                    "seed": 101,
                    "generation_status": "PENDING_GENERATION",
                    "review_status": "PENDING_GENERATION",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            batch["assets"][0]["output_path"] = str(root / "raw/sun.png")
            manifest_path = root / "manifest.json"
            generate_batch(
                batch, manifest_path, root / "candidate", "project-123", "us-central1",
                "gemini-image-model", "3:4", 200, 1, image_client,
                uploader=fake_uploader, gcs_bucket="private-assets",
            )

        self.assertEqual(batch["assets"][0]["generation_status"], "GENERATED")
        self.assertTrue(batch["assets"][0]["source_uri"].startswith("gs://private-assets/"))
        self.assertTrue(batch["assets"][0]["candidate_page_uri"].startswith("gs://private-assets/"))
        self.assertEqual(len(uploaded), 3)

    def test_resumes_gcs_upload_without_generating_again(self):
        source = BytesIO()
        Image.new("RGB", (768, 1024), "white").save(source, format="PNG")
        image_client = self.FakeImageClient(source.getvalue())
        uploaded = []

        def fake_uploader(bucket, object_name, local_path):
            uploaded.append(object_name)
            return f"gs://{bucket}/{object_name}"

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw_path = root / "raw/sun.png"
            raw_path.parent.mkdir()
            raw_path.write_bytes(source.getvalue())
            candidate_path = root / "candidate/sun.png"
            from scripts.generate_images_google import normalize_candidate
            normalize_candidate(source.getvalue(), candidate_path)
            batch = {
                "batch_id": "test-batch",
                "series_id": "test-series",
                "edition_id": "v1-core",
                "assets": [
                    {
                        "subject_id": "sun",
                        "generation_status": "GENERATED_LOCAL_PENDING_UPLOAD",
                        "review_status": "PENDING_QA",
                        "source_local_path": str(raw_path),
                        "candidate_page_local_path": str(candidate_path),
                        "source_uri": None,
                        "candidate_page_uri": None,
                    }
                ],
            }

            archived = generate_batch(
                batch, root / "manifest.json", root / "candidate", "project-123", "us-central1",
                "gemini-image-model", "3:4", 200, 1, image_client,
                uploader=fake_uploader, gcs_bucket="private-assets",
            )

        self.assertEqual(archived, 1)
        self.assertEqual(image_client.calls, [])
        self.assertEqual(batch["assets"][0]["generation_status"], "GENERATED")
        self.assertEqual(len(uploaded), 3)

    def test_generation_limit_rejects_batches_over_four(self):
        with self.assertRaisesRegex(ValueError, "between 1 and 4"):
            generate_batch(
                {"assets": []}, Path("out.json"), Path("candidate"), "project-123", "us-central1",
                "model", "3:4", 200, 5, self.FakeImageClient(b""),
            )


class InteriorBuilderTests(unittest.TestCase):
    def _make_test_manifest(self, root: Path, qa_status: str = "PASS") -> Path:
        asset_root = root / "assets"
        asset_root.mkdir()
        image = Image.new("RGB", (2550, 3300), "white")
        ImageDraw.Draw(image).ellipse((300, 400, 2250, 2850), outline="black", width=20)
        image.save(asset_root / "sun.png")
        manifest = {
            "title": "Test Coloring Book",
            "subtitle": "A Test",
            "publisher": "Test Publisher",
            "trim": {"width_in": 8.5, "height_in": 11.0, "bleed": "all"},
            "reverse_page": "black",
            "minimum_dpi": 300,
            "minimum_safe_margin_in": 0.5,
            "expected_page_count": 4,
            "expected_subjects": ["sun"],
            "asset_root": "assets",
            "pages": [
                {"number": 1, "type": "title"},
                {"number": 2, "type": "reverse", "design": "black"},
                {
                    "number": 3,
                    "type": "illustration",
                    "subject_id": "sun",
                    "asset": "sun.png",
                    "qa_status": qa_status,
                },
                {"number": 4, "type": "reverse", "design": "black"},
            ],
        }
        manifest_path = root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def test_builds_bleed_sized_pdf_from_approved_asset(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = self._make_test_manifest(root)
            manifest, asset_root, _ = load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")
            output = root / "proof.pdf"

            build_pdf(manifest, asset_root, output)

            reader = PdfReader(str(output))
            self.assertEqual(len(reader.pages), 4)
            self.assertAlmostEqual(float(reader.pages[0].mediabox.width), 8.625 * 72, places=1)
            self.assertAlmostEqual(float(reader.pages[0].mediabox.height), 11.25 * 72, places=1)

    def test_rejects_unapproved_art_before_build(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = self._make_test_manifest(Path(directory), qa_status="PENDING_QA")

            with self.assertRaisesRegex(ValueError, "not QA-approved"):
                load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")

    def test_rejects_full_black_reverse_without_bleed(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = self._make_test_manifest(Path(directory))
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            data["trim"]["bleed"] = "none"
            manifest_path.write_text(json.dumps(data), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "require bleed=all"):
                load_and_validate_manifest(manifest_path, "8.5x11", "none", "black")

    def test_production_manifest_has_exact_32_page_subject_sequence(self):
        manifest = json.loads(
            (ROOT / "manifests/solar-system-explorers-v1.0-core.json").read_text(encoding="utf-8")
        )

        validate_page_plan(manifest)

        self.assertEqual(manifest["expected_page_count"], 32)
        self.assertEqual(len(manifest["expected_subjects"]), 15)

    def test_build_gate_requires_registry_for_manifest_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = self._make_test_manifest(root)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["edition_id"] = "test-edition-v1"
            manifest["asset_registry"] = "registry.json"
            manifest["pages"][2]["asset_id"] = "solar.sun.v1"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            (root / "registry.json").write_text(json.dumps(empty_registry()), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "is not registered"):
                load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")

    def _write_flexible_manifest(self, root: Path, include_color_reference: bool = True) -> Path:
        asset_root = root / "assets"
        asset_root.mkdir()
        line_art = Image.new("RGB", (2550, 3300), "white")
        ImageDraw.Draw(line_art).ellipse((400, 500, 2150, 2800), outline="black", width=24)
        line_art.save(asset_root / "line.png")
        colored_reference = Image.new("RGB", (2550, 3300), "white")
        ImageDraw.Draw(colored_reference).ellipse((400, 500, 2150, 2800), fill=(240, 80, 40), outline="black", width=24)
        colored_reference.save(asset_root / "colored.png")
        reference_page = {
            "number": 3,
            "type": "color_reference",
            "line_art": {"asset": "line.png", "qa_status": "PASS"},
            "colored_reference": {"asset": "colored.png", "qa_status": "PASS"},
            "line_art_width_ratio": 0.68,
        }
        pages = [
            {"number": 1, "type": "title"},
            {
                "number": 2,
                "type": "multi_panel",
                "panels": [
                    {"asset": "line.png", "qa_status": "PASS", "rect": {"x": 0.08, "y": 0.52, "width": 0.4, "height": 0.4}},
                    {"asset": "line.png", "qa_status": "PASS", "rect": {"x": 0.52, "y": 0.52, "width": 0.4, "height": 0.4}},
                ],
            },
            reference_page,
            {
                "number": 4,
                "type": "connect_dots",
                "minimum_age_years": 4,
                "points": [
                    {"x": 0.3, "y": 0.3, "label": 1},
                    {"x": 0.5, "y": 0.3, "label": 2},
                    {"x": 0.7, "y": 0.3, "label": 3},
                    {"x": 0.7, "y": 0.5, "label": 4},
                    {"x": 0.7, "y": 0.7, "label": 5},
                    {"x": 0.5, "y": 0.7, "label": 6},
                    {"x": 0.3, "y": 0.7, "label": 7},
                    {"x": 0.3, "y": 0.5, "label": 8},
                ],
            },
            {
                "number": 5,
                "type": "trace_path",
                "points": [
                    {"x": 0.3, "y": 0.4},
                    {"x": 0.32, "y": 0.4},
                    {"x": 0.34, "y": 0.4},
                ],
            },
        ]
        manifest = {
            "title": "Activity Layout Proof",
            "subtitle": "Layout QA fixture",
            "publisher": "Test Publisher",
            "page_plan_mode": "flexible_activity",
            "interior_color_mode": "color" if include_color_reference else "black_and_white",
            "trim": {"width_in": 8.5, "height_in": 11.0, "bleed": "all"},
            "reverse_page": "black",
            "minimum_dpi": 300,
            "minimum_safe_margin_in": 0.5,
            "expected_page_count": len(pages),
            "asset_root": "assets",
            "pages": pages,
        }
        manifest_path = root / "activity-manifest.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        return manifest_path

    def test_builds_flexible_multi_activity_pdf(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = self._write_flexible_manifest(root)
            manifest, asset_root, asset_paths = load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")
            output = root / "activity-proof.pdf"

            build_pdf(manifest, asset_root, output)

            reader = PdfReader(str(output))
            self.assertEqual(len(reader.pages), 5)
            self.assertAlmostEqual(float(reader.pages[2].mediabox.width), 8.625 * 72, places=1)
            self.assertGreaterEqual(len(asset_paths), 4)

    def test_color_reference_rejected_for_black_and_white_interior(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = self._write_flexible_manifest(Path(directory), include_color_reference=False)

            with self.assertRaisesRegex(ValueError, "interior_color_mode=color"):
                load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")

    def test_connect_dots_rejects_too_close_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = self._write_flexible_manifest(Path(directory))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["pages"][3]["points"][1]["x"] = 0.301
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "too close for print readability"):
                load_and_validate_manifest(manifest_path, "8.5x11", "all", "black")


class AssetReuseTests(unittest.TestCase):
    def _write_preview(self, path: Path, color=(0, 0, 0), shape="ellipse") -> None:
        image = Image.new("RGB", (2550, 3300), "white")
        draw = ImageDraw.Draw(image)
        if shape == "ellipse":
            draw.ellipse((500, 700, 2050, 2600), outline=color, width=24)
        else:
            draw.rectangle((500, 700, 2050, 2600), outline=color, width=24)
        image.save(path)

    def _register(self, registry, root: Path, asset_id="animals.rabbit.v1", shape="ellipse", parent=None):
        svg = root / f"{asset_id}.svg"
        path_data = "M10 50 C20 10 80 10 90 50 Z" if shape == "ellipse" else "M10 10 H90 V90 H10 Z"
        svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="{path_data}"/></svg>', encoding="utf-8")
        preview = root / f"{asset_id}.png"
        self._write_preview(preview, shape=shape)
        return register_asset_record(
            registry,
            asset_id,
            "animals",
            "rabbit",
            svg,
            preview,
            f"gs://private/assets/svg/animals/{asset_id}/v1.svg",
            f"gs://private/assets/previews/animals/{asset_id}/v1.png",
            parent_asset_id=parent,
            change_note="Redrawn with a distinct pose, silhouette, and separated ear shapes." if parent else None,
        )

    def test_registration_tracks_svg_and_preview_provenance(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            record = self._register(registry, Path(directory))

        self.assertEqual(record["status"], "pending_review")
        self.assertEqual(len(record["svg_sha256"]), 64)
        self.assertEqual(len(record["normalized_svg_sha256"]), 64)
        self.assertEqual(len(record["visual_fingerprint"]), 16)
        self.assertEqual(record["edition_history"], [])

    def test_svg_normalized_hash_ignores_formatting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "first.svg"
            second = root / "second.svg"
            first.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M0 0L1 1"/></svg>', encoding="utf-8")
            second.write_text('<svg xmlns="http://www.w3.org/2000/svg">\n <path d="M0 0L1 1" />\n</svg>', encoding="utf-8")

            self.assertEqual(normalized_svg_sha256(first), normalized_svg_sha256(second))

    def test_svg_script_and_external_references_are_rejected(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            svg = root / "unsafe.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>', encoding="utf-8")
            preview = root / "preview.png"
            self._write_preview(preview)

            with self.assertRaisesRegex(ValueError, "script elements"):
                register_asset_record(
                    registry, "animals.unsafe.v1", "animals", "animal", svg, preview,
                    "gs://private/assets/svg/animals/animals.unsafe.v1/v1.svg",
                    "gs://private/assets/previews/animals/animals.unsafe.v1/v1.png",
                )

    def test_exact_duplicate_master_or_preview_is_rejected(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self._register(registry, root)
            svg = root / "duplicate.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M10 10L90 90"/></svg>', encoding="utf-8")
            preview = root / "duplicate.png"
            self._write_preview(preview)

            with self.assertRaisesRegex(ValueError, "exactly duplicates registered asset"):
                register_asset_record(
                    registry, "animals.rabbit.copy", "animals", "rabbit", svg, preview,
                    "gs://private/assets/svg/animals/animals.rabbit.copy/v1.svg",
                    "gs://private/assets/previews/animals/animals.rabbit.copy/v1.png",
                )

    def test_near_duplicate_published_art_requires_human_review(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = self._register(registry, root)
            approve_asset_record(registry, original["asset_id"], "human-reviewer", "2026-10-13T12:00:00Z")
            original["status"] = "published"
            original["edition_history"].append({"edition_id": "v1", "status": "published"})

            svg = root / "variant.svg"
            svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"><path d="M10 10L80 90"/></svg>', encoding="utf-8")
            preview = root / "variant.png"
            self._write_preview(preview, color=(1, 1, 1))
            with self.assertRaisesRegex(ValueError, "similar to published art"):
                register_asset_record(
                    registry, "animals.rabbit.v2", "animals", "rabbit", svg, preview,
                    "gs://private/assets/svg/animals/animals.rabbit.v2/v2.svg",
                    "gs://private/assets/previews/animals/animals.rabbit.v2/v2.png",
                    parent_asset_id=original["asset_id"],
                    change_note="Changed pose and facial expression with new ear contour.",
                )

    def test_manifest_exact_reuse_from_published_asset_is_blocked(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            candidate = self._register(registry, root, asset_id="animals.rabbit.v2", shape="ellipse")
            approve_asset_record(registry, candidate["asset_id"], "human-reviewer", "2026-10-13T12:00:00Z")
            published = dict(candidate)
            published["asset_id"] = "animals.rabbit.v1"
            published["edition_history"] = [{"edition_id": "published-v1", "status": "published"}]
            registry["assets"][published["asset_id"]] = published
            preview_root = root / "approved"
            preview_root.mkdir()
            preview = preview_root / "rabbit.png"
            self._write_preview(preview)
            manifest = {
                "edition_id": "planned-v2",
                "asset_registry": "../catalogs/asset_registry.json",
                "pages": [{"number": 1, "type": "illustration", "asset_id": candidate["asset_id"], "asset": "rabbit.png"}],
            }

            with self.assertRaisesRegex(ValueError, "exactly reuses the published artwork"):
                check_manifest_reuse(manifest, preview_root, registry)

    def test_similar_published_art_requires_manifest_review(self):
        registry = empty_registry()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            published = self._register(registry, root, asset_id="animals.shape.published", shape="ellipse")
            published["edition_history"] = [{"edition_id": "published-v1", "status": "published"}]
            preview_root = root / "preview"
            preview_root.mkdir()
            preview = preview_root / "candidate.png"
            with Image.open(root / "animals.shape.published.png") as original:
                near_copy = original.copy()
            near_copy.putpixel((0, 0), (254, 254, 254))
            near_copy.save(preview)
            current_svg = root / "animals.shape.current.svg"
            current_svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M10 10 C30 0 70 100 90 90"/></svg>',
                encoding="utf-8",
            )
            review = {
                "decision": "ACCEPT_DISTINCT",
                "reviewer": "human-reviewer",
                "rationale": "Changed pose and overall contour after side-by-side human comparison.",
                "reviewed_at_utc": "2026-10-13T12:00:00Z",
            }
            current = register_asset_record(
                registry,
                "animals.shape.current",
                "animals",
                "shape",
                current_svg,
                preview,
                "gs://private/assets/svg/animals/animals.shape.current/v1.svg",
                "gs://private/assets/previews/animals/animals.shape.current/v1.png",
                parent_asset_id=published["asset_id"],
                change_note="Changed pose and overall contour after iterative redraw.",
                similarity_review=review,
            )
            approve_asset_record(registry, current["asset_id"], "human-reviewer", "2026-10-13T12:00:00Z")
            manifest = {
                "edition_id": "planned-v2",
                "asset_registry": "../catalogs/asset_registry.json",
                "pages": [{"number": 1, "type": "illustration", "asset_id": current["asset_id"], "asset": "candidate.png"}],
            }
            current["similarity_review"] = None

            with self.assertRaisesRegex(ValueError, "documented ACCEPT_DISTINCT human review"):
                check_manifest_reuse(manifest, preview_root, registry)

            manifest["similarity_reviews"] = [{
                "asset_id": current["asset_id"],
                "similar_to_asset_id": published["asset_id"],
                "decision": "ACCEPT_DISTINCT",
                "reviewer": "human-reviewer",
                "rationale": "New pose and composition are visually distinct despite shared subject category.",
                "reviewed_at_utc": "2026-10-13T12:00:00Z",
            }]
            findings = check_manifest_reuse(manifest, preview_root, registry)
            self.assertTrue(findings)


class VectorizationPipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_sample_line_art(self, path: Path, shape_size: int = 200) -> None:
        """Create a synthetic 800x1000 raster image with a centered dark circle."""
        im = Image.new("RGB", (800, 1000), (255, 255, 255))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(im)
        center_x, center_y = 400, 500
        r = shape_size // 2
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r], outline=(0, 0, 0), width=16)
        im.save(path)

    def test_crop_to_content(self):
        from scripts.vectorize_asset import crop_to_content
        sample_path = self.root / "sample.png"
        self._create_sample_line_art(sample_path, shape_size=200)
        with Image.open(sample_path) as im:
            cropped, crop_box = crop_to_content(im, threshold=200, padding_px=10)
            self.assertLess(cropped.width, 800)
            self.assertLess(cropped.height, 1000)
            self.assertGreaterEqual(cropped.width, 190)
            self.assertGreaterEqual(cropped.height, 190)

    def test_vectorize_and_render_end_to_end(self):
        from scripts.vectorize_asset import vectorize_and_render_asset
        raw_path = self.root / "raw.png"
        self._create_sample_line_art(raw_path, shape_size=300)

        svg_out = self.root / "master.svg"
        preview_out = self.root / "preview.png"

        meta = vectorize_and_render_asset(
            input_image_path=raw_path,
            output_svg_path=svg_out,
            output_preview_path=preview_out,
            fill_ratio=0.85,
        )

        self.assertTrue(svg_out.exists())
        self.assertTrue(preview_out.exists())
        self.assertEqual(meta["page_width_px"], 2550)
        self.assertEqual(meta["page_height_px"], 3300)
        with Image.open(preview_out) as preview:
            self.assertEqual(preview.size, (2550, 3300))

    def test_process_single_asset_with_registration(self):
        from scripts.vectorize_asset import process_single_asset
        from scripts.asset_reuse import empty_registry
        from scripts.asset_registry import write_registry

        raw_path = self.root / "star.png"
        self._create_sample_line_art(raw_path, shape_size=250)

        reg_path = self.root / "asset_registry.json"
        write_registry(reg_path, empty_registry())

        meta = process_single_asset(
            input_path=raw_path,
            asset_id="solar_system_explorers.test_star.v1",
            category="solar-system",
            subject_id="test_star",
            svg_master_path=self.root / "v1.svg",
            preview_path=self.root / "v1.png",
            registry_path=reg_path,
            fill_ratio=0.80,
        )

        self.assertTrue(meta["registered"])
        self.assertEqual(meta["record"]["asset_id"], "solar_system_explorers.test_star.v1")
        self.assertEqual(meta["record"]["category"], "solar-system")


if __name__ == "__main__":
    unittest.main()