"""Manage the versioned asset ledger and verify edition artwork reuse."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.asset_reuse import (
        approve_asset_record,
        check_manifest_reuse,
        empty_registry,
        load_registry,
        record_published_edition,
        register_asset_record,
    )
except ModuleNotFoundError:
    from asset_reuse import (
        approve_asset_record,
        check_manifest_reuse,
        empty_registry,
        load_registry,
        record_published_edition,
        register_asset_record,
    )


def write_registry(path: Path, registry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(registry, stream, indent=2)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def load_or_create(path: Path) -> dict[str, Any]:
    if path.exists():
        return load_registry(path)
    return empty_registry()


def _similarity_review(args: argparse.Namespace) -> dict[str, str] | None:
    if not (args.similarity_reviewer or args.similarity_rationale or args.similarity_reviewed_at):
        return None
    if not all((args.similarity_reviewer, args.similarity_rationale, args.similarity_reviewed_at)):
        raise ValueError("similarity reviewer, rationale, and reviewed-at timestamp must be supplied together")
    return {
        "decision": "ACCEPT_DISTINCT",
        "reviewer": args.similarity_reviewer,
        "rationale": args.similarity_rationale,
        "reviewed_at_utc": args.similarity_reviewed_at,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=Path("catalogs/asset_registry.json"))
    commands = parser.add_subparsers(dest="command", required=True)

    register = commands.add_parser("register", help="Register a rights-cleared SVG master and QA preview as pending review")
    register.add_argument("--asset-id", required=True)
    register.add_argument("--category", required=True)
    register.add_argument("--subject-id", required=True)
    register.add_argument("--svg", type=Path, required=True)
    register.add_argument("--preview", type=Path, required=True)
    register.add_argument("--svg-uri", help="Optional versioned gs:// URI for the editable SVG master")
    register.add_argument("--preview-uri", help="Optional versioned gs:// URI for the approved-size preview")
    register.add_argument("--parent-asset-id")
    register.add_argument("--change-note")
    register.add_argument("--similarity-reviewer")
    register.add_argument("--similarity-rationale")
    register.add_argument("--similarity-reviewed-at")

    approve = commands.add_parser("approve", help="Record human QA approval after the SVG and print preview pass")
    approve.add_argument("--asset-id", required=True)
    approve.add_argument("--reviewer", required=True)
    approve.add_argument("--reviewed-at-utc", required=True)

    publish = commands.add_parser("publish", help="Record an edition release and its used assets")
    publish.add_argument("--edition-id", required=True)
    publish.add_argument("--book-id", required=True)
    publish.add_argument("--published-at", required=True)
    publish.add_argument("--asset-id", required=True, action="append")

    check = commands.add_parser("check", help="Fail on exact reuse and require review for near-identical published content")
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--similarity-distance", type=int, default=6)

    args = parser.parse_args()
    try:
        registry = load_or_create(args.registry)
        if args.command == "register":
            record = register_asset_record(
                registry,
                args.asset_id,
                args.category,
                args.subject_id,
                args.svg,
                args.preview,
                args.svg_uri,
                args.preview_uri,
                parent_asset_id=args.parent_asset_id,
                change_note=args.change_note,
                similarity_review=_similarity_review(args),
            )
            write_registry(args.registry, registry)
            print(f"Registered {record['asset_id']} as PENDING_QA; SVG and preview hashes recorded.")
        elif args.command == "approve":
            approve_asset_record(registry, args.asset_id, args.reviewer, args.reviewed_at_utc)
            write_registry(args.registry, registry)
            print(f"Approved {args.asset_id}; release history is still unchanged.")
        elif args.command == "publish":
            record_published_edition(registry, args.edition_id, args.book_id, args.published_at, args.asset_id)
            write_registry(args.registry, registry)
            print(f"Recorded published edition {args.edition_id} with {len(args.asset_id)} assets.")
        else:
            manifest_path = args.manifest.resolve(strict=True)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            asset_root = (manifest_path.parent / manifest["asset_root"]).resolve(strict=True)
            findings = check_manifest_reuse(manifest, asset_root, registry, args.similarity_distance)
            print(json.dumps({"edition_id": manifest["edition_id"], "similarity_reviews": findings}, indent=2))
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
