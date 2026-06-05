from __future__ import annotations

"""Optional FastAPI entry point for later dissertation development.

The CLI is the recommended minimum viable prototype because it is easier to reproduce in VS Code
and during experiments. This file shows how the pipeline can later be wrapped by a service layer
without changing the core inspection logic.
"""

from pathlib import Path

from risk_aware_inspection.config import load_config
from risk_aware_inspection.detectors.simple_statistical import StatisticalReferenceDetector
from risk_aware_inspection.pipeline import RiskAwareInspectionPipeline
from risk_aware_inspection.semantics import RuleBasedSemanticLabeler


def build_pipeline(config_path: str | Path, model_path: str | Path, output_dir: str | Path) -> RiskAwareInspectionPipeline:
    config = load_config(config_path)
    detector = StatisticalReferenceDetector.load(model_path, config["detector"])
    labeler = RuleBasedSemanticLabeler(config["taxonomy"], config["semantic_rules"])
    return RiskAwareInspectionPipeline(
        config=config,
        detector=detector,
        semantic_labeler=labeler,
        output_dir=output_dir,
    )


# Example FastAPI implementation outline:
#
# from fastapi import FastAPI, UploadFile
# app = FastAPI(title="Risk-Aware Inspection API")
# pipeline = build_pipeline("config/pipeline.yaml", "outputs/simple_reference_model.npz", "outputs/api")
#
# @app.post("/inspect")
# async def inspect_image(file: UploadFile):
#     temporary_path = Path("outputs/api/uploads") / file.filename
#     temporary_path.parent.mkdir(parents=True, exist_ok=True)
#     temporary_path.write_bytes(await file.read())
#     record = pipeline.process_image(temporary_path)
#     return record.to_dict()
