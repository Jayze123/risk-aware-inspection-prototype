from __future__ import annotations

import argparse
from pathlib import Path

from anomalib.data import Folder
from anomalib.engine import Engine
from anomalib.models.image.padim import Padim


def train_padim_folder(
    category_root: Path,
    output_dir: Path,
    train_batch_size: int = 4,
    eval_batch_size: int = 4,
    num_workers: int = 0,
    backbone: str = "resnet18",
    n_features: int | None = None,
) -> None:
    print(f"PaDiM backbone: {backbone}")
    print(f"PaDiM n_features: {n_features}")

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

    model = Padim(
        backbone=backbone,
        layers=["layer1", "layer2", "layer3"],
        pre_trained=True,
        n_features=n_features,
    )

    engine = Engine(
        default_root_dir=output_dir,
        accelerator="cpu",
        devices=1,
        max_epochs=1,
    )

    print("Starting PaDiM Folder experiment")
    print(f"Category root: {category_root}")
    print(f"Output directory: {output_dir}")
    print("Abnormal folders:")
    for path in abnormal_dirs:
        print(f"  {path.name}")

    engine.fit(model=model, datamodule=datamodule)
    engine.test(model=model, datamodule=datamodule)

    print("PaDiM Folder experiment complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train PaDiM on an MVTec category using Anomalib Folder datamodule."
    )

    parser.add_argument(
    "--backbone",
    default="resnet18",
    help="CNN backbone used by PaDiM.",
    )

    parser.add_argument(
    "--n-features",
    type=int,
    default=None,
    help="Number of features retained by PaDiM. Use default None unless testing dimensionality reduction.",
    )

    parser.add_argument("--train-batch-size", type=int, default=4)
    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)

    args = parser.parse_args()

    train_padim_folder(
        category_root=args.category_root,
        output_dir=args.output,
        train_batch_size=args.train_batch_size,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
        backbone=args.backbone,
        n_features=args.n_features,
    )


if __name__ == "__main__":
    main()