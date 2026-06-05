from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import pandas as pd

from risk_aware_inspection.models import LocalisationResult, PipelineRecord
from risk_aware_inspection.utils import ensure_dir, flatten_dict


def save_visual_artefacts(
    *,
    image_bgr: np.ndarray,
    heatmap: np.ndarray,
    mask: np.ndarray,
    localisation: LocalisationResult,
    image_id: str,
    output_dir: str | Path,
) -> dict[str, str]:
    """Save heatmap overlay, binary mask and box-annotated image for audit review."""
    artefact_dir = ensure_dir(Path(output_dir) / "artefacts")
    heat_uint8 = np.uint8(np.clip(heatmap, 0.0, 1.0) * 255)
    heat_colour = cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(image_bgr, 0.65, heat_colour, 0.35, 0)
    annotated = overlay.copy()

    for box in localisation.boxes:
        cv2.rectangle(annotated, (box.x, box.y), (box.x2, box.y2), (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"{box.mean_heat:.2f}",
            (box.x, max(0, box.y - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 255, 0),
            1,
            cv2.LINE_AA,
        )

    paths = {
        "heatmap_overlay": str(artefact_dir / f"{image_id}_heatmap_overlay.png"),
        "mask": str(artefact_dir / f"{image_id}_mask.png"),
        "annotated": str(artefact_dir / f"{image_id}_annotated.png"),
    }
    cv2.imwrite(paths["heatmap_overlay"], overlay)
    cv2.imwrite(paths["mask"], mask)
    cv2.imwrite(paths["annotated"], annotated)
    return paths


def append_jsonl(record: PipelineRecord, output_dir: str | Path) -> None:
    output_dir = ensure_dir(output_dir)
    with (Path(output_dir) / "results.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def save_batch_csv(records: Iterable[PipelineRecord], output_dir: str | Path) -> Path:
    output_dir = ensure_dir(output_dir)
    rows = [flatten_dict(record.to_dict()) for record in records]
    df = pd.DataFrame(rows)
    csv_path = Path(output_dir) / "results.csv"
    df.to_csv(csv_path, index=False)
    return csv_path
