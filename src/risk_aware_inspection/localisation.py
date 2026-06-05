from __future__ import annotations

import cv2
import numpy as np

from risk_aware_inspection.models import BoundingBox, LocalisationResult
from risk_aware_inspection.utils import clamp


def _odd_kernel(value: int) -> int:
    value = max(1, int(value))
    return value if value % 2 == 1 else value + 1


def localise_anomalies(heatmap: np.ndarray, cfg: dict) -> tuple[LocalisationResult, np.ndarray]:
    """Convert a continuous anomaly heatmap into a refined binary mask and bounding boxes."""
    heatmap = np.clip(heatmap.astype(np.float32), 0.0, 1.0)
    blur_kernel = _odd_kernel(int(cfg.get("gaussian_blur_kernel", 5)))
    smooth = cv2.GaussianBlur(heatmap, (blur_kernel, blur_kernel), 0)

    threshold = float(cfg.get("heatmap_threshold", 0.42))
    binary = (smooth >= threshold).astype(np.uint8) * 255

    kernel_size = _odd_kernel(int(cfg.get("morph_kernel_size", 5)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    opened = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        kernel,
        iterations=int(cfg.get("morph_open_iterations", 1)),
    )
    mask = cv2.morphologyEx(
        opened,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=int(cfg.get("morph_close_iterations", 2)),
    )

    num_labels, labels, stats, _centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    h, w = heatmap.shape[:2]
    image_area = float(h * w)
    min_area_px = int(cfg.get("min_component_area_px", 35))
    min_area_ratio = float(cfg.get("min_component_area_ratio", 0.0006))
    boxes: list[BoundingBox] = []

    for component_id in range(1, num_labels):
        x, y, bw, bh, area = stats[component_id]
        area = int(area)
        area_ratio = area / image_area
        if area < min_area_px or area_ratio < min_area_ratio:
            continue
        component_mask = labels == component_id
        component_heat = heatmap[component_mask]
        boxes.append(
            BoundingBox(
                x=int(x),
                y=int(y),
                w=int(bw),
                h=int(bh),
                area_px=area,
                area_ratio=float(area_ratio),
                mean_heat=float(component_heat.mean()) if component_heat.size else 0.0,
                max_heat=float(component_heat.max()) if component_heat.size else 0.0,
            )
        )

    boxes = sorted(boxes, key=lambda b: (b.mean_heat * b.area_px), reverse=True)
    boxes = boxes[: int(cfg.get("max_boxes", 8))]

    if not boxes:
        result = LocalisationResult(boxes=[], confidence=0.0, mask_area_ratio=0.0, component_count=0)
        return result, mask

    selected_area = sum(b.area_px for b in boxes)
    selected_area_ratio = selected_area / image_area
    largest_area = max(b.area_px for b in boxes)
    coherence = largest_area / max(1, selected_area)
    mean_box_heat = float(np.mean([b.mean_heat for b in boxes]))
    component_penalty = 1.0 / (1.0 + 0.12 * max(0, len(boxes) - 1))
    coverage_quality = clamp(selected_area_ratio / 0.08) if selected_area_ratio < 0.08 else 0.8
    confidence = clamp(0.45 * mean_box_heat + 0.35 * coherence + 0.20 * component_penalty + 0.05 * coverage_quality)

    result = LocalisationResult(
        boxes=boxes,
        confidence=confidence,
        mask_area_ratio=float(selected_area_ratio),
        component_count=len(boxes),
    )
    return result, mask
