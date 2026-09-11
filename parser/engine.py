#!/usr/bin/env python3
"""
Enhanced Document Parser Engine
Comprehensive parsing logic for RTM, OTC, DEL elements with recursive mapping
"""

import csv
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
    """Enhanced parser engine with recursive mapping and bidirectional updates"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.parsed_elements = []
        self.element_relationships = {}
        self.parsing_statistics = {}
        self.last_analysis_result: Optional[Dict[str, Any]] = None
        
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
            },
            "qps_triage": {
                "enabled": False,
                "taxonomy_path": "federation/ADR_OCD/taxonomy.yaml",
                "applicability_path": "federation/ADR_OCD/qps_triage_applicability.yaml",
                "fail_on_error": False
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f) or {}
                default_config.update(user_config)
        
        return default_config
    
    def parse_document(self, doc_path: str, analysis_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Parse document with enhanced logic and recursive mapping"""
        logger.info(f"Starting enhanced parsing of {doc_path}")
        
        if analysis_data:
            # Use existing analysis data
            sections = analysis_data.get('sections', [])
            rtm_requirements = analysis_data.get('rtm_requirements', [])
            otc_elements = analysis_data.get('otc_elements', [])
            del_deliverables = analysis_data.get('del_deliverables', [])
        else:
            # Parse from scratch
            document = Document(doc_path)
            sections, rtm_requirements, otc_elements, del_deliverables = self._parse_from_document(document)
        
        # Enhanced processing with recursive mapping
        enhanced_rtm = self._enhance_rtm_elements(rtm_requirements, sections)
        enhanced_otc = self._enhance_otc_elements(otc_elements, sections)
        enhanced_del = self._enhance_del_elements(del_deliverables, sections)
        
        # Build relationship mapping
        relationships = self._build_relationship_mapping(enhanced_rtm, enhanced_otc, enhanced_del)
        
        # Generate parsing statistics
        statistics = self._generate_parsing_statistics(enhanced_rtm, enhanced_otc, enhanced_del)
        
        result = {
            "parsing_metadata": {
                "document_path": doc_path,
                "parsed_at": datetime.now().isoformat(),
                "parser_version": "2.0.0",
                "confidence_scores": statistics.get("confidence_distribution", {})
            },
            "enhanced_rtm_elements": [asdict(elem) for elem in enhanced_rtm],
            "enhanced_otc_elements": [asdict(elem) for elem in enhanced_otc],
            "enhanced_del_elements": [asdict(elem) for elem in enhanced_del],
            "relationship_mapping": relationships,
            "parsing_statistics": statistics,
            "recursive_mapping": self._create_recursive_mapping(enhanced_rtm, enhanced_otc, enhanced_del)
        }
        
        result = self._maybe_enrich_qps_triage(result)
        self.last_analysis_result = result
        logger.info(f"Enhanced parsing completed. Found {len(enhanced_rtm)} RTM, {len(enhanced_otc)} OTC, {len(enhanced_del)} DEL elements")
        return result

    def _maybe_enrich_qps_triage(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Optionally enrich parser output with QPS triage items and trace rows."""
        qps_config = self.config.get("qps_triage", {})
        if not isinstance(qps_config, dict) or not qps_config.get("enabled", False):
            result.setdefault("parsing_metadata", {})["qps_triage_bridge"] = {
                "enabled": False,
                "reason": "disabled_by_config"
            }
            return result

        try:
            from parser.qps_triage_bridge import QPSTriageBridge

            bridge = QPSTriageBridge(
                taxonomy_path=qps_config.get("taxonomy_path", "federation/ADR_OCD/taxonomy.yaml"),
                applicability_path=qps_config.get("applicability_path", "federation/ADR_OCD/qps_triage_applicability.yaml"),
            )
            return bridge.enrich_analysis(result)
        except Exception as exc:  # pragma: no cover - defensive runtime guard
            logger.exception("QPS triage enrichment failed")
            if qps_config.get("fail_on_error", False):
                raise
            result.setdefault("parsing_metadata", {})["qps_triage_bridge"] = {
                "enabled": True,
                "status": "failed",
                "error": str(exc)
            }
            return result
    
    def _parse_from_document(self, document: Document) -> Tuple[List, List, List, List]:
        """Parse document from scratch"""
        # This would implement the basic parsing logic
        # For now, return empty lists as we're using existing analysis
        return [], [], [], []
    
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
                    'processing_version': '2.0'
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
                    'processing_version': '2.0'
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
                    'processing_version': '2.0'
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
        """Calculate confidence score for parsed element"""
        score = 0.5
        if len(text) > 50:
            score += 0.1
        if len(text) > 100:
            score += 0.1
        patterns = self.config.get(f"{element_type}_patterns", [])
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 0.2
                break
        keywords = {
            'rtm': ['shall', 'must', 'requirement', 'system', 'function'],
            'otc': ['test', 'verify', 'check', 'validate', 'ensure'],
            'del': ['deliverable', 'document', 'report', 'specification', 'output']
        }
        element_keywords = keywords.get(element_type, [])
        keyword_matches = sum(1 for keyword in element_keywords if keyword.lower() in text.lower())
        score += min(keyword_matches * 0.1, 0.3)
        return min(score, 1.0)
    
    def _advanced_categorization(self, text: str) -> str:
        """Advanced categorization using multiple criteria"""
        text_lower = text.lower()
        if any(word in text_lower for word in ['performance', 'speed', 'latency', 'throughput', 'response']):
            return "Performance"
        elif any(word in text_lower for word in ['security', 'authentication', 'authorization', 'encryption']):
            return "Security"
        elif any(word in text_lower for word in ['interface', 'api', 'integration', 'communication']):
            return "Interface"
        elif any(word in text_lower for word in ['usability', 'user', 'interface', 'experience']):
            return "Usability"
        elif any(word in text_lower for word in ['reliability', 'availability', 'fault', 'error']):
            return "Reliability"
        elif any(word in text_lower for word in ['maintainability', 'maintenance', 'support']):
            return "Maintainability"
        elif any(word in text_lower for word in ['functional', 'function', 'operation', 'behavior']):
            return "Functional"
        else:
            return "General"
    
    def _extract_relationships(self, text: str, sections: List[Dict]) -> List[str]:
        """Extract relationships to other elements"""
        relationships = []
        ref_patterns = [
            r'(?i)section\s+(\d+(?:\.\d+)*)',
            r'(?i)requirement\s+(\w+[-_]?\d+)',
            r'(?i)test\s+(\w+[-_]?\d+)',
            r'(?i)deliverable\s+(\w+[-_]?\d+)'
        ]
        for pattern in ref_patterns:
            matches = re.findall(pattern, text)
            relationships.extend(matches)
        return list(set(relationships))
    
    def _build_relationship_mapping(self, rtm_elements: List[RTMElement], otc_elements: List[OTCElement], del_elements: List[DELElement]) -> Dict[str, Any]:
        """Build comprehensive relationship mapping"""
        mapping = {
            "rtm_to_otc": {},
            "rtm_to_del": {},
            "otc_to_del": {},
            "cross_references": {},
            "dependency_graph": {}
        }
        all_elements = rtm_elements + otc_elements + del_elements
        for element in all_elements:
            mapping["cross_references"][element.id] = {
                "type": element.type,
                "relationships": element.relationships,
                "confidence": element.confidence_score
            }
        for rtm in rtm_elements:
            related_otc = [otc.id for otc in otc_elements if rtm.id in otc.linked_requirements]
            if related_otc:
                mapping["rtm_to_otc"][rtm.id] = related_otc
            related_del = [del_elem.id for del_elem in del_elements if any(rel in del_elem.dependencies for rel in rtm.relationships)]
            if related_del:
                mapping["rtm_to_del"][rtm.id] = related_del
        return mapping
    
    def _generate_parsing_statistics(self, rtm_elements: List[RTMElement], otc_elements: List[OTCElement], del_elements: List[DELElement]) -> Dict[str, Any]:
        """Generate comprehensive parsing statistics"""
        all_elements = rtm_elements + otc_elements + del_elements
        confidence_scores = [elem.confidence_score for elem in all_elements]
        confidence_distribution = {
            "high": len([s for s in confidence_scores if s >= self.config["confidence_thresholds"]["high"]]),
            "medium": len([s for s in confidence_scores if self.config["confidence_thresholds"]["medium"] <= s < self.config["confidence_thresholds"]["high"]]),
            "low": len([s for s in confidence_scores if s < self.config["confidence_thresholds"]["medium"]])
        }
        rtm_categories = {}
        for rtm in rtm_elements:
            rtm_categories[rtm.category] = rtm_categories.get(rtm.category, 0) + 1
        total_relationships = sum(len(elem.relationships) for elem in all_elements)
        return {
            "total_elements": len(all_elements),
            "rtm_count": len(rtm_elements),
            "otc_count": len(otc_elements),
            "del_count": len(del_elements),
            "confidence_distribution": confidence_distribution,
            "average_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0,
            "rtm_category_distribution": rtm_categories,
            "total_relationships": total_relationships,
            "relationship_density": total_relationships / len(all_elements) if all_elements else 0
        }
    
    def _create_recursive_mapping(self, rtm_elements: List[RTMElement], otc_elements: List[OTCElement], del_elements: List[DELElement]) -> Dict[str, Any]:
        """Create recursive mapping structure for bidirectional updates"""
        recursive_map = {
            "element_hierarchy": {},
            "dependency_chains": {},
            "update_propagation_rules": {},
            "bidirectional_links": {}
        }
        for rtm in rtm_elements:
            section_key = rtm.source_section.split(' - ')[0] if ' - ' in rtm.source_section else rtm.source_section
            if section_key not in recursive_map["element_hierarchy"]:
                recursive_map["element_hierarchy"][section_key] = {"rtm": [], "otc": [], "del": []}
            recursive_map["element_hierarchy"][section_key]["rtm"].append(rtm.id)
        for otc in otc_elements:
            for req_id in otc.linked_requirements:
                if req_id not in recursive_map["bidirectional_links"]:
                    recursive_map["bidirectional_links"][req_id] = {"otc": [], "del": []}
                recursive_map["bidirectional_links"][req_id]["otc"].append(otc.id)
        for del_elem in del_elements:
            if del_elem.dependencies:
                recursive_map["dependency_chains"][del_elem.id] = del_elem.dependencies
        recursive_map["update_propagation_rules"] = {
            "rtm_update": ["linked_otc", "dependent_del"],
            "otc_update": ["linked_rtm", "related_del"],
            "del_update": ["dependency_chain", "linked_rtm"]
        }
        return recursive_map
    
    def update_element(self, element_id: str, updates: Dict[str, Any], propagate: bool = True) -> Dict[str, Any]:
        """Update element with bidirectional propagation"""
        logger.info(f"Updating element {element_id} with propagation={propagate}")
        update_result = {
            "updated_element": element_id,
            "changes": updates,
            "propagated_updates": [],
            "timestamp": datetime.now().isoformat()
        }
        if propagate:
            propagated = self._propagate_updates(element_id, updates)
            update_result["propagated_updates"] = propagated
        return update_result
    
    def _propagate_updates(self, element_id: str, updates: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Propagate updates to related elements"""
        propagated = []
        return propagated

    def _write_json(self, path: Path, payload: Any) -> None:
        with path.open('w', encoding='utf-8') as handle:
            json.dump(payload, handle, indent=2)

    def _write_csv(self, path: Path, rows: List[Dict[str, Any]]) -> None:
        if not rows:
            return
        fieldnames = sorted({field for row in rows for field in row.keys()})
        with path.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def _build_qps_triage_downstream_index(self, result: Dict[str, Any]) -> Dict[str, Any]:
        rows = result.get('qps_triage_traceability_rows', [])
        if not isinstance(rows, list):
            rows = []
        by_relation: Dict[str, List[Dict[str, Any]]] = {}
        by_target_type: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            by_relation.setdefault(str(row.get('relation', 'unknown')), []).append(row)
            by_target_type.setdefault(str(row.get('to_type', 'unknown')), []).append(row)
        return {
            'generated_at': datetime.now().isoformat(),
            'source': 'EnhancedParserEngine.export_enhanced_analysis',
            'triage_item_count': len(result.get('qps_triage_items', [])),
            'traceability_row_count': len(rows),
            'by_relation_counts': {key: len(value) for key, value in by_relation.items()},
            'by_target_type_counts': {key: len(value) for key, value in by_target_type.items()},
            'rtm_rows': by_target_type.get('RTM Row', []),
            'dtm_rows': by_target_type.get('DTM Row', []),
            'adr_rows': by_target_type.get('ADR Design Decision', []),
            'ocd_rows': by_target_type.get('OCD Operational Scenario', []),
            'corrigendum_rows': by_target_type.get('Corrigendum Entry', [])
        }
    
    def export_enhanced_analysis(self, output_path: str) -> None:
        """Persist enhanced analysis results and QPS triage exports when available."""
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        result = self.last_analysis_result
        if result is None:
            metadata = {
                'exported_at': datetime.now().isoformat(),
                'status': 'no_analysis_result',
                'message': 'Call parse_document() before export_enhanced_analysis().'
            }
            self._write_json(output_dir / 'export_manifest.json', metadata)
            logger.warning('No enhanced analysis result is available to export')
            return

        self._write_json(output_dir / 'enhanced_analysis.json', result)
        self._write_json(output_dir / 'enhanced_rtm_elements.json', result.get('enhanced_rtm_elements', []))
        self._write_json(output_dir / 'enhanced_otc_elements.json', result.get('enhanced_otc_elements', []))
        self._write_json(output_dir / 'enhanced_del_elements.json', result.get('enhanced_del_elements', []))
        self._write_json(output_dir / 'relationship_mapping.json', result.get('relationship_mapping', {}))
        self._write_json(output_dir / 'recursive_mapping.json', result.get('recursive_mapping', {}))
        self._write_json(output_dir / 'parsing_statistics.json', result.get('parsing_statistics', {}))

        triage_items = result.get('qps_triage_items', [])
        traceability_rows = result.get('qps_triage_traceability_rows', [])
        triage_exports = []
        if triage_items:
            self._write_json(output_dir / 'qps_triage_items.json', triage_items)
            triage_exports.append('qps_triage_items.json')
        if traceability_rows:
            self._write_json(output_dir / 'qps_triage_traceability_rows.json', traceability_rows)
            self._write_csv(output_dir / 'qps_triage_traceability_rows.csv', traceability_rows)
            downstream_index = self._build_qps_triage_downstream_index(result)
            self._write_json(output_dir / 'qps_triage_downstream_index.json', downstream_index)
            self._write_csv(output_dir / 'qps_triage_rtm_rows.csv', downstream_index.get('rtm_rows', []))
            self._write_csv(output_dir / 'qps_triage_dtm_rows.csv', downstream_index.get('dtm_rows', []))
            triage_exports.extend([
                'qps_triage_traceability_rows.json',
                'qps_triage_traceability_rows.csv',
                'qps_triage_downstream_index.json',
                'qps_triage_rtm_rows.csv',
                'qps_triage_dtm_rows.csv'
            ])

        export_manifest = {
            'exported_at': datetime.now().isoformat(),
            'output_path': str(output_dir),
            'core_exports': [
                'enhanced_analysis.json',
                'enhanced_rtm_elements.json',
                'enhanced_otc_elements.json',
                'enhanced_del_elements.json',
                'relationship_mapping.json',
                'recursive_mapping.json',
                'parsing_statistics.json'
            ],
            'qps_triage_exports': triage_exports,
            'qps_triage_enabled': bool(triage_items or traceability_rows),
            'triage_item_count': len(triage_items) if isinstance(triage_items, list) else 0,
            'traceability_row_count': len(traceability_rows) if isinstance(traceability_rows, list) else 0
        }
        self._write_json(output_dir / 'export_manifest.json', export_manifest)
        logger.info(f"Enhanced analysis exported to {output_path}")

def main():
    """Main function for testing the parser engine"""
    parser = EnhancedParserEngine()
    analysis_path = "/home/ubuntu/workspace/output/analysis.json"
    if Path(analysis_path).exists():
        with open(analysis_path, 'r') as f:
            analysis_data = json.load(f)
        result = parser.parse_document("test_document.docx", analysis_data)
        output_path = Path("enhanced_parsing_results.json")
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Enhanced parsing completed. Results saved to {output_path}")
    else:
        print("No analysis data found. Please run the document processor first.")

if __name__ == "__main__":
    main()
