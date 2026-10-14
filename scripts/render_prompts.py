"""Render versioned prompt-registry entries to deterministic JSON Lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


def render_registry(
    registry: dict[str, Any],
    series_id: str,
    edition_id: str,
    skill_level_id: str | None = None,
) -> list[dict[str, Any]]:
    blueprints = registry.get("book_series_blueprints", {})
    if series_id not in blueprints:
        raise ValueError(f"Unknown series_id: {series_id}")

    blueprint = blueprints[series_id]
    if edition_id not in registry.get("edition_modifiers", {}):
        raise ValueError(f"Unknown edition_id: {edition_id}")

    skill_level_id = skill_level_id or blueprint.get("default_skill_level", "beginner")
    if skill_level_id not in registry.get("skill_levels", {}):
        raise ValueError(f"Unknown skill_level: {skill_level_id}")

    age_profile_id = blueprint["target_age_profile"]
    age_profile = registry["age_profiles"][age_profile_id]
    skill_level = registry["skill_levels"][skill_level_id]
    edition = registry["edition_modifiers"][edition_id]
    settings = registry["global_settings"]
    base_seed = int(blueprint.get("base_seed", settings["seed_management"]["base_seed"]))
    order = settings["prompt_assembly_order"]

    rendered: list[dict[str, Any]] = []
    for subject in blueprint.get("subjects", []):
        try:
            template = blueprint["prompt_template"].format(**subject)
        except (KeyError, ValueError, IndexError) as e:
            raise ValueError(
                f"Template interpolation failed for subject '{subject.get('name', subject.get('id', '?'))}': {e}. "
                f"Check prompt_template placeholders match subject fields."
            ) from e
        sections = {
            "global_style": settings["global_style"],
            "age_profiles[blueprint.age_profile].modifier": age_profile["modifier"],
            "skill_levels[skill_level].modifier": skill_level["modifier"],
            "edition_modifiers[edition].image_modifier": edition["image_modifier"],
            "blueprint.prompt_template interpolated with subject parameters": template,
            "global_negative_prompt": settings["global_negative_prompt"],
        }
        try:
            prompt = "\n\n".join(sections[key].strip() for key in order)
        except KeyError as error:
            raise ValueError(f"Unsupported prompt assembly section: {error.args[0]}") from error

        rendered.append(
            {
                "registry_version": registry["schema_version"],
                "series_id": series_id,
                "edition_id": edition_id,
                "age_profile_id": age_profile_id,
                "skill_level_id": skill_level_id,
                "subject_id": subject["id"],
                "seed": base_seed + int(subject["index"]),
                "prompt": prompt,
            }
        )

    if not rendered:
        raise ValueError(f"Series has no subjects: {series_id}")
    if len({item["subject_id"] for item in rendered}) != len(rendered):
        raise ValueError(f"Series contains duplicate subject IDs: {series_id}")
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("prompts.yaml"))
    parser.add_argument("--series", required=True)
    parser.add_argument("--edition", required=True)
    parser.add_argument("--skill-level", choices=["beginner", "intermediate", "advanced"])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        registry = yaml.safe_load(args.registry.read_text(encoding="utf-8"))
        prompts = render_registry(registry, args.series, args.edition, args.skill_level)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            "".join(json.dumps(prompt, ensure_ascii=True) + "\n" for prompt in prompts),
            encoding="utf-8",
        )
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as error:
        parser.error(str(error))

    print(f"Rendered {len(prompts)} prompts to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())