# Final Project Evidence Checklist

## Purpose

This checklist summarises the main technical, experimental and documentation evidence produced for the risk-aware inspection dissertation project. It is intended to confirm that the repository contains sufficient evidence to support the methodology, results, discussion and implementation chapters of the final dissertation.

The project should be presented as a risk-aware industrial visual inspection prototype rather than only an anomaly detection experiment. The evidence below shows that the work includes anomaly detection, localisation, semantic interpretation, confidence fusion, risk-aware gating, quality disposition, audit logging and operator-facing review.

## 1. Repository and implementation status

| Evidence item                                 | Status   | Repository evidence                  |
| --------------------------------------------- | -------- | ------------------------------------ |
| Git repository created and maintained         | Complete | GitHub repository and commit history |
| README updated with current project scope     | Complete | `README.md`                          |
| Project structure documented                  | Complete | `README.md`                          |
| Dissertation writing support notes referenced | Complete | `README.md`                          |
| Working tree clean after latest changes       | Complete | `git status` output                  |

## 2. Core inspection pipeline

| Evidence item                                         | Status   | Repository evidence                                         |
| ----------------------------------------------------- | -------- | ----------------------------------------------------------- |
| Image ingestion and preprocessing                     | Complete | `src/risk_aware_inspection/ingestion.py`                    |
| Modular pipeline execution                            | Complete | `src/risk_aware_inspection/pipeline.py`                     |
| Swappable detector interface                          | Complete | `src/risk_aware_inspection/detectors/`                      |
| Statistical baseline detector                         | Complete | `src/risk_aware_inspection/detectors/simple_statistical.py` |
| Anomalib detector integration pathway                 | Complete | `src/risk_aware_inspection/detectors/anomalib_adapter.py`   |
| Output generation for CSV, JSONL and visual artefacts | Complete | `src/risk_aware_inspection/outputs.py`                      |

## 3. Anomaly detection architecture evidence

| Evidence item                                               | Status   | Repository evidence                                                                                 |
| ----------------------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| PatchCore implemented and evaluated                         | Complete | `scripts/train_patchcore_folder_mvtec.py`                                                           |
| PaDiM implemented and evaluated                             | Complete | `scripts/train_padim_folder_mvtec.py`                                                               |
| PatchCore backbone parameterisation                         | Complete | `--backbone` argument in PatchCore script                                                           |
| PatchCore coreset ratio parameterisation                    | Complete | `--coreset-sampling-ratio` argument                                                                 |
| PatchCore nearest-neighbour parameterisation                | Complete | `--num-neighbors` argument                                                                          |
| PaDiM backbone parameterisation                             | Complete | `--backbone` argument in PaDiM script                                                               |
| PaDiM retained feature parameterisation                     | Complete | `--n-features` argument                                                                             |
| Architecture comparison across bottle, capsule and hazelnut | Complete | `docs/experiments/architecture_comparison/`                                                         |
| Combined architecture comparison plot                       | Complete | `docs/figures/architecture_comparison/all_categories_architecture_comparison.png`                   |
| Architecture comparison interpretation                      | Complete | `docs/experiments/architecture_comparison/all_categories_architecture_comparison_interpretation.md` |

## 4. Selected anomaly detection architecture

| Evidence item                                                    | Status   | Dissertation relevance                                             |
| ---------------------------------------------------------------- | -------- | ------------------------------------------------------------------ |
| PatchCore and PaDiM both used as anomaly detection architectures | Complete | Supports methodological comparison                                 |
| PatchCore selected as preferred image-level detector             | Complete | Supported by architecture comparison results                       |
| PatchCore with ResNet50 selected as preferred configuration      | Complete | Strongest overall balance across bottle, capsule and hazelnut      |
| PaDiM retained as baseline and localisation reference            | Complete | Supports balanced evaluation rather than one-sided model selection |

The dissertation should state that both PatchCore and PaDiM use feature embeddings extracted from pre-trained convolutional neural network backbones, but they model normality differently. PatchCore uses a memory bank of representative normal patch embeddings and nearest-neighbour distance, while PaDiM models normal patch embeddings using multivariate Gaussian distributions and Mahalanobis distance.

## 5. Image-level results evidence

