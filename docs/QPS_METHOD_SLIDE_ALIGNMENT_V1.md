# QPS TRIAGE method-slide alignment pulse

Date: 2026-09-14

## Purpose

This pulse separates the **standalone method** presentation from any explicit offer-content dependency, while still making the method usable by QPS TRIAGE as a controlled pattern.

## Scanned inputs

| Input | Role | SHA-256 |
|---|---|---|
| Gemini_Generated_Image_nd82rrnd82rrnd82.png | Base slide image: evaluation architecture/order of operations | 8e49d967d719be7f6205715d29f3044d17de92a80a948c257d9c24f0ebbfbed0 |
| Gemini_Generated_Image_vj8a97vj8a97vj8a.png | Base slide image: DMAIC cycle | af34f8f9aa8817161884faa05c12bc056d673a3c1b1660bcc3bda0498913ce65 |
| OFFER_Tecnical_Content_Applicant_submission_requirements_UPDATED_v2.xlsx | QPS applicant offer/content structure and audit corrections | 86421bdffd8cb2d3dcefe33e5d7a1f81c637d46f5ecdb10c8e725d8a48053827 |
| QPS_Applicant_DOCLIST_1004_0854_UPDATED.docx | Applicant document list source | 192f27a283baed04387ec6e8e1d8552b6f507bc039c48b1e8b035896e1ee7ad9 |
| 2024-106-IVE_Cryoplant & Storage (QPS)_Addendum II Technical Requirements_MASTER_0804.docx | QPS technical requirement source | 8bd6c3db5452766526737da0af98a995068733be025b23f3d38b582c43531d4d |
| Thinking_and_Method_POLISHED_OCR_aligned_v2.pptx | Generated polished editable deck | bfac7eb830115378fedd6066896e40a5d02c0d685ce5321bf0e841d4846ed5b3 |

## OCR extraction

### Slide 1

- Title: `Evaluation architecture and order of operations`
- Layer A: `Static BT seed`
- Layer B: `Extraction schema` *(source image was blurred; this is corrected from visible intent and existing parsed slide text)*
- Layer C: `A vs B pairwise BT`
- Final block: `Risk overlay and final score`
- Footer rule: `Static requirement ranking must happen before bidder comparison. Risk modifies confidence in bidder delivery, not importance of the requirement.`

### Slide 2

- Core cycle: `Define -> Measure -> Analyze -> Improve -> Control`
- Method descriptors retained: `Iterative`, `Evolutionary`, `Recursive`, `Idempotent`

## Boundary decision

The presentation is **method-only**. It does not become an offer-content slide deck. QPS TRIAGE may consume it as a governed methodology pattern only.

## TRIAGE alignment mapping

| Method item | QPS TRIAGE interpretation | Authority boundary |
|---|---|---|
| Static BT seed | Priority baseline for requirement importance | Fixed before bidder/content comparison |
| Extraction schema | Evidence normalization and source capture | Does not alter priority baseline |
| A vs B pairwise BT | Controlled comparison logic | Uses frozen baseline |
| Risk overlay | Confidence/delivery adjustment | Does not rewrite requirement importance |
| DMAIC cycle | Recursive method governance | Changes only through controlled Improve/Control gate |

## Federation fit

This method note is compatible with the PCA federation lane in this PR, but it does **not** collapse BT, PCA, risk, or evidence disposition into one score. The boundaries remain:

- BT: ranking/comparison method.
- PCA: multivariate diagnostic/reduction method.
- Risk overlay: confidence/delivery modifier after comparison.
- QPS TRIAGE: evidence identity, disposition, traceability, and promotion authority.

## Validation

- PPT generated with editable text/shapes, not pasted text-as-figure.
- Slide render completed successfully.
- `slides_test.py` passed with no overflow.
- OCR ambiguities are documented rather than silently normalized.
