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
- schemas/glossary.schema.json
- schemas/adr_ocd_bridge_manifest.schema.json
- scripts/validate_adr_ocd_bridge.py
- tests/test_adr_ocd_bridge_validation.py
- federation/ADR_OCD/README.md
- federation/ADR_OCD/bridge_manifest.yaml
- federation/ADR_OCD/taxonomy.yaml
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
- Drop-in handoff exists.
- Wave 1 schema validation is implemented.
- Parser taxonomy bridge has started through taxonomy.yaml.
- No invasive parser, visualization, orchestration, docs/section9, or config changes have been made yet.

Validation commands:

python scripts/validate_adr_ocd_bridge.py
pytest tests/test_adr_ocd_bridge_validation.py

Next low-hanging technical implementation:

1. Connect federation/ADR_OCD/taxonomy.yaml to the existing parser configuration or extraction taxonomy.
2. Keep the parser change narrow and reversible.
3. Add RTM and DTM export placeholders for QPS to ADR to OCD traceability edges.
4. Add negotiation-stage and final-corrigendum release manifest templates.

Three moves forward:

Move 1: Parser taxonomy bridge.
Connect taxonomy.yaml to parser extraction configuration so QPS, ADR, OCD, Corrigendum, Negotiation Stage, Fixed Price Offer, Applicant, RTM, and DTM can be recognized consistently.

Move 2: Traceability export bridge.
Add a first QPS to ADR to OCD traceability export model that can later feed RTM and DTM generation.

Move 3: Corrigendum and negotiation release bridge.
Add release manifests for publication baseline, negotiation stage 1, negotiation stage 2, final Corrigendum, and contract baseline.

Major waves:

Wave 0: Governance bridge bootstrap. Implemented.
Wave 1: Schema validation and tests. Implemented.
Wave 2: Parser taxonomy hooks. Started through taxonomy.yaml, not yet wired to parser.
Wave 3: RTM and DTM traceability expansion.
Wave 4: DOCX rendering for ADR and OCD.
Wave 5: Negotiation-stage and Corrigendum release manifests.
Wave 6: Final contract-baseline packaging and dashboard reporting.

Engineering rule:

First in, first to complete. Complete the easiest durable files first, especially glossary, manifest, schema, validation, taxonomy, and tests. Avoid broad refactors until the bridge vocabulary and traceability objects are stable.

Chat-agent handling rule:

When asked about RFO, respond that RFO is a legacy/internal shorthand. For outward-facing procurement content, use QPS Requirements as the standard term unless the context specifically calls for Invitation to Tender, Corrigendum, Applicant, Tenderer, Bidder, Fixed Price Offer, or Negotiation Stage.

---
