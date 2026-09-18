#!/usr/bin/env python3
"""Build the deterministic reference DOCX for data-rich document projections."""

from __future__ import annotations

import argparse
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


NUM_ID = 77
ABSTRACT_NUM_ID = 77


def _set_attr(el, name: str, value: str) -> None:
    el.set(qn(name), value)


def _append(parent, tag: str, **attrs):
    el = OxmlElement(tag)
    for key, value in attrs.items():
        _set_attr(el, f"w:{key}", str(value))
    parent.append(el)
    return el


def _remove_children(parent, tag: str) -> None:
    full = qn(tag)
    for child in list(parent):
        if child.tag == full:
            parent.remove(child)


def _link_style_to_numbering(style, num_id: int, ilvl: int) -> None:
    ppr = style.element.get_or_add_pPr()
    _remove_children(ppr, "w:numPr")
    num_pr = OxmlElement("w:numPr")
    _append(num_pr, "w:ilvl", val=ilvl)
    _append(num_pr, "w:numId", val=num_id)
    ppr.append(num_pr)


def _install_multilevel_numbering(doc: Document) -> None:
    numbering = doc.part.numbering_part.element

    # Remove our deterministic IDs if the script is run against a previously
    # generated template. This makes regeneration idempotent.
    for child in list(numbering):
        if child.tag == qn("w:abstractNum") and child.get(qn("w:abstractNumId")) == str(ABSTRACT_NUM_ID):
            numbering.remove(child)
        elif child.tag == qn("w:num") and child.get(qn("w:numId")) == str(NUM_ID):
            numbering.remove(child)

    abstract = OxmlElement("w:abstractNum")
    _set_attr(abstract, "w:abstractNumId", str(ABSTRACT_NUM_ID))
    _append(abstract, "w:multiLevelType", val="multilevel")

    level_text = ["%1", "%1.%2", "%1.%2.%3"]
    for ilvl in range(3):
        lvl = OxmlElement("w:lvl")
        _set_attr(lvl, "w:ilvl", str(ilvl))
        _append(lvl, "w:start", val=1)
        _append(lvl, "w:numFmt", val="decimal")
        _append(lvl, "w:pStyle", val=f"Heading{ilvl + 1}")
        _append(lvl, "w:lvlText", val=level_text[ilvl])
        _append(lvl, "w:lvlJc", val="left")
        _append(lvl, "w:suff", val="space")

        ppr = OxmlElement("w:pPr")
        ind = OxmlElement("w:ind")
        _set_attr(ind, "w:left", str(ilvl * 360))
        _set_attr(ind, "w:hanging", "0")
        ppr.append(ind)
        lvl.append(ppr)

        abstract.append(lvl)

    numbering.append(abstract)

    num = OxmlElement("w:num")
    _set_attr(num, "w:numId", str(NUM_ID))
    _append(num, "w:abstractNumId", val=ABSTRACT_NUM_ID)
    numbering.append(num)

    for ilvl, name in enumerate(("Heading 1", "Heading 2", "Heading 3")):
        _link_style_to_numbering(doc.styles[name], NUM_ID, ilvl)


def _configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(11)

    sizes = {
        "Heading 1": 16,
        "Heading 2": 13.5,
        "Heading 3": 12,
    }
    for name, size in sizes.items():
        style = doc.styles[name]
        style.font.name = "Aptos Display"
        style.font.size = Pt(size)
        style.font.bold = True

    title = doc.styles["Title"]
    title.font.name = "Aptos Display"
    title.font.size = Pt(22)
    title.font.bold = True


def build_reference_docx(output: Path) -> Path:
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    _configure_styles(doc)
    _install_multilevel_numbering(doc)

    # Content is only a visual/structural fixture. Pandoc --reference-doc uses
    # the style, numbering and theme parts, not this body.
    doc.add_paragraph("Data-rich Document Reference", style="Title")
    doc.add_paragraph("Context and Scope", style="Heading 1")
    doc.add_paragraph("Reference template fixture for Heading 1.")
    doc.add_paragraph("Objectives", style="Heading 2")
    doc.add_paragraph("Reference template fixture for Heading 2.")
    doc.add_paragraph("Architecture Decision", style="Heading 1")
    doc.add_paragraph("Section and Content Model", style="Heading 2")
    doc.add_paragraph("Change Transactions", style="Heading 3")
    doc.add_paragraph("Reference template fixture for Heading 3.")

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("config/reference.docx"),
    )
    args = parser.parse_args()
    path = build_reference_docx(args.output)
    print(f"PASS: reference DOCX -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
