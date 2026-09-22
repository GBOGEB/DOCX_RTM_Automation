"""Requirement-local verification for Schrijfeditor document-core records.

This module replaces the Genesis global-content verification heuristic with a
strict one-rule-to-one-requirement evaluation boundary. Verification evidence
is searched only inside the mapped requirement record. No requirement can be
satisfied by a phrase found in another requirement.

W276 scope is validation only. It does not edit source/requirements, invoke an
LLM, create canonical locks/tags, or grant QPS/global CONTROL.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any


class RequirementLocalValidationError(ValueError):
    """Raised when the validator contract itself is malformed."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RequirementLocalValidationError(message)


def _text_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def semantic_sha256(payload: dict[str, Any]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _index_document_core(document_core: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _require(
        document_core.get("schema") == "gmi.document_core.requirements/v1",
        "document_core schema must be gmi.document_core.requirements/v1",
    )
    records = document_core.get("records")
    _require(isinstance(records, list), "document_core records must be a list")
    _require(
        document_core.get("record_count") == len(records),
        "document_core record_count mismatch",
    )

    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        _require(isinstance(record, dict), "document_core record must be an object")
        req_id = record.get("requirement_id")
        _require(
            isinstance(req_id, str) and bool(req_id.strip()),
            "document_core record missing requirement_id",
        )
        _require(req_id not in indexed, f"duplicate document_core requirement_id: {req_id}")
        text = record.get("text")
        _require(
            isinstance(text, str) and bool(text.strip()),
            f"{req_id}: missing local requirement text",
        )
        indexed[req_id] = record
    return indexed


def validate_requirement_rules(
    document_core: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    """Validate each rule only against its explicitly mapped requirement record.

    Legacy rule dictionaries remain compatible: when target_requirement_id is
    absent, the rule dictionary key itself is the target requirement ID.
    Missing targets are DEFER, present targets with absent local evidence are
    REJECT, and only an exact case-insensitive local verification-method match
    is ACCEPT.
    """
    indexed = _index_document_core(document_core)
    _require(isinstance(rules, dict) and bool(rules), "rules must be a non-empty object")

    seen_targets: set[str] = set()
    results: list[dict[str, Any]] = []

    for rule_id in sorted(rules):
        rule = rules[rule_id]
        _require(isinstance(rule, dict), f"{rule_id}: rule must be an object")

        target = rule.get("target_requirement_id", rule_id)
        _require(
            isinstance(target, str) and bool(target.strip()),
            f"{rule_id}: target_requirement_id must be a non-empty string",
        )
        _require(
            target not in seen_targets,
            f"duplicate target_requirement_id across rules: {target}",
        )
        seen_targets.add(target)

        method = rule.get("verification_method")
        _require(
            isinstance(method, str) and bool(method.strip()),
            f"{rule_id}: verification_method must be a non-empty string",
        )
        method = method.strip()

        record = indexed.get(target)
        if record is None:
            results.append(
                {
                    "rule_id": rule_id,
                    "target_requirement_id": target,
                    "decision": "DEFER",
                    "reason": "target_requirement_missing",
                    "verification_method": method,
                    "evidence_scope": "requirement_local",
                    "local_text_sha256": None,
                    "matched_phrase": None,
                }
            )
            continue

        local_text = record["text"]
        matched = method.casefold() in local_text.casefold()
        results.append(
            {
                "rule_id": rule_id,
                "target_requirement_id": target,
                "decision": "ACCEPT" if matched else "REJECT",
                "reason": (
                    "verification_method_found_in_target_requirement"
                    if matched
                    else "verification_method_absent_from_target_requirement"
                ),
                "verification_method": method,
                "evidence_scope": "requirement_local",
                "local_text_sha256": _text_sha256(local_text),
                "matched_phrase": method if matched else None,
            }
        )

    decisions = [item["decision"] for item in results]
    if "REJECT" in decisions:
        overall = "REJECT"
    elif "DEFER" in decisions:
        overall = "DEFER"
    else:
        overall = "ACCEPT"

    payload = {
        "schema": "gmi.document_core.requirement_local_validation/v1",
        "document_core_record_count": len(indexed),
        "rule_count": len(results),
        "accept_count": decisions.count("ACCEPT"),
        "reject_count": decisions.count("REJECT"),
        "defer_count": decisions.count("DEFER"),
        "overall_decision": overall,
        "non_compensating": True,
        "results": results,
    }
    payload["semantic_sha256"] = semantic_sha256(payload)
    return payload
