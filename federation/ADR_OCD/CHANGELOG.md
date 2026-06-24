# ADR_OCD Bridge Changelog

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
