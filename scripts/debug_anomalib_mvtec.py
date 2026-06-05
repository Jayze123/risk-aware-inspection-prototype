from __future__ import annotations

import argparse
from pathlib import Path

from anomalib.data import MVTecAD


def count_pngs(path: Path) -> int:
    return len(list(path.rglob("*.png")))


def try_len(name: str, obj) -> None:
    try:
        print(f"{name}: {len(obj)}")
    except Exception as exc:
        print(f"{name}: could not read length ({exc})")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--category", required=True)
    args = parser.parse_args()

    category_path = args.dataset_root / args.category
    train_good = category_path / "train" / "good"
    test_path = category_path / "test"
    gt_path = category_path / "ground_truth"

    print("Filesystem check")
    print(f"dataset_root: {args.dataset_root}")
    print(f"category_path: {category_path}")
    print(f"train_good exists: {train_good.exists()}")
    print(f"train_good png count: {count_pngs(train_good) if train_good.exists() else 0}")
    print(f"test exists: {test_path.exists()}")
    print(f"test png count: {count_pngs(test_path) if test_path.exists() else 0}")
    print(f"ground_truth exists: {gt_path.exists()}")
    print()

    print("Anomalib MVTecAD check")
    datamodule = MVTecAD(
        root=args.dataset_root,
        category=args.category,
        train_batch_size=4,
        eval_batch_size=4,
        num_workers=0,
    )

    datamodule.prepare_data()
    datamodule.setup()

    for attr in ["train_data", "val_data", "test_data"]:
        if hasattr(datamodule, attr):
            try_len(attr, getattr(datamodule, attr))
        else:
            print(f"{attr}: missing")

    print()

    try:
        train_loader = datamodule.train_dataloader()
        print(f"train dataloader batches: {len(train_loader)}")
        batch = next(iter(train_loader))
        print("First train batch type:", type(batch))
        if hasattr(batch, "keys"):
            print("First train batch keys:", list(batch.keys()))
    except Exception as exc:
        print("train dataloader failed:")
        print(type(exc).__name__, exc)

    try:
        test_loader = datamodule.test_dataloader()
        print(f"test dataloader batches: {len(test_loader)}")
        batch = next(iter(test_loader))
        print("First test batch type:", type(batch))
        if hasattr(batch, "keys"):
            print("First test batch keys:", list(batch.keys()))
    except Exception as exc:
        print("test dataloader failed:")
        print(type(exc).__name__, exc)


if __name__ == "__main__":
    main()