"""Create a provenance-complete batch manifest from rendered prompt JSONL."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


REQUIRED_PROMPT_FIELDS = {
    "registry_version",
    "series_id",
    "edition_id",
    "age_profile_id",
    "skill_level_id",
    "subject_id",
    "seed",
    "prompt",
}


def load_prompt_batch(path: Path) -> list[dict[str, Any]]:
    prompts: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            prompt = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Invalid JSON on prompt line {line_number}: {error.msg}") from error
        missing_fields = REQUIRED_PROMPT_FIELDS - prompt.keys()
        if missing_fields:
            raise ValueError(f"Prompt line {line_number} is missing fields: {', '.join(sorted(missing_fields))}")
        prompts.append(prompt)

    if not prompts:
        raise ValueError("Prompt batch is empty")
    for field in ("registry_version", "series_id", "edition_id", "age_profile_id", "skill_level_id"):
        if len({prompt[field] for prompt in prompts}) != 1:
            raise ValueError(f"Prompt batch must contain one consistent {field}")
    for field in ("subject_id", "seed"):
        values = [prompt[field] for prompt in prompts]
        if len(set(values)) != len(values):
            raise ValueError(f"Prompt batch contains duplicate {field} values")
    return prompts


def build_batch_manifest(
    prompts: list[dict[str, Any]],
    provider: str,
    model: str,
    model_version: str,
    asset_dir: Path,
    edition_id: str | None = None,
) -> dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    batch_id = "-".join(
        [
            prompts[0]["series_id"],
            prompts[0]["edition_id"],
            datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            uuid4().hex[:8],
        ]
    )
    prompt_edition_modifier_id = prompts[0]["edition_id"]
    edition_id = edition_id or prompt_edition_modifier_id
    assets = []
    for prompt in prompts:
        assets.append(
            {
                "asset_id": f"{prompts[0]['series_id']}.{prompt['subject_id']}.v1",
                "subject_id": prompt["subject_id"],
                "edition_id": edition_id,
                "prompt_edition_modifier_id": prompt_edition_modifier_id,
                "prompt_registry_version": prompt["registry_version"],
                "prompt_text": prompt["prompt"],
                "provider": provider,
                "model": model,
                "model_version": model_version,
                "seed": prompt["seed"],
                "generation_settings": {},
                "generated_at_utc": None,
                "source_uri": None,
                "output_path": str(asset_dir / f"{prompt['subject_id']}.png"),
                "review_status": "PENDING_GENERATION",
            }
        )

    return {
        "schema_version": "1.0.0",
        "batch_id": batch_id,
        "series_id": prompts[0]["series_id"],
        "edition_id": edition_id,
        "prompt_edition_modifier_id": prompt_edition_modifier_id,
        "age_profile_id": prompts[0]["age_profile_id"],
        "skill_level_id": prompts[0]["skill_level_id"],
        "provider": provider,
        "model": model,
        "model_version": model_version,
        "batch_created_at_utc": created_at,
        "output_asset_directory": str(asset_dir),
        "assets": assets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prompts", required=True, type=Path)
    parser.add_argument("--provider", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-version", required=True)
    parser.add_argument("--edition-id", help="Actual product edition/version, e.g. v1.0-core")
    parser.add_argument("--asset-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    for field in ("provider", "model", "model_version"):
        if not getattr(args, field).strip():
            parser.error(f"--{field.replace('_', '-')} cannot be empty")

    try:
        prompts = load_prompt_batch(args.prompts)
        manifest = build_batch_manifest(
            prompts,
            args.provider.strip(),
            args.model.strip(),
            args.model_version.strip(),
            args.asset_dir,
            args.edition_id,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    except (OSError, TypeError, ValueError) as error:
        parser.error(str(error))

    print(f"Prepared {len(manifest['assets'])} generation records in {args.output}")
    print("Records remain PENDING_GENERATION until provider output and source URIs are recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())