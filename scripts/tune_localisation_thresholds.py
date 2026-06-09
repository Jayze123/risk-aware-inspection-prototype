from __future__ import annotations

import argparse
import re
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def read_binary_mask(path: Path) -> np.ndarray:
    mask = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        raise FileNotFoundError(f"Could not read mask: {path}")
    return mask > 0


def read_anomaly_map(path: Path) -> np.ndarray:
    amap = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if amap is None:
        raise FileNotFoundError(f"Could not read anomaly map: {path}")

    amap = amap.astype(np.float32)

    min_value = float(amap.min())
    max_value = float(amap.max())

    if max_value > min_value:
        amap = (amap - min_value) / (max_value - min_value)
    else:
        amap = np.zeros_like(amap, dtype=np.float32)

    return amap


def resize_to_gt(pred: np.ndarray, gt_shape: tuple[int, int]) -> np.ndarray:
    if pred.shape == gt_shape:
        return pred

    resized = cv2.resize(
        pred.astype(np.float32),
        (gt_shape[1], gt_shape[0]),
        interpolation=cv2.INTER_LINEAR,
    )
    return resized


def get_actual_folder(image_path: str, image_id: str) -> str:
    match = re.search(r"[\\/]test[\\/](?P<folder>[^\\/]+)[\\/]", image_path)
    if match:
        return match.group("folder")

    parts = image_id.split("__")
    if "test" in parts:
        idx = parts.index("test")
        if idx + 1 < len(parts):
            return parts[idx + 1]

    return "unknown"


def get_image_stem(image_path: str, image_id: str) -> str:
    if image_path:
        return Path(image_path).stem

    parts = image_id.split("__")
    return parts[-1]


def find_ground_truth_mask(ground_truth_root: Path, actual_folder: str, image_stem: str) -> Path | None:
    if actual_folder == "good":
        return None

    candidates = [
        ground_truth_root / actual_folder / f"{image_stem}_mask.png",
        ground_truth_root / actual_folder / f"{image_stem}.png",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def find_anomaly_map(anomaly_map_dir: Path, image_id: str) -> Path | None:
    simple_id = image_id.replace("__", "_")

    candidates = [
        anomaly_map_dir / f"{image_id}.png",
        anomaly_map_dir / f"{image_id}_anomaly_map.png",
        anomaly_map_dir / f"{simple_id}.png",
        anomaly_map_dir / f"{simple_id}_anomaly_map.png",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = list(anomaly_map_dir.rglob(f"{image_id}*.png"))
    if not matches:
        matches = list(anomaly_map_dir.rglob(f"{simple_id}*.png"))

    return matches[0] if matches else None


def compute_iou_and_dice(pred_mask: np.ndarray, gt_mask: np.ndarray) -> tuple[float, float]:
    pred_mask = pred_mask.astype(bool)
    gt_mask = gt_mask.astype(bool)

    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()

    pred_sum = pred_mask.sum()
    gt_sum = gt_mask.sum()

    iou = intersection / union if union > 0 else 1.0
    dice = (2 * intersection) / (pred_sum + gt_sum) if (pred_sum + gt_sum) > 0 else 1.0

    return float(iou), float(dice)


def parse_thresholds(text: str | None) -> list[float]:
    if text:
        return [float(item.strip()) for item in text.split(",") if item.strip()]

    return [round(x, 2) for x in np.arange(0.05, 1.00, 0.05)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Risk-aware results.csv file")
    parser.add_argument("--anomaly-map-dir", required=True, help="Folder containing anomaly map PNG files")
    parser.add_argument("--ground-truth-root", required=True, help="MVTec category ground_truth folder")
    parser.add_argument("--output", required=True, help="Output folder")
    parser.add_argument(
        "--thresholds",
        default=None,
        help="Comma-separated thresholds. Default: 0.05,0.10,...,0.95",
    )
    args = parser.parse_args()

    results_path = Path(args.results)
    anomaly_map_dir = Path(args.anomaly_map_dir)
    ground_truth_root = Path(args.ground_truth_root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    thresholds = parse_thresholds(args.thresholds)
    df = pd.read_csv(results_path)

    per_image_rows = []
    summary_rows = []

    prepared_records = []

    for _, row in df.iterrows():
        image_id = str(row["image_id"])
        image_path = str(row["image_path"])

        actual_folder = get_actual_folder(image_path, image_id)
        image_stem = get_image_stem(image_path, image_id)

        gt_path = find_ground_truth_mask(ground_truth_root, actual_folder, image_stem)
        if gt_path is None:
            continue

        anomaly_map_path = find_anomaly_map(anomaly_map_dir, image_id)
        if anomaly_map_path is None:
            continue

        gt_mask = read_binary_mask(gt_path)
        anomaly_map = read_anomaly_map(anomaly_map_path)
        anomaly_map = resize_to_gt(anomaly_map, gt_mask.shape)

        prepared_records.append(
            {
                "image_id": image_id,
                "actual_folder": actual_folder,
                "gt_mask": gt_mask,
                "anomaly_map": anomaly_map,
                "gt_path": str(gt_path),
                "anomaly_map_path": str(anomaly_map_path),
            }
        )

    if not prepared_records:
        raise RuntimeError(
            "No records were prepared. Check the results CSV, anomaly-map folder and ground-truth folder."
        )

    for threshold in thresholds:
        threshold_rows = []

        for record in prepared_records:
            pred_mask = record["anomaly_map"] >= threshold
            iou, dice = compute_iou_and_dice(pred_mask, record["gt_mask"])

            row_data = {
                "threshold": threshold,
                "image_id": record["image_id"],
                "actual_folder": record["actual_folder"],
                "iou": iou,
                "dice": dice,
                "gt_area_pixels": int(record["gt_mask"].sum()),
                "pred_area_pixels": int(pred_mask.sum()),
                "gt_path": record["gt_path"],
                "anomaly_map_path": record["anomaly_map_path"],
            }

            per_image_rows.append(row_data)
            threshold_rows.append(row_data)

        threshold_df = pd.DataFrame(threshold_rows)

        summary_rows.append(
            {
                "threshold": threshold,
                "count": len(threshold_df),
                "mean_iou": threshold_df["iou"].mean(),
                "mean_dice": threshold_df["dice"].mean(),
                "median_iou": threshold_df["iou"].median(),
                "median_dice": threshold_df["dice"].median(),
            }
        )

    per_image_df = pd.DataFrame(per_image_rows)
    summary_df = pd.DataFrame(summary_rows)

    best_iou_row = summary_df.sort_values("mean_iou", ascending=False).iloc[0]
    best_dice_row = summary_df.sort_values("mean_dice", ascending=False).iloc[0]

    per_image_path = output_dir / "threshold_sweep_per_image.csv"
    summary_path = output_dir / "threshold_sweep_summary.csv"

    per_image_df.to_csv(per_image_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    print("Localisation threshold sweep complete.")
    print(f"Results analysed: {results_path}")
    print(f"Anomaly map directory: {anomaly_map_dir}")
    print(f"Ground-truth root: {ground_truth_root}")
    print(f"Prepared defective records: {len(prepared_records)}")
    print(f"Per-image output: {per_image_path}")
    print(f"Summary output: {summary_path}")
    print()
    print("Best threshold by mean IoU:")
    print(best_iou_row.to_string())
    print()
    print("Best threshold by mean Dice:")
    print(best_dice_row.to_string())
    print()
    print("Full threshold summary:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()