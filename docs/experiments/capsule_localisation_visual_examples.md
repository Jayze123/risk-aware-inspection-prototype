# Capsule Localisation Visual Examples

## Purpose

This note records qualitative examples from the PatchCore capsule localisation threshold sweep. The figures compare the original image, MVTec ground-truth mask, PatchCore anomaly map, default predicted mask and tuned threshold mask.

## Summary

The examples show that the default predicted masks often over-segmented the capsule image by selecting several broad anomaly regions. After applying the tuned threshold of 0.85, the predicted masks became more selective and aligned more closely with the ground-truth defect regions.

Example improvements include:

| Image                           | Default Dice | Tuned Dice |
| ------------------------------- | -----------: | ---------: |
| capsule_test_crack_018          |        0.064 |      0.683 |
| capsule_test_faulty_imprint_000 |        0.095 |      0.716 |
| capsule_test_faulty_imprint_006 |        0.055 |      0.697 |
| capsule_test_faulty_imprint_008 |        0.055 |      0.684 |
| capsule_test_scratch_006        |        0.068 |      0.686 |
| capsule_test_squeeze_010        |        0.205 |      0.861 |

## Interpretation

The visual examples support the numerical threshold sweep result. PatchCore’s anomaly maps contained useful localisation information, but the original binary mask conversion was too permissive. A higher threshold reduced false mask regions and improved alignment with the ground-truth defect masks.

This is useful for the dissertation because it shows that localisation quality can be improved through post-processing without retraining the anomaly detector.
