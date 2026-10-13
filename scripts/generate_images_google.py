"""Generate print-page candidates through Gemini on Google Agent Platform."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import re
import tempfile
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageOps


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def google_image_prompt(prompt: str) -> str:
    """Convert the registry's provider-neutral negative suffix to natural language."""
    marker = "\n\n--no "
    if marker not in prompt:
        return prompt
    positive, negative = prompt.rsplit(marker, 1)
    exclusions = ", ".join(item.strip() for item in negative.replace("\n", " ").split(","))
    return f"{positive.strip()}\n\nAvoid including: {exclusions}."


def extract_image_bytes(response: Any) -> bytes:
    for part in getattr(response, "parts", []) or []:
        inline_data = getattr(part, "inline_data", None)
        image_bytes = getattr(inline_data, "data", None) if inline_data else None
        if image_bytes:
            return image_bytes
    raise ValueError("Google image model returned no image data; the request may have been blocked or returned text only")


def normalize_candidate(raw_bytes: bytes, destination: Path, threshold: int = 200) -> None:
    if not 0 < threshold < 255:
        raise ValueError("threshold must be between 1 and 254")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(BytesIO(raw_bytes)) as opened:
        source = ImageOps.exif_transpose(opened).convert("L")
        source.thumbnail((2250, 3000), Image.Resampling.LANCZOS)
        binary = source.point(lambda pixel: 0 if pixel < threshold else 255, mode="1").convert("L")
        page = Image.new("L", (2550, 3300), 255)
        page.paste(binary, ((2550 - binary.width) // 2, (3300 - binary.height) // 2))
        page.convert("1").save(destination, format="PNG", dpi=(300, 300), optimize=True)


def _upload_file(bucket_name: str, object_name: str, local_path: Path) -> str:
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    content_type = mimetypes.guess_type(local_path.name)[0] or "application/octet-stream"
    blob.upload_from_filename(str(local_path), content_type=content_type)
    return f"gs://{bucket_name}/{object_name}"


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(payload, stream, indent=2)
        stream.write("\n")
        temporary_path = Path(stream.name)
    temporary_path.replace(path)


def _archive_manifest(batch: dict[str, Any], manifest_path: Path, bucket: str, uploader: Any) -> None:
    object_name = "/".join(
        [batch["series_id"], batch["edition_id"], batch["batch_id"], "generation-manifest.json"]
    )
    batch["manifest_uri"] = f"gs://{bucket}/{object_name}"
    _write_json_atomic(manifest_path, batch)
    uploader(bucket, object_name, manifest_path)


def generate_batch(
    batch: dict[str, Any],
    output_manifest: Path,
    candidate_dir: Path,
    project: str,
    location: str,
    model: str,
    aspect_ratio: str,
    threshold: int,
    max_assets: int,
    image_client: Any,
    uploader: Any = None,
    gcs_bucket: str | None = None,
) -> int:
    if not 1 <= max_assets <= 4:
        raise ValueError("max_assets must be between 1 and 4 per run")
    if not re.fullmatch(r"[A-Za-z0-9_-]+", project):
        raise ValueError("Google Cloud project ID is missing or invalid")
    if not re.fullmatch(r"[a-z0-9-]+", location):
        raise ValueError("Google Cloud location is missing or invalid")

    assets = batch.get("assets", [])
    pending_uploads = [asset for asset in assets if asset.get("generation_status") == "GENERATED_LOCAL_PENDING_UPLOAD"]
    if pending_uploads:
        if not gcs_bucket:
            raise ValueError("This batch has generated local files awaiting GCS upload; supply --gcs-bucket to resume without regenerating")
        uploader = uploader or _upload_file
        for asset in pending_uploads:
            raw_path = Path(asset["source_local_path"])
            candidate_path = Path(asset["candidate_page_local_path"])
            if not raw_path.is_file() or not candidate_path.is_file():
                raise FileNotFoundError(f"Cannot resume archival; local source or candidate is missing for {asset['subject_id']}")
            prefix = "/".join([batch["series_id"], batch["edition_id"], batch["batch_id"]])
            if not asset.get("source_uri"):
                asset["source_uri"] = uploader(gcs_bucket, f"{prefix}/raw/{asset['subject_id']}.png", raw_path)
                _write_json_atomic(output_manifest, batch)
            if not asset.get("candidate_page_uri"):
                asset["candidate_page_uri"] = uploader(
                    gcs_bucket, f"{prefix}/candidate-pages/{asset['subject_id']}.png", candidate_path
                )
            asset["generation_status"] = "GENERATED"
            _write_json_atomic(output_manifest, batch)
        _archive_manifest(batch, output_manifest, gcs_bucket, uploader)
        return len(pending_uploads)

    candidates = [asset for asset in assets if asset.get("generation_status", "PENDING_GENERATION") == "PENDING_GENERATION"]
    if not candidates:
        raise ValueError("Batch has no PENDING_GENERATION assets")
    selected = candidates[:max_assets]
    completed = 0

    for asset in selected:
        raw_path = Path(asset["output_path"])
        candidate_path = candidate_dir / f"{asset['subject_id']}.png"
        if raw_path.exists() or candidate_path.exists():
            raise FileExistsError(f"Refusing to overwrite generated asset for {asset['subject_id']}")

        prompt = google_image_prompt(asset["prompt_text"])
        response = image_client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_modalities": ["IMAGE"],
                "image_config": {"aspect_ratio": aspect_ratio},
            },
        )
        raw_bytes = extract_image_bytes(response)
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(raw_bytes)
        normalize_candidate(raw_bytes, candidate_path, threshold)

        asset.update(
            {
                "provider": "Google Gemini Enterprise Agent Platform",
                "model": model,
                "model_version": model,
                "generation_status": "GENERATED_LOCAL_PENDING_UPLOAD",
                "review_status": "PENDING_QA",
                "generation_settings": {
                    "aspect_ratio": aspect_ratio,
                    "output_format": "PNG",
                    "candidate_threshold": threshold,
                    "seed_recorded_but_not_sent": asset.get("seed"),
                    "prompt_enhancement": "provider default",
                },
                "prompt_sent": prompt,
                "generated_at_utc": _utc_now(),
                "source_local_path": str(raw_path.resolve()),
                "candidate_page_local_path": str(candidate_path.resolve()),
                "source_uri": None,
                "candidate_page_uri": None,
            }
        )
        _write_json_atomic(output_manifest, batch)

        if gcs_bucket:
            if uploader is None:
                uploader = _upload_file
            prefix = "/".join(
                [batch["series_id"], batch["edition_id"], batch["batch_id"]]
            )
            raw_object = f"{prefix}/raw/{asset['subject_id']}.png"
            candidate_object = f"{prefix}/candidate-pages/{asset['subject_id']}.png"
            asset["source_uri"] = uploader(gcs_bucket, raw_object, raw_path)
            _write_json_atomic(output_manifest, batch)
            asset["candidate_page_uri"] = uploader(gcs_bucket, candidate_object, candidate_path)
            asset["generation_status"] = "GENERATED"
            _write_json_atomic(output_manifest, batch)
        completed += 1

    if gcs_bucket:
        uploader = uploader or _upload_file
        _archive_manifest(batch, output_manifest, gcs_bucket, uploader)
    return completed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--candidate-dir", type=Path, required=True)
    parser.add_argument("--project", default=os.getenv("GOOGLE_CLOUD_PROJECT"))
    parser.add_argument("--location", default=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
    parser.add_argument("--model", default=os.getenv("GOOGLE_IMAGE_MODEL", "gemini-3.1-flash-lite-image"))
    parser.add_argument("--aspect-ratio", default=os.getenv("GOOGLE_IMAGE_ASPECT_RATIO", "3:4"))
    parser.add_argument("--threshold", type=int, default=int(os.getenv("GOOGLE_IMAGE_THRESHOLD", "200")))
    parser.add_argument("--max-assets", type=int, required=True, help="Explicit cost guard: generate at most this many images")
    parser.add_argument("--gcs-bucket", default=os.getenv("GCS_ASSET_BUCKET"))
    args = parser.parse_args()

    if not args.project or args.project == "your-google-cloud-project-id":
        parser.error("set --project or GOOGLE_CLOUD_PROJECT to a real Google Cloud project ID")
    if args.gcs_bucket == "your-private-production-assets-bucket":
        parser.error("set --gcs-bucket or GCS_ASSET_BUCKET to a provisioned private bucket, or pass an empty value to keep outputs local")

    try:
        from google import genai

        batch = json.loads(args.batch.read_text(encoding="utf-8"))
        client = genai.Client(enterprise=True, project=args.project, location=args.location)
        completed = generate_batch(
            batch=batch,
            output_manifest=args.output_manifest,
            candidate_dir=args.candidate_dir,
            project=args.project,
            location=args.location,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            threshold=args.threshold,
            max_assets=args.max_assets,
            image_client=client,
            gcs_bucket=args.gcs_bucket or None,
        )
    except (ImportError, OSError, KeyError, TypeError, ValueError) as error:
        parser.error(str(error))

    print(f"Generated {completed} candidate page(s); all remain PENDING_QA.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())