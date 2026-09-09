# Current execution paths

This repository contains both reusable standalone tooling and older project-seeded QPLANT/RTM generators. They are not the same authority class.

## Current source-driven path

Use this path when the input document itself is the evidence being inspected:

```bash
python scripts/parse_document_current.py input.docx --output out/source_extraction.json
```

Implementation:
- `parser/source_extractor.py`
- `scripts/parse_document_current.py`
- `tests/test_source_extractor.py`
- `.github/workflows/direct-docx-source-smoke.yml`

The extractor reads DOCX paragraphs and table rows, retains source section/kind/index, and emits candidate `rtm_requirements`, `otc_elements` and `del_deliverables` populations. These are discovery/traceability candidates only. Lexical extraction never establishes compliance, acceptance, closure, or current QPS authority by itself.

## Existing enhanced-analysis path

`parser/engine.py` remains the established downstream enhancement/mapping engine. Its direct `Document` parsing hook is still legacy/stubbed; use supplied `analysis_data` or the current source-extraction JSON until a dedicated compatibility migration is accepted.

## Historical seeded generators

Files such as `scripts/improved_rtm_generator.py` and related automation/archive copies contain useful historical QPLANT hierarchy, SBS classification, verification-method heuristics, acceptance-pattern logic and presentation ideas. They also contain manually seeded requirement populations, historical assumptions, and in some cases machine-specific paths.

Treat these as `LEGACY_SEEDED_REFERENCE`:
- mine reusable algorithms and taxonomy;
- do not treat embedded RTM values as current source authority;
- do not use agreement with a seeded value as compliance credit;
- bind any migrated rule to the current source document and exact source identity.

## TRIAGE/QPS integration value

The strongest reusable lanes are:
1. source-driven DOCX extraction as an independent P2 requirements/crosswalk check;
2. SBS and verification-method heuristics as optional enrichment after extraction;
3. Word/Markdown round-trip and rendering mechanics for outward document QA;
4. ADR/OCD and procurement terminology bridge for P1 negotiation presentation;
5. deterministic artifact indexing/offline grep for source discovery.

Primary QPS authority remains in `GBOGEB/cryoplant-project`; this repository supplies independent extraction, transformation and QA capabilities only until an exact-source child receipt explicitly promotes a result.
