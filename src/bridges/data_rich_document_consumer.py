#!/usr/bin/env python3
"""Consume a data-rich document projection and render a governed DOCX.

The upstream JSON stays authoritative. This consumer validates the outward
manifest, renders Markdown through Pandoc + reference.docx, then emits a return
receipt with exact hashes and structural heading/numbering proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Tuple
from xml.etree import ElementTree as ET

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


MANIFEST_SCHEMA = "gbogeb.docx-rtm-outward-document-manifest/1.0.0"
CONSUMER_REPO = "GBOGEB/DOCX_RTM_Automation"
NUMBERED_TITLE_RE = re.compile(r"^\s*\d{1,3}(?:\.\d+)*[.)]?\s+")
REQUIREMENT_TITLE_RE = re.compile(r"^\s*REQ-\d+\s+[—-]\s+")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}


class ConsumerError(ValueError):
    pass


def w(tag: str) -> str:
    return f"{{{W}}}{tag}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(
    manifest: Dict[str, Any],
    markdown_path: Path,
    expected_source_ref: str,
) -> None:
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ConsumerError(
            f"unsupported manifest schema: {manifest.get('schema')!r}"
        )

    authority = manifest.get("authority", {})
    forbidden_true = {
        "rendered_output_authoritative",
        "authority_transfer",
        "engineering_credit",
        "compliance_credit",
        "semantic_changes_allowed_in_consumer",
    }
    for key in forbidden_true:
        if authority.get(key) is not False:
            raise ConsumerError(f"authority guard {key!r} must be false")

    consumer = manifest.get("docx_rtm_consumer", {})
    if consumer.get("repo") != CONSUMER_REPO:
        raise ConsumerError(
            f"manifest consumer repo mismatch: {consumer.get('repo')!r}"
        )
    if consumer.get("forbidden_numbering_filter") != "config/filters/extend_headings.lua":
        raise ConsumerError("manifest must explicitly forbid literal heading-number filter")

    source_ref = manifest.get("source", {}).get("git_ref")
    if not source_ref:
        raise ConsumerError("manifest source.git_ref is required")
    if expected_source_ref and source_ref != expected_source_ref:
        raise ConsumerError(
            f"source git ref mismatch: observed {source_ref}, expected {expected_source_ref}"
        )

    observed_md_hash = sha256_file(markdown_path)
    expected_md_hash = manifest.get("projection", {}).get("sha256")
    if observed_md_hash != expected_md_hash:
        raise ConsumerError(
            f"projection markdown hash mismatch: {observed_md_hash} != {expected_md_hash}"
        )

    heading = manifest.get("projection", {}).get("heading_contract", {})
    if heading.get("numbering") != "TEMPLATE_MANAGED":
        raise ConsumerError("projection numbering must be TEMPLATE_MANAGED")
    if heading.get("heading_text_contains_numbers") is not False:
        raise ConsumerError("projection headings must not contain literal numbers")


def _zip_xml(docx_path: Path, member: str) -> ET.Element:
    with zipfile.ZipFile(docx_path) as archive:
        try:
            payload = archive.read(member)
        except KeyError as exc:
            raise ConsumerError(f"{docx_path}: missing {member}") from exc
    return ET.fromstring(payload)


def inspect_numbering_contract(docx_path: Path) -> Dict[str, Any]:
    styles = _zip_xml(docx_path, "word/styles.xml")
    numbering = _zip_xml(docx_path, "word/numbering.xml")

    style_links: Dict[str, Dict[str, str]] = {}
    for level in (1, 2, 3):
        style_id = f"Heading{level}"
        style = styles.find(f".//w:style[@w:styleId='{style_id}']", NS)
        if style is None:
            raise ConsumerError(f"{docx_path}: missing style {style_id}")

        num_id_el = style.find("./w:pPr/w:numPr/w:numId", NS)
        ilvl_el = style.find("./w:pPr/w:numPr/w:ilvl", NS)
        if num_id_el is None or ilvl_el is None:
            raise ConsumerError(
                f"{docx_path}: {style_id} is not linked to multilevel numbering"
            )

        style_links[style_id] = {
            "num_id": num_id_el.get(w("val"), ""),
            "ilvl": ilvl_el.get(w("val"), ""),
        }

    num_ids = {item["num_id"] for item in style_links.values()}
    if len(num_ids) != 1:
        raise ConsumerError(
            f"{docx_path}: Heading1-3 do not share one numbering instance: {style_links}"
        )
    num_id = next(iter(num_ids))

    num = numbering.find(f".//w:num[@w:numId='{num_id}']", NS)
    if num is None:
        raise ConsumerError(f"{docx_path}: numbering instance {num_id} missing")
    abstract_id_el = num.find("./w:abstractNumId", NS)
    if abstract_id_el is None:
        raise ConsumerError(f"{docx_path}: numbering instance {num_id} has no abstractNum")
    abstract_id = abstract_id_el.get(w("val"), "")

    abstract = numbering.find(
        f".//w:abstractNum[@w:abstractNumId='{abstract_id}']",
        NS,
    )
    if abstract is None:
        raise ConsumerError(
            f"{docx_path}: abstract numbering {abstract_id} missing"
        )

    expected_text = {0: "%1", 1: "%1.%2", 2: "%1.%2.%3"}
    level_details: Dict[str, Dict[str, str]] = {}
    for ilvl, expected_style in enumerate(("Heading1", "Heading2", "Heading3")):
        lvl = abstract.find(f"./w:lvl[@w:ilvl='{ilvl}']", NS)
        if lvl is None:
            raise ConsumerError(f"{docx_path}: numbering level {ilvl} missing")
        pstyle = lvl.find("./w:pStyle", NS)
        lvl_text = lvl.find("./w:lvlText", NS)
        if pstyle is None or pstyle.get(w("val")) != expected_style:
            raise ConsumerError(
                f"{docx_path}: level {ilvl} not linked to {expected_style}"
            )
        if lvl_text is None or lvl_text.get(w("val")) != expected_text[ilvl]:
            raise ConsumerError(
                f"{docx_path}: level {ilvl} numbering text mismatch"
            )
        level_details[str(ilvl)] = {
            "pstyle": pstyle.get(w("val"), ""),
            "lvl_text": lvl_text.get(w("val"), ""),
        }

    for level, style_id in enumerate(("Heading1", "Heading2", "Heading3")):
        if style_links[style_id]["ilvl"] != str(level):
            raise ConsumerError(
                f"{docx_path}: {style_id} ilvl mismatch: {style_links[style_id]}"
            )

    return {
        "status": "PASS",
        "num_id": num_id,
        "abstract_num_id": abstract_id,
        "styles": style_links,
        "levels": level_details,
    }


def _paragraph_style_and_text(p: ET.Element) -> Tuple[str, str]:
    pstyle = p.find("./w:pPr/w:pStyle", NS)
    style = pstyle.get(w("val"), "") if pstyle is not None else ""
    text = "".join(node.text or "" for node in p.findall(".//w:t", NS))
    return style, text


def inspect_rendered_headings(
    docx_path: Path,
    manifest: Dict[str, Any],
) -> Dict[str, Any]:
    document = _zip_xml(docx_path, "word/document.xml")
    observed: List[Tuple[str, str]] = []
    for paragraph in document.findall(".//w:body/w:p", NS):
        style, text = _paragraph_style_and_text(paragraph)
        if style in {"Heading1", "Heading2", "Heading3"}:
            observed.append((style, text))

    expected: List[Tuple[str, str]] = []
    for row in manifest.get("section_map", []):
        level = int(row["heading_level"])
        expected.append((f"Heading{level}", row["title"]))

    if observed != expected:
        raise ConsumerError(
            f"rendered heading sequence mismatch: observed={observed}, expected={expected}"
        )

    numbered = [
        {"style": style, "text": text}
        for style, text in observed
        if NUMBERED_TITLE_RE.match(text)
    ]
    if numbered:
        raise ConsumerError(
            f"literal heading numbering detected in rendered DOCX: {numbered}"
        )

    return {
        "heading_style_check": "PASS",
        "duplicate_numbering_check": "PASS",
        "observed": [
            {"style": style, "text": text}
            for style, text in observed
        ],
    }



def _paragraph_style_name(paragraph) -> str:
    style = paragraph.style
    return style.name if style is not None else ""


def _requirement_blocks(doc: Document) -> List[Tuple[int, int]]:
    """Return inclusive paragraph ranges for rendered requirement blocks."""
    paragraphs = doc.paragraphs
    blocks: List[Tuple[int, int]] = []
    index = 0
    while index < len(paragraphs):
        if not REQUIREMENT_TITLE_RE.match(paragraphs[index].text.strip()):
            index += 1
            continue

        start = index
        end = index
        cursor = index + 1
        while cursor < len(paragraphs):
            text = paragraphs[cursor].text.strip()
            style_name = _paragraph_style_name(paragraphs[cursor])
            if style_name in {"Heading 1", "Heading 2", "Heading 3"}:
                break
            if REQUIREMENT_TITLE_RE.match(text):
                break
            if text:
                end = cursor
            cursor += 1

        blocks.append((start, end))
        index = max(cursor, index + 1)
    return blocks


def _set_borderless_table(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "nil")
        borders.append(element)
    tbl_pr.append(borders)


def _set_zero_cell_margins(cell) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement("w:tcMar")
    for edge in ("top", "left", "bottom", "right"):
        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:w"), "0")
        element.set(qn("w:type"), "dxa")
        tc_mar.append(element)
    tc_pr.append(tc_mar)


def enforce_requirement_block_pagination(docx_path: Path) -> Dict[str, Any]:
    """Wrap each requirement block in one borderless non-splitting table row."""
    doc = Document(docx_path)
    blocks = _requirement_blocks(doc)

    # Move from the end so paragraph indices captured above remain valid.
    for start, end in reversed(blocks):
        paragraphs = doc.paragraphs
        block = paragraphs[start : end + 1]
        if not block:
            continue

        # Preserve paragraph-level protection as a secondary renderer hint.
        for index, paragraph in enumerate(block):
            paragraph.paragraph_format.keep_together = True
            paragraph.paragraph_format.keep_with_next = index < len(block) - 1

        table = doc.add_table(rows=1, cols=1)
        _set_borderless_table(table)
        row = table.rows[0]
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)

        cell = row.cells[0]
        _set_zero_cell_margins(cell)

        # Position the table where the first requirement paragraph was.
        block[0]._p.addprevious(table._tbl)

        placeholder = cell.paragraphs[0]._p
        for paragraph in block:
            placeholder.addprevious(paragraph._p)
        placeholder.getparent().remove(placeholder)

    doc.save(docx_path)
    return {
        "status": "PASS",
        "requirement_block_count": len(blocks),
        "mode": "BORDERLESS_TABLE_ROW_CANT_SPLIT",
    }


def inspect_requirement_pagination(docx_path: Path) -> Dict[str, Any]:
    document = _zip_xml(docx_path, "word/document.xml")
    observations = []
    for row in document.findall(".//w:tr", NS):
        text = "".join(node.text or "" for node in row.findall(".//w:t", NS)).strip()
        match = re.search(r"REQ-\d+\s+[—-]\s+[^\\n]+", text)
        if not match:
            continue
        cant_split = row.find("./w:trPr/w:cantSplit", NS)
        if cant_split is None:
            raise ConsumerError(
                f"{docx_path}: requirement table row is missing w:cantSplit"
            )
        observations.append({"requirement_id": match.group(0), "cant_split": True})

    if not observations:
        raise ConsumerError(f"{docx_path}: no governed requirement table rows found")

    return {
        "status": "PASS",
        "requirement_block_count": len(observations),
        "mode": "BORDERLESS_TABLE_ROW_CANT_SPLIT",
        "observations": observations,
    }

def render_docx(
    markdown_path: Path,
    reference_docx: Path,
    output_docx: Path,
) -> None:
    if not reference_docx.exists():
        raise ConsumerError(f"reference DOCX missing: {reference_docx}")

    reference_proof = inspect_numbering_contract(reference_docx)
    if reference_proof["status"] != "PASS":
        raise ConsumerError("reference numbering contract failed")

    output_docx.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "pandoc",
        str(markdown_path),
        "-o",
        str(output_docx),
        f"--reference-doc={reference_docx}",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise ConsumerError(f"pandoc render failed: {result.stderr.strip()}")
    if not output_docx.exists() or output_docx.stat().st_size == 0:
        raise ConsumerError("pandoc completed without a non-empty DOCX")

    enforce_requirement_block_pagination(output_docx)


def build_return_receipt(
    manifest: Dict[str, Any],
    markdown_path: Path,
    reference_docx: Path,
    output_docx: Path,
) -> Dict[str, Any]:
    numbering = inspect_numbering_contract(output_docx)
    headings = inspect_rendered_headings(output_docx, manifest)
    pagination = inspect_requirement_pagination(output_docx)

    return {
        "schema": "docx_rtm.data_rich_document_render_receipt/1.0.0",
        "source_json_sha256": manifest["source"]["sha256"],
        "projection_markdown_sha256": sha256_file(markdown_path),
        "source_git_ref": manifest["source"]["git_ref"],
        "reference_doc_sha256": sha256_file(reference_docx),
        "rendered_docx_sha256": sha256_file(output_docx),
        "render_status": "PASS",
        "heading_style_check": headings["heading_style_check"],
        "template_numbering_check": numbering["status"],
        "duplicate_numbering_check": headings["duplicate_numbering_check"],
        "requirement_pagination_check": pagination["status"],
        "requirement_pagination_observations": pagination,
        "heading_observations": headings["observed"],
        "numbering_observations": numbering,
        "authority": {
            "authority_transfer": False,
            "rendered_output_authoritative": False,
            "engineering_credit": False,
            "compliance_credit": False,
            "semantic_writeback": "JSON_CHANGE_SET_ONLY",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--reference-doc", type=Path, required=True)
    parser.add_argument("--output-docx", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--expected-source-ref", default="")
    args = parser.parse_args()

    try:
        manifest = load_manifest(args.manifest)
        validate_manifest(
            manifest,
            args.markdown,
            expected_source_ref=args.expected_source_ref,
        )
        render_docx(args.markdown, args.reference_doc, args.output_docx)
        receipt = build_return_receipt(
            manifest,
            args.markdown,
            args.reference_doc,
            args.output_docx,
        )
    except (OSError, json.JSONDecodeError, ConsumerError) as exc:
        print(f"FAIL: {exc}")
        return 1

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"PASS: rendered DOCX -> {args.output_docx}")
    print(f"PASS: render receipt -> {args.receipt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
