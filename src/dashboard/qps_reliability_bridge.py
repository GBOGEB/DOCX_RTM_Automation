#!/usr/bin/env python3
"""Narrow QPS triage -> reliability model bridge.

This module consumes already-governed QPS evidence/scenario inputs and emits
reliability-model records for a deliberately small pilot surface:

- HP_COMPRESSOR
- PVPS
- COLD_COMPRESSOR_TRAIN
- TURBINE_EXPANDER
- QPLANT_CLASS_A_SYSTEM

It does not establish engineering compliance or procurement acceptance.  It
preserves the upstream evidence disposition and derives deterministic MTBF,
lambda, P(0), P(>=1), and Poisson count probabilities for analysis/dashboard
consumption.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

HOURS_PER_YEAR = 8760.0
ALLOWED_COMPONENTS = {
    "HP_COMPRESSOR",
    "PVPS",
    "COLD_COMPRESSOR_TRAIN",
    "TURBINE_EXPANDER",
    "QPLANT_CLASS_A_SYSTEM",
}
ALLOWED_ORIGINS = {"SOURCE_BOUND", "SCENARIO", "USER_OVERRIDE"}
ALLOWED_EVIDENCE = {"ACCEPT", "DEFER"}
ALLOWED_REFERENCE_PERIODS = {
    "calendar_year",
    "operating_hours_year",
    "custom_operating_hours",
}


def _is_exact_sha(value: Any) -> bool:
    text = str(value or "").lower()
    return len(text) == 40 and all(c in "0123456789abcdef" for c in text)


def _positive_number(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


def _normalise_rates(item: dict[str, Any]) -> tuple[dict[str, float] | None, list[str]]:
    errors: list[str] = []
    mtbf_y = _positive_number(item.get("mtbf_years"))
    mtbf_h = _positive_number(item.get("mtbf_hours"))
    lam_y = _positive_number(item.get("lambda_per_year"))

    supplied = [value is not None for value in (mtbf_y, mtbf_h, lam_y)]
    if not any(supplied):
        return None, ["reliability_value_missing"]

    candidates: list[float] = []
    if mtbf_y is not None:
        candidates.append(mtbf_y)
    if mtbf_h is not None:
        candidates.append(mtbf_h / HOURS_PER_YEAR)
    if lam_y is not None:
        candidates.append(1.0 / lam_y)

    reference = candidates[0]
    for candidate in candidates[1:]:
        if abs(candidate - reference) / reference > 1e-6:
            errors.append("reliability_values_inconsistent")
            break

    mtbf_years = reference
    return {
        "mtbf_years": mtbf_years,
        "mtbf_hours": mtbf_years * HOURS_PER_YEAR,
        "lambda_per_year": 1.0 / mtbf_years,
        "lambda_per_hour": 1.0 / (mtbf_years * HOURS_PER_YEAR),
    }, errors


def _poisson_pmf(mu: float, max_count: int) -> list[dict[str, float | int]]:
    return [
        {"k": k, "probability": math.exp(-mu) * (mu**k) / math.factorial(k)}
        for k in range(max_count + 1)
    ]


def evaluate_item(item: dict[str, Any], *, campaign_days: float = 90.0, histogram_max_count: int = 8) -> dict[str, Any]:
    errors: list[str] = []
    component = str(item.get("component", "")).upper()
    origin = str(item.get("origin", "")).upper()
    evidence = str(item.get("evidence_disposition", "DEFER")).upper()
    qps_item_id = str(item.get("qps_item_id", "")).strip() or None
    reference_period = str(item.get("reference_period", "")).strip()
    source_sha = str(item.get("source_git_sha", "")).strip() or None

    if component not in ALLOWED_COMPONENTS:
        errors.append("component_not_in_pilot_scope")
    if origin not in ALLOWED_ORIGINS:
        errors.append("origin_invalid")
    if evidence not in ALLOWED_EVIDENCE:
        errors.append("evidence_disposition_invalid")
    if reference_period not in ALLOWED_REFERENCE_PERIODS:
        errors.append("reference_period_missing_or_invalid")

    rates, rate_errors = _normalise_rates(item)
    errors.extend(rate_errors)

    provenance = {
        "qps_item_id": qps_item_id,
        "origin": origin,
        "evidence_disposition": evidence,
        "source_git_sha": source_sha,
        "source_sha_valid": _is_exact_sha(source_sha),
        "source_ref": item.get("source_ref"),
        "reference_period": reference_period or None,
    }

    architecture = item.get("architecture", {}) if isinstance(item.get("architecture"), dict) else {}
    arch_checks = {
        "redundancy_basis_known": architecture.get("redundancy_basis_known") is True,
        "common_cause_basis_known": architecture.get("common_cause_basis_known") is True,
        "degraded_state_known": architecture.get("degraded_state_known") is True,
        "recovery_duration_known": _positive_number(architecture.get("recovery_hours")) is not None,
    }

    source_bound = origin == "SOURCE_BOUND"
    source_identity_ok = (not source_bound) or (_is_exact_sha(source_sha) and bool(qps_item_id))
    evidence_ok = (not source_bound) or evidence == "ACCEPT"
    reference_ok = reference_period in ALLOWED_REFERENCE_PERIODS
    architecture_complete = all(arch_checks.values())
    model_scope = "system" if architecture_complete else "component_only"

    readiness_checks = {
        "source_identity": source_identity_ok,
        "evidence_accept": evidence_ok,
        "units_reference_period": reference_ok,
        "architecture": architecture_complete,
        "deterministic_model": rates is not None and not rate_errors,
    }
    readiness_score = sum(bool(v) for v in readiness_checks.values())

    model: dict[str, Any] | None = None
    if rates is not None and not rate_errors:
        duration_years = float(campaign_days) / 365.0
        mu = rates["lambda_per_year"] * duration_years
        p0 = math.exp(-mu)
        model = {
            **rates,
            "campaign_days": float(campaign_days),
            "campaign_years": duration_years,
            "mu": mu,
            "p0": p0,
            "p_ge_1": 1.0 - p0,
            "poisson_counts": _poisson_pmf(mu, histogram_max_count),
        }

    if errors:
        disposition = "EXCLUDED"
    elif source_bound and not (source_identity_ok and evidence_ok):
        disposition = "SCENARIO_ONLY"
    elif readiness_score < 5:
        disposition = "SCENARIO_ONLY"
    else:
        disposition = "ACTIVE"

    return {
        "component": component,
        "provenance": provenance,
        "architecture": {**architecture, "checks": arch_checks},
        "model_scope": model_scope,
        "model_readiness": {
            "checks": readiness_checks,
            "score": readiness_score,
            "total": len(readiness_checks),
            "disposition": disposition,
        },
        "model": model,
        "errors": sorted(set(errors)),
        "authority_boundary": "ANALYSIS_CONSUMER_ONLY_NO_ENGINEERING_OR_COMPLIANCE_PROMOTION",
    }


def build_bridge(payload: dict[str, Any], *, campaign_days: float = 90.0, histogram_max_count: int = 8) -> dict[str, Any]:
    raw_items = payload.get("items", []) if isinstance(payload, dict) else []
    items = [
        evaluate_item(item, campaign_days=campaign_days, histogram_max_count=histogram_max_count)
        for item in raw_items
        if isinstance(item, dict)
    ]
    counts = {"ACTIVE": 0, "SCENARIO_ONLY": 0, "EXCLUDED": 0}
    for item in items:
        counts[item["model_readiness"]["disposition"]] += 1
    return {
        "type": "qps_reliability_bridge",
        "schema_version": "1.0.0",
        "pilot_scope": sorted(ALLOWED_COMPONENTS),
        "campaign_days": float(campaign_days),
        "items": items,
        "summary": {
            "item_count": len(items),
            "active_count": counts["ACTIVE"],
            "scenario_only_count": counts["SCENARIO_ONLY"],
            "excluded_count": counts["EXCLUDED"],
        },
        "authority_boundary": "CONSUMES_GOVERNED_QPS_EVIDENCE_DOES_NOT_ESTABLISH_ENGINEERING_TRUTH",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build narrow QPS reliability bridge JSON")
    parser.add_argument("--input", required=True, help="Input JSON with an items array")
    parser.add_argument("--output", required=True)
    parser.add_argument("--campaign-days", type=float, default=90.0)
    parser.add_argument("--histogram-max-count", type=int, default=8)
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = build_bridge(payload, campaign_days=args.campaign_days, histogram_max_count=args.histogram_max_count)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
