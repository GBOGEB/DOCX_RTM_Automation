# ADR_OCD Active PR Manifest

Active PR:
- Number: 17
- Title: ADR_OCD: QPS procurement terminology and federation bridge
- Repository: GBOGEB/DOCX_RTM_Automation
- Branch: feature/ADR_OCD-qps-procurement-bridge
- Base: main
- State: open draft

Purpose:
Add a lightweight federation bridge for QPS Requirements, ADR, and OCD terminology and traceability.

Produced artifacts:
- glossary/GLOSSARY.yaml: outward-facing procurement and document glossary.
- federation/ADR_OCD/README.md: bridge overview and terminology policy.
- federation/ADR_OCD/bridge_manifest.yaml: document roles, traceability edges, stages, quality gates, and pruning policy.
- federation/ADR_OCD/CHANGELOG.md: first bridge baseline.
- federation/ADR_OCD/PR_ACTIVE_MANIFEST.md: this active PR manifest.

Repository area created:

DOCX_RTM_Automation/
  glossary/
    GLOSSARY.yaml
  federation/
    ADR_OCD/
      README.md
      bridge_manifest.yaml
      CHANGELOG.md
      PR_ACTIVE_MANIFEST.md

Existing areas intentionally not modified:
- parser/
- visualization/
- orchestration_ts/
- docs/section9/
- configs/

Terminology control:
- Preferred outward-facing term: QPS Requirements
- Internal legacy alias: RFO
- Accepted procurement package term: Invitation to Tender
- Commercial response term: Fixed Price Offer
- Amendment term: Corrigendum
- Stages: publication baseline, negotiation stage 1, negotiation stage 2, final corrigendum, contract baseline

Wave 0 - Governance bridge bootstrap:
Status: started in PR 17
Completed:
- Created ADR_OCD branch.
- Created draft PR.
- Added glossary.
- Added bridge README.
- Added bridge manifest.
- Added bridge changelog.
- Added active PR manifest.
Remaining:
- Add glossary schema.
- Add bridge manifest schema.
- Add validation script.

Wave 1 - Validation and schema hardening:
Status: planned
Moves:
1. Add schemas/glossary.schema.json.
2. Add schemas/adr_ocd_bridge_manifest.schema.json.
3. Add scripts/validate_adr_ocd_bridge.py.
4. Add simple YAML validation test.

Wave 2 - Parser taxonomy hooks:
Status: planned
Moves:
1. Recognize QPS Requirements, ADR, OCD, Corrigendum, Negotiation Stage, Fixed Price Offer, Applicant, RTM, and DTM terms.
2. Keep changes isolated until schemas are stable.
3. Map extracted sections to document roles.

Wave 3 - Traceability exports:
Status: planned
Moves:
1. Export QPS to ADR to OCD edges.
2. Export Corrigendum impact rows.
3. Extend RTM and DTM outputs with document-role metadata.

Wave 4 - Rendering and DOCX integration:
Status: planned
Moves:
1. Render ADR and OCD from structured sources.
2. Preserve Word heading hierarchy.
3. Preserve RTM and DTM traceability fields.

Wave 5 - Release and review automation:
Status: planned
Moves:
1. Add release manifest for negotiation-stage and final-corrigendum baselines.
2. Add CI checks for glossary and bridge manifest.
3. Promote PR from draft when validation exists.

First-in, first-to-complete policy:
Complete the easiest governance items first because they reduce ambiguity and can be merged or removed safely:
1. Glossary and term reuse.
2. Bridge manifest.
3. Changelog and active PR manifest.
4. Schema validation.
5. Parser hooks.
6. RTM and DTM integration.
7. DOCX rendering.

Immediate next step:
Add schema validation for glossary/GLOSSARY.yaml and federation/ADR_OCD/bridge_manifest.yaml.
