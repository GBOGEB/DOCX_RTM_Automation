#!/usr/bin/env python3
"""Validate the ADR_OCD QPS bridge artifacts.

This validator intentionally uses only dependencies already present in the
repository requirements: PyYAML plus the Python standard library. It performs a
focused structural validation against the bridge JSON schema files and catches
missing required fields, duplicate glossary IDs, and broken core terminology.
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
GLOSSARY_SCHEMA = REPO_ROOT / "schemas" / "glossary.schema.json"
MANIFEST_SCHEMA = REPO_ROOT / "schemas" / "adr_ocd_bridge_manifest.schema.json"


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
        "Architecture Design Report",
        "Operational Concept Document",
    }
    missing_terms = sorted(expected_terms - standard_terms)
    if missing_terms:
        raise ValidationError("Glossary missing core terms: " + ", ".join(missing_terms))


def validate_manifest(manifest: dict[str, Any], schema: dict[str, Any]) -> None:
    require_keys(manifest, schema_required_keys(schema), "bridge_manifest")
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


def validate_taxonomy(taxonomy: dict[str, Any]) -> None:
    require_keys(
        taxonomy,
        ["taxonomy_id", "version", "status", "purpose", "document_roles", "procurement_terms", "traceability_relations", "extraction_categories"],
        "taxonomy",
    )
    roles = taxonomy["document_roles"]
    if not isinstance(roles, list) or len(roles) < 3:
        raise ValidationError("taxonomy.document_roles must include QPS, ADR, and OCD roles")
    role_terms = {str(role.get("standard_term")) for role in roles if isinstance(role, dict)}
    for expected in ["QPS Requirements", "Architecture Design Report", "Operational Concept Document"]:
        if expected not in role_terms:
            raise ValidationError(f"taxonomy missing document role: {expected}")


def validate_all(glossary_path: Path, manifest_path: Path, taxonomy_path: Path) -> list[str]:
    glossary_schema = load_json(GLOSSARY_SCHEMA)
    manifest_schema = load_json(MANIFEST_SCHEMA)
    glossary = load_yaml(glossary_path)
    manifest = load_yaml(manifest_path)
    taxonomy = load_yaml(taxonomy_path)

    validate_glossary(glossary, glossary_schema)
    validate_manifest(manifest, manifest_schema)
    validate_taxonomy(taxonomy)

    return [
        f"validated glossary: {glossary_path}",
        f"validated bridge manifest: {manifest_path}",
        f"validated taxonomy: {taxonomy_path}",
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ADR_OCD QPS bridge artifacts.")
    parser.add_argument("--glossary", type=Path, default=DEFAULT_GLOSSARY)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        messages = validate_all(args.glossary, args.manifest, args.taxonomy)
    except ValidationError as exc:
        print(f"ADR_OCD bridge validation failed: {exc}", file=sys.stderr)
        return 1
    for message in messages:
        print(message)
    print("ADR_OCD bridge validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
