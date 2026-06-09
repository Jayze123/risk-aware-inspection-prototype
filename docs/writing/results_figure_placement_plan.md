# Results Chapter Figure Placement Plan

## Purpose

This note identifies the figures to use in the Results and Discussion chapter and explains where each figure should be placed. The aim is to make the final dissertation chapter easier to assemble in Word.

## Figure 4.1: PatchCore capsule localisation before and after threshold tuning

Suggested location: after Section 4.5, first paragraph.

Suggested file:

`docs/figures/capsule_threshold_sweep/capsule__test__squeeze__010_comparison.png`

Caption:

Figure 4.1: PatchCore capsule localisation before and after threshold tuning. The figure compares the original image, MVTec ground-truth mask, PatchCore anomaly map, default predicted mask and tuned mask. The tuned threshold of 0.85 produced a more selective localisation mask and improved the Dice score from 0.205 to 0.861.

## Figure 4.2: PatchCore bottle localisation before and after threshold tuning

Suggested location: after the discussion of bottle localisation in Section 4.5.

Suggested file:

`docs/figures/bottle_patchcore_threshold_sweep/bottle__test__contamination__000_comparison.png`

Caption:

Figure 4.2: PatchCore bottle localisation before and after threshold tuning. The tuned threshold of 0.70 reduced over-segmentation and produced a mask that aligned more closely with the ground-truth contamination region. The Dice score improved from 0.358 to 0.853.

## Figure 4.3: PaDiM bottle localisation before and after threshold tuning

Suggested location: after Figure 4.2 or in the same bottle comparison subsection.

Suggested file:

`docs/figures/bottle_padim_threshold_sweep/bottle__test__broken_large__003_comparison.png`

Caption:

Figure 4.3: PaDiM bottle localisation before and after threshold tuning. The tuned threshold of 0.35 improved the overlap between the predicted mask and the ground-truth broken-large defect region, although the overall tuned bottle localisation score remained lower than PatchCore.

## Figure 4.4: PatchCore hazelnut localisation before and after threshold tuning

Suggested location: after the hazelnut localisation discussion in Section 4.5.

Suggested file:

`docs/figures/hazelnut_patchcore_threshold_sweep/hazelnut__test__crack__004_comparison.png`

Caption:

Figure 4.4: PatchCore hazelnut localisation before and after threshold tuning. The tuned threshold of 0.80 produced a more focused mask around the damaged hazelnut region and improved the Dice score from 0.226 to 0.873.

## Figure 4.5: PaDiM hazelnut localisation before and after threshold tuning

Suggested location: after Figure 4.4 or in the same hazelnut comparison subsection.

Suggested file:

`docs/figures/hazelnut_padim_threshold_sweep/hazelnut__test__hole__000_comparison.png`

Caption:

Figure 4.5: PaDiM hazelnut localisation before and after threshold tuning. The tuned threshold of 0.50 improved the predicted mask compared with the default output, increasing the Dice score from 0.497 to 0.677.

## Notes for dissertation writing

The figures should be inserted after the quantitative localisation tables. The tables provide the overall numerical evidence, while the figures provide qualitative examples showing why threshold tuning improved the masks.

The strongest visual examples are PatchCore capsule, PatchCore bottle and PatchCore hazelnut because they show clear improvements after threshold tuning. PaDiM examples can be included to show comparison, but they should not dominate the discussion because PatchCore produced the stronger tuned localisation results overall.
