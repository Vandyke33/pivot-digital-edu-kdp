import json
import tempfile
import unittest
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw
from pypdf import PdfReader

from scripts.compile_interior import build_pdf, load_and_validate_manifest, validate_page_plan
from scripts.generate_images_google import generate_batch, google_image_prompt
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

    def test_batch_manifest_carries_provider_and_subject_provenance(self):
        registry = yaml.safe_load((ROOT / "prompts.yaml").read_text(encoding="utf-8"))
        prompts = render_registry(registry, "solar_system_explorers", "core_coloring")

        batch = build_batch_manifest(prompts, "test-provider", "test-model", "v1", Path("assets"))

        self.assertEqual(len(batch["assets"]), 15)
        self.assertEqual(batch["assets"][0]["subject_id"], "sun")
        self.assertEqual(batch["assets"][0]["review_status"], "PENDING_GENERATION")
        self.assertIsNone(batch["assets"][0]["generated_at_utc"])

    def test_rejects_duplicate_subjects_in_prompt_batch(self):
        prompt = {
            "registry_version": "1.0.0",
            "series_id": "series",
            "edition_id": "edition",
            "age_profile_id": "age",
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
            self.assertEqual(batch["assets"][0]["generation_status"], "GENERATED_LOCAL_PENDING_UPLOAD")
            self.assertTrue(batch["assets"][0]["generation_settings"]["seed_recorded_but_not_sent"])
            self.assertEqual(len(image_client.calls), 1)

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


if __name__ == "__main__":
    unittest.main()