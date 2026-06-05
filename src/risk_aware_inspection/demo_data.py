from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from risk_aware_inspection.utils import ensure_dir


def _base_plate(seed: int, size: int = 256) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.full((size, size, 3), 160, dtype=np.uint8)
    noise = rng.normal(0, 4, base.shape).astype(np.int16)
    image = np.clip(base.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    # Mild texture lines make the reference less trivial.
    for y in range(20, size, 32):
        cv2.line(image, (8, y), (size - 8, y + rng.integers(-2, 3)), (150, 150, 150), 1)
    cv2.rectangle(image, (18, 18), (size - 18, size - 18), (172, 172, 172), 2)
    return image


def create_demo_dataset(output_dir: str | Path, n_normal: int = 12) -> None:
    """Create synthetic normal/anomalous images so the prototype can run immediately."""
    output_dir = Path(output_dir)
    normal_dir = ensure_dir(output_dir / "normal")
    test_dir = ensure_dir(output_dir / "test")

    for i in range(n_normal):
        cv2.imwrite(str(normal_dir / f"normal_{i:02d}.png"), _base_plate(seed=i))

    # Normal test image.
    cv2.imwrite(str(test_dir / "test_normal_like.png"), _base_plate(seed=101))

    # Scratch: a thin elongated mark.
    scratch = _base_plate(seed=102)
    cv2.line(scratch, (45, 118), (212, 132), (55, 55, 55), 3)
    cv2.imwrite(str(test_dir / "test_scratch.png"), scratch)

    # Fracture: darker irregular line.
    fracture = _base_plate(seed=103)
    pts = np.array([[60, 70], [92, 89], [130, 84], [170, 113], [205, 121]], np.int32)
    cv2.polylines(fracture, [pts], False, (25, 25, 25), 4)
    cv2.imwrite(str(test_dir / "test_fracture.png"), fracture)

    # Contamination: coloured blob.
    contamination = _base_plate(seed=104)
    cv2.circle(contamination, (165, 94), 22, (40, 110, 190), -1)
    cv2.imwrite(str(test_dir / "test_contamination.png"), contamination)

    # Dent/stain: wider dark patch.
    dent = _base_plate(seed=105)
    cv2.ellipse(dent, (125, 160), (32, 22), 0, 0, 360, (95, 95, 95), -1)
    cv2.imwrite(str(test_dir / "test_dent.png"), dent)
