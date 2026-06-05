from __future__ import annotations

import argparse
from pathlib import Path

from anomalib.data import Folder
from anomalib.engine import Engine
from anomalib.models import Patchcore


def train_patchcore_folder(
    category_root: Path,
    output_dir: Path,
    train_batch_size: int = 4,
    eval_batch_size: int = 4,
    num_workers: int = 0,
) -> None:
    test_root = category_root / "test"

    abnormal_dirs = [
        path for path in test_root.iterdir()
        if path.is_dir() and path.name != "good"
    ]

    if not abnormal_dirs:
        raise ValueError(f"No abnormal test folders found in {test_root}")

    datamodule = Folder(
        name=category_root.name,
        root=category_root,
        normal_dir="train/good",
        normal_test_dir="test/good",
        abnormal_dir=[str(path.relative_to(category_root)) for path in abnormal_dirs],
        train_batch_size=train_batch_size,
        eval_batch_size=eval_batch_size,
        num_workers=num_workers,
        val_split_mode="same_as_test",
    )

    model = Patchcore(
        backbone="wide_resnet50_2",
        layers=["layer2", "layer3"],
        coreset_sampling_ratio=0.1,
        num_neighbors=9,
    )

    engine = Engine(
        default_root_dir=output_dir,
        accelerator="cpu",
        devices=1,
        max_epochs=1,
    )

    print("Starting PatchCore Folder experiment")
    print(f"Category root: {category_root}")
    print(f"Output directory: {output_dir}")
    print("Abnormal folders:")
    for path in abnormal_dirs:
        print(f"  {path.name}")

    engine.fit(model=model, datamodule=datamodule)
    engine.test(model=model, datamodule=datamodule)

    print("PatchCore Folder experiment complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train PatchCore on an MVTec category using Anomalib Folder datamodule."
    )

    parser.add_argument(
        "--category-root",
        required=True,
        type=Path,
        help="Path to one MVTec category folder, e.g. mvtec_anomaly_detection/bottle.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory for anomalib experiment results.",
    )

    parser.add_argument("--train-batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)

    args = parser.parse_args()

    train_patchcore_folder(
        category_root=args.category_root,
        output_dir=args.output,
        train_batch_size=args.train_batch_size,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
    )


if __name__ == "__main__":
    main()