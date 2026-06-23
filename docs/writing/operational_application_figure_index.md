# Operational Application Figure Index

## Purpose

This note identifies the operational application figures captured from the risk-aware inspection prototype and records their intended use in the final dissertation. The figures provide visual evidence of the PostgreSQL audit service, FastAPI backend, NiceGUI operator dashboard, risk-governed quality disposition and evidence-linked operator review workflow.

The complete set of screenshots is stored in:

`docs/figures/operational_application/`

Not every screenshot needs to appear in the main dissertation chapter. Representative figures should be used in the main results and discussion chapter, while additional category-specific examples may be placed in an appendix.

## 1. PostgreSQL and Docker evidence

### `docker_desktop_postgresql_service.png`

**Suggested caption:**
*Docker Desktop showing the running PostgreSQL container used by the risk-aware inspection prototype.*

**Dissertation placement:**
Operational application layer or implementation chapter.

**Purpose:**
This figure provides visual confirmation that the PostgreSQL audit database was deployed as a containerised service. It supports discussion of reproducibility, service isolation and local deployment through Docker Compose.

### `docker_postgresql_service.png`

**Suggested caption:**
*Docker Compose service status confirming that the PostgreSQL audit database is running and healthy.*

**Dissertation placement:**
Operational validation subsection or appendix.

**Purpose:**
This terminal-based figure provides more precise technical evidence than the Docker Desktop screenshot because it shows the container name, PostgreSQL image, mapped host port and service health status.

For the main dissertation, the terminal-based service-status figure is the stronger technical figure. The Docker Desktop screenshot may be retained as supplementary evidence.

## 2. FastAPI backend evidence

### `fastapi_health_check.png`

**Suggested caption:**
*FastAPI health-check response confirming successful connection to the PostgreSQL audit database and the availability of 650 inspection records.*

**Dissertation placement:**
FastAPI backend validation subsection.

**Purpose:**
This figure demonstrates that the API service was running successfully and communicating with the PostgreSQL database. The response confirms both database connectivity and the number of inspection records available to the operational application.

### `fastapi_openapi_documentation.png`

**Suggested caption:**
*Automatically generated OpenAPI documentation for the risk-aware inspection backend.*

**Dissertation placement:**
Operational application layer or system implementation chapter.

**Purpose:**
The figure shows the implemented API endpoints for health checking, record retrieval, quality-assurance decision support, operator review submission and inspection summary retrieval. It demonstrates that the backend exposes the inspection workflow through a structured service interface.

## 3. NiceGUI database summary

### `nicegui_database_summary.png`

**Suggested caption:**
*NiceGUI operational dashboard showing the inspection-record summary by product category and anomaly detection model.*

**Dissertation placement:**
Results and discussion section covering the operator dashboard.

**Purpose:**
This figure demonstrates the dashboard connection to the PostgreSQL audit database. It shows the total number of inspection records and the number requiring operator review for PatchCore and PaDiM across bottle, capsule and hazelnut.

The figure also provides operational evidence that detector selection affects review workload. PatchCore produces fewer review-required cases than PaDiM across the evaluated categories.

## 4. Selected-record and quality-disposition evidence

### `nicegui_selected_record_qa_decision_bottle.png`

**Suggested caption:**
*Bottle inspection record and corresponding risk-governed quality disposition displayed in the operator dashboard.*

### `nicegui_selected_record_qa_decision_capsule.png`

**Suggested caption:**
*Capsule inspection record showing the quality-assurance recommendation and latest operator review decision.*

### `nicegui_selected_record_qa_decision_hazelnut.png`

**Suggested caption:**
*Hazelnut inspection record and risk-governed quality disposition presented to the operator.*

**Dissertation placement:**
Risk-aware decision support and quality-disposition subsection.

**Purpose:**
These figures demonstrate how database records are converted into operator-facing quality-control recommendations. They show the selected record, anomaly information, semantic label, risk class, confidence, review requirement, quality-assurance action and latest operator decision.

The capsule example is recommended for the main dissertation because it demonstrates the false-positive release workflow clearly. The system initially routed the case for review because of uncertainty, after which the operator marked it as safe to release. The resulting disposition was `RELEASE_AFTER_REVIEW`.

The bottle and hazelnut examples can be included in an appendix to demonstrate that the workflow operates across multiple product categories.

## 5. Evidence-linked operator review panels

### `nicegui_evidence_linked_review_panel_bottle.png`

**Suggested caption:**
*Evidence-linked operator review panel for a bottle inspection record.*

### `nicegui_evidence_linked_review_panel_capsule.png`

**Suggested caption:**
*Evidence-linked operator review panel showing annotated detection, heatmap, predicted mask and anomaly-map evidence for a capsule inspection record.*

### `nicegui_evidence_linked_review_panel_hazelnut.png`

**Suggested caption:**
*Evidence-linked operator review panel for a hazelnut inspection record.*

**Dissertation placement:**
Evidence-linked human review subsection within the results and discussion chapter.

**Purpose:**
These figures demonstrate the connection between an inspection record and its associated visual evidence. The dashboard displays the annotated inspection result, heatmap overlay, predicted anomaly mask and anomaly map before the operator records a decision.

This feature provides a traceable link between:

1. the original inspection record;
2. anomaly detection and localisation evidence;
3. the operator’s interpretation;
4. the saved review decision;
5. the final quality disposition.

The capsule evidence panel is recommended as the representative main-text figure because the localisation evidence is visually clear and corresponds to the documented false-positive release case. The bottle and hazelnut panels should be retained as supporting evidence or appendix figures.

## 6. Recommended figures for the main dissertation

The following figures provide the strongest and least repetitive operational evidence for the main dissertation:

1. `fastapi_openapi_documentation.png`;
2. `fastapi_health_check.png`;
3. `nicegui_database_summary.png`;
4. `nicegui_selected_record_qa_decision_capsule.png`;
5. `nicegui_evidence_linked_review_panel_capsule.png`;
6. `docker_postgresql_service.png`.

The remaining bottle, hazelnut and Docker Desktop figures can be placed in an appendix or retained in the repository as supplementary implementation evidence.

## 7. Interpretation guidance

The figures should not be described as screenshots of software alone. They should be interpreted as evidence that the anomaly detection experiments were integrated into an operational decision-support workflow.

The PostgreSQL figures demonstrate persistence and traceability. The FastAPI figures demonstrate structured backend access. The NiceGUI summary demonstrates database-driven operational monitoring. The selected-record figures demonstrate risk-aware quality disposition, while the evidence-linked panels demonstrate that human decisions are supported by visual anomaly and localisation evidence.

Together, these figures show that the project extends beyond offline anomaly detection evaluation and provides a prototype implementation of a traceable, human-in-the-loop industrial inspection workflow.
