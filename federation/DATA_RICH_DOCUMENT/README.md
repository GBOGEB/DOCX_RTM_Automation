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

Requirement title, statement and metadata paragraphs are kept together when possible so a page break does not orphan the remainder of a requirement block.

The CI workflow additionally renders the DOCX to PDF/PNG and uploads the full
receipt bundle. The binary rendering is evidence of execution; visual approval
remains a separate human-facing review gate.

## Files

- `federation/DATA_RICH_DOCUMENT/consumer_contract.yaml`
- `scripts/build_data_rich_reference_docx.py`
- `src/bridges/data_rich_document_consumer.py`
- `tests/test_data_rich_document_consumer.py`
- `.github/workflows/data-rich-document-consumer.yml`
