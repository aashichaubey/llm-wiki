"""
Step 1: Convert a PDF into one image per page.
Usage: python convert_pdf.py <path_to_pdf>
"""

import sys
import os
from pathlib import Path
from pdf2image import convert_from_path

def convert_pdf_to_images(pdf_path: str) -> list[Path]:
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found")
        sys.exit(1)

    # output folder named after the PDF
    output_dir = Path("temp_images") / pdf_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Converting {pdf_path.name} to images...")
    pages = convert_from_path(pdf_path, dpi=200)

    image_paths = []
    for i, page in enumerate(pages):
        image_path = output_dir / f"page_{i+1:03d}.png"
        page.save(image_path, "PNG")
        image_paths.append(image_path)
        print(f"  ✓ Page {i+1}/{len(pages)}")

    print(f"Done. {len(pages)} pages saved to {output_dir}\n")
    return image_paths

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_pdf.py <path_to_pdf>")
        sys.exit(1)
    convert_pdf_to_images(sys.argv[1])
