from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command: list[str]) -> None:
    print("\nRunning command:")
    print(" ".join(command))
    result = subprocess.run(command, check=False)

    if result.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {result.returncode}")


def find_checkpoint(output_dir: Path) -> Path:
    checkpoints = list(output_dir.rglob("*.ckpt"))

    if not checkpoints:
        raise FileNotFoundError(f"No checkpoint found inside {output_dir}")

    latest_candidates = [path for path in checkpoints if "latest" in str(path).lower()]

    if latest_candidates:
        return latest_candidates[0]

    return checkpoints[0]


def run_full_experiment(
    model: str,
    category: str,
    dataset_root: Path,
    output_root: Path,
    config_path: Path,
) -> None:
    category_root = dataset_root / category

    if not category_root.exists():
        raise FileNotFoundError(f"Category folder does not exist: {category_root}")

    model = model.lower()

    if model not in {"patchcore", "padim"}:
        raise ValueError("model must be either 'patchcore' or 'padim'")

    train_script = {
        "patchcore": "scripts/train_patchcore_folder_mvtec.py",
        "padim": "scripts/train_padim_folder_mvtec.py",
    }[model]

    anomalib_output = output_root / f"anomalib_{model}_folder_{category}"
    prediction_output = output_root / f"{model}_{category}_predictions"
    risk_output = output_root / f"risk_{model}_{category}"

    print("=" * 80)
    print(f"Running full MVTec experiment")
    print(f"Model: {model}")
    print(f"Category: {category}")
    print(f"Category root: {category_root}")
    print(f"Output root: {output_root}")
    print("=" * 80)

    run_command(
        [
            sys.executable,
            train_script,
            "--category-root",
            str(category_root),
            "--output",
            str(anomalib_output),
        ]
    )

    checkpoint = find_checkpoint(anomalib_output)
    print(f"\nCheckpoint found: {checkpoint}")

    run_command(
        [
            sys.executable,
            "scripts/export_anomalib_predictions.py",
            "--model",
            model,
            "--category-root",
            str(category_root),
            "--checkpoint",
            str(checkpoint),
            "--output",
            str(prediction_output),
        ]
    )

    run_command(
        [
            sys.executable,
            "scripts/run_risk_pipeline_from_anomalib_export.py",
            "--predictions",
            str(prediction_output / "predictions.csv"),
            "--config",
            str(config_path),
            "--output",
            str(risk_output),
        ]
    )

    run_command(
        [
            sys.executable,
            "scripts/evaluate_mvtec_run.py",
            "--results",
            str(risk_output / "results.csv"),
            "--output",
            str(risk_output / "evaluation"),
        ]
    )

    print("\nFull experiment complete.")
    print(f"Anomalib output: {anomalib_output}")
    print(f"Prediction output: {prediction_output}")
    print(f"Risk-aware output: {risk_output}")
    print(f"Evaluation output: {risk_output / 'evaluation'}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run full Anomalib + risk-aware MVTec experiment."
    )

    parser.add_argument(
        "--model",
        required=True,
        choices=["patchcore", "padim"],
        help="Model to run.",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="MVTec category, e.g. bottle, hazelnut, cable, capsule.",
    )

    parser.add_argument(
        "--dataset-root",
        required=True,
        type=Path,
        help="Path to extracted MVTec AD dataset root.",
    )

    parser.add_argument(
        "--output-root",
        default=Path("outputs"),
        type=Path,
        help="Root output folder.",
    )

    parser.add_argument(
        "--config",
        default=Path("config/pipeline.yaml"),
        type=Path,
        help="Risk-aware pipeline config file.",
    )

    args = parser.parse_args()

    run_full_experiment(
        model=args.model,
        category=args.category,
        dataset_root=args.dataset_root,
        output_root=args.output_root,
        config_path=args.config,
    )


if __name__ == "__main__":
    main()