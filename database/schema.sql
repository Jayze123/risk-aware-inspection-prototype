-- PostgreSQL audit schema for the risk-aware inspection prototype.
-- This schema stores automated inspection outputs and optional operator review decisions.

CREATE TABLE IF NOT EXISTS inspection_records (
    id BIGSERIAL PRIMARY KEY,

    image_id TEXT NOT NULL,
    image_path TEXT,
    category TEXT,
    model_name TEXT NOT NULL,

    anomaly_score DOUBLE PRECISION,
    anomaly_threshold DOUBLE PRECISION,
    is_anomalous BOOLEAN,

    semantic_label TEXT,
    semantic_confidence DOUBLE PRECISION,

    risk_class TEXT,
    fused_confidence DOUBLE PRECISION,
    requires_review BOOLEAN,

    review_reasons TEXT,
    result_payload JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS operator_reviews (
    id BIGSERIAL PRIMARY KEY,

    inspection_record_id BIGINT NOT NULL REFERENCES inspection_records(id) ON DELETE CASCADE,

    operator_decision TEXT NOT NULL,
    operator_note TEXT,
    reviewed_by TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inspection_records_image_id
    ON inspection_records(image_id);

CREATE INDEX IF NOT EXISTS idx_inspection_records_model_name
    ON inspection_records(model_name);

CREATE INDEX IF NOT EXISTS idx_inspection_records_category
    ON inspection_records(category);

CREATE INDEX IF NOT EXISTS idx_inspection_records_requires_review
    ON inspection_records(requires_review);

CREATE INDEX IF NOT EXISTS idx_inspection_records_risk_class
    ON inspection_records(risk_class);

CREATE INDEX IF NOT EXISTS idx_operator_reviews_inspection_record_id
    ON operator_reviews(inspection_record_id);