from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a required configuration value is missing or invalid."""


def load_config(config_path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file used to control the full pipeline."""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    validate_config(config)
    return config


def validate_config(config: dict[str, Any]) -> None:
    required_sections = [
        "image",
        "detector",
        "localisation",
        "taxonomy",
        "risk_inputs",
        "confidence_fusion",
        "gating",
        "actions",
        "rpm_table",
    ]
    missing = [section for section in required_sections if section not in config]
    if missing:
        raise ConfigError(f"Missing configuration sections: {missing}")

    allowed_labels = config["taxonomy"].get("allowed_labels", [])
    if not allowed_labels or "unknown" not in allowed_labels:
        raise ConfigError("taxonomy.allowed_labels must include at least one label and the 'unknown' label.")

    for row in config.get("rpm_table", []):
        for key in ("severity", "occurrence", "detection", "risk_class"):
            if key not in row:
                raise ConfigError(f"RPM table row is missing '{key}': {row}")
