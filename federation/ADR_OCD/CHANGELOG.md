# ADR_OCD Bridge Changelog

## Advisory relation contracts - 2026-11-20

- Taxonomy 0.3.1 and QPS triage applicability 0.3.2 register the parser's
  `proposed_mapping_to` and `source_reference_to` relations as five explicit
  source/target type signatures.
- Proposed ADR, OCD and Corrigendum candidates remain unresolved advisory
  mappings. Parser RTM and DTM source references remain source pointers.
- Each new declaration carries `advisory: true` and `authority_transfer: false`;
  the existing child engineering authority and controlled relations are retained.
- Export consumer tests cover both policy lists and reject unknown relations,
  untyped candidates and substitutions of controlled targets. This closes the
  relation-registration finding after PR #116 without changing parser promotion.

## 0.2.0 - 2026-06-24

### Added

- Added schemas/glossary.schema.json for the outward-facing QPS, ADR, and OCD glossary.
- Added schemas/adr_ocd_bridge_manifest.schema.json for the federation bridge manifest.
- Added scripts/validate_adr_ocd_bridge.py to validate glossary, bridge manifest, and taxonomy artifacts using PyYAML and the Python standard library.
- Added tests/test_adr_ocd_bridge_validation.py for pytest coverage of the bridge artifacts.
- Added federation/ADR_OCD/taxonomy.yaml as the first isolated parser taxonomy bridge for QPS, ADR, OCD, negotiation, and Corrigendum terms.

### Changed

- Updated PR_ACTIVE_MANIFEST.md to mark Wave 0 complete and Wave 1 implemented.
- Updated DROP_IN_HANDOFF.md so the next engineering session starts from parser taxonomy wiring rather than schema bootstrap.

### Status

- Wave 0: implemented.
- Wave 1: implemented.
- Wave 2: started lightly through taxonomy.yaml; parser wiring remains open.

## 0.1.0 - 2026-06-24

### Added

- Introduced ADR_OCD federation bridge for QPS Requirements, ADR, and OCD alignment.
- Added outward-facing glossary/GLOSSARY.yaml for procurement and document terminology reuse.
- Added bridge_manifest.yaml describing document roles, procurement stages, traceability edges, quality gates, and integration policy.
- Clarified that RFO remains an internal legacy alias only; outward-facing content should prefer QPS Requirements and procurement-appropriate terms.

### Procurement terminology baseline

- QPS Requirements: primary technical requirements content used by Applicants to prepare a Fixed Price Offer.
- Invitation to Tender: accepted procurement package or procedure term where appropriate.
- Corrigendum: formal amendment or correction mechanism after publication.
- Negotiation Stage: formal stage for clarifications and agreed changes before final baseline.

### Integration intent

- Keep ADR and OCD inside DOCX_RTM_Automation.
- Add federation and bridge files that can later be promoted into the main implementation.
- Avoid invasive changes to parser, visualization, orchestration, and existing documentation generation paths in this first PR.
