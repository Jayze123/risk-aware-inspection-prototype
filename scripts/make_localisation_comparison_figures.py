from __future__ import annotations

import argparse
import re
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def read_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return image


def read_gray(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Could not read grayscale image: {path}")
    return image


def normalise_map(image: np.ndarray) -> np.ndarray:
    image = image.astype(np.float32)
    min_value = float(image.min())
    max_value = float(image.max())

    if max_value > min_value:
        image = (image - min_value) / (max_value - min_value)
    else:
        image = np.zeros_like(image)

    return image


def resize_to(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_NEAREST)


def get_actual_folder(image_path: str, image_id: str) -> str:
    match = re.search(r"[\\/]test[\\/](?P<folder>[^\\/]+)[\\/]", image_path)
    if match:
        return match.group("folder")

    parts = image_id.split("__")
    if "test" in parts:
        index = parts.index("test")
        if index + 1 < len(parts):
            return parts[index + 1]

    return "unknown"


def find_ground_truth_mask(ground_truth_root: Path, image_path: str, image_id: str) -> Path | None:
    actual_folder = get_actual_folder(image_path, image_id)
    if actual_folder == "good":
        return None

    image_stem = Path(image_path).stem

    candidates = [
        ground_truth_root / actual_folder / f"{image_stem}_mask.png",
        ground_truth_root / actual_folder / f"{image_stem}.png",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def find_named_png(folder: Path, image_id: str, suffix_options: list[str]) -> Path | None:
    simple_id = image_id.replace("__", "_")

    candidates = []
    for suffix in suffix_options:
        candidates.append(folder / f"{image_id}{suffix}.png")
        candidates.append(folder / f"{simple_id}{suffix}.png")

    for candidate in candidates:
        if candidate.exists():
            return candidate

    matches = list(folder.rglob(f"{image_id}*.png"))
    if not matches:
        matches = list(folder.rglob(f"{simple_id}*.png"))

    return matches[0] if matches else None


def make_panel(title: str, image: np.ndarray, panel_size: tuple[int, int]) -> np.ndarray:
    width, height = panel_size

    if image.ndim == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    image = cv2.resize(image, (width, height), interpolation=cv2.INTER_NEAREST)

    title_bar = np.full((36, width, 3), 255, dtype=np.uint8)
    cv2.putText(
        title_bar,
        title,
        (8, 24),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 0, 0),
        1,
        cv2.LINE_AA,
    )

    return np.vstack([title_bar, image])


def mask_to_bgr(mask: np.ndarray) -> np.ndarray:
    mask = (mask > 0).astype(np.uint8) * 255
    return cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)


def anomaly_map_to_colour(amap: np.ndarray) -> np.ndarray:
    amap = normalise_map(amap)
    amap_uint8 = (amap * 255).astype(np.uint8)
    return cv2.applyColorMap(amap_uint8, cv2.COLORMAP_JET)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--default-localisation", required=True)
    parser.add_argument("--threshold-sweep-per-image", required=True)
    parser.add_argument("--anomaly-map-dir", required=True)
    parser.add_argument("--default-mask-dir", required=True)
    parser.add_argument("--ground-truth-root", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--threshold", type=float, default=0.85)
    parser.add_argument("--top-n", type=int, default=6)
    args = parser.parse_args()

    results_path = Path(args.results)
    default_localisation_path = Path(args.default_localisation)
    threshold_sweep_path = Path(args.threshold_sweep_per_image)
    anomaly_map_dir = Path(args.anomaly_map_dir)
    default_mask_dir = Path(args.default_mask_dir)
    ground_truth_root = Path(args.ground_truth_root)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df = pd.read_csv(results_path)
    default_df = pd.read_csv(default_localisation_path)
    sweep_df = pd.read_csv(threshold_sweep_path)

    tuned_df = sweep_df[np.isclose(sweep_df["threshold"], args.threshold)].copy()

    comparison = default_df[["image_id", "iou", "dice"]].rename(
        columns={"iou": "default_iou", "dice": "default_dice"}
    ).merge(
        tuned_df[["image_id", "iou", "dice"]].rename(
            columns={"iou": "tuned_iou", "dice": "tuned_dice"}
        ),
        on="image_id",
        how="inner",
    )

    comparison["iou_improvement"] = comparison["tuned_iou"] - comparison["default_iou"]
    comparison["dice_improvement"] = comparison["tuned_dice"] - comparison["default_dice"]

    comparison = comparison.sort_values("dice_improvement", ascending=False).head(args.top_n)

    selected = comparison.merge(results_df, on="image_id", how="left")

    panel_size = (220, 220)

    summary_rows = []

    for _, row in selected.iterrows():
        image_id = str(row["image_id"])
        image_path = Path(str(row["image_path"]))

        gt_path = find_ground_truth_mask(ground_truth_root, str(image_path), image_id)
        anomaly_map_path = find_named_png(anomaly_map_dir, image_id, ["", "_anomaly_map"])
        default_mask_path = find_named_png(default_mask_dir, image_id, ["_mask", ""])

        if gt_path is None or anomaly_map_path is None or default_mask_path is None:
            print(f"Skipping {image_id}: missing required file")
            continue

        original = read_image(image_path)
        gt_mask = read_gray(gt_path)
        anomaly_map = read_gray(anomaly_map_path)
        default_mask = read_gray(default_mask_path)

        anomaly_map_norm = normalise_map(anomaly_map)
        tuned_mask = (anomaly_map_norm >= args.threshold).astype(np.uint8) * 255

        gt_mask = resize_to(gt_mask, (original.shape[1], original.shape[0]))
        anomaly_colour = resize_to(anomaly_map_to_colour(anomaly_map), (original.shape[1], original.shape[0]))
        default_mask = resize_to(default_mask, (original.shape[1], original.shape[0]))
        tuned_mask = resize_to(tuned_mask, (original.shape[1], original.shape[0]))

        panels = [
            make_panel("Original", original, panel_size),
            make_panel("GT mask", mask_to_bgr(gt_mask), panel_size),
            make_panel("Anomaly map", anomaly_colour, panel_size),
            make_panel("Default mask", mask_to_bgr(default_mask), panel_size),
            make_panel(f"Tuned mask {args.threshold:.2f}", mask_to_bgr(tuned_mask), panel_size),
        ]

        montage = np.hstack(panels)

        caption = np.full((52, montage.shape[1], 3), 255, dtype=np.uint8)
        caption_text = (
            f"{image_id} | default Dice={row['default_dice']:.3f}, "
            f"tuned Dice={row['tuned_dice']:.3f}"
        )
        cv2.putText(
            caption,
            caption_text,
            (10, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

        figure = np.vstack([montage, caption])

        output_path = output_dir / f"{image_id}_comparison.png"
        cv2.imwrite(str(output_path), figure)

        summary_rows.append(
            {
                "image_id": image_id,
                "default_iou": row["default_iou"],
                "tuned_iou": row["tuned_iou"],
                "default_dice": row["default_dice"],
                "tuned_dice": row["tuned_dice"],
                "figure": str(output_path),
            }
        )

    summary_df = pd.DataFrame(summary_rows)
    summary_path = output_dir / "figure_summary.csv"
    summary_df.to_csv(summary_path, index=False)

    print("Localisation comparison figures generated.")
    print(f"Output directory: {output_dir}")
    print(f"Summary: {summary_path}")
    print()
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()