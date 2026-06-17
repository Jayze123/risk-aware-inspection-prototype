from pathlib import Path
import csv
import matplotlib.pyplot as plt


INPUT_CSV = Path("docs/experiments/architecture_comparison/capsule_architecture_comparison_summary.csv")
OUTPUT_DIR = Path("docs/figures/architecture_comparison")
OUTPUT_PATH = OUTPUT_DIR / "capsule_architecture_comparison.png"


def load_results(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Could not find input CSV: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("The architecture comparison CSV is empty.")

    return rows


def main() -> None:
    rows = load_results(INPUT_CSV)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    labels = []
    auroc_values = []
    f1_values = []

    for row in rows:
        model = row["model"]
        backbone = row["backbone"]
        n_features = row.get("n_features", "")

        if n_features and n_features != "default":
            label = f"{model}\n{backbone}\nn={n_features}"
        else:
            label = f"{model}\n{backbone}"

        labels.append(label)
        auroc_values.append(float(row["image_auroc"]))
        f1_values.append(float(row["image_f1score"]))

    x_positions = range(len(labels))
    bar_width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))

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

    ax.set_title("Capsule Architecture Comparison")
    ax.set_ylabel("Score")
    ax.set_ylim(0.85, 1.01)
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    fig.tight_layout()
    fig.savefig(OUTPUT_PATH, dpi=300)
    print(f"Saved figure to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()