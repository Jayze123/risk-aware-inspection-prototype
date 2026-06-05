from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

SUPPORTED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}


def iter_image_paths(input_path: str | Path) -> Iterable[Path]:
    """Yield image files from either a single file path or a directory."""
    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Input path not found: {path}")
    if path.is_file():
        if path.suffix.lower() not in SUPPORTED_IMAGE_SUFFIXES:
            raise ValueError(f"Unsupported image type: {path.suffix}")
        yield path
        return
    for child in sorted(path.rglob("*")):
        if child.is_file() and child.suffix.lower() in SUPPORTED_IMAGE_SUFFIXES:
            yield child


def load_image_bgr(path: str | Path) -> np.ndarray:
    """Read an image in OpenCV BGR format."""
    path = Path(path)
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"Could not read image: {path}")
    return image


def preprocess_image(image_bgr: np.ndarray, image_cfg: dict) -> np.ndarray:
    """Resize and optionally apply lighting correction using CLAHE on the luminance channel."""
    target_w, target_h = image_cfg.get("target_size", [256, 256])
    resized = cv2.resize(image_bgr, (int(target_w), int(target_h)), interpolation=cv2.INTER_AREA)

    if image_cfg.get("apply_clahe", False):
        lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        clip_limit = float(image_cfg.get("clahe_clip_limit", 2.0))
        tile_grid_size = tuple(image_cfg.get("clahe_tile_grid_size", [8, 8]))
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        corrected_l = clahe.apply(l_channel)
        lab_corrected = cv2.merge([corrected_l, a_channel, b_channel])
        return cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2BGR)

    return resized


def to_grayscale_float(image_bgr: np.ndarray) -> np.ndarray:
    """Convert a BGR image to a float grayscale array in [0, 1]."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    return gray.astype(np.float32) / 255.0
