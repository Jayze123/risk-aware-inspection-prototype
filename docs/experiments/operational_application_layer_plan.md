# Operational Application Layer Plan

## Purpose

This note defines the next implementation stage for the risk-aware inspection prototype. The research pipeline already supports anomaly detection, localisation, semantic interpretation, risk mapping, confidence fusion, review gating and result export. The remaining technical gap is the operational application layer, which is needed to demonstrate how the pipeline could be used by an operator in a deployable inspection workflow.

## Current status

The current implementation has completed the main experimental pipeline. PatchCore and PaDiM have been evaluated on selected MVTec AD categories, including bottle, hazelnut and capsule. The system produces image-level anomaly decisions, anomaly maps, localisation masks, semantic labels, risk classes, confidence values, review decisions and audit-style CSV/JSON outputs.

The next stage is to wrap these outputs in a lightweight application layer so that the prototype demonstrates a realistic inspection workflow rather than only command-line experimentation.

## Minimum viable operational layer

The operational layer will include four main components:

1. FastAPI backend for inspection requests and result retrieval.
2. NiceGUI dashboard for operator interaction.
3. PostgreSQL audit database for storing inspection results and review decisions.
4. Docker/Docker Compose configuration for reproducible system execution.

The aim is not to build a full industrial production system. The aim is to provide a working deployment prototype that supports the dissertation objective of demonstrating a risk-aware, review-aware and auditable visual inspection pipeline.

## FastAPI backend

The FastAPI backend will provide a simple service layer around the existing pipeline. The first version should include endpoints for:

* checking system health;
* listing available inspection results;
* running or loading an inspection result;
* returning a single inspection record;
* saving an operator review decision.

The backend should reuse the existing pipeline outputs where possible, rather than retraining or rerunning heavy anomaly detection models every time. This keeps the application lightweight and suitable for dissertation demonstration.

## NiceGUI operator dashboard

The NiceGUI interface will provide a simple operator-facing view. The dashboard should allow the operator to:

* view inspection records;
* see the original image, anomaly map and predicted mask where available;
* view the anomaly score, semantic label, confidence value and risk class;
* identify whether human review is required;
* record a review decision such as accepted, rejected or needs further inspection.

This dashboard will demonstrate the human-in-the-loop part of the system and show how the risk-aware output can support decision-making.

## PostgreSQL audit logging

A PostgreSQL database will be used to store structured inspection records. The audit table should include fields such as:

* record ID;
* image ID;
* image path;
* model name;
* anomaly score;
* anomaly decision;
* semantic label;
* risk class;
* confidence value;
* review requirement;
* operator decision;
* review note;
* created timestamp;
* updated timestamp.

This will support traceability by keeping a persistent record of automated predictions and operator decisions.

## Docker and reproducibility

Docker will be used to make the application easier to reproduce. Docker Compose should define at least two services:

* an application service for the FastAPI/NiceGUI prototype;
* a PostgreSQL database service.

The Docker setup does not need to include GPU training. The first version can focus on serving existing results and demonstrating the operational workflow. This is sufficient for showing system integration and reproducibility at dissertation prototype level.

## Implementation order

The implementation should be completed in the following order:

1. Add the PostgreSQL audit schema.
2. Add a small database utility module.
3. Add the FastAPI backend.
4. Add the NiceGUI dashboard.
5. Add Dockerfile and docker-compose.yml.
6. Run an end-to-end operational test using existing inspection results.
7. Document the operational workflow and limitations.

## Expected dissertation contribution

This stage will strengthen the project by showing that the proposed inspection system is not only an experimental anomaly detection pipeline. It will demonstrate how detection, localisation, semantic interpretation, risk mapping and human review can be integrated into an operational workflow.

The operational layer will also support the dissertation discussion on auditability, traceability and human-in-the-loop governance.
