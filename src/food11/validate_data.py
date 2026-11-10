from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, UnidentifiedImageError

try:
    from src.food11.data import CLASSES
except ModuleNotFoundError:
    # Support running this file directly as a script.
    from data import CLASSES


SPLITS = ("training", "validation", "evaluation")


def validate_dataset(root: Path, min_per_class: int, tau: float) -> bool:
    results = {}
    counts = {}
    hashes = {}

    # Check 1: Exact class folders in each split
    folder_errors = []

    for split in SPLITS:
        split_dir = root / split
        actual = (
            {p.name for p in split_dir.iterdir() if p.is_dir()}
            if split_dir.is_dir()
            else set()
        )

        if actual != set(CLASSES):
            missing = set(CLASSES) - actual
            extra = actual - set(CLASSES)
            folder_errors.append(
                f"{split}: missing={sorted(missing)}, extra={sorted(extra)}"
            )

    results["Class folders"] = len(folder_errors) == 0

    # Checks 2, 3, and 4: images, counts, and hashes
    image_errors = []
    count_errors = []
    duplicate_errors = []
    seen_hashes = {}

    for split in SPLITS:
        counts[split] = Counter()
        hashes[split] = set()

        for category in CLASSES:
            folder = root / split / category

            if not folder.is_dir():
                count_errors.append(f"{split}/{category}: folder missing")
                continue

            images = sorted(
                p for p in folder.iterdir()
                if p.is_file() and p.suffix.lower() in (".jpg", ".jpeg", ".png")
            )

            counts[split][category] = len(images)

            if len(images) < min_per_class:
                count_errors.append(
                    f"{split}/{category}: {len(images)} < {min_per_class}"
                )

            for path in images:
                try:
                    with Image.open(path) as img:
                        img.load()
                        if img.mode != "RGB" or img.size != (128, 128):
                            image_errors.append(
                                f"{path}: mode={img.mode}, size={img.size}"
                            )
                except (OSError, UnidentifiedImageError) as exc:
                    image_errors.append(f"{path}: {exc}")

                digest = hashlib.md5(path.read_bytes()).hexdigest()

                if digest in seen_hashes:
                    previous_split, previous_path = seen_hashes[digest]
                    if previous_split != split:
                        duplicate_errors.append(
                            f"{previous_path} <-> {path}"
                        )
                else:
                    seen_hashes[digest] = (split, path)

                hashes[split].add(digest)

    results["Image integrity (RGB, 128x128)"] = not image_errors
    results["Minimum images per class"] = not count_errors
    results["No cross-split duplicates"] = not duplicate_errors

    # Check 5: Training/validation class distribution
    train_total = sum(counts["training"].values())
    val_total = sum(counts["validation"].values())
    distribution_errors = []

    if train_total == 0 or val_total == 0:
        distribution_errors.append("Training or validation split is empty")
    else:
        for category in CLASSES:
            train_share = counts["training"][category] / train_total
            val_share = counts["validation"][category] / val_total

            if abs(train_share - val_share) > tau:
                distribution_errors.append(
                    f"{category}: train={train_share:.4f}, "
                    f"validation={val_share:.4f}"
                )

    results["Class distribution"] = not distribution_errors

    # Print report
    print(f"\nDataset: {root}")
    print(f"Minimum per class: {min_per_class}")
    print(f"Distribution tolerance: {tau}\n")

    details = {
        "Class folders": folder_errors,
        "Image integrity (RGB, 128x128)": image_errors,
        "Minimum images per class": count_errors,
        "No cross-split duplicates": duplicate_errors,
        "Class distribution": distribution_errors,
    }

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}")

        if not passed:
            for error in details[name][:5]:
                print(f"       {error}")
            if len(details[name]) > 5:
                print(f"       ... and {len(details[name]) - 5} more")

    success = all(results.values())
    print("\nRESULT:", "PASS" if success else "FAIL")
    return success


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--min-per-class", type=int, default=50)
    parser.add_argument("--tau", type=float, default=0.05)

    args = parser.parse_args()

    if args.min_per_class < 0 or args.tau < 0:
        parser.error("Minimum count and tolerance must be non-negative")

    success = validate_dataset(
        args.dataset, args.min_per_class, args.tau
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
