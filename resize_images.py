#!/usr/bin/env python3
"""
Resize fullsize images to 720x720 for the Waveshare P4 display.

Scans all model directories and Other/ under images/ for fullsize/ originals,
then creates 720x720/ versions using high-quality LANCZOS downscaling.
Skips any image smaller than 720px on either dimension.
"""

import os
import sys
from pathlib import Path
from PIL import Image

TARGET_SIZE = (720, 720)
IMAGES_DIR = Path(__file__).parent / "images"


def resize_directory(fullsize_dir: Path, output_dir: Path) -> tuple[int, int]:
    """Resize all PNGs in fullsize_dir to TARGET_SIZE, saving to output_dir.

    Returns (processed_count, skipped_count).
    """
    processed = 0
    skipped = 0

    for img_path in sorted(fullsize_dir.glob("*.png")):
        with Image.open(img_path) as img:
            w, h = img.size

            if w < TARGET_SIZE[0] or h < TARGET_SIZE[1]:
                print(f"  SKIP {img_path.name} ({w}x{h} — too small, would require upscaling)")
                skipped += 1
                continue

            output_dir.mkdir(parents=True, exist_ok=True)
            resized = img.resize(TARGET_SIZE, Image.LANCZOS)
            out_path = output_dir / img_path.name
            resized.save(out_path, "PNG", optimize=True)
            print(f"  {img_path.name} ({w}x{h} -> {TARGET_SIZE[0]}x{TARGET_SIZE[1]})")
            processed += 1

    return processed, skipped


def main():
    if not IMAGES_DIR.is_dir():
        print(f"Error: images directory not found at {IMAGES_DIR}")
        sys.exit(1)

    total_processed = 0
    total_skipped = 0

    # Process all subdirectories that have a fullsize/ folder
    for model_dir in sorted(IMAGES_DIR.iterdir()):
        if not model_dir.is_dir():
            continue

        fullsize_dir = model_dir / "fullsize"
        if not fullsize_dir.is_dir():
            continue

        pngs = list(fullsize_dir.glob("*.png"))
        if not pngs:
            continue

        output_dir = model_dir / f"{TARGET_SIZE[0]}x{TARGET_SIZE[1]}"

        print(f"\n{model_dir.name}/ ({len(pngs)} images)")
        processed, skipped = resize_directory(fullsize_dir, output_dir)
        total_processed += processed
        total_skipped += skipped

    print(f"\nDone: {total_processed} images resized, {total_skipped} skipped")


if __name__ == "__main__":
    main()
