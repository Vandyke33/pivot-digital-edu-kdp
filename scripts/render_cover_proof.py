"""
Render a 300 DPI PNG Proof from a KDP Cover Spread PDF using PyMuPDF.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pymupdf


def render_pdf_to_image(
    pdf_path: str | Path,
    output_png: str | Path,
    dpi: int = 300,
) -> Path:
    pdf_p = Path(pdf_path)
    out_p = Path(output_png)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    if not pdf_p.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_p}")

    doc = pymupdf.open(pdf_p)
    if len(doc) == 0:
        raise ValueError(f"PDF has no pages: {pdf_p}")

    page = doc.load_page(0)
    # PyMuPDF uses 72 DPI base matrix
    zoom = dpi / 72.0
    matrix = pymupdf.Matrix(zoom, zoom)

    pix = page.get_pixmap(matrix=matrix, alpha=False)
    pix.save(str(out_p))
    doc.close()

    print(f"[OK] Rendered {dpi} DPI proof: {out_p} ({pix.width}x{pix.height} px)")
    return out_p


def main():
    parser = argparse.ArgumentParser(description="Render PDF Cover Spread to 300 DPI PNG Proof")
    parser.add_argument("--pdf", type=Path, required=True, help="Input PDF path")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI (default 300)")
    args = parser.parse_args()

    render_pdf_to_image(args.pdf, args.output, dpi=args.dpi)


if __name__ == "__main__":
    main()
