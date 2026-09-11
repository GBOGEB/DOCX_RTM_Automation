#!/usr/bin/env python3
"""Validate the ADR_OCD QPS bridge artifacts.

This validator intentionally uses only dependencies already present in the
repository requirements: PyYAML plus the Python standard library. It performs a
focused structural validation against the bridge JSON schema files and catches
missing required fields, duplicate glossary IDs, broken core terminology, QPS
child-authority violations, and QPS triage applicability gaps.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GLOSSARY = REPO_ROOT / "glossary" / "GLOSSARY.yaml"
DEFAULT_MANIFEST = REPO_ROOT / "federation" / "ADR_OCD" / "bridge_manifest.yaml"
DEFAULT_TAXONOMY = REPO_ROOT / "federation" / "ADR_OCD" / "taxonomy.yaml"
DEFAULT_APPLICABILITY = REPO_ROOT / "federation" / "ADR_OCD" / "qps_triage_applicability.yaml"
GLOSSARY_SCHEMA = REPO_ROOT / "schemas" / "glossary.schema.json"
MANIFEST_SCHEMA = REPO_ROOT / "schemas" / "adr_ocd_bridge_manifest.schema.json"

QPS_AUTHORITY_REPO = "GBOGEB/cryoplant-project"
QPS_AUTHORITY_ARTIFACT = "ocd-adr/20_canonical/control/QPS_GLOBAL_ADR_OCD_SSOT_v1.json"
QPS_CANONICAL_OCD = "ocd-adr/20_canonical/ocd/QPS_OCD_v0.8_CONSOLIDATED.md"
QPS_CANONICAL_ADR_REGISTER = "ocd-adr/20_canonical/adr/QPS_ADR_REGISTER_v0.3.md"
ADR_TERM = "Architecture Decision Record"
OCD_TERM = "Operational Concept Description"


class ValidationError(ValueError):
    """Raised when bridge validation fails."""


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"Missing YAML file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValidationError(f"Expected mapping at root of {path}")
    return data


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValidationError(f"Missing JSON schema file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValidationError(f"Expected mapping at root of {path}")
    return data


def require_keys(data: dict[str, Any], required: list[str], label: str) -> None:
    missing = [key for key in required if key not in data]
    if missing:
        raise ValidationError(f"{label} missing required keys: {', '.join(missing)}")


def schema_required_keys(schema: dict[str, Any]) -> list[str]:
    required = schema.get("required", [])
    if not isinstance(required, list):
        raise ValidationError("Schema required field must be a list")
    return [str(item) for item in required]


def validate_authority_source(authority: Any, label: str, *, projection_role: str | None = None) -> None:
    if not isinstance(authority, dict):
        raise ValidationError(f"{label} must be a mapping")
    require_keys(
        authority,
        ["repo", "artifact", "authority_scope", "projection_role", "engineering_promotion_forbidden", "source_or_payload_digest_when_exchanged"],
        label,
    )
    if authority["repo"] != QPS_AUTHORITY_REPO:
        raise ValidationError(f"{label}.repo must be {QPS_AUTHORITY_REPO}")
    if authority["artifact"] != QPS_AUTHORITY_ARTIFACT:
        raise ValidationError(f"{label}.artifact must be {QPS_AUTHORITY_ARTIFACT}")
    if authority["authority_scope"] != "QPS_ENGINEERING":
        raise ValidationError(f"{label}.authority_scope must be QPS_ENGINEERING")
    if authority["engineering_promotion_forbidden"] is not True:
        raise ValidationError(f"{label}.engineering_promotion_forbidden must be true")
    if authority["source_or_payload_digest_when_exchanged"] != "REQUIRED":
        raise ValidationError(f"{label}.source_or_payload_digest_when_exchanged must be REQUIRED")
    if projection_role and authority["projection_role"] != projection_role:
        raise ValidationError(f"{label}.projection_role must be {projection_role}")


def validate_glossary(glossary: dict[str, Any], schema: dict[str, Any]) -> None:
    require_keys(glossary, schema_required_keys(schema), "glossary")
    metadata = glossary["metadata"]
    terms = glossary["terms"]
    if not isinstance(metadata, dict):
        raise ValidationError("glossary.metadata must be a mapping")
    if not isinstance(terms, list) or not terms:
        raise ValidationError("glossary.terms must be a non-empty list")

    metadata_required = schema["properties"]["metadata"].get("required", [])
    require_keys(metadata, metadata_required, "glossary.metadata")

    term_schema = schema["$defs"]["term"]
    term_required = term_schema.get("required", [])
    seen_ids: set[str] = set()
    standard_terms: set[str] = set()

    for index, term in enumerate(terms):
        if not isinstance(term, dict):
            raise ValidationError(f"glossary.terms[{index}] must be a mapping")
        require_keys(term, term_required, f"glossary.terms[{index}]")
        term_id = term["term_id"]
        if term_id in seen_ids:
            raise ValidationError(f"Duplicate glossary term_id: {term_id}")
        seen_ids.add(term_id)
        standard_terms.add(str(term["standard_term"]))
        if not isinstance(term.get("aliases"), list):
            raise ValidationError(f"{term_id}.aliases must be a list")
        if not isinstance(term.get("use_in"), list):
            raise ValidationError(f"{term_id}.use_in must be a list")

    expected_terms = {
        "QPS Requirements",
        "Invitation to Tender",
        "Fixed Price Offer",
        "Applicant",
        "Negotiation Stage",
        "Corrigendum",
        ADR_TERM,
        OCD_TERM,
    }
    missing_terms = sorted(expected_terms - standard_terms)
    if missing_terms:
        raise ValidationError("Glossary missing core terms: " + ", ".join(missing_terms))

    authority = metadata.get("qps_authority_source")
    if not isinstance(authority, dict) or authority.get("repo") != QPS_AUTHORITY_REPO or authority.get("artifact") != QPS_AUTHORITY_ARTIFACT:
        raise ValidationError("glossary.metadata.qps_authority_source must bind the QPS child global ADR/OCD SSOT")


def validate_manifest(manifest: dict[str, Any], schema: dict[str, Any]) -> None:
    require_keys(manifest, schema_required_keys(schema), "bridge_manifest")
    authority = manifest["qps_authority_source"]
    validate_authority_source(authority, "bridge_manifest.qps_authority_source", projection_role="TOOLING_TRANSFORM")
    if authority.get("canonical_ocd") != QPS_CANONICAL_OCD:
        raise ValidationError(f"bridge_manifest.qps_authority_source.canonical_ocd must be {QPS_CANONICAL_OCD}")
    if authority.get("canonical_adr_register") != QPS_CANONICAL_ADR_REGISTER:
        raise ValidationError(f"bridge_manifest.qps_authority_source.canonical_adr_register must be {QPS_CANONICAL_ADR_REGISTER}")

    federated = manifest["federated_documents"]
    if not isinstance(federated, dict):
        raise ValidationError("bridge_manifest.federated_documents must be a mapping")
    require_keys(federated, ["qps_requirements", "adr", "ocd"], "bridge_manifest.federated_documents")

    for doc_key in ["qps_requirements", "adr", "ocd"]:
        document = federated[doc_key]
        if not isinstance(document, dict):
            raise ValidationError(f"federated_documents.{doc_key} must be a mapping")
        require_keys(document, ["canonical_name", "role", "outputs"], f"federated_documents.{doc_key}")
        if not isinstance(document["outputs"], list) or not document["outputs"]:
            raise ValidationError(f"federated_documents.{doc_key}.outputs must be a non-empty list")

    if federated["adr"]["canonical_name"] != ADR_TERM:
        raise ValidationError(f"federated_documents.adr.canonical_name must be {ADR_TERM}")
    if federated["ocd"]["canonical_name"] != OCD_TERM:
        raise ValidationError(f"federated_documents.ocd.canonical_name must be {OCD_TERM}")

    stages = manifest["change_process"].get("stages", [])
    if "final_corrigendum" not in stages:
        raise ValidationError("change_process.stages must include final_corrigendum")

    edges = manifest.get("traceability_edges", [])
    if not isinstance(edges, list) or not edges:
        raise ValidationError("traceability_edges must be a non-empty list")
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            raise ValidationError(f"traceability_edges[{index}] must be a mapping")
        require_keys(edge, ["from", "to", "relation"], f"traceability_edges[{index}]")

    quality_gates = manifest.get("quality_gates", [])
    if not isinstance(quality_gates, list) or not quality_gates:
        raise ValidationError("quality_gates must be a non-empty list")
    for index, gate in enumerate(quality_gates):
        if not isinstance(gate, dict):
            raise ValidationError(f"quality_gates[{index}] must be a mapping")
        require_keys(gate, ["id", "name", "rule"], f"quality_gates[{index}]")
    if not any(gate.get("name") == "child_authority_binding" for gate in quality_gates if isinstance(gate, dict)):
        raise ValidationError("quality_gates must include child_authority_binding")


def validate_taxonomy(taxonomy: dict[str, Any]) -> None:
    require_keys(
        taxonomy,
        ["taxonomy_id", "version", "status", "purpose", "qps_authority_source", "document_roles", "procurement_terms", "traceability_relations", "extraction_categories"],
        "taxonomy",
    )
    validate_authority_source(taxonomy["qps_authority_source"], "taxonomy.qps_authority_source", projection_role="TOOLING_TAXONOMY")
    roles = taxonomy["document_roles"]
    if not isinstance(roles, list) or len(roles) < 3:
        raise ValidationError("taxonomy.document_roles must include QPS, ADR, and OCD roles")
    role_terms = {str(role.get("standard_term")) for role in roles if isinstance(role, dict)}
    for expected in ["QPS Requirements", ADR_TERM, OCD_TERM]:
        if expected not in role_terms:
            raise ValidationError(f"taxonomy missing document role: {expected}")

    categories = set(taxonomy.get("extraction_categories", []))
    expected_categories = {"qps_requirement", "adr_decision", "ocd_scenario", "triage_item", "triage_disposition", "maturity_level"}
    missing_categories = sorted(expected_categories - categories)
    if missing_categories:
        raise ValidationError("taxonomy missing QPS triage extraction categories: " + ", ".join(missing_categories))


def validate_applicability(applicability: dict[str, Any]) -> None:
    require_keys(
        applicability,
        ["applicability_id", "version", "status", "purpose", "qps_authority_source", "scope", "terminology_policy", "triage_lanes", "triage_dispositions", "maturity_levels", "priority_scoring", "qps_to_triage_edges", "control_gates"],
        "qps_triage_applicability",
    )
    validate_authority_source(applicability["qps_authority_source"], "qps_triage_applicability.qps_authority_source", projection_role="TOOLING_TRIAGE")

    applies_to = set(applicability["scope"].get("applies_to", []))
    for expected in ["QPS Requirements", ADR_TERM, OCD_TERM, "Triage", "Requirements Traceability Matrix", "Deliverables Traceability Matrix"]:
        if expected not in applies_to:
            raise ValidationError(f"qps_triage_applicability.scope.applies_to missing {expected}")

    policy = applicability["terminology_policy"]
    if policy.get("preferred_outward_facing") != "QPS Requirements":
        raise ValidationError("terminology_policy.preferred_outward_facing must be QPS Requirements")
    if policy.get("legacy_internal_alias") != "RFO":
        raise ValidationError("terminology_policy.legacy_internal_alias must be RFO")

    lanes = applicability["triage_lanes"]
    if not isinstance(lanes, list) or not lanes:
        raise ValidationError("triage_lanes must be a non-empty list")
    lane_ids = {lane.get("lane_id") for lane in lanes if isinstance(lane, dict)}
    for expected in ["TRIAGE-QPS", "TRIAGE-ADR", "TRIAGE-OCD", "TRIAGE-RTM-DTM"]:
        if expected not in lane_ids:
            raise ValidationError(f"triage_lanes missing {expected}")

    dispositions = {item.get("disposition") for item in applicability["triage_dispositions"] if isinstance(item, dict)}
    for expected in ["ACCEPT", "DEFER", "REJECT", "NEEDS_SOURCE", "NEEDS_IMPLEMENTATION", "NEEDS_REVIEW"]:
        if expected not in dispositions:
            raise ValidationError(f"triage_dispositions missing {expected}")

    maturity_levels = {str(item.get("level")) for item in applicability["maturity_levels"] if isinstance(item, dict)}
    for expected in ["0.0", "0.3", "0.6", "0.8", "1.0"]:
        if expected not in maturity_levels:
            raise ValidationError(f"maturity_levels missing {expected}")

    edge_relations = {edge.get("relation") for edge in applicability["qps_to_triage_edges"] if isinstance(edge, dict)}
    for expected in ["classified_as", "design_impact_to", "operational_impact_to", "traceability_impact_to", "deliverable_impact_to", "amendment_impact_to"]:
        if expected not in edge_relations:
            raise ValidationError(f"qps_to_triage_edges missing {expected}")


def validate_all(
    glossary_path: Path,
    manifest_path: Path,
    taxonomy_path: Path,
    applicability_path: Path = DEFAULT_APPLICABILITY,
) -> list[str]:
    glossary_schema = load_json(GLOSSARY_SCHEMA)
    manifest_schema = load_json(MANIFEST_SCHEMA)
    glossary = load_yaml(glossary_path)
    manifest = load_yaml(manifest_path)
    taxonomy = load_yaml(taxonomy_path)

    validate_glossary(glossary, glossary_schema)
    validate_manifest(manifest, manifest_schema)
    validate_taxonomy(taxonomy)

    messages = [
        f"validated glossary: {glossary_path}",
        f"validated bridge manifest: {manifest_path}",
        f"validated taxonomy: {taxonomy_path}",
    ]

    if applicability_path.exists():
        applicability = load_yaml(applicability_path)
        validate_applicability(applicability)
        messages.append(f"validated QPS triage applicability: {applicability_path}")

    return messages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ADR_OCD QPS bridge artifacts.")
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    parser.add_argument("--applicability", type=Path, default=DEFAULT_APPLICABILITY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        messages = validate_all(args.glossary, args.manifest, args.taxonomy, args.applicability)
    except ValidationError as exc:
        print(f"ADR_OCD bridge validation failed: {exc}", file=sys.stderr)
        return 1
    for message in messages:
        print(message)
    print("ADR_OCD bridge validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
