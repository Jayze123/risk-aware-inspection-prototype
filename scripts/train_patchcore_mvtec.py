from __future__ import annotations

import argparse
from pathlib import Path

from anomalib.data import MVTecAD
from anomalib.engine import Engine
from anomalib.models import Patchcore




def train_patchcore(
    dataset_root: Path,
    category: str,
    output_dir: Path,
    train_batch_size: int = 8,
    eval_batch_size: int = 8,
    num_workers: int = 0,
    backbone: str = "wide_resnet50_2",
    coreset_sampling_ratio: float = 0.1,
    num_neighbors: int = 9,
) -> None:
    print(f"PatchCore backbone: {backbone}")
    print(f"PatchCore coreset sampling ratio: {coreset_sampling_ratio}")
    print(f"PatchCore number of neighbours: {num_neighbors}")
    """
    Train and evaluate PatchCore on one MVTec AD category.

    This script is intentionally kept separate from the risk-aware pipeline first.
    The aim is to confirm that anomalib can train and evaluate a stronger anomaly
    detector before integrating its predictions into the risk-aware governance layer.
    """

    datamodule = MVTecAD(
        root=dataset_root,
        category=category,
        train_batch_size=train_batch_size,
        eval_batch_size=eval_batch_size,
        num_workers=num_workers,
    )

    model = Patchcore(
        backbone=backbone,
        layers=("layer2", "layer3"),
        pre_trained=True,
        coreset_sampling_ratio=coreset_sampling_ratio,
        num_neighbors=num_neighbors,
    )

    engine = Engine(
        default_root_dir=output_dir,
        accelerator="cpu",
        devices=1,
        max_epochs=1,
    )

    print("Starting PatchCore experiment")
    print(f"Dataset root: {dataset_root}")
    print(f"Category: {category}")
    print(f"Output directory: {output_dir}")

    engine.fit(model=model, datamodule=datamodule)
    engine.test(model=model, datamodule=datamodule)

    print("PatchCore experiment complete.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train and evaluate PatchCore on one MVTec AD category."
    )

    parser.add_argument(
        "--backbone",
        default="wide_resnet50_2",
        help="CNN backbone used by PatchCore.",
    )

    parser.add_argument(
        "--coreset-sampling-ratio",
        type=float,
        default=0.1,
        help="PatchCore memory-bank coreset sampling ratio.",
    )

    parser.add_argument(
        "--num-neighbors",
        type=int,
        default=9,
        help="Number of nearest neighbours used by PatchCore.",
    )

    
    parser.add_argument("--train-batch-size", type=int, default=8)
    parser.add_argument("--eval-batch-size", type=int, default=8)
    parser.add_argument("--num-workers", type=int, default=0)

    args = parser.parse_args()

    train_patchcore(
        dataset_root=args.dataset_root,
        category=args.category,
        output_dir=args.output,
        train_batch_size=args.train_batch_size,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
        backbone=args.backbone,
        coreset_sampling_ratio=args.coreset_sampling_ratio,
        num_neighbors=args.num_neighbors,
    )


if __name__ == "__main__":
    main()