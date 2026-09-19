# Data-rich JSON -> DOCX consumer bridge

This bridge consumes the governed outward manifest produced by
`GBOGEB/document-organization-system` and renders its Markdown projection to
DOCX without taking semantic authority away from the JSON source.

## Authority chain

```text
document-organization-system JSON SSOT
  -> projection Markdown + outward manifest
  -> DOCX_RTM consumer validation
  -> deterministic reference.docx
  -> Pandoc render
  -> DOCX + render receipt
```

The DOCX is a generated view. Any semantic edit discovered in Word must return
as a JSON change-set proposal and be approved upstream before it can affect the
canonical document.

## Heading rule

The producer sends unnumbered Markdown headings:

- `#` -> Heading 1
- `##` -> Heading 2
- `###` -> Heading 3

The reference DOCX links Heading 1/2/3 to one multilevel numbering definition.
The consumer must not use `config/filters/extend_headings.lua` for this path,
because that filter inserts literal numbers into heading text.


## Governed visual style layer

The accepted DOCX/PDF pair is an immutable visual regression baseline. New
appearance work is driven only by
`federation/DATA_RICH_DOCUMENT/visual_style.json`, validated against
`visual_style.schema.json`.

The style file deliberately separates **roles** from hard-coded formatting.
You can change, independently:

- body, heading and mono font names;
- Title, Heading 1/2/3, body, caption, requirement-title and metadata sizes;
- body, hierarchy, special-number, requirement-ID, caption and metadata colors;
- heading-number appearance separately from heading text;
- requirement-ID and metadata-label emphasis;
- caption and caption-number styling;
- page margins and paragraph spacing;
- table-header, border, fill and callout roles.

User fonts are referenced by font **name** only and must exist in the render
environment. Font files are never embedded or committed by this contract.

Word stores font sizes in half-points, so all size tokens are governed at **0.5 pt** granularity. Quarter-point values are rejected instead of being silently rounded by the renderer.

The current first style candidate is
`QPS_TECH_GRAPHITE_TEAL_COPPER_V1`: graphite body text, deep-teal hierarchy
and copper special-number accents. It is a candidate, not a replacement for
the approved baseline.

CI proves the style candidate is style-only by comparing source/projection
hashes with the approved baseline, then measures the rendered PNG delta. A
new candidate cannot replace the approved visual baseline without explicit
user approval.

## Controlled render

The consumer validates:

1. manifest schema and authority guards;
2. source/projection hashes and exact source Git ref;
3. reference DOCX numbering/style contract;
4. Pandoc render success;
5. Heading 1/2/3 counts against the manifest;
6. absence of literal numeric prefixes in heading text;
7. requirement blocks are bound with Word keep-with-next / keep-together pagination controls;
8. rendered DOCX SHA-256.

Requirement paragraphs first receive Word keep-with-next/keep-together hints. CI then measures the actual LibreOffice PDF pagination. If any requirement spans pages, the consumer inserts an explicit page break before that requirement, re-renders, and fails closed unless the final PDF keeps the entire block on one page.

The CI workflow additionally renders the DOCX to PDF/PNG and uploads the full
receipt bundle. The binary rendering is evidence of execution; visual approval
remains a separate human-facing review gate.

## Files

- `federation/DATA_RICH_DOCUMENT/consumer_contract.yaml`
- `federation/DATA_RICH_DOCUMENT/visual_style.json`
- `federation/DATA_RICH_DOCUMENT/visual_style.schema.json`
- `scripts/build_data_rich_reference_docx.py`
- `scripts/measure_visual_style_diff.py`
- `src/bridges/data_rich_document_consumer.py`
- `tests/test_data_rich_document_consumer.py`
- `.github/workflows/data-rich-document-consumer.yml`
