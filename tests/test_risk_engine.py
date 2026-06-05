from risk_aware_inspection.config import load_config
from risk_aware_inspection.models import BoundingBox
from risk_aware_inspection.risk import RiskPriorityMatrix


def test_rpm_returns_review_required_for_missing_tuple(tmp_path):
    cfg = load_config("config/pipeline.yaml")
    cfg["rpm_table"] = []
    engine = RiskPriorityMatrix(cfg)
    result = engine.evaluate(label="fracture", boxes=[], fused_confidence=0.9)
    assert result.risk_class == "Review Required"
    assert not result.mapped


def test_rpm_maps_high_severity_region():
    cfg = load_config("config/pipeline.yaml")
    engine = RiskPriorityMatrix(cfg)
    box = BoundingBox(x=0, y=0, w=80, h=80, area_px=6400, area_ratio=0.10, mean_heat=0.7, max_heat=0.9)
    result = engine.evaluate(label="fracture", boxes=[box], fused_confidence=0.4)
    assert result.severity == "S4"
    assert result.detection == "D3"
    assert result.risk_class in {"High", "Critical"}
