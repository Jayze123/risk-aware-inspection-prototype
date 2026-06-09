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


def resize_mask(mask: np.ndarray, target_shape: tuple[int, int]) -> np.ndarray:
    if mask.shape == target_shape:
        return mask
    resized = cv2.resize(
        mask.astype(np.uint8),
        (target_shape[1], target_shape[0]),
        interpolation=cv2.INTER_NEAREST,
    )
    return resized > 0


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
    try:
        return Path(image_path).stem
    except Exception:
        return image_id.split("__")[-1]


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


def find_predicted_mask(pred_mask_dir: Path, image_id: str) -> Path | None:
    simple_id = image_id.replace("__", "_")

    candidates = [
        pred_mask_dir / f"{image_id}_mask.png",
        pred_mask_dir / f"{simple_id}_mask.png",
        pred_mask_dir / f"{image_id}.png",
        pred_mask_dir / f"{simple_id}.png",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = list(pred_mask_dir.rglob(f"{image_id}*mask*.png"))
    if not matches:
        matches = list(pred_mask_dir.rglob(f"{simple_id}*mask*.png"))

    return matches[0] if matches else None


def compute_iou_and_dice(pred: np.ndarray, gt: np.ndarray) -> tuple[float, float]:
    pred = pred.astype(bool)
    gt = gt.astype(bool)

    intersection = np.logical_and(pred, gt).sum()
    union = np.logical_or(pred, gt).sum()
    pred_sum = pred.sum()
    gt_sum = gt.sum()

    iou = intersection / union if union > 0 else 1.0
    dice = (2 * intersection) / (pred_sum + gt_sum) if (pred_sum + gt_sum) > 0 else 1.0

    return float(iou), float(dice)


def choose_pred_mask_dir(results_path: Path, supplied_dir: str | None) -> Path:
    if supplied_dir:
        return Path(supplied_dir)

    run_dir = results_path.parent
    for name in ["artifacts", "artefacts"]:
        candidate = run_dir / name
        if candidate.exists():
            return candidate

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Risk-aware results.csv file")
    parser.add_argument("--ground-truth-root", required=True, help="MVTec category ground_truth folder")
    parser.add_argument("--output", required=True, help="Output folder for localisation evaluation")
    parser.add_argument("--pred-mask-dir", default=None, help="Optional folder containing predicted mask PNGs")
    args = parser.parse_args()

    results_path = Path(args.results)
    ground_truth_root = Path(args.ground_truth_root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    pred_mask_dir = choose_pred_mask_dir(results_path, args.pred_mask_dir)

    df = pd.read_csv(results_path)
    rows = []

    for _, row in df.iterrows():
        image_id = str(row["image_id"])
        image_path = str(row["image_path"])

        actual_folder = get_actual_folder(image_path, image_id)
        image_stem = get_image_stem(image_path, image_id)

        gt_path = find_ground_truth_mask(ground_truth_root, actual_folder, image_stem)

        if gt_path is None:
            continue

        pred_path = find_predicted_mask(pred_mask_dir, image_id)

        gt_mask = read_binary_mask(gt_path)

        if pred_path is None:
            pred_mask = np.zeros_like(gt_mask, dtype=bool)
            pred_path_text = ""
        else:
            pred_mask = read_binary_mask(pred_path)
            pred_mask = resize_mask(pred_mask, gt_mask.shape)
            pred_path_text = str(pred_path)

        iou, dice = compute_iou_and_dice(pred_mask, gt_mask)

        rows.append(
            {
                "image_id": image_id,
                "actual_folder": actual_folder,
                "gt_mask": str(gt_path),
                "pred_mask": pred_path_text,
                "iou": iou,
                "dice": dice,
                "gt_area_pixels": int(gt_mask.sum()),
                "pred_area_pixels": int(pred_mask.sum()),
            }
        )

    per_image = pd.DataFrame(rows)

    if per_image.empty:
        raise RuntimeError(
            "No localisation records were evaluated. Check ground-truth path and predicted mask filenames."
        )

    per_image_path = output_dir / "localisation_per_image.csv"
    summary_path = output_dir / "localisation_summary.csv"

    per_image.to_csv(per_image_path, index=False)

    summary = (
        per_image.groupby("actual_folder")
        .agg(
            count=("image_id", "count"),
            mean_iou=("iou", "mean"),
            mean_dice=("dice", "mean"),
            median_iou=("iou", "median"),
            median_dice=("dice", "median"),
        )
        .reset_index()
    )

    overall = pd.DataFrame(
        [
            {
                "actual_folder": "OVERALL",
                "count": len(per_image),
                "mean_iou": per_image["iou"].mean(),
                "mean_dice": per_image["dice"].mean(),
                "median_iou": per_image["iou"].median(),
                "median_dice": per_image["dice"].median(),
            }
        ]
    )

    summary = pd.concat([summary, overall], ignore_index=True)
    summary.to_csv(summary_path, index=False)

    print("Localisation evaluation complete.")
    print(f"Results analysed: {results_path}")
    print(f"Predicted mask directory: {pred_mask_dir}")
    print(f"Ground-truth root: {ground_truth_root}")
    print(f"Per-image output: {per_image_path}")
    print(f"Summary output: {summary_path}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()