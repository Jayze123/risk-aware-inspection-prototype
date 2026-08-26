# Final Experimental Evidence

This directory contains the portable final-result records supporting the quantitative results reported for the risk-aware industrial visual-inspection prototype.

## Evidence scope

The six CSV files contain one record for each evaluated MVTec AD test image across the bottle, capsule and hazelnut categories. Together, they contain 650 inspection records.

| Detector | Category | Evidence file | Records | Requires review | Review rate |
|---|---|---|---:|---:|---:|
| PatchCore | Bottle | `final_results/risk_patchcore_bottle.csv` | 83 | 16 | 19.28% |
| PaDiM | Bottle | `final_results/risk_padim_bottle.csv` | 83 | 57 | 68.67% |
| PatchCore | Capsule | `final_results/risk_patchcore_capsule_semantic_v3.csv` | 132 | 68 | 51.52% |
| PaDiM | Capsule | `final_results/risk_padim_capsule_semantic_v3.csv` | 132 | 111 | 84.09% |
| PatchCore | Hazelnut | `final_results/risk_patchcore_hazelnut.csv` | 110 | 19 | 17.27% |
| PaDiM | Hazelnut | `final_results/risk_padim_hazelnut.csv` | 110 | 99 | 90.00% |
| **Total** |  |  | **650** | **370** | **56.92%** |

Each record preserves the detector output, localisation information, semantic label, confidence fusion, risk classification and operator-review routing decision produced by the implemented pipeline.

## Portability and integrity

The source experiment files were generated locally under the ignored `outputs/` directory. Portable copies are provided here for examination and reproducibility.

The following path-only changes were made:

- Local absolute image paths were converted from machine-specific paths to `data/mvtec_anomaly_detection/...`.
- Backslashes in relative artefact paths were converted to forward slashes.

No scores, thresholds, labels, risk classes, confidence values, review decisions, identifiers, hashes or timestamps were changed. Verification confirmed that all column structures and 650 records were preserved, with zero unexpected differences.

## Dataset and generated artefacts

The MVTec AD source images are not redistributed in this repository. They must be obtained separately and placed under `data/mvtec_anomaly_detection/` using the category structure referenced in the CSV files.

The `artefacts.*` columns retain the relative locations produced during the original runs. Per-image heatmaps, masks and annotated images remain generated runtime outputs and are not included in this evidence directory.

## Result-set naming

The `semantic_v3` suffix identifies the final capsule runs that used the implemented rule-based semantic labelling configuration. The inactive vision-language semantic labeller remains an extension interface and was not used to produce these results.
