from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, UnidentifiedImageError


IMAGE_SIZE = (128, 128)
MINI_LIMIT_PER_SPLIT_CLASS = 100
SPLITS = ("training", "evaluation", "validation")
CLASS_NAMES = {
    "0": "Bread",
    "1": "Dairy product",
    "2": "Dessert",
    "3": "Egg",
    "4": "Fried food",
    "5": "Meat",
    "6": "Noodles-Pasta",
    "7": "Rice",
    "8": "Seafood",
    "9": "Soup",
    "10": "Vegetable-Fruit",
}


@dataclass(frozen=True)
class ProcessingStats:
    processed_files: int
    mini_files: int
    failed_files: tuple[Path, ...]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def find_raw_data_dir(data_dir: Path) -> Path:
    preferred = data_dir / "food11_raw"
    if has_expected_splits(preferred):
        return preferred

    local_download_name = data_dir / "food11 dataset"
    if has_expected_splits(local_download_name):
        return local_download_name

    raise FileNotFoundError(
        "Could not find Food-11 raw data. Expected data/food11_raw with "
        "training, evaluation, and validation folders."
    )


def has_expected_splits(path: Path) -> bool:
    return path.is_dir() and all((path / split).is_dir() for split in SPLITS)


def class_id_for(image_path: Path) -> str:
    return image_path.stem.split("_", maxsplit=1)[0]


def collect_images(raw_dir: Path) -> dict[str, dict[str, list[Path]]]:
    images: dict[str, dict[str, list[Path]]] = {
        split: {class_id: [] for class_id in CLASS_NAMES} for split in SPLITS
    }

    for split in SPLITS:
        split_dir = raw_dir / split
        for image_path in sorted(split_dir.glob("*.jpg")):
            class_id = class_id_for(image_path)
            if class_id in CLASS_NAMES:
                images[split][class_id].append(image_path)

    return images


def reset_output_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def resize_image(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        resized = image.convert("RGB").resize(IMAGE_SIZE, Image.Resampling.LANCZOS)
        resized.save(destination, format="JPEG", quality=95)


def prepare_datasets(raw_dir: Path, processed_dir: Path, mini_dir: Path) -> ProcessingStats:
    images = collect_images(raw_dir)
    reset_output_dir(processed_dir)
    reset_output_dir(mini_dir)

    processed_files = 0
    mini_files = 0
    failed_files: list[Path] = []

    for split in SPLITS:
        for class_id, class_name in CLASS_NAMES.items():
            class_images = images[split][class_id]
            for index, source in enumerate(class_images):
                processed_destination = processed_dir / split / class_name / source.name
                try:
                    resize_image(source, processed_destination)
                    processed_files += 1

                    if index < MINI_LIMIT_PER_SPLIT_CLASS:
                        mini_destination = mini_dir / split / class_name / source.name
                        resize_image(source, mini_destination)
                        mini_files += 1
                except (OSError, UnidentifiedImageError) as exc:
                    print(f"Failed to process {source}: {exc}")
                    failed_files.append(source)

    return ProcessingStats(
        processed_files=processed_files,
        mini_files=mini_files,
        failed_files=tuple(failed_files),
    )


def print_expected_counts(images: dict[str, dict[str, list[Path]]]) -> None:
    print("Input images by split and class:")
    for split in SPLITS:
        print(f"  {split}")
        for class_id, class_name in CLASS_NAMES.items():
            print(f"    {class_id:>2} {class_name}: {len(images[split][class_id])}")


def main() -> None:
    root = repo_root()
    data_dir = root / "data"
    raw_dir = find_raw_data_dir(data_dir)
    processed_dir = data_dir / "food11_processed"
    mini_dir = data_dir / "food11_processed_mini"

    print(f"Using raw data: {raw_dir.relative_to(root)}")
    print_expected_counts(collect_images(raw_dir))

    stats = prepare_datasets(raw_dir, processed_dir, mini_dir)

    print(f"Processed dataset: {processed_dir.relative_to(root)} ({stats.processed_files} files)")
    print(f"Mini dataset: {mini_dir.relative_to(root)} ({stats.mini_files} files)")
    print(f"Failed files: {len(stats.failed_files)}")

    if stats.failed_files:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