| Evidence item                                 | Status   | Repository evidence                                        |
| --------------------------------------------- | -------- | ---------------------------------------------------------- |
| Bottle integrated results                     | Complete | `README.md` and experiment notes                           |
| Capsule integrated results                    | Complete | `README.md` and experiment notes                           |
| Hazelnut integrated results                   | Complete | `README.md` and experiment notes                           |
| Accuracy, precision, recall and F1 discussion | Complete | `README.md`, architecture interpretation and results notes |
| Human-review rate included                    | Complete | `README.md` and experiment summaries                       |

## 6. Localisation evidence

| Evidence item                                | Status   | Repository evidence                                            |
| -------------------------------------------- | -------- | -------------------------------------------------------------- |
| Pixel-level anomaly localisation implemented | Complete | `src/risk_aware_inspection/localisation.py`                    |
| Heatmap thresholding implemented             | Complete | Localisation module and output artefacts                       |
| Morphological post-processing implemented    | Complete | Localisation module                                            |
| Connected-component localisation implemented | Complete | Localisation module                                            |
| IoU and Dice localisation evaluation         | Complete | Localisation evaluation results in README and experiment notes |
| Capsule localisation threshold sweep         | Complete | README and localisation threshold notes                        |
| Visual localisation artefacts generated      | Complete | `outputs/.../artefacts/*.png`                                  |

## 7. Semantic interpretation and governance evidence

| Evidence item                                       | Status   | Repository evidence                      |
| --------------------------------------------------- | -------- | ---------------------------------------- |
| Fixed defect taxonomy used                          | Complete | `src/risk_aware_inspection/semantics.py` |
| Unknown-label handling implemented                  | Complete | Semantic interpretation and review logic |
| Capsule semantic fallback rule implemented          | Complete | README and experiment notes              |
| Semantic fallback evaluated against review workload | Complete | README capsule semantic fallback section |

## 8. Risk-aware decision support evidence

| Evidence item                                 | Status   | Repository evidence                                           |
| --------------------------------------------- | -------- | ------------------------------------------------------------- |
| Risk Priority Matrix implemented              | Complete | `src/risk_aware_inspection/risk.py`                           |
| Confidence fusion implemented                 | Complete | `src/risk_aware_inspection/confidence.py`                     |
| Human-review gating implemented               | Complete | `src/risk_aware_inspection/gating.py`                         |
| Risk-governed quality disposition implemented | Complete | `src/risk_aware_inspection/qa_release.py`                     |
| False-positive release workflow demonstrated  | Complete | Dashboard test with record 650                                |
| QA release documentation created              | Complete | `docs/experiments/risk_governed_quality_disposition_layer.md` |

## 9. Database and audit evidence

| Evidence item                                      | Status   | Repository evidence                              |
| -------------------------------------------------- | -------- | ------------------------------------------------ |
| PostgreSQL audit database implemented              | Complete | `src/risk_aware_inspection/audit_db.py`          |
| Docker Compose PostgreSQL service configured       | Complete | `docker-compose.yml`                             |
| Database schema documented                         | Complete | `database/schema.sql`                            |
| Inspection records loaded into database            | Complete | PostgreSQL table contains 650 inspection records |
| Operator review table linked to inspection records | Complete | PostgreSQL foreign key relationship              |
| Database connection verified                       | Complete | Local connection test output                     |

## 10. API and dashboard evidence

| Evidence item                        | Status   | Repository evidence                                    |
| ------------------------------------ | -------- | ------------------------------------------------------ |
| FastAPI backend implemented          | Complete | `src/risk_aware_inspection/api_app.py`                 |
| Health endpoint tested               | Complete | `/health` returns database connection and record count |
| Summary endpoint tested              | Complete | `/summary` returns category/model review summaries     |
| Record endpoint implemented          | Complete | `/records` and `/records/{record_id}`                  |
| Operator review endpoint implemented | Complete | `/reviews`                                             |
| NiceGUI dashboard implemented        | Complete | `src/risk_aware_inspection/dashboard_app.py`           |
| Dashboard tested on local port 8090  | Complete | Browser test output                                    |
| Operator decision saving tested      | Complete | Review saved for inspection record 650                 |

## 11. Evidence-linked operator review panel

