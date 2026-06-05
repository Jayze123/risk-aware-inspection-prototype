from __future__ import annotations

import argparse
import csv
from pathlib import Path


def parse_float(value: str) -> float:
    try:
        return float(value)
    except Exception:
        return 0.0


def extract_actual_folder(image_path: str) -> str:
    normalised = image_path.replace("/", "\\")
    parts = normalised.split("\\")
    if "test" not in parts:
        return "unknown"

    test_index = parts.index("test")
    if test_index + 1 >= len(parts):
        return "unknown"

    return parts[test_index + 1]


def safe_divide(a: float, b: float) -> float:
    return a / b if b else 0.0


def evaluate_at_threshold(records: list[dict], threshold: float) -> dict:
    tp = tn = fp = fn = 0

    for row in records:
        actual_folder = extract_actual_folder(row["image_path"])
        actual_defective = actual_folder != "good"

        score = parse_float(row["detection.image_score"])
        predicted_defective = score >= threshold

        if actual_defective and predicted_defective:
            tp += 1
        elif not actual_defective and not predicted_defective:
            tn += 1
        elif not actual_defective and predicted_defective:
            fp += 1
        else:
            fn += 1

    total = tp + tn + fp + fn
    accuracy = safe_divide(tp + tn, total)
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    specificity = safe_divide(tn, tn + fp)
    f1 = safe_divide(2 * precision * recall, precision + recall)

    return {
        "threshold": round(threshold, 6),
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "specificity": round(specificity, 4),
        "f1_score": round(f1, 4),
    }


def run_sensitivity(results_csv: Path, output_csv: Path) -> None:
    with results_csv.open("r", newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    if not records:
        raise ValueError("No records found in results CSV.")

    original_threshold = parse_float(records[0]["detection.threshold"])

    multipliers = [
        0.30, 0.40, 0.50, 0.60, 0.70,
        0.80, 0.90, 1.00, 1.10, 1.20,
        1.30, 1.40, 1.50,
    ]

    rows = []

    for multiplier in multipliers:
        threshold = original_threshold * multiplier
        result = evaluate_at_threshold(records, threshold)
        result["threshold_multiplier"] = multiplier
        rows.append(result)

    output_csv.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "threshold_multiplier",
        "threshold",
        "tp",
        "tn",
        "fp",
        "fn",
        "accuracy",
        "precision",
        "recall",
        "specificity",
        "f1_score",
    ]

    with output_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    best = max(rows, key=lambda row: row["f1_score"])

    print("Threshold sensitivity complete.")
    print(f"Results analysed: {results_csv}")
    print(f"Output saved to: {output_csv}")
    print()
    print("Best threshold by F1-score:")
    for key in fieldnames:
        print(f"{key}: {best[key]}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run threshold sensitivity testing on an MVTec results summary."
    )
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    run_sensitivity(args.results, args.output)


if __name__ == "__main__":
    main()