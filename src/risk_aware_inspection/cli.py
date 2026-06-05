from __future__ import annotations

import argparse
import json
from pathlib import Path

from risk_aware_inspection.config import load_config
from risk_aware_inspection.demo_data import create_demo_dataset
from risk_aware_inspection.detectors.simple_statistical import StatisticalReferenceDetector
from risk_aware_inspection.ingestion import iter_image_paths
from risk_aware_inspection.outputs import save_batch_csv
from risk_aware_inspection.pipeline import RiskAwareInspectionPipeline
from risk_aware_inspection.semantics import RuleBasedSemanticLabeler
from risk_aware_inspection.utils import ensure_dir


def build_detector(config: dict, model_path: str | Path | None = None) -> StatisticalReferenceDetector:
    detector = StatisticalReferenceDetector(config["detector"])
    if model_path is not None:
        detector = StatisticalReferenceDetector.load(model_path, config["detector"])
    return detector


def command_make_demo(args: argparse.Namespace) -> None:
    create_demo_dataset(args.output)
    print(f"Demo dataset created at: {args.output}")


def command_calibrate(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    detector = build_detector(config)
    detector.fit_from_directory(args.normal_dir, config["image"])
    detector.save(args.model)
    print(json.dumps({"model": str(args.model), "threshold": detector.threshold}, indent=2))


def command_inspect(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    ensure_dir(args.output)

    detector = build_detector(config, args.model)

    original_threshold = float(detector.threshold)

    if args.threshold_override is not None and args.threshold_multiplier is not None:
        raise ValueError(
            "Use either --threshold-override or --threshold-multiplier, not both."
        )

    if args.threshold_override is not None:
        detector.threshold = float(args.threshold_override)
        threshold_mode = "absolute_override"
    elif args.threshold_multiplier is not None:
        detector.threshold = float(detector.threshold) * float(args.threshold_multiplier)
        threshold_mode = "multiplier_override"
    else:
        threshold_mode = "calibrated_model_threshold"

    effective_threshold = float(detector.threshold)

    metadata = {
        "input": str(args.input),
        "config": str(args.config),
        "model": str(args.model),
        "output": str(args.output),
        "original_model_threshold": original_threshold,
        "effective_threshold": effective_threshold,
        "threshold_mode": threshold_mode,
        "threshold_override": args.threshold_override,
        "threshold_multiplier": args.threshold_multiplier,
    }

    metadata_path = Path(args.output) / "run_metadata.json"
    with metadata_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(json.dumps(metadata, indent=2))

    labeler = RuleBasedSemanticLabeler(config["taxonomy"], config["semantic_rules"])
    pipeline = RiskAwareInspectionPipeline(
        config=config,
        detector=detector,
        semantic_labeler=labeler,
        output_dir=args.output,
    )

    records = []
    for image_path in iter_image_paths(args.input):
        record = pipeline.process_image(image_path)
        records.append(record)
        print(
            json.dumps(
                {
                    "image": str(image_path),
                    "score": record.detection["image_score"],
                    "threshold": record.detection["threshold"],
                    "anomalous": record.detection["is_anomalous"],
                    "label": record.semantic["label"],
                    "risk_class": record.risk["risk_class"],
                    "requires_review": record.review["requires_review"],
                    "review_reasons": record.review["reasons"],
                },
                indent=2,
            )
        )

    csv_path = save_batch_csv(records, args.output)
    print(f"Saved {len(records)} records to {csv_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Risk-aware industrial inspection prototype: detect, localise, label, risk-score and gate for human review."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    demo = sub.add_parser("make-demo", help="Create synthetic demo images for a quick local run.")
    demo.add_argument("--output", default="data/demo", help="Output directory for demo images.")
    demo.set_defaults(func=command_make_demo)

    calibrate = sub.add_parser("calibrate", help="Fit the simple statistical reference detector on normal images.")
    calibrate.add_argument("--normal-dir", required=True, help="Directory containing normal reference images.")
    calibrate.add_argument("--config", default="config/pipeline.yaml", help="Path to pipeline YAML configuration.")
    calibrate.add_argument("--model", default="outputs/simple_reference_model.npz", help="Path to save calibrated detector model.")
    calibrate.set_defaults(func=command_calibrate)

    inspect = sub.add_parser("inspect", help="Run the full risk-aware inspection pipeline.")
    inspect.add_argument("--input", required=True, help="Image file or directory to inspect.")
    inspect.add_argument("--config", default="config/pipeline.yaml", help="Path to pipeline YAML configuration.")
    inspect.add_argument("--model", required=True, help="Calibrated detector model path.")
    inspect.add_argument("--output", default="outputs/run", help="Output directory for records and visual artefacts.")

    inspect.add_argument(
        "--threshold-override",
        type=float,
        default=None,
        help="Use an absolute anomaly threshold instead of the calibrated model threshold.",
    )

    inspect.add_argument(
        "--threshold-multiplier",
        type=float,
        default=None,
        help="Multiply the calibrated model threshold by this value at inspection time.",
    )

    inspect.set_defaults(func=command_inspect)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
