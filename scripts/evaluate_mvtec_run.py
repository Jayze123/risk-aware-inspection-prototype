from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def extract_actual_folder(image_path: str) -> str:
    """
    Extracts the MVTec defect folder from paths such as:
    C:\\...\\bottle\\test\\broken_large\\000.png
    """
    normalised = image_path.replace("/", "\\")
    parts = normalised.split("\\")

    if "test" not in parts:
        return "unknown"

    test_index = parts.index("test")
    if test_index + 1 >= len(parts):
        return "unknown"

    return parts[test_index + 1]


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def write_counter_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def evaluate(results_csv: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    with results_csv.open("r", newline="", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    evaluated_rows = []

    for row in records:
        actual_folder = extract_actual_folder(row["image_path"])
        actual_defective = actual_folder != "good"
        predicted_defective = parse_bool(row["detection.is_anomalous"])

        if actual_defective and predicted_defective:
            outcome = "TP"
        elif not actual_defective and not predicted_defective:
            outcome = "TN"
        elif not actual_defective and predicted_defective:
            outcome = "FP"
        else:
            outcome = "FN"

        evaluated_rows.append(
            {
                "image_id": row["image_id"],
                "image_path": row["image_path"],
                "actual_folder": actual_folder,
                "actual_defective": actual_defective,
                "predicted_defective": predicted_defective,
                "outcome": outcome,
                "detection.image_score": row.get("detection.image_score", ""),
                "detection.threshold": row.get("detection.threshold", ""),
                "semantic.label": row.get("semantic.label", ""),
                "risk.risk_class": row.get("risk.risk_class", ""),
                "review.requires_review": row.get("review.requires_review", ""),
                "confidence.fusion.preferred": row.get("confidence.fusion.preferred", ""),
            }
        )

    counts = Counter(row["outcome"] for row in evaluated_rows)

    tp = counts["TP"]
    tn = counts["TN"]
    fp = counts["FP"]
    fn = counts["FN"]

    total = tp + tn + fp + fn
    accuracy = safe_divide(tp + tn, total)
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    specificity = safe_divide(tn, tn + fp)
    f1 = safe_divide(2 * precision * recall, precision + recall)

    review_count = sum(parse_bool(row["review.requires_review"]) for row in evaluated_rows)
    review_rate = safe_divide(review_count, total)

    metrics_rows = [
        {"metric": "total_images", "value": total},
        {"metric": "true_positives", "value": tp},
        {"metric": "true_negatives", "value": tn},
        {"metric": "false_positives", "value": fp},
        {"metric": "false_negatives", "value": fn},
        {"metric": "accuracy", "value": round(accuracy, 4)},
        {"metric": "precision", "value": round(precision, 4)},
        {"metric": "recall", "value": round(recall, 4)},
        {"metric": "specificity", "value": round(specificity, 4)},
        {"metric": "f1_score", "value": round(f1, 4)},
        {"metric": "human_review_count", "value": review_count},
        {"metric": "human_review_rate", "value": round(review_rate, 4)},
    ]

    write_counter_csv(
        output_dir / "metrics_summary.csv",
        ["metric", "value"],
        metrics_rows,
    )

    write_counter_csv(
        output_dir / "evaluated_records.csv",
        list(evaluated_rows[0].keys()),
        evaluated_rows,
    )

    by_folder_detection = Counter(
        (row["actual_folder"], str(row["predicted_defective"]))
        for row in evaluated_rows
    )

    write_counter_csv(
        output_dir / "by_folder_detection.csv",
        ["actual_folder", "predicted_defective", "count"],
        [
            {
                "actual_folder": key[0],
                "predicted_defective": key[1],
                "count": count,
            }
            for key, count in sorted(by_folder_detection.items())
        ],
    )

    by_folder_risk = Counter(
        (row["actual_folder"], row["risk.risk_class"])
        for row in evaluated_rows
    )

    write_counter_csv(
        output_dir / "by_folder_risk.csv",
        ["actual_folder", "risk_class", "count"],
        [
            {
                "actual_folder": key[0],
                "risk_class": key[1],
                "count": count,
            }
            for key, count in sorted(by_folder_risk.items())
        ],
    )

    semantic_counts = Counter(row["semantic.label"] for row in evaluated_rows)

    write_counter_csv(
        output_dir / "semantic_label_summary.csv",
        ["semantic_label", "count"],
        [
            {
                "semantic_label": label,
                "count": count,
            }
            for label, count in sorted(semantic_counts.items())
        ],
    )

    review_counts = Counter(row["review.requires_review"] for row in evaluated_rows)

    write_counter_csv(
        output_dir / "review_summary.csv",
        ["review_required", "count"],
        [
            {
                "review_required": key,
                "count": count,
            }
            for key, count in sorted(review_counts.items())
        ],
    )

    missed_defects = [
        row for row in evaluated_rows
        if row["actual_defective"] is True and row["predicted_defective"] is False
    ]

    if missed_defects:
        write_counter_csv(
            output_dir / "missed_defects.csv",
            list(missed_defects[0].keys()),
            missed_defects,
        )

    false_positives = [
        row for row in evaluated_rows
        if row["actual_defective"] is False and row["predicted_defective"] is True
    ]

    if false_positives:
        write_counter_csv(
            output_dir / "false_positives.csv",
            list(false_positives[0].keys()),
            false_positives,
        )

    print("Evaluation complete.")
    print(f"Results analysed: {results_csv}")
    print(f"Evaluation outputs saved to: {output_dir}")
    print()
    print(f"TP: {tp}")
    print(f"TN: {tn}")
    print(f"FP: {fp}")
    print(f"FN: {fn}")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")
    print(f"F1-score: {f1:.4f}")
    print(f"Human review rate: {review_rate:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate an MVTec AD run from the risk-aware inspection prototype."
    )

    parser.add_argument(
        "--results",
        required=True,
        type=Path,
        help="Path to results_summary.csv",
    )

    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Directory where evaluation CSV files will be saved.",
    )

    args = parser.parse_args()

    evaluate(args.results, args.output)


if __name__ == "__main__":
    main()