from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    """Clamp a numeric value into a bounded range."""
    return max(low, min(high, float(value)))


def ensure_dir(path: str | Path) -> Path:
    """Create a directory if it does not already exist and return it as a Path."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sha256_file(path: str | Path, block_size: int = 65536) -> str:
    """Return a SHA256 checksum for audit logging and reproducibility."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


def flatten_dict(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested dictionaries for CSV-friendly records."""
    out: dict[str, Any] = {}
    for key, value in d.items():
        new_key = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            out.update(flatten_dict(value, new_key))
        else:
            out[new_key] = value
    return out
