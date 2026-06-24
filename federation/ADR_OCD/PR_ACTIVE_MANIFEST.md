# ADR_OCD Active PR Manifest

Active PR:
- Number: 17
- Title: ADR_OCD: QPS procurement terminology and federation bridge
- Repository: GBOGEB/DOCX_RTM_Automation
- Branch: feature/ADR_OCD-qps-procurement-bridge
- Base: main
- State: open draft

Purpose:
Add a lightweight federation bridge for QPS Requirements, ADR, and OCD terminology, schema validation, parser taxonomy hooks, and traceability preparation.

Produced artifacts:
- glossary/GLOSSARY.yaml: outward-facing procurement and document glossary.
- federation/ADR_OCD/README.md: bridge overview and terminology policy.
- federation/ADR_OCD/bridge_manifest.yaml: document roles, traceability edges, stages, quality gates, and pruning policy.
- federation/ADR_OCD/CHANGELOG.md: first bridge baseline and Wave 1 continuation.
- federation/ADR_OCD/PR_ACTIVE_MANIFEST.md: active PR manifest.
- federation/ADR_OCD/SESSION_REPLAY.md: structured prompt and reply lineage.
- federation/ADR_OCD/DROP_IN_HANDOFF.md: drop-in continuation prompt for engineering, coding, and chat handling.
- federation/ADR_OCD/taxonomy.yaml: isolated parser taxonomy bridge for QPS, ADR, OCD, negotiation, and corrigendum terms.
- schemas/glossary.schema.json: structural schema for glossary/GLOSSARY.yaml.
- schemas/adr_ocd_bridge_manifest.schema.json: structural schema for bridge_manifest.yaml.
- scripts/validate_adr_ocd_bridge.py: focused validation script using PyYAML and the Python standard library.
- tests/test_adr_ocd_bridge_validation.py: pytest coverage for glossary, manifest, and taxonomy validation.

Repository area created:

DOCX_RTM_Automation/
  glossary/
    GLOSSARY.yaml
  schemas/
    glossary.schema.json
    adr_ocd_bridge_manifest.schema.json
  scripts/
    validate_adr_ocd_bridge.py
  tests/
    test_adr_ocd_bridge_validation.py
  federation/
    ADR_OCD/
      README.md
      bridge_manifest.yaml
      taxonomy.yaml
      CHANGELOG.md
      PR_ACTIVE_MANIFEST.md
      SESSION_REPLAY.md
      DROP_IN_HANDOFF.md

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
Status: completed in PR 17
Completed:
- Created ADR_OCD branch.
- Created draft PR.
- Added glossary.
- Added bridge README.
- Added bridge manifest.
- Added bridge changelog.
- Added session replay.
- Added drop-in handoff.
- Added active PR manifest.

Wave 1 - Validation and schema hardening:
Status: implemented in PR 17
Completed:
1. Added schemas/glossary.schema.json.
2. Added schemas/adr_ocd_bridge_manifest.schema.json.
3. Added scripts/validate_adr_ocd_bridge.py.
4. Added tests/test_adr_ocd_bridge_validation.py.
5. Added federation/ADR_OCD/taxonomy.yaml as the first parser-taxonomy bridge.

Validation command:
python scripts/validate_adr_ocd_bridge.py

Pytest target:
pytest tests/test_adr_ocd_bridge_validation.py

Wave 2 - Parser taxonomy hooks:
Status: started lightly through taxonomy.yaml; implementation still planned
Next moves:
1. Connect taxonomy.yaml to parser extraction configuration.
2. Map extracted sections to document roles: QPS, ADR, OCD.
3. Preserve parser isolation until schemas and taxonomy are accepted.

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
3. Promote PR from draft when validation has been reviewed.

Wave 6 - Final contract-baseline packaging:
Status: planned
Moves:
1. Add contract baseline manifest.
2. Add final Corrigendum impact pack.
3. Add dashboard or report output for QPS, ADR, OCD, RTM, DTM, and lineage.

First-in, first-to-complete policy:
Complete durable, low-risk bridge files first:
1. Glossary and term reuse. Done.
2. Bridge manifest. Done.
3. Changelog, active PR manifest, session replay, and handoff. Done.
4. Schema validation. Implemented.
5. Parser taxonomy hooks. Started through taxonomy.yaml.
6. RTM and DTM integration. Next major technical wave.
7. DOCX rendering. Later wave.

Immediate next step:
Run or review the Wave 1 validation command and tests, then connect taxonomy.yaml to the existing parser configuration in a narrow Wave 2 PR section.
