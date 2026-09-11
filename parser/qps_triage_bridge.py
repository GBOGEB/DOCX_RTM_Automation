#!/usr/bin/env python3
"""QPS triage bridge for parser outputs.

This module wires the ADR_OCD taxonomy and QPS triage applicability model into
parser-side processing without rewriting the existing parser engine. It consumes
existing enhanced parser outputs such as enhanced_rtm_elements,
enhanced_otc_elements, and enhanced_del_elements, then emits:

- qps_triage_items
- qps_triage_traceability_rows

The design is intentionally narrow and reversible: it can be called after
EnhancedParserEngine.parse_document() or used standalone by export scripts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from typing import Any, Iterable

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TAXONOMY_PATH = REPO_ROOT / "federation" / "ADR_OCD" / "taxonomy.yaml"
DEFAULT_APPLICABILITY_PATH = REPO_ROOT / "federation" / "ADR_OCD" / "qps_triage_applicability.yaml"


@dataclass
class QPSTriageItem:
    """Controlled triage item emitted from parser output."""

    triage_id: str
    source_id: str
    source_type: str
    source_content: str
    primary_lane: str
    secondary_lanes: list[str]
    disposition: str
    maturity_level: float
    priority_score: int
    evidence_class: str
    qps_refs: list[str]
    adr_refs: list[str]
    ocd_refs: list[str]
    rtm_refs: list[str]
    dtm_refs: list[str]
    corrigendum_refs: list[str]
    reasons: list[str]
    parser_tags: list[str]
    generated_at: str


@dataclass
class QPSTriageTraceabilityRow:
    """Flat export row for QPS to triage to downstream traceability."""

    row_id: str
    triage_id: str
    from_object: str
    from_type: str
    relation: str
    to_object: str
    to_type: str
    disposition: str
    maturity_level: float
    priority_score: int
    evidence_class: str


class QPSTriageBridge:
    """Bridge existing parser outputs to QPS triage objects."""

    def __init__(self, taxonomy_path: Path | str = DEFAULT_TAXONOMY_PATH, applicability_path: Path | str = DEFAULT_APPLICABILITY_PATH):
        self.taxonomy_path = Path(taxonomy_path)
        self.applicability_path = Path(applicability_path)
        self.taxonomy = self._load_yaml(self.taxonomy_path)
        self.applicability = self._load_yaml(self.applicability_path)
        self.dispositions = {item["disposition"] for item in self.applicability.get("triage_dispositions", [])}
        self.lane_ids = {item["lane_id"] for item in self.applicability.get("triage_lanes", [])}
        self.extraction_categories = set(self.taxonomy.get("extraction_categories", []))

    @staticmethod
    def _load_yaml(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Missing QPS triage bridge YAML: {path}")
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        if not isinstance(data, dict):
            raise ValueError(f"Expected mapping at root of {path}")
        return data

    @staticmethod
    def _stable_id(prefix: str, *parts: str) -> str:
        digest = sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
        return f"{prefix}-{digest}"

    def enrich_analysis(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """Return a copy of analysis with QPS triage items and trace rows."""
        triage_items = self.emit_triage_items(analysis)
        traceability_rows = self.export_traceability_rows(triage_items)
        enriched = dict(analysis)
        enriched["qps_triage_items"] = [asdict(item) for item in triage_items]
        enriched["qps_triage_traceability_rows"] = [asdict(row) for row in traceability_rows]
        enriched.setdefault("parsing_metadata", {})["qps_triage_bridge"] = {
            "taxonomy_path": str(self.taxonomy_path),
            "applicability_path": str(self.applicability_path),
            "generated_at": datetime.now().isoformat(),
            "triage_item_count": len(triage_items),
            "traceability_row_count": len(traceability_rows),
        }
        return enriched

    def emit_triage_items(self, analysis: dict[str, Any]) -> list[QPSTriageItem]:
        """Emit triage items from enhanced RTM, OTC, and DEL parser output."""
        items: list[QPSTriageItem] = []
        for source_type, entries in self._iter_sources(analysis):
            for entry in entries:
                items.append(self._item_from_entry(source_type, entry))
        return items

    def _iter_sources(self, analysis: dict[str, Any]) -> Iterable[tuple[str, list[dict[str, Any]]]]:
        source_map = {
            "RTM": "enhanced_rtm_elements",
            "OTC": "enhanced_otc_elements",
            "DTM": "enhanced_del_elements",
        }
        for source_type, key in source_map.items():
            entries = analysis.get(key, [])
            if isinstance(entries, list):
                yield source_type, [entry for entry in entries if isinstance(entry, dict)]

    def _item_from_entry(self, source_type: str, entry: dict[str, Any]) -> QPSTriageItem:
        source_id = str(entry.get("id") or self._stable_id("SRC", source_type, str(entry)))
        content = str(entry.get("content") or entry.get("requirement_text") or entry.get("description") or entry.get("objective") or "")
        tags = self._match_tags(content, source_type)
        lane = self._primary_lane(source_type, content)
        secondary_lanes = self._secondary_lanes(content, lane)
        disposition, reasons = self._disposition_and_reasons(entry, content)
        maturity_level = self._maturity_level(entry, disposition)
        evidence_class = self._evidence_class(disposition, maturity_level)
        priority_score = self._priority_score(content, lane, disposition)
        triage_id = self._stable_id("TRIAGE", source_type, source_id, content)

        return QPSTriageItem(
            triage_id=triage_id,
            source_id=source_id,
            source_type=source_type,
            source_content=content,
            primary_lane=lane,
            secondary_lanes=secondary_lanes,
            disposition=disposition,
            maturity_level=maturity_level,
            priority_score=priority_score,
            evidence_class=evidence_class,
            qps_refs=self._refs_for("QPS", source_type, source_id, content),
            adr_refs=self._refs_for("ADR", source_type, source_id, content),
            ocd_refs=self._refs_for("OCD", source_type, source_id, content),
            rtm_refs=[source_id] if source_type == "RTM" else [],
            dtm_refs=[source_id] if source_type == "DTM" else [],
            corrigendum_refs=self._refs_for("Corrigendum", source_type, source_id, content),
            reasons=reasons,
            parser_tags=tags,
            generated_at=datetime.now().isoformat(),
        )

    def _match_tags(self, content: str, source_type: str) -> list[str]:
        content_lower = content.lower()
        tags = [source_type.lower()]
        for collection_name in ["document_roles", "procurement_terms", "triage_terms"]:
            for item in self.taxonomy.get(collection_name, []):
                for tag in item.get("parser_tags", []):
                    tag_text = str(tag).lower()
                    if tag_text in content_lower or tag_text.replace("_", " ") in content_lower:
                        tags.append(str(tag))
        for category in self.taxonomy.get("extraction_categories", []):
            if str(category).replace("_", " ") in content_lower:
                tags.append(str(category))
        return sorted(set(tags))

    def _primary_lane(self, source_type: str, content: str) -> str:
        content_lower = content.lower()
        if source_type == "RTM":
            return "TRIAGE-QPS"
        if source_type == "OTC":
            return "TRIAGE-OCD"
        if source_type == "DTM":
            return "TRIAGE-RTM-DTM"
        if "adr" in content_lower or "decision" in content_lower or "architecture" in content_lower:
            return "TRIAGE-ADR"
        if "operational" in content_lower or "workflow" in content_lower or "scenario" in content_lower:
            return "TRIAGE-OCD"
        if "deliverable" in content_lower or "traceability" in content_lower:
            return "TRIAGE-RTM-DTM"
        if "qps" in content_lower or "shall" in content_lower or "requirement" in content_lower:
            return "TRIAGE-QPS"
        return "TRIAGE-QPS"

    @staticmethod
    def _secondary_lanes(content: str, primary_lane: str) -> list[str]:
        content_lower = content.lower()
        candidates = []
        if any(term in content_lower for term in ["architecture", "decision", "interface", "control"]):
            candidates.append("TRIAGE-ADR")
        if any(term in content_lower for term in ["operational", "scenario", "workflow", "maintenance", "training"]):
            candidates.append("TRIAGE-OCD")
        if any(term in content_lower for term in ["rtm", "dtm", "deliverable", "evidence", "traceability"]):
            candidates.append("TRIAGE-RTM-DTM")
        return sorted({lane for lane in candidates if lane != primary_lane})

    @staticmethod
    def _disposition_and_reasons(entry: dict[str, Any], content: str) -> tuple[str, list[str]]:
        reasons: list[str] = []
        confidence = float(entry.get("confidence_score") or 0.0)
        if not content.strip():
            return "REJECT", ["empty_source_content"]
        if confidence >= 0.8:
            return "ACCEPT", ["high_confidence_parser_output"]
        if confidence >= 0.6:
            return "NEEDS_REVIEW", ["medium_confidence_parser_output"]
        if any(term in content.lower() for term in ["tbd", "unknown", "missing", "source", "evidence"]):
            reasons.append("source_or_evidence_gap_detected")
            return "NEEDS_SOURCE", reasons
        reasons.append("low_confidence_or_unbound_parser_output")
        return "DEFER", reasons

    @staticmethod
    def _maturity_level(entry: dict[str, Any], disposition: str) -> float:
        confidence = float(entry.get("confidence_score") or 0.0)
        if disposition == "ACCEPT" and confidence >= 0.8:
            return 1.0
        if disposition in {"ACCEPT", "NEEDS_REVIEW"} and confidence >= 0.6:
            return 0.8
        if disposition == "NEEDS_SOURCE":
            return 0.3
        if disposition == "REJECT":
            return 0.0
        return 0.6 if confidence >= 0.4 else 0.3

    @staticmethod
    def _evidence_class(disposition: str, maturity_level: float) -> str:
        if disposition == "ACCEPT" and maturity_level >= 1.0:
            return "controlled"
        if maturity_level >= 0.8:
            return "traceable"
        if disposition == "NEEDS_SOURCE":
            return "source_missing"
        if disposition == "NEEDS_IMPLEMENTATION":
            return "implementation_missing"
        if disposition == "REJECT":
            return "rejected"
        return "structured"

    @staticmethod
    def _priority_score(content: str, lane: str, disposition: str) -> int:
        content_lower = content.lower()
        score = 0
        if disposition in {"NEEDS_SOURCE", "NEEDS_IMPLEMENTATION", "NEEDS_REVIEW"}:
            score += 3
        if lane == "TRIAGE-QPS":
            score += 2
        if any(term in content_lower for term in ["safety", "contract", "corrigendum", "shall", "fixed price"]):
            score += 4
        if any(term in content_lower for term in ["adr", "ocd", "rtm", "dtm", "deliverable", "evidence"]):
            score += 2
        return score

    def _refs_for(self, target: str, source_type: str, source_id: str, content: str) -> list[str]:
        content_lower = content.lower()
        if target == "QPS" and (source_type == "RTM" or "qps" in content_lower or "shall" in content_lower):
            return [source_id]
        if target == "ADR" and any(term in content_lower for term in ["adr", "architecture", "decision", "interface", "control"]):
            return [self._stable_id("ADR", source_id, content)]
        if target == "OCD" and any(term in content_lower for term in ["ocd", "operational", "scenario", "workflow", "maintenance", "training"]):
            return [self._stable_id("OCD", source_id, content)]
        if target == "Corrigendum" and any(term in content_lower for term in ["corrigendum", "amendment", "change", "negotiation"]):
            return [self._stable_id("COR", source_id, content)]
        return []

    def export_traceability_rows(self, triage_items: list[QPSTriageItem]) -> list[QPSTriageTraceabilityRow]:
        rows: list[QPSTriageTraceabilityRow] = []
        for item in triage_items:
            rows.append(self._row(item, item.source_id, item.source_type, "classified_as", item.triage_id, "Triage Item"))
            for ref in item.adr_refs:
                rows.append(self._row(item, item.triage_id, "Triage Item", "design_impact_to", ref, "ADR Design Decision"))
            for ref in item.ocd_refs:
                rows.append(self._row(item, item.triage_id, "Triage Item", "operational_impact_to", ref, "OCD Operational Scenario"))
            for ref in item.rtm_refs:
                rows.append(self._row(item, item.triage_id, "Triage Item", "traceability_impact_to", ref, "RTM Row"))
            for ref in item.dtm_refs:
                rows.append(self._row(item, item.triage_id, "Triage Item", "deliverable_impact_to", ref, "DTM Row"))
            for ref in item.corrigendum_refs:
                rows.append(self._row(item, item.triage_id, "Triage Item", "amendment_impact_to", ref, "Corrigendum Entry"))
        return rows

    def _row(self, item: QPSTriageItem, from_object: str, from_type: str, relation: str, to_object: str, to_type: str) -> QPSTriageTraceabilityRow:
        return QPSTriageTraceabilityRow(
            row_id=self._stable_id("TRACE", item.triage_id, from_object, relation, to_object),
            triage_id=item.triage_id,
            from_object=from_object,
            from_type=from_type,
            relation=relation,
            to_object=to_object,
            to_type=to_type,
            disposition=item.disposition,
            maturity_level=item.maturity_level,
            priority_score=item.priority_score,
            evidence_class=item.evidence_class,
        )
