#!/usr/bin/env python3
"""
Enhanced Document Parser Engine
Comprehensive parsing logic for RTM, OTC, DEL elements with recursive mapping.
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import yaml
from docx import Document
import logging

from parser.source_extractor import extract_document

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParsedElement:
    """Base class for parsed elements"""
    id: str
    type: str
    content: str
    metadata: Dict[str, Any]
    relationships: List[str]
    confidence_score: float


@dataclass
class RTMElement(ParsedElement):
    """Requirements Traceability Matrix element"""
    requirement_text: str
    category: str
    priority: str
    verification_method: str
    acceptance_criteria: str
    source_section: str


@dataclass
class OTCElement(ParsedElement):
    """Operational Test Case element"""
    test_name: str
    objective: str
    preconditions: str
    test_steps: List[str]
    expected_results: str
    linked_requirements: List[str]


@dataclass
class DELElement(ParsedElement):
    """Deliverable element"""
    deliverable_name: str
    description: str
    deliverable_type: str
    due_date: str
    responsible_party: str
    status: str
    dependencies: List[str]


class EnhancedParserEngine:
    """Enhanced parser engine with recursive mapping and bidirectional updates."""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.parsed_elements = []
        self.element_relationships = {}
        self.parsing_statistics = {}

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load parser configuration"""
        default_config = {
            "rtm_patterns": [
                r'(?i)requirement\s+(\w+[-_]?\d+)?\s*:?\s*(.+?)(?=\n|$)',
                r'(?i)req[-_](\d+)\s*:?\s*(.+?)(?=\n|$)',
                r'(?i)shall\s+(.+?)(?=\n|$)',
                r'(?i)must\s+(.+?)(?=\n|$)',
                r'(?i)the\s+system\s+shall\s+(.+?)(?=\n|$)'
            ],
            "otc_patterns": [
                r'(?i)test\s+case\s+(\w+[-_]?\d+)?\s*:?\s*(.+?)(?=\n|$)',
                r'(?i)test\s+(\d+)\s*:?\s*(.+?)(?=\n|$)',
                r'(?i)verification\s+(.+?)(?=\n|$)',
                r'(?i)testing\s+(.+?)(?=\n|$)'
            ],
            "del_patterns": [
                r'(?i)deliverable\s+(\w+[-_]?\d+)?\s*:?\s*(.+?)(?=\n|$)',
                r'(?i)document\s+(.+?)(?=\n|$)',
                r'(?i)report\s+(.+?)(?=\n|$)',
                r'(?i)specification\s+(.+?)(?=\n|$)'
            ],
            "confidence_thresholds": {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
        }

        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)

        return default_config

    def parse_document(self, doc_path: str, analysis_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Parse a document, then apply enhanced mapping and scoring.

        When ``analysis_data`` is omitted the engine now performs real DOCX source
        extraction through ``parser.source_extractor`` rather than returning empty
        RTM/OTC/DEL populations. Source extraction remains candidate discovery only;
        downstream scoring does not turn lexical matches into formal compliance.
        """
        logger.info(f"Starting enhanced parsing of {doc_path}")

        if analysis_data is None:
            analysis_data = extract_document(doc_path)

        sections = analysis_data.get('sections', [])
        rtm_requirements = analysis_data.get('rtm_requirements', [])
        otc_elements = analysis_data.get('otc_elements', [])
        del_deliverables = analysis_data.get('del_deliverables', [])

        enhanced_rtm = self._enhance_rtm_elements(rtm_requirements, sections)
        enhanced_otc = self._enhance_otc_elements(otc_elements, sections)
        enhanced_del = self._enhance_del_elements(del_deliverables, sections)

        relationships = self._build_relationship_mapping(enhanced_rtm, enhanced_otc, enhanced_del)
        statistics = self._generate_parsing_statistics(enhanced_rtm, enhanced_otc, enhanced_del)

        result = {
            "parsing_metadata": {
                "document_path": doc_path,
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "2.1.0",
                "source_extraction": "DIRECT_DOCX" if analysis_data.get("source") else "SUPPLIED_ANALYSIS_DATA",
                "authority_boundary": (
                    "Candidate source extraction and enrichment only; formal compliance, "
                    "acceptance and current QPS authority require governed source binding."
                ),
                "confidence_scores": statistics.get("confidence_distribution", {})
            },
            "enhanced_rtm_elements": [asdict(elem) for elem in enhanced_rtm],
            "enhanced_otc_elements": [asdict(elem) for elem in enhanced_otc],
            "enhanced_del_elements": [asdict(elem) for elem in enhanced_del],
            "relationship_mapping": relationships,
            "parsing_statistics": statistics,
            "recursive_mapping": self._create_recursive_mapping(enhanced_rtm, enhanced_otc, enhanced_del)
        }

        logger.info(
            "Enhanced parsing completed. Found %s RTM, %s OTC, %s DEL elements",
            len(enhanced_rtm), len(enhanced_otc), len(enhanced_del)
        )
        return result

    def _parse_from_document(self, document: Document) -> Tuple[List, List, List, List]:
        """Deprecated compatibility hook.

        Direct document parsing is source-path based so source location/provenance can
        be retained. Call ``parse_document(path)`` instead.
        """
        raise NotImplementedError(
            "Use parse_document(doc_path) for direct source extraction; "
            "the Document-object compatibility hook is intentionally deprecated."
        )

    def _enhance_rtm_elements(self, rtm_requirements: List[Dict], sections: List[Dict]) -> List[RTMElement]:
        """Enhance RTM elements with advanced processing"""
        enhanced_elements = []

        for req in rtm_requirements:
            confidence = self._calculate_confidence_score(req.get('description', ''), 'rtm')
            category = self._advanced_categorization(req.get('description', ''))
            relationships = self._extract_relationships(req.get('description', ''), sections)

            enhanced_element = RTMElement(
                id=req.get('id', ''),
                type='RTM',
                content=req.get('description', ''),
                metadata={
                    'original_data': req,
                    'enhanced_at': datetime.now().isoformat(),
                    'processing_version': '2.1'
                },
                relationships=relationships,
                confidence_score=confidence,
                requirement_text=req.get('description', ''),
                category=category,
                priority=req.get('priority', 'Medium'),
                verification_method=req.get('verification_method', 'Review'),
                acceptance_criteria=req.get('acceptance_criteria', 'TBD'),
                source_section=req.get('source_section', '')
            )

            enhanced_elements.append(enhanced_element)

        return enhanced_elements

    def _enhance_otc_elements(self, otc_elements: List[Dict], sections: List[Dict]) -> List[OTCElement]:
        """Enhance OTC elements with advanced processing"""
        enhanced_elements = []

        for otc in otc_elements:
            confidence = self._calculate_confidence_score(otc.get('objective', ''), 'otc')
            relationships = self._extract_relationships(otc.get('objective', ''), sections)

            enhanced_element = OTCElement(
                id=otc.get('id', ''),
                type='OTC',
                content=otc.get('objective', ''),
                metadata={
                    'original_data': otc,
                    'enhanced_at': datetime.now().isoformat(),
                    'processing_version': '2.1'
                },
                relationships=relationships,
                confidence_score=confidence,
                test_name=otc.get('name', ''),
                objective=otc.get('objective', ''),
                preconditions=otc.get('preconditions', ''),
                test_steps=otc.get('test_steps', []),
                expected_results=otc.get('expected_results', ''),
                linked_requirements=otc.get('linked_requirements', [])
            )

            enhanced_elements.append(enhanced_element)

        return enhanced_elements

    def _enhance_del_elements(self, del_deliverables: List[Dict], sections: List[Dict]) -> List[DELElement]:
        """Enhance DEL elements with advanced processing"""
        enhanced_elements = []

        for del_item in del_deliverables:
            confidence = self._calculate_confidence_score(del_item.get('description', ''), 'del')
            relationships = self._extract_relationships(del_item.get('description', ''), sections)

            enhanced_element = DELElement(
                id=del_item.get('id', ''),
                type='DEL',
                content=del_item.get('description', ''),
                metadata={
                    'original_data': del_item,
                    'enhanced_at': datetime.now().isoformat(),
                    'processing_version': '2.1'
                },
                relationships=relationships,
                confidence_score=confidence,
                deliverable_name=del_item.get('name', ''),
                description=del_item.get('description', ''),
                deliverable_type=del_item.get('type', ''),
                due_date=del_item.get('due_date', ''),
                responsible_party=del_item.get('responsible_party', ''),
                status=del_item.get('status', ''),
                dependencies=del_item.get('dependencies', [])
            )

            enhanced_elements.append(enhanced_element)

        return enhanced_elements

    def _calculate_confidence_score(self, text: str, element_type: str) -> float:
        """Calculate confidence score based on text characteristics"""
        if not text:
            return 0.0

        score = 0.5
        patterns = self.config.get(f'{element_type}_patterns', [])
        if any(re.search(pattern, text) for pattern in patterns):
            score += 0.2
        if len(text) > 50:
            score += 0.1
        if re.search(r'\d', text):
            score += 0.1
        return min(score, 1.0)

    def _advanced_categorization(self, text: str) -> str:
        """Categorize a requirement with lightweight keyword heuristics."""
        lower = text.lower()
        categories = {
            'Safety': ['safety', 'hazard', 'interlock', 'emergency', 'relief'],
            'Performance': ['capacity', 'flow', 'pressure', 'temperature', 'efficiency'],
            'Verification': ['fat', 'sat', 'test', 'verification', 'acceptance'],
            'Reliability': ['reliability', 'availability', 'mtbf', 'mttr', 'redundancy'],
            'Maintenance': ['maintenance', 'spare', 'repair', 'service'],
        }
        for category, words in categories.items():
            if any(word in lower for word in words):
                return category
        return 'General'

    def _extract_relationships(self, text: str, sections: List[Dict]) -> List[str]:
        """Extract explicit RTM/REQ/OTC/DEL style identifiers from text."""
        return sorted(set(re.findall(r'\b(?:RTM|REQ|OTC|DEL|CReq)[-_ ]?\d+(?:\.\d+)*\b', text, re.I)))

    def _build_relationship_mapping(self, rtm, otc, deliverables):
        """Build a compact relationship map keyed by element ID."""
        mapping = {}
        for elem in [*rtm, *otc, *deliverables]:
            mapping[elem.id] = list(elem.relationships)
        return mapping

    def _generate_parsing_statistics(self, rtm, otc, deliverables):
        """Generate basic parsing statistics."""
        elements = [*rtm, *otc, *deliverables]
        buckets = {'high': 0, 'medium': 0, 'low': 0}
        for elem in elements:
            score = elem.confidence_score
            if score >= self.config['confidence_thresholds']['high']:
                buckets['high'] += 1
            elif score >= self.config['confidence_thresholds']['medium']:
                buckets['medium'] += 1
            else:
                buckets['low'] += 1
        return {
            'total': len(elements),
            'rtm': len(rtm),
            'otc': len(otc),
            'del': len(deliverables),
            'confidence_distribution': buckets,
        }

    def _create_recursive_mapping(self, rtm, otc, deliverables):
        """Return a serializable recursive mapping projection."""
        return {
            'rtm': {elem.id: elem.relationships for elem in rtm},
            'otc': {elem.id: elem.relationships for elem in otc},
            'deliverables': {elem.id: elem.relationships for elem in deliverables},
        }

    def export_enhanced_analysis(self, output_dir: str) -> None:
        """Compatibility placeholder retained for existing callers."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
