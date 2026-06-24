# ADR_OCD Drop-In Engineering Handoff

Use this text at the start of the next engineering, coding, or chat-agent session.

---

You are continuing work on GBOGEB/DOCX_RTM_Automation, active draft PR 17, branch feature/ADR_OCD-qps-procurement-bridge.

The objective is to keep ADR and OCD inside DOCX_RTM_Automation while aligning outward-facing procurement terminology with QPS Requirements rather than RFO.

Important terminology rules:

1. Use QPS Requirements as the preferred outward-facing term for the main procurement-facing technical requirements used by Applicants to prepare a Fixed Price Offer.
2. Treat RFO as an internal legacy alias only.
3. Use Invitation to Tender only where describing the procurement package or procedure.
4. Use Corrigendum for formal amendments or corrections after publication.
5. Use Negotiation Stage for the intermediate procurement alignment rounds.
6. Reuse glossary/GLOSSARY.yaml before inventing new terms.

Current files in the PR:

- glossary/GLOSSARY.yaml
- federation/ADR_OCD/README.md
- federation/ADR_OCD/bridge_manifest.yaml
- federation/ADR_OCD/CHANGELOG.md
- federation/ADR_OCD/PR_ACTIVE_MANIFEST.md
- federation/ADR_OCD/SESSION_REPLAY.md
- federation/ADR_OCD/DROP_IN_HANDOFF.md

Current implementation state:

- Governance bridge exists.
- Glossary exists.
- Bridge manifest exists.
- Session replay exists.
- Active PR manifest exists.
- No invasive parser, visualization, orchestration, docs/section9, or config changes have been made yet.

Next low-hanging technical implementation:

1. Add schemas/glossary.schema.json.
2. Add schemas/adr_ocd_bridge_manifest.schema.json.
3. Add scripts/validate_adr_ocd_bridge.py.
4. Validate glossary/GLOSSARY.yaml and federation/ADR_OCD/bridge_manifest.yaml.
5. Add a minimal test that loads both YAML files and checks required keys.

Three moves forward:

Move 1: Schema hardening.
Create JSON schemas for the glossary and bridge manifest, then validate them locally and in CI.

Move 2: Parser taxonomy bridge.
Add isolated taxonomy constants or mapping files for QPS, ADR, OCD, Corrigendum, Negotiation Stage, Fixed Price Offer, Applicant, RTM, and DTM. Do not yet rewrite the parser engine.

Move 3: Traceability export bridge.
Add a first QPS to ADR to OCD traceability export model that can later feed RTM and DTM generation.

Major waves:

Wave 0: Governance bridge bootstrap. Current PR.
Wave 1: Schema validation and CI.
Wave 2: Parser taxonomy hooks.
Wave 3: RTM and DTM traceability expansion.
Wave 4: DOCX rendering for ADR and OCD.
Wave 5: Negotiation-stage and Corrigendum release manifests.
Wave 6: Final contract-baseline packaging and dashboard reporting.

Engineering rule:

First in, first to complete. Complete the easiest durable files first, especially glossary, manifest, schema, validation, and tests. Avoid broad refactors until the bridge vocabulary and traceability objects are stable.

Chat-agent handling rule:

When asked about RFO, respond that RFO is a legacy/internal shorthand. For outward-facing procurement content, use QPS Requirements as the standard term unless the context specifically calls for Invitation to Tender, Corrigendum, Applicant, Tenderer, Bidder, Fixed Price Offer, or Negotiation Stage.

---
