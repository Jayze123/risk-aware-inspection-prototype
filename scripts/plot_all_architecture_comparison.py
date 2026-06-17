from pathlib import Path
import csv
import matplotlib.pyplot as plt


INPUT_CSV = Path("docs/experiments/architecture_comparison/all_categories_architecture_comparison_summary.csv")
OUTPUT_DIR = Path("docs/figures/architecture_comparison")
OUTPUT_PATH = OUTPUT_DIR / "all_categories_architecture_comparison.png"


def load_results(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find input CSV: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("The combined architecture comparison CSV is empty.")

    return rows


def make_label(row: dict) -> str:
    category = row["category"]
    model = row["model"]
    backbone = row["backbone"]
    n_features = row.get("n_features", "")

    if n_features and n_features not in {"default", ""}:
        return f"{category}\n{model}\n{backbone}\nn={n_features}"

    return f"{category}\n{model}\n{backbone}"


def main() -> None:
    rows = load_results(INPUT_CSV)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    labels = [make_label(row) for row in rows]
    auroc_values = [float(row["image_auroc"]) for row in rows]
    f1_values = [float(row["image_f1score"]) for row in rows]

    x_positions = range(len(labels))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(16, 7))

    ax.bar(
        [x - bar_width / 2 for x in x_positions],
        auroc_values,
        width=bar_width,
        label="Image AUROC",
    )

    ax.bar(
        [x + bar_width / 2 for x in x_positions],
        f1_values,
        width=bar_width,
        label="Image F1-score",
    )

    ax.set_title("Architecture Comparison Across MVTec AD Categories")
    ax.set_ylabel("Score")
    ax.set_ylim(0.70, 1.02)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=300)
    print(f"Saved figure to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()