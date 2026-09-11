#!/usr/bin/env python3
"""Validate the non-authoritative W111 QPS power/utility projection bridge."""
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "federation" / "POWER_UTILITY" / "W111_bridge_manifest.yaml"


def need(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    d = yaml.safe_load(PATH.read_text(encoding="utf-8"))
    need(d.get("repo") == "GBOGEB/DOCX_RTM_Automation", "repo identity mismatch")
    need(d.get("authority_scope") == "TOOLING_TRANSFORM", "must remain tooling transform")
    need(d.get("engineering_promotion_forbidden") is True, "engineering promotion must be forbidden")
    child = d.get("qps_child_authority", {})
    need(child.get("repo") == "GBOGEB/cryoplant-project", "child authority mismatch")
    need(child.get("source_ssot") == "ocd-adr/20_canonical/control/QPS_W111_POWER_UTILITY_SOURCE_SSOT_v1.json", "wrong source SSOT")
    keys = set(d.get("projection_grain", {}).get("required_keys", []))
    for key in ("source_id", "source_sha256_or_member_sha256", "source_page_or_section", "evidence_class", "child_disposition"):
        need(key in keys, f"projection grain missing {key}")
    rules = set(d.get("source_locator_policy", {}).get("rules", []))
    need("working_SSOT_name_alone_is_not_a_sufficient_source_citation" in rules, "source citation guard missing")
    gates = set(d.get("quality_gates", []))
    for gate in ("child_authority_binding", "exact_source_locator_preserved", "no_unknown_zero_fill", "confidentiality_boundary"):
        need(gate in gates, f"quality gate missing {gate}")
    scope_cols = set(d.get("scope_transfer_projection", {}).get("required_columns", []))
    for col in ("terminal_point", "contractor_supply", "SCK_supply", "CAPEX_owner", "OPEX_energy_owner", "evidence_locator"):
        need(col in scope_cols, f"HVAC scope-transfer projection missing {col}")
    print("QPS_W111_DOCX_RTM_BRIDGE_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print("QPS_W111_DOCX_RTM_BRIDGE_VALIDATION=FAIL", file=sys.stderr)
        print(exc, file=sys.stderr)
        raise SystemExit(1)