| Evidence item                                    | Status   | Repository evidence                                         |
| ------------------------------------------------ | -------- | ----------------------------------------------------------- |
| Dashboard links records to visual artefacts      | Complete | `src/risk_aware_inspection/dashboard_app.py`                |
| Annotated evidence displayed                     | Complete | Dashboard evidence panel                                    |
| Heatmap evidence displayed                       | Complete | Dashboard evidence panel                                    |
| Predicted mask evidence displayed                | Complete | Dashboard evidence panel                                    |
| Anomaly-map evidence displayed                   | Complete | Dashboard evidence panel                                    |
| Evidence panel documented                        | Complete | `docs/experiments/evidence_linked_operator_review_panel.md` |
| README updated with evidence-linked review panel | Complete | `README.md`                                                 |

## 12. Operational application figure evidence

| Evidence item                                              | Status   | Repository evidence                                                                      |
| ---------------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------- |
| Docker Desktop PostgreSQL service captured                 | Complete | `docs/figures/operational_application/docker_desktop_postgresql_service.png`             |
| Docker Compose PostgreSQL health status captured           | Complete | `docs/figures/operational_application/docker_postgresql_service.png`                     |
| FastAPI health-check response captured                     | Complete | `docs/figures/operational_application/fastapi_health_check.png`                          |
| FastAPI OpenAPI documentation captured                     | Complete | `docs/figures/operational_application/fastapi_openapi_documentation.png`                 |
| NiceGUI database summary captured                          | Complete | `docs/figures/operational_application/nicegui_database_summary.png`                      |
| Bottle selected-record and QA-decision evidence captured   | Complete | `docs/figures/operational_application/nicegui_selected_record_qa_decision_bottle.png`    |
| Capsule selected-record and QA-decision evidence captured  | Complete | `docs/figures/operational_application/nicegui_selected_record_qa_decision_capsule.png`   |
| Hazelnut selected-record and QA-decision evidence captured | Complete | `docs/figures/operational_application/nicegui_selected_record_qa_decision_hazelnut.png`  |
| Bottle evidence-linked review panel captured               | Complete | `docs/figures/operational_application/nicegui_evidence_linked_review_panel_bottle.png`   |
| Capsule evidence-linked review panel captured              | Complete | `docs/figures/operational_application/nicegui_evidence_linked_review_panel_capsule.png`  |
| Hazelnut evidence-linked review panel captured             | Complete | `docs/figures/operational_application/nicegui_evidence_linked_review_panel_hazelnut.png` |
| Operational figure placement and captions documented       | Complete | `docs/writing/operational_application_figure_index.md`                                   |

## 13. Dissertation writing support evidence

| Evidence item                                   | Status   | Repository evidence                                                                                 |
| ----------------------------------------------- | -------- | --------------------------------------------------------------------------------------------------- |
| Methodology alignment note created              | Complete | `docs/writing/methodology_chapter_alignment_note.md`                                                |
| Results and discussion placement note created   | Complete | `docs/writing/results_and_discussion_placement_note.md`                                             |
| Architecture comparison interpretation created  | Complete | `docs/experiments/architecture_comparison/all_categories_architecture_comparison_interpretation.md` |
| Evidence-linked dashboard documentation created | Complete | `docs/experiments/evidence_linked_operator_review_panel.md`                                         |
| README references writing support notes         | Complete | `README.md`                                                                                         |

## 14. Current dissertation readiness assessment

The project is in a strong position for dissertation write-up. It contains evidence for:

* model architecture comparison;
* model selection justification;
* image-level anomaly detection results;
* localisation evaluation;
* semantic interpretation;
* risk-aware decision support;
* human-review gating;
* quality disposition;
* audit logging;
* API-based access;
* operator dashboard interaction;
* evidence-linked review.

The project should be described as a prototype-level risk-aware visual inspection system. It is not a fully deployed production-line controller, because it does not physically control a conveyor, reject gate or robotic sorting mechanism. However, it demonstrates the software-side decision logic, traceability and operator workflow that could be connected to a manufacturing execution system or industrial controller after further validation.

## 15. Revised remaining actions before final dissertation writing

The major technical implementation and evidence-capture activities are complete. The remaining work should focus on dissertation consolidation:

1. verify that all tables in the README and experiment notes match the latest CSV results;
2. assign dissertation figure and table numbers to the selected results;
3. prepare final captions and in-text references for the architecture comparison, localisation results and operational application figures;
4. decide which supplementary figures should be placed in the dissertation appendix;
5. begin drafting the methodology, results and discussion chapters using the repository writing-support notes;
6. conduct a final reference, formatting and technical-consistency review before submission.
