"""Asset identity, SVG integrity, and published-content reuse checks."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from PIL import Image, ImageOps


REGISTRY_SCHEMA_VERSION = "1.0.0"
DEFAULT_SIMILARITY_DISTANCE = 6


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_svg_sha256(path: Path) -> str:
    """Hash structural SVG content while ignoring editor metadata and formatting."""
    root = ET.parse(path).getroot()
    ignored = {"metadata", "namedview"}
    for parent in root.iter():
        for child in list(parent):
            local_name = child.tag.rsplit("}", 1)[-1].lower()
            if local_name in ignored or local_name.startswith("inkscape"):
                parent.remove(child)
    canonical = ET.canonicalize(ET.tostring(root, encoding="unicode"), strip_text=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_svg_master(path: Path) -> None:
    raw = path.read_bytes()
    upper = raw.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("SVG masters may not declare DTDs or entities")
    root = ET.fromstring(raw)
    if root.tag.rsplit("}", 1)[-1].lower() != "svg":
        raise ValueError("Source master root element must be SVG")
    forbidden = {"script", "foreignobject", "iframe", "image", "audio", "video"}
    for element in root.iter():
        local_tag = element.tag.rsplit("}", 1)[-1].lower()
        if local_tag in forbidden:
            raise ValueError(f"SVG masters may not include {local_tag} elements")
        for name, value in element.attrib.items():
            local_name = name.rsplit("}", 1)[-1].lower()
            if local_name.startswith("on"):
                raise ValueError("SVG masters may not contain event-handler attributes")
            if local_name in {"href", "src"} and value and not value.startswith("#"):
                raise ValueError("SVG masters may only use internal fragment references")


def validate_preview(path: Path) -> None:
    with Image.open(path) as image:
        width, height = image.size
        if width < 2550 or height < 3300:
            raise ValueError(f"QA preview must be at least 2550x3300 pixels; got {width}x{height}")
        if image.convert("RGBA").getchannel("A").getextrema() != (255, 255):
            raise ValueError("QA preview may not contain transparency")
        image.load()


def visual_fingerprint(path: Path) -> str:
    """Return a 64-bit difference hash for near-duplicate review, not identity proof."""
    with Image.open(path) as opened:
        image = ImageOps.exif_transpose(opened).convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = image.tobytes()
    bits = 0
    for row in range(8):
        for column in range(8):
            left = pixels[row * 9 + column]
            right = pixels[row * 9 + column + 1]
            bits = (bits << 1) | int(left > right)
    return f"{bits:016x}"


def fingerprint_distance(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def load_registry(path: Path) -> dict[str, Any]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    if registry.get("schema_version") != REGISTRY_SCHEMA_VERSION:
        raise ValueError(f"Unsupported asset registry schema: {registry.get('schema_version')}")
    if not isinstance(registry.get("assets"), dict):
        raise ValueError("Asset registry must contain an assets object keyed by asset_id")
    return registry


def page_asset_references(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    for page in manifest.get("pages", []):
        page_type = page.get("type")
        if page_type == "illustration":
            references.append({"asset_id": page.get("asset_id"), "asset": page.get("asset"), "page": page.get("number")})
        elif page_type == "multi_panel":
            for panel_index, panel in enumerate(page.get("panels", []), start=1):
                references.append(
                    {
                        "asset_id": panel.get("asset_id"),
                        "asset": panel.get("asset"),
                        "page": page.get("number"),
                        "component": f"panel-{panel_index}",
                    }
                )
        elif page_type == "color_reference":
            for key in ("line_art", "colored_reference"):
                component = page.get(key, {})
                references.append(
                    {
                        "asset_id": component.get("asset_id"),
                        "asset": component.get("asset"),
                        "page": page.get("number"),
                        "component": key,
                    }
                )
    return references


def _published_usages(asset: dict[str, Any]) -> list[dict[str, Any]]:
    usages = asset.get("edition_history", [])
    return [usage for usage in usages if usage.get("status") == "published"]


def check_manifest_reuse(
    manifest: dict[str, Any],
    asset_root: Path,
    registry: dict[str, Any],
    similarity_distance: int = DEFAULT_SIMILARITY_DISTANCE,
) -> list[dict[str, Any]]:
    """Fail on missing/unregistered/reused assets; return approved similarity-review notes."""
    references = page_asset_references(manifest)
    if not references:
        return []
    edition_id = manifest.get("edition_id")
    if not edition_id:
        raise ValueError("Manifest edition_id is required for asset reuse checks")

    ids = [reference.get("asset_id") for reference in references]
    if any(not asset_id for asset_id in ids):
        raise ValueError("Every illustration component must declare a stable asset_id")
    duplicates = sorted({asset_id for asset_id in ids if ids.count(asset_id) > 1})
    if duplicates:
        raise ValueError(f"An asset may appear only once per edition unless explicitly redesigned: {', '.join(duplicates)}")

    if not manifest.get("asset_registry"):
        raise ValueError("Production manifest must declare asset_registry")

    registry_assets = registry["assets"]
    if edition_id in registry.get("published_editions", {}):
        raise ValueError(f"Edition {edition_id} is already recorded as published; create a new edition ID")

    review_records = {
        (item.get("asset_id"), item.get("similar_to_asset_id")): item
        for item in manifest.get("similarity_reviews", [])
        if item.get("decision") == "ACCEPT_DISTINCT"
        and item.get("reviewer")
        and item.get("rationale")
        and item.get("reviewed_at_utc")
    }
    similarity_findings: list[dict[str, Any]] = []
    candidates: list[tuple[str, str, str, str]] = []

    for reference in references:
        asset_id = reference["asset_id"]
        record = registry_assets.get(asset_id)
        if record is None:
            raise ValueError(f"Asset {asset_id} is not registered")
        if record.get("status") not in {"approved", "published"}:
            raise ValueError(f"Asset {asset_id} is not approved in the asset registry")
        if record.get("category") not in registry.get("categories", []):
            raise ValueError(f"Asset {asset_id} has an unrecognized category")
        if not record.get("svg_sha256") or not record.get("normalized_svg_sha256"):
            raise ValueError(f"Asset {asset_id} is missing SVG integrity hashes")
        svg_master_path_value = record.get("svg_master_path")
        if svg_master_path_value:
            svg_master_path = Path(svg_master_path_value)
            if not svg_master_path.is_absolute():
                svg_master_path = Path(__file__).resolve().parents[1] / svg_master_path
            svg_master_path = svg_master_path.resolve(strict=True)
            if sha256_file(svg_master_path) != record["svg_sha256"]:
                raise ValueError(f"Asset {asset_id} SVG master changed since registration; create a new asset version")
            if normalized_svg_sha256(svg_master_path) != record["normalized_svg_sha256"]:
                raise ValueError(f"Asset {asset_id} normalized SVG content changed since registration")
        elif not record.get("svg_master_uri"):
            raise ValueError(f"Asset {asset_id} needs a local svg_master_path or a versioned GCS SVG URI")

        local_preview = (asset_root / reference["asset"]).resolve(strict=True)
        try:
            local_preview.relative_to(asset_root.resolve())
        except ValueError as error:
            raise ValueError(f"Asset {asset_id} preview path escapes asset_root") from error
        preview_sha256 = sha256_file(local_preview)
        expected_sha256 = record.get("preview_sha256")
        if preview_sha256 != expected_sha256:
            raise ValueError(f"Asset {asset_id} preview hash does not match the approved registry record")
        fingerprint = visual_fingerprint(local_preview)
        if fingerprint != record.get("visual_fingerprint"):
            raise ValueError(f"Asset {asset_id} visual fingerprint does not match the approved registry record")
        candidates.append((asset_id, record["svg_sha256"], preview_sha256, fingerprint))

    for asset_id, svg_hash, preview_sha256, fingerprint in candidates:
        for published_id, record in registry_assets.items():
            if published_id == asset_id or not _published_usages(record):
                continue
            if svg_hash == record.get("svg_sha256") or preview_sha256 == record.get("preview_sha256"):
                raise ValueError(f"Asset {asset_id} exactly reuses the published artwork of {published_id}")
            distance = fingerprint_distance(fingerprint, record.get("visual_fingerprint", "0000000000000000"))
            if distance <= similarity_distance:
                registered_review = record.get("similarity_review") or {}
                finding = {
                    "asset_id": asset_id,
                    "similar_to_asset_id": published_id,
                    "fingerprint_distance": distance,
                    "published_editions": [usage.get("edition_id") for usage in _published_usages(record)],
                }
                manifest_review = review_records.get((asset_id, published_id))
                registered_review_applies = published_id in record.get("similar_to_asset_ids", [])
                review = manifest_review or (registered_review if registered_review_applies else {})
                if not (
                    review.get("decision") == "ACCEPT_DISTINCT"
                    and review.get("reviewer")
                    and review.get("rationale")
                    and review.get("reviewed_at_utc")
                ):
                    raise ValueError(
                        f"Asset {asset_id} is visually similar to published asset {published_id} "
                        f"(distance {distance}); add a documented ACCEPT_DISTINCT human review"
                    )
                finding["review"] = review
                similarity_findings.append(finding)

    return similarity_findings


def empty_registry() -> dict[str, Any]:
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "categories": ["animals", "flowers", "trees", "cartoons", "solar-system", "vehicles", "other"],
        "reuse_policy": {
            "exact_published_duplicate": "block",
            "similarity_metric": "64-bit dHash over approved QA preview",
            "similarity_hamming_threshold": DEFAULT_SIMILARITY_DISTANCE,
            "similarity_action": "require documented human ACCEPT_DISTINCT review",
        },
        "assets": {},
        "published_editions": {},
    }


def register_asset_record(
    registry: dict[str, Any],
    asset_id: str,
    category: str,
    subject_id: str,
    svg_path: Path,
    preview_path: Path,
    svg_master_uri: str | None = None,
    preview_uri: str | None = None,
    parent_asset_id: str | None = None,
    change_note: str | None = None,
    similarity_review: dict[str, str] | None = None,
) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{2,95}", asset_id):
        raise ValueError("asset_id must be a stable lowercase slug (3-96 characters)")
    if category not in registry.get("categories", []):
        raise ValueError(f"Unknown asset category: {category}")
    for label, uri, folder in (
        ("svg_master_uri", svg_master_uri, "assets/svg"),
        ("preview_uri", preview_uri, "assets/previews"),
    ):
        if uri and (not uri.startswith("gs://") or f"/{folder}/{category}/{asset_id}/" not in uri.replace("\\", "/")):
            raise ValueError(f"{label} must be versioned under gs://<bucket>/{folder}/{category}/{asset_id}/")
    if asset_id in registry["assets"]:
        raise ValueError(f"Asset ID already exists: {asset_id}; revisions require a new asset_id")
    if parent_asset_id:
        if parent_asset_id not in registry["assets"]:
            raise ValueError(f"Unknown parent_asset_id: {parent_asset_id}")
        if not change_note or len(change_note.strip()) < 20:
            raise ValueError("A derivative requires a specific change_note of at least 20 characters")

    svg_path = svg_path.resolve(strict=True)
    preview_path = preview_path.resolve(strict=True)
    if svg_path.suffix.lower() != ".svg":
        raise ValueError("Editable source master must be an SVG file")
    validate_svg_master(svg_path)
    validate_preview(preview_path)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        svg_master_path = svg_path.relative_to(repo_root).as_posix()
    except ValueError:
        svg_master_path = str(svg_path)
    try:
        preview_path_value = preview_path.relative_to(repo_root).as_posix()
    except ValueError:
        preview_path_value = str(preview_path)

    svg_hash = sha256_file(svg_path)
    normalized_hash = normalized_svg_sha256(svg_path)
    preview_hash = sha256_file(preview_path)
    fingerprint = visual_fingerprint(preview_path)
    similar_published: list[tuple[str, int]] = []
    for existing_id, existing in registry["assets"].items():
        if existing.get("svg_sha256") == svg_hash or existing.get("normalized_svg_sha256") == normalized_hash:
            raise ValueError(f"SVG master exactly duplicates registered asset {existing_id}")
        if existing.get("preview_sha256") == preview_hash:
            raise ValueError(f"QA preview exactly duplicates registered asset {existing_id}")
        if _published_usages(existing):
            distance = fingerprint_distance(fingerprint, existing.get("visual_fingerprint", "0000000000000000"))
            if distance <= int(registry.get("reuse_policy", {}).get("similarity_hamming_threshold", DEFAULT_SIMILARITY_DISTANCE)):
                similar_published.append((existing_id, distance))
    if similar_published and not (
        similarity_review
        and similarity_review.get("decision") == "ACCEPT_DISTINCT"
        and similarity_review.get("reviewer")
        and len(similarity_review.get("rationale", "").strip()) >= 20
        and similarity_review.get("reviewed_at_utc")
    ):
        matches = ", ".join(f"{existing_id} (distance {distance})" for existing_id, distance in similar_published)
        raise ValueError(f"Preview is similar to published art: {matches}; provide a documented human similarity review")

    record = {
        "asset_id": asset_id,
        "category": category,
        "subject_id": subject_id,
        "status": "pending_review",
        "master_format": "svg",
        "svg_master_path": svg_master_path,
        "svg_master_uri": svg_master_uri,
        "svg_sha256": svg_hash,
        "normalized_svg_sha256": normalized_hash,
        "preview_path": preview_path_value,
        "preview_uri": preview_uri,
        "preview_sha256": preview_hash,
        "visual_fingerprint": fingerprint,
        "fingerprint_algorithm": "dhash-64-v1",
        "parent_asset_id": parent_asset_id,
        "change_note": change_note,
        "similarity_review": similarity_review,
        "similar_to_asset_ids": [existing_id for existing_id, _ in similar_published],
        "qa": {"status": "PENDING_QA", "reviewer": None, "reviewed_at_utc": None},
        "edition_history": [],
    }
    registry["assets"][asset_id] = record
    return record


def approve_asset_record(
    registry: dict[str, Any], asset_id: str, reviewer: str, reviewed_at_utc: str
) -> None:
    if asset_id not in registry["assets"]:
        raise ValueError(f"Unknown asset_id: {asset_id}")
    if not reviewer.strip() or not reviewed_at_utc.strip():
        raise ValueError("reviewer and reviewed_at_utc are required")
    record = registry["assets"][asset_id]
    record["status"] = "approved"
    record["qa"] = {"status": "PASS", "reviewer": reviewer, "reviewed_at_utc": reviewed_at_utc}


def record_published_edition(
    registry: dict[str, Any], edition_id: str, book_id: str, published_at: str, asset_ids: list[str]
) -> None:
    if edition_id in registry["published_editions"]:
        raise ValueError(f"Edition already recorded as published: {edition_id}")
    if not asset_ids or len(asset_ids) != len(set(asset_ids)):
        raise ValueError("Publication requires a non-empty unique asset_ids list")
    for asset_id in asset_ids:
        if asset_id not in registry["assets"]:
            raise ValueError(f"Cannot publish unregistered asset: {asset_id}")
        if registry["assets"][asset_id].get("status") not in {"approved", "published"}:
            raise ValueError(f"Cannot publish unapproved asset: {asset_id}")

    registry["published_editions"][edition_id] = {
        "book_id": book_id,
        "published_at": published_at,
        "asset_ids": asset_ids,
        "status": "published",
    }
    for asset_id in asset_ids:
        record = registry["assets"][asset_id]
        record["status"] = "published"
        record["edition_history"].append(
            {"edition_id": edition_id, "book_id": book_id, "published_at": published_at, "status": "published"}
        )
