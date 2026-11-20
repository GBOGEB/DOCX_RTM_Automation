# QPS parser proposal contract v2

The existing direct DOCX reader feeds `EnhancedParserEngine.parse_document()` when no analysis mapping is supplied. An explicitly supplied empty mapping remains empty and does not open a file. The old direct branch silently called an empty stub; this integration reuses `parser/direct_docx.py` rather than adding another parser.

## Output and source pointers

Direct extraction hashes and parses the same immutable byte snapshot. It records a source SHA-256 and a locator for each nonempty main-story paragraph or table-row projection. The locator comprises `part`, `locator_type`, `block_ordinal` and `source_kind`. The ordinal counts the existing reader's nonempty blocks in source order, including headings. It is not a Word page number, raw XML paragraph index or canonical requirement ID.

Source provenance is retained in enhanced-element original data and copied into triage items. Enrichment returns new parsing metadata without modifying the supplied analysis. The metadata advertises `qps.triage-proposal.v2` and `authority_transfer: false`.

The reader is a conservative main-story projection. Tracked insertions/deletions, comments, field evaluation, nested stories and render fidelity require the existing specialist markup and native-render lanes. Parser-generated `AUTO` identifiers remain candidates. A larger candidate count does not establish more controlled requirements.

## Advisory-only semantic classification

Parser confidence cannot confer acceptance. High and medium confidence produce `NEEDS_REVIEW`; parser-only evidence remains below controlled/traceable maturity. Malformed, Boolean and non-finite confidence values provide no promotion credit. An unverified pasted `authority_receipt` is not evaluated as approval.

Keyword-derived ADR/OCD/corrigendum references live in `proposed_refs` with `PROPOSED_UNRESOLVED`, a `PROPOSED-` identifier prefix and `proposed_mapping_to` edges. Verified reference arrays remain empty. RTM/DTM source references retain their input IDs and use `source_reference_to` with `Parser RTM source` / `Parser DTM source` target types.

The existing downstream export index includes these source-reference rows in `rtm_rows` / `dtm_rows` and exposes `proposed_reference_rows`. Legacy controlled target types remain readable for compatibility; the new parser does not produce them. Consumers that require exact old relation/type strings must adopt this contract. Existing numeric review-lane assignments and engineering decisions are outside this parser bridge.

## Verification and admission

Run the direct-reader tests, bridge integration tests and advisory-contract tests together. They cover parser → triage → JSON/CSV → dashboard integration as well as malformed-confidence and source-provenance regressions. A focused local run is not repository-wide coverage, native Word fidelity, exact-commit CI, owner review or release admission.
