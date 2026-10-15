"""
scripts/backup_vault.py
=======================
Asset Vault & Non-Idempotency Backup Protection System
for "The Pivot Kids: Copy to Color" (12 Volumes)

Guarantees:
1. Non-Idempotency Protection: Preserves approved AI generations, logos, and print artifacts.
2. Cryptographic Integrity: Computes and verifies SHA-256 checksums for all gold-master assets.
3. Automated Snapshots: Archives assets, manifests, catalogs, and builds to backups/vault_snapshot_<timestamp>.
4. Disaster Recovery: Instant verification and restoration against corruption or accidental overwriting.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKUPS_DIR = REPO_ROOT / "backups"
CATALOGS_DIR = REPO_ROOT / "catalogs"
VAULT_MANIFEST = CATALOGS_DIR / "asset_vault_manifest.json"

VAULT_TARGET_DIRS = [
    "assets/brand",
    "assets/logos",
    "assets/cover_heroes",
    "assets/series_ai",
    "assets/cover",
    "assets/fonts",
    "manifests",
    "catalogs",
    "local_builds/animals/v1.0-core",
]


def compute_sha256(file_path: Path) -> str:
    """Computes SHA-256 checksum of a file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def create_vault_snapshot(label: str | None = None) -> Path:
    """
    Creates an immutable, timestamped archive of all gold-master assets, logos,
    manifests, and production builds to protect against non-idempotent AI overwrites.
    """
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    CATALOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    archive_name = f"vault_snapshot_{timestamp}"
    if label:
        archive_name += f"_{label}"
    zip_path = BACKUPS_DIR / f"{archive_name}.zip"

    manifest_records = {}
    print("=" * 80)
    print(f"CREATING ASSET VAULT SNAPSHOT: {zip_path.name}")
    print("=" * 80)

    total_files = 0
    total_bytes = 0

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel_dir in VAULT_TARGET_DIRS:
            target_path = REPO_ROOT / rel_dir
            if not target_path.exists():
                continue

            for root, _, files in os.walk(target_path):
                for f in sorted(files):
                    fp = Path(root) / f
                    rel_p = fp.relative_to(REPO_ROOT).as_posix()
                    # Skip temporary, cache, or self-manifest files
                    if "__pycache__" in rel_p or rel_p.endswith((".pyc", ".tmp", ".log")) or rel_p == "catalogs/asset_vault_manifest.json":
                        continue

                    sha256 = compute_sha256(fp)
                    size = fp.stat().st_size
                    zf.write(fp, arcname=rel_p)

                    manifest_records[rel_p] = {
                        "size": size,
                        "sha256": sha256,
                        "mtime": fp.stat().st_mtime,
                    }
                    total_files += 1
                    total_bytes += size

    # Save manifest record
    vault_summary = {
        "snapshot_id": archive_name,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_files": total_files,
        "total_bytes": total_bytes,
        "archive_path": str(zip_path.relative_to(REPO_ROOT)),
        "files": manifest_records,
    }

    with open(VAULT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(vault_summary, f, indent=2)

    mb = total_bytes / (1024 * 1024)
    zip_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Vault snapshot completed successfully!")
    print(f"     Total Files:  {total_files}")
    print(f"     Uncompressed: {mb:.2f} MB")
    print(f"     Compressed:   {zip_mb:.2f} MB")
    print(f"     Archive:      {zip_path}")
    print(f"     Manifest:     {VAULT_MANIFEST}")
    return zip_path


def verify_vault_integrity() -> bool:
    """
    Audits current workspace assets against the gold-master vault manifest
    to detect any missing, modified, or corrupted assets.
    """
    if not VAULT_MANIFEST.exists():
        print(f"[ERROR] No vault manifest found at {VAULT_MANIFEST}. Run create-snapshot first.")
        return False

    with open(VAULT_MANIFEST, "r", encoding="utf-8") as f:
        vault = json.load(f)

    print("=" * 80)
    print(f"VERIFYING ASSET VAULT INTEGRITY against snapshot '{vault['snapshot_id']}'")
    print("=" * 80)

    mismatches = []
    missing = []
    verified = 0

    for rel_path, meta in vault["files"].items():
        fp = REPO_ROOT / rel_path
        if not fp.exists():
            missing.append(rel_path)
            continue

        curr_sha256 = compute_sha256(fp)
        if curr_sha256 != meta["sha256"]:
            mismatches.append((rel_path, meta["sha256"], curr_sha256))
        else:
            verified += 1

    print(f"[AUDIT] Verified: {verified}/{len(vault['files'])} files intact.")
    if missing:
        print(f"[FAIL] Missing {len(missing)} gold-master files:")
        for m in missing[:10]:
            print(f"       - {m}")
    if mismatches:
        print(f"[FAIL] Checksum mismatch in {len(mismatches)} files (modified or non-idempotent overwrite):")
        for p, exp, act in mismatches[:10]:
            print(f"       - {p} (expected {exp[:8]}, got {act[:8]})")

    if not missing and not mismatches:
        print("\n[PASS] 100% VAULT INTEGRITY VERIFIED: All gold-master assets are pristine.")
        return True
    return False


def restore_vault_snapshot(snapshot_zip: str | Path | None = None) -> None:
    """Restores files from a vault snapshot archive."""
    if snapshot_zip is None:
        if not VAULT_MANIFEST.exists():
            print("[ERROR] No vault manifest found to identify latest snapshot.")
            sys.exit(1)
        with open(VAULT_MANIFEST, "r", encoding="utf-8") as f:
            vault = json.load(f)
        snapshot_zip = REPO_ROOT / vault["archive_path"]

    zip_p = Path(snapshot_zip)
    if not zip_p.exists():
        print(f"[ERROR] Snapshot archive not found at {zip_p}")
        sys.exit(1)

    print(f"[RESTORE] Restoring all assets from {zip_p.name}...")
    with zipfile.ZipFile(zip_p, "r") as zf:
        zf.extractall(REPO_ROOT)
    print("[OK] Restore completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="Asset Vault & Non-Idempotency Backup System")
    subparsers = parser.add_subparsers(dest="command")

    # snapshot
    p_snap = subparsers.add_parser("create-snapshot", help="Create a timestamped backup snapshot of all master assets")
    p_snap.add_argument("--label", default=None, help="Optional label to append to archive name")

    # verify
    subparsers.add_parser("verify", help="Verify current workspace files against gold-master vault checksums")

    # restore
    p_res = subparsers.add_parser("restore", help="Restore assets from a vault snapshot archive")
    p_res.add_argument("--archive", default=None, help="Archive path (default: latest recorded snapshot)")

    args = parser.parse_args()

    if args.command == "create-snapshot":
        create_vault_snapshot(args.label)
    elif args.command == "verify":
        ok = verify_vault_integrity()
        sys.exit(0 if ok else 1)
    elif args.command == "restore":
        restore_vault_snapshot(args.archive)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

