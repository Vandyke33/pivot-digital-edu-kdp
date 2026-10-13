"""Unified KDP Publishing Operations Runner Suite."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
_VENV_PYTHON = REPO_ROOT / ".venv" / "Scripts" / "python.exe" if os.name == "nt" else REPO_ROOT / ".venv" / "bin" / "python"
PYTHON = str(_VENV_PYTHON) if _VENV_PYTHON.exists() else sys.executable


def run_cmd(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print(f"\n[EXEC] {' '.join(str(a) for a in args)}")
    result = subprocess.run(args, cwd=str(REPO_ROOT), text=True)
    if check and result.returncode != 0:
        print(f"\n[ERROR] Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    return result


def get_status() -> None:
    print("=" * 60)
    print("  THE PIVOT DIGITAL PUBLICATION - KDP PIPELINE STATUS")
    print("=" * 60)

    # 1. Catalog
    cat_path = REPO_ROOT / "catalogs" / "catalog_master.json"
    if cat_path.exists():
        cat = json.loads(cat_path.read_text(encoding="utf-8"))
        editions = cat.get("editions", [])
        print(f"\n[OK] Catalog Master: {cat.get('publisher_imprint')}")
        print(f"  Editions tracked: {len(editions)}")
        for ed in editions:
            print(f"    - {ed.get('book_id')}: {ed.get('title')} ({ed.get('edition_id')})")
    else:
        print("\n[--] Catalog Master: missing")

    # 2. Asset Registry
    reg_path = REPO_ROOT / "catalogs" / "asset_registry.json"
    if reg_path.exists():
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        assets = reg.get("assets", {})
        approved = sum(1 for a in assets.values() if a.get("status") == "approved")
        print(f"\n[OK] Asset Registry: {len(assets)} assets registered ({approved} approved)")
        for aid, a in assets.items():
            print(f"    - {aid} [{a.get('category')}]: {a.get('status')} (qa: {a.get('qa', {}).get('status')})")
    else:
        print("\n[--] Asset Registry: missing")

    # 3. Solar System Explorers Generation Batch
    batch_manifest = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "generation-manifest.json"
    if batch_manifest.exists():
        bm = json.loads(batch_manifest.read_text(encoding="utf-8"))
        bm_assets = bm.get("assets", [])
        gen_count = sum(1 for a in bm_assets if a.get("generation_status") == "GENERATED_LOCAL")
        pass_count = sum(1 for a in bm_assets if a.get("review_status") == "PASS")
        print(f"\n[OK] Generation Manifest: {bm.get('series_id')} ({bm.get('edition_id')})")
        print(f"  Total Subjects: {len(bm_assets)}")
        print(f"  Generated Local: {gen_count} / {len(bm_assets)}")
        print(f"  QA Approved: {pass_count} / {len(bm_assets)}")
    else:
        print("\n[--] Generation Manifest: not prepared yet")

    # 4. Compiled Proofs
    interior_pdf = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "interior.pdf"
    cover_pdf = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "cover-proof.pdf"
    print("\n[OK] Compiled Artifacts:")
    print(f"  Interior PDF: {'EXISTS (' + str(round(interior_pdf.stat().st_size / 1024, 1)) + ' KB)' if interior_pdf.exists() else 'NOT BUILT'}")
    print(f"  Cover PDF:    {'EXISTS (' + str(round(cover_pdf.stat().st_size / 1024, 1)) + ' KB)' if cover_pdf.exists() else 'NOT BUILT'}")
    print("=" * 60 + "\n")


def cmd_render(args: argparse.Namespace) -> None:
    out_dir = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "prompts.jsonl"
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "render_prompts.py"),
        "--series", args.series,
        "--edition", args.edition,
        "--output", str(out_file),
    ])
    print(f"\n[OK] Prompts rendered to {out_file}")


def cmd_prepare(args: argparse.Namespace) -> None:
    prompts_file = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "prompts.jsonl"
    if not prompts_file.exists():
        cmd_render(args)

    out_manifest = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "generation-manifest.json"
    raw_dir = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "raw"
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "prepare_generation_batch.py"),
        "--prompts", str(prompts_file),
        "--provider", "google-gemini-agent-platform",
        "--model", args.model,
        "--model-version", args.model,
        "--edition-id", args.edition_id,
        "--asset-dir", str(raw_dir),
        "--output", str(out_manifest),
    ])
    print(f"\n[OK] Generation batch manifest prepared at {out_manifest}")


def cmd_generate(args: argparse.Namespace) -> None:
    batch_manifest = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "generation-manifest.json"
    if not batch_manifest.exists():
        cmd_prepare(args)

    candidate_dir = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "pilot-candidates"
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "generate_images_google.py"),
        "--batch", str(batch_manifest),
        "--output-manifest", str(batch_manifest),
        "--candidate-dir", str(candidate_dir),
        "--model", args.model,
        "--location", args.location,
        "--max-assets", str(args.max_assets),
        "--local-only",
    ])
    print(f"\n[OK] Generation completed for {args.max_assets} asset(s).")


def cmd_vectorize(args: argparse.Namespace) -> None:
    batch_manifest = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "generation-manifest.json"
    approved_dir = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "approved-line-art"
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "vectorize_asset.py"),
        "--batch-manifest", str(batch_manifest),
        "--category", "solar-system",
        "--register",
        "--copy-to", str(approved_dir / "placeholder.png"),
    ])
    print("\n[OK] Vectorization & 300-DPI auto-framing completed.")


def cmd_build_interior(args: argparse.Namespace) -> None:
    manifest = REPO_ROOT / "manifests" / "solar-system-explorers-v1.0-core.json"
    out_pdf = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "interior.pdf"
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "compile_interior.py"),
        "--manifest", str(manifest),
        "--output", str(out_pdf),
        "--trim", "8.5x11",
        "--bleed", "all",
        "--reverse-page", "black",
    ])
    print(f"\n[OK] Interior PDF compiled: {out_pdf}")


def cmd_build_cover(args: argparse.Namespace) -> None:
    out_pdf = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "cover-proof.pdf"
    cover_art = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "cover-art.png"
    front_art = cover_art if cover_art.exists() else None

    # Thumbnail previews for back cover "LOOK INSIDE" gallery
    thumb_sun = REPO_ROOT / "local_builds" / "solar-system-explorers" / "v1.0-core" / "approved-line-art" / "sun.png"
    thumbnails = [thumb_sun] if thumb_sun.exists() else []

    # High-resolution native logo
    logo_png = REPO_ROOT / "assets" / "logos" / "pivot_kids.png"
    logo_file = logo_png if logo_png.exists() else (REPO_ROOT / "assets" / "logo" / "pivot_kids.svg")

    cover_cmd = [
        PYTHON,
        str(REPO_ROOT / "scripts" / "compile_cover.py"),
        "--output", str(out_pdf),
        "--title", "SOLAR SYSTEM EXPLORERS",
        "--subtitle", "Coloring Book for Kids Ages 4-6",
        "--publisher", "The Pivot Digital Publication",
        "--logo", str(logo_file),
        "--page-count", "32",
    ]
    if front_art:
        cover_cmd.extend(["--front-art", str(front_art)])
    if thumbnails:
        cover_cmd.extend(["--thumbnails"] + [str(t) for t in thumbnails])
    if getattr(args, "author", None):
        cover_cmd.extend(["--author", args.author])
    run_cmd(cover_cmd)
    print(f"\n[OK] Full-Wrap Cover PDF compiled: {out_pdf}")


def cmd_build_animals_cover(args: argparse.Namespace) -> None:
    out_pdf = getattr(args, "output", None) or (REPO_ROOT / "local_builds" / "animals" / "v1.0-core" / "animals-cover-spread.pdf")
    page_count = getattr(args, "page_count", 32)
    run_cmd([
        PYTHON,
        str(REPO_ROOT / "scripts" / "compile_animals_cover.py"),
        "--output", str(out_pdf),
        "--page-count", str(page_count),
    ])
    print(f"\n[OK] Animals Cover Spread compiled: {out_pdf}")


def main() -> int:
    parser = argparse.ArgumentParser(description="KDP Publishing Operations Runner Suite")
    subparsers = parser.add_subparsers(dest="command")

    # status
    subparsers.add_parser("status", help="Print overall pipeline and asset status")

    # render
    p_render = subparsers.add_parser("render", help="Render prompt registry to local prompts.jsonl")
    p_render.add_argument("--series", default="solar_system_explorers")
    p_render.add_argument("--edition", default="core_coloring")

    # prepare
    p_prep = subparsers.add_parser("prepare", help="Prepare batch generation manifest")
    p_prep.add_argument("--series", default="solar_system_explorers")
    p_prep.add_argument("--edition", default="core_coloring")
    p_prep.add_argument("--edition-id", default="v1.0-core")
    p_prep.add_argument("--model", default="gemini-3.1-flash-lite-image")

    # generate
    p_gen = subparsers.add_parser("generate", help="Generate artwork via Google Gemini")
    p_gen.add_argument("--max-assets", type=int, default=1, help="Number of images to generate (1-4)")
    p_gen.add_argument("--model", default="gemini-3.1-flash-lite-image")
    p_gen.add_argument("--location", default="global")
    p_gen.add_argument("--series", default="solar_system_explorers")
    p_gen.add_argument("--edition", default="core_coloring")
    p_gen.add_argument("--edition-id", default="v1.0-core")

    # vectorize
    subparsers.add_parser("vectorize", help="Vectorize, auto-frame, and render 300-DPI previews")

    # build-interior
    subparsers.add_parser("build-interior", help="Compile 32-page interior PDF")

    # build-cover
    p_cover = subparsers.add_parser("build-cover", help="Compile KDP full-wrap paperback cover PDF")
    p_cover.add_argument("--author", default=None, help="Author name to display on cover")

    # build-animals-cover
    p_animals = subparsers.add_parser("build-animals-cover", help="Compile 'My First Copy to Colour: Animals' full-wrap cover spread")
    p_animals.add_argument("--output", type=Path, default=None, help="Destination PDF path")
    p_animals.add_argument("--page-count", type=int, default=32, help="Book page count for spine calculation")

    # build-all
    p_all = subparsers.add_parser("build-all", help="Compile both interior and cover PDFs")
    p_all.add_argument("--author", default=None, help="Author name to display on cover")

    # test
    subparsers.add_parser("test", help="Run full pipeline test suite")

    args = parser.parse_args()

    if not args.command or args.command == "status":
        get_status()
        return 0
    elif args.command == "render":
        cmd_render(args)
    elif args.command == "prepare":
        cmd_prepare(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "vectorize":
        cmd_vectorize(args)
    elif args.command == "build-interior":
        cmd_build_interior(args)
    elif args.command == "build-cover":
        cmd_build_cover(args)
    elif args.command == "build-animals-cover":
        cmd_build_animals_cover(args)
    elif args.command == "build-all":
        cmd_build_cover(args)
        cmd_build_interior(args)
    elif args.command == "test":
        run_cmd([PYTHON, "-m", "unittest", "discover", "-s", "tests", "-v"])

    return 0


if __name__ == "__main__":
    sys.exit(main())
