#!/usr/bin/env python3
"""Conservative direct DOCX extraction for the standalone RTM product.

This module replaces the historical assumption that direct parsing can silently
produce an empty analysis. It extracts document structure in source order and
emits the analysis_data contract consumed by ``EnhancedParserEngine``.

The extractor is deliberately conservative: it recognises explicit IDs and
normative/test/deliverable language, preserves source text and section context,
and does not invent compliance or traceability relationships.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, Tuple

from docx import Document
from docx.document import Document as _Document
from docx.table import Table
from docx.text.paragraph import Paragraph

REQ_ID = re.compile(r"\b(?:RTM|REQ|REQUIREMENT)[-_\s]?(\d+(?:\.\d+)*)\b", re.I)
OTC_ID = re.compile(r"\b(?:OTC|TEST(?:\s+CASE)?)[-_\s]?(\d+(?:\.\d+)*)\b", re.I)
DEL_ID = re.compile(r"\b(?:DEL|DELIVERABLE)[-_\s]?(\d+(?:\.\d+)*)\b", re.I)
NORMATIVE = re.compile(r"\b(shall|must|required to|is required to)\b", re.I)
TEST_WORDS = re.compile(r"\b(test|verify|verification|validate|validation|acceptance)\b", re.I)
DEL_WORDS = re.compile(r"\b(deliverable|submit|submission|document|report|drawing|manual|certificate)\b", re.I)


def _iter_blocks(parent: _Document) -> Iterator[Tuple[str, str, str]]:
    """Yield (kind, text, style) for paragraphs and table rows in document order."""
    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            para = Paragraph(child, parent)
            text = para.text.strip()
            if text:
                yield "paragraph", text, para.style.name or ""
        elif tag == "tbl":
            table = Table(child, parent)
            for row_index, row in enumerate(table.rows, start=1):
                cells = [" ".join(c.text.split()) for c in row.cells]
                text = " | ".join(c for c in cells if c)
                if text:
                    yield "table_row", text, f"table-row-{row_index}"


def _stable_id(prefix: str, match: re.Match[str] | None, ordinal: int) -> str:
    if match:
        return f"{prefix}-{match.group(1)}"
    return f"{prefix}-AUTO-{ordinal:04d}"


def extract_analysis_data(doc_path: str | Path) -> Dict[str, Any]:
    """Extract sections, RTM requirements, OTC items and deliverables from DOCX.

    Returned keys intentionally match the ``analysis_data`` contract accepted by
    ``EnhancedParserEngine.parse_document``.
    """
    path = Path(doc_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if path.suffix.lower() != ".docx":
        raise ValueError(f"direct_docx only accepts .docx, got {path.suffix!r}")

    document = Document(path)
    sections = []
    requirements = []
    otc = []
    deliverables = []
    current_section = path.stem
    counters = {"RTM": 0, "OTC": 0, "DEL": 0}

    for kind, text, style in _iter_blocks(document):
        if kind == "paragraph" and style.lower().startswith("heading"):
            current_section = text
            sections.append({"title": text, "style": style})
            continue

        source = {
            "source_section": current_section,
            "source_kind": kind,
            "source_style": style,
            "source_text": text,
        }

        req_match = REQ_ID.search(text)
        if req_match or NORMATIVE.search(text):
            counters["RTM"] += 1
            requirements.append({
                "id": _stable_id("RTM", req_match, counters["RTM"]),
                "description": text,
                "priority": "Medium",
                "verification_method": "Review",
                "acceptance_criteria": "TBD",
                **source,
            })

        otc_match = OTC_ID.search(text)
        if otc_match or (TEST_WORDS.search(text) and not NORMATIVE.search(text)):
            counters["OTC"] += 1
            otc.append({
                "id": _stable_id("OTC", otc_match, counters["OTC"]),
                "name": text[:120],
                "objective": text,
                "preconditions": "",
                "test_steps": [],
                "expected_results": "",
                "linked_requirements": sorted(set(f"RTM-{m}" for m in REQ_ID.findall(text))),
                **source,
            })

        del_match = DEL_ID.search(text)
        if del_match or (DEL_WORDS.search(text) and not NORMATIVE.search(text)):
            counters["DEL"] += 1
            deliverables.append({
                "id": _stable_id("DEL", del_match, counters["DEL"]),
                "name": text[:120],
                "description": text,
                "type": "Document" if re.search(r"\b(document|report|drawing|manual|certificate)\b", text, re.I) else "Deliverable",
                "due_date": "",
                "responsible_party": "",
                "status": "Open",
                "dependencies": sorted(set(f"RTM-{m}" for m in REQ_ID.findall(text))),
                **source,
            })

    return {
        "sections": sections,
        "rtm_requirements": requirements,
        "otc_elements": otc,
        "del_deliverables": deliverables,
        "direct_extraction": {
            "source": str(path),
            "mode": "conservative_explicit_and_normative",
            "counts": {
                "sections": len(sections),
                "rtm": len(requirements),
                "otc": len(otc),
                "del": len(deliverables),
            },
            "credit_rule": "extraction_is_candidate_traceability_not_compliance_credit",
        },
    }
