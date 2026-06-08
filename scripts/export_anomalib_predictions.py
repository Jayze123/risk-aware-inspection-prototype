from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from anomalib.data import Folder
from anomalib.engine import Engine
from anomalib.models import Patchcore
from anomalib.models.image.padim import Padim


def build_folder_datamodule(
    category_root: Path,
    eval_batch_size: int,
    num_workers: int,
) -> Folder:
    test_root = category_root / "test"

    abnormal_dirs = [
        path for path in test_root.iterdir()
        if path.is_dir() and path.name != "good"
    ]

    if not abnormal_dirs:
        raise ValueError(f"No abnormal test folders found in {test_root}")

    return Folder(
        name=category_root.name,
        root=category_root,
        normal_dir="train/good",
        normal_test_dir="test/good",
        abnormal_dir=[str(path.relative_to(category_root)) for path in abnormal_dirs],
        train_batch_size=4,
        eval_batch_size=eval_batch_size,
        num_workers=num_workers,
        val_split_mode="same_as_test",
    )


def build_model(model_name: str):
    model_name = model_name.lower()

    if model_name == "patchcore":
        return Patchcore(
            backbone="wide_resnet50_2",
            layers=["layer2", "layer3"],
            coreset_sampling_ratio=0.1,
            num_neighbors=9,
        )

    if model_name == "padim":
        return Padim(
            backbone="resnet18",
            layers=["layer1", "layer2", "layer3"],
        )

    raise ValueError(f"Unsupported model: {model_name}")


def get_field(batch: Any, field: str) -> Any:
    if isinstance(batch, dict):
        return batch[field]
    return getattr(batch, field)


def to_numpy(value: Any) -> np.ndarray:
    if hasattr(value, "detach"):
        return value.detach().cpu().numpy()
    return np.asarray(value)


def safe_image_id(image_path: str) -> str:
    path = Path(image_path)
    parts = path.with_suffix("").parts[-4:]
    return "__".join(part.replace(" ", "_").replace("-", "_") for part in parts)


def normalise_anomaly_map(anomaly_map: np.ndarray) -> np.ndarray:
    anomaly_map = np.asarray(anomaly_map, dtype=np.float32)
    min_value = float(anomaly_map.min())
    max_value = float(anomaly_map.max())

    if max_value - min_value < 1e-8:
        return np.zeros_like(anomaly_map, dtype=np.uint8)

    normalised = (anomaly_map - min_value) / (max_value - min_value)
    return (normalised * 255).astype(np.uint8)


def save_anomaly_map(anomaly_map: np.ndarray, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image = Image.fromarray(normalise_anomaly_map(anomaly_map))
    image.save(output_path)


def export_predictions(
    model_name: str,
    category_root: Path,
    checkpoint: Path,
    output_dir: Path,
    eval_batch_size: int,
    num_workers: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    maps_dir = output_dir / "anomaly_maps"

    datamodule = build_folder_datamodule(
        category_root=category_root,
        eval_batch_size=eval_batch_size,
        num_workers=num_workers,
    )

    model = build_model(model_name)

    engine = Engine(
        accelerator="cpu",
        devices=1,
    )

    print("Running Anomalib prediction export")
    print(f"Model: {model_name}")
    print(f"Category root: {category_root}")
    print(f"Checkpoint: {checkpoint}")
    print(f"Output directory: {output_dir}")

    predictions = engine.predict(
        model=model,
        datamodule=datamodule,
        ckpt_path=str(checkpoint),
    )

    rows = []

    for batch in predictions:
        image_paths = list(get_field(batch, "image_path"))
        pred_scores = to_numpy(get_field(batch, "pred_score")).reshape(-1)
        pred_labels = to_numpy(get_field(batch, "pred_label")).reshape(-1)

        anomaly_maps = to_numpy(get_field(batch, "anomaly_map"))

        if anomaly_maps.ndim == 4:
            anomaly_maps = anomaly_maps[:, 0, :, :]
        elif anomaly_maps.ndim == 3:
            pass
        elif anomaly_maps.ndim == 2:
            anomaly_maps = anomaly_maps[None, :, :]
        else:
            raise ValueError(f"Unexpected anomaly map shape: {anomaly_maps.shape}")

        for index, image_path in enumerate(image_paths):
            image_id = safe_image_id(str(image_path))
            map_path = maps_dir / f"{image_id}_anomaly_map.png"

            save_anomaly_map(anomaly_maps[index], map_path)

            rows.append(
                {
                    "image_id": image_id,
                    "image_path": str(image_path),
                    "model": model_name,
                    "category": category_root.name,
                    "pred_score": float(pred_scores[index]),
                    "pred_label": bool(pred_labels[index]),
                    "anomaly_map_path": str(map_path),
                }
            )

    csv_path = output_dir / "predictions.csv"

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_id",
                "image_path",
                "model",
                "category",
                "pred_score",
                "pred_label",
                "anomaly_map_path",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved {len(rows)} prediction records to {csv_path}")
    print(f"Saved anomaly maps to {maps_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export Anomalib model predictions for later risk-aware pipeline integration."
    )

    parser.add_argument(
        "--model",
        required=True,
        choices=["patchcore", "padim"],
        help="Anomalib model type to export predictions from.",
    )

    parser.add_argument(
        "--category-root",
        required=True,
        type=Path,
        help="Path to one MVTec category folder.",
    )

    parser.add_argument(
        "--checkpoint",
        required=True,
        type=Path,
        help="Path to Anomalib model checkpoint.",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output directory for exported predictions.",
    )

    parser.add_argument("--eval-batch-size", type=int, default=4)
    parser.add_argument("--num-workers", type=int, default=0)

    args = parser.parse_args()

    export_predictions(
        model_name=args.model,
        category_root=args.category_root,
        checkpoint=args.checkpoint,
        output_dir=args.output,
        eval_batch_size=args.eval_batch_size,
        num_workers=args.num_workers,
    )


if __name__ == "__main__":
    main()