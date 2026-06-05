from __future__ import annotations

import argparse
from pathlib import Path

from anomalib.data import Folder


def count_pngs(path: Path) -> int:
    return len(list(path.rglob("*.png"))) if path.exists() else 0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--category-root", required=True, type=Path)
    args = parser.parse_args()

    category_root = args.category_root
    train_good = category_root / "train" / "good"
    test_good = category_root / "test" / "good"

    abnormal_dirs = [
        path for path in (category_root / "test").iterdir()
        if path.is_dir() and path.name != "good"
    ]

    print("Filesystem check")
    print(f"category_root: {category_root}")
    print(f"train_good: {train_good} -> {count_pngs(train_good)} images")
    print(f"test_good: {test_good} -> {count_pngs(test_good)} images")
    print("abnormal_dirs:")
    for path in abnormal_dirs:
        print(f"  {path} -> {count_pngs(path)} images")
    print()

    datamodule = Folder(
        name=category_root.name,
        root=category_root,
        normal_dir="train/good",
        normal_test_dir="test/good",
        abnormal_dir=[str(path.relative_to(category_root)) for path in abnormal_dirs],
        train_batch_size=4,
        eval_batch_size=4,
        num_workers=0,
    )

    datamodule.setup()

    print("Anomalib Folder datamodule check")
    print(f"train_data: {len(datamodule.train_data)}")
    print(f"val_data: {len(datamodule.val_data)}")
    print(f"test_data: {len(datamodule.test_data)}")

    train_loader = datamodule.train_dataloader()
    test_loader = datamodule.test_dataloader()

    print(f"train dataloader batches: {len(train_loader)}")
    print(f"test dataloader batches: {len(test_loader)}")

    train_batch = next(iter(train_loader))
    test_batch = next(iter(test_loader))

    print("First train batch type:", type(train_batch))
    if hasattr(train_batch, "keys"):
        print("First train batch keys:", list(train_batch.keys()))

    print("First test batch type:", type(test_batch))
    if hasattr(test_batch, "keys"):
        print("First test batch keys:", list(test_batch.keys()))


if __name__ == "__main__":
    main()