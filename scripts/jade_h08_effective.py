"""Read-only JADE H08 evidence assessment; never activates GitHub policy.

Pass in GitHub REST branch JSON and *expanded* repository ruleset JSON objects.
Matching control configuration is NOT a blocked RED-canary proof, eligible
review, or owner admission. No network calls, writes or administrative tokens.
"""
from __future__ import annotations
import json
from pathlib import Path

REPOSITORY = "GBOGEB/DOCX_RTM_Automation"
TARGET = "main"


def assess(branch: dict, rulesets: list[dict], policy: dict) -> dict:
    defects = []
    def require(condition: bool, reason: str):
        if not condition:
            defects.append(reason)

    expected = policy["desired_enforcement"]
    require(branch.get("name") == TARGET, "wrong_branch")
    require(branch.get("protected") is True, "unprotected_main")
    applicable = []
    for ruleset in rulesets:
        if ruleset.get("enforcement") != "active" or ruleset.get("target") != "branch":
            continue
        ref = (ruleset.get("conditions") or {}).get("ref_name") or {}
        includes = ref.get("include") or []
        excludes = ref.get("exclude") or []
        if not any(v in includes for v in ("~DEFAULT_BRANCH", "~ALL", "refs/heads/main")):
            continue
        if any(v in excludes for v in ("refs/heads/main", "~DEFAULT_BRANCH", "~ALL")):
            continue
        applicable.append(ruleset)
    require(bool(applicable), "no_active_applicable_ruleset")

    # No compensating evidence: a missing individual requirement is a failure.
    require(all(not r.get("bypass_actors") for r in applicable), "ruleset_bypass_present")
    by_type = {}
    for rule in applicable:
        for item in rule.get("rules") or []:
            by_type.setdefault(item.get("type"), []).append(item.get("parameters") or {})
    require("deletion" in by_type, "delete_not_blocked")
    require("non_fast_forward" in by_type, "force_push_not_blocked")
    approvals = by_type.get("pull_request", [])
    matching_review = any(
        p.get("required_approving_review_count", 0) >= expected["required_approving_reviews"]
        and p.get("dismiss_stale_reviews_on_push") is True
        and p.get("require_last_push_approval") is True
        and p.get("required_review_thread_resolution") is True
        for p in approvals
    )
    require(matching_review, "review_policy_not_enforced")
    required = {entry["job"] for entry in expected["required_checks"]}
    matching_checks = any(
        p.get("strict_required_status_checks_policy") is True
        and required <= {x.get("context") for x in p.get("required_status_checks", [])}
        for p in by_type.get("required_status_checks", [])
    )
    require(matching_checks, "required_status_contexts_missing")
    return {
        "schema": "jade.docx.h08.effective_readback.v1",
        "repository": REPOSITORY,
        "branch": TARGET,
        "branch_head": (branch.get("commit") or {}).get("sha"),
        "config_match": not defects,
        "status": "CONFIG_MATCHED_PENDING_CANARY" if not defects else "BLOCKED",
        "defects": sorted(set(defects)),
        "red_canary_verified": False,
        "independent_review_verified": False,
        "h08_release_credit": 0,
        "merge_admission": "HOLD",
    }


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", type=Path, required=True)
    ap.add_argument("--rulesets", type=Path, required=True)
    ap.add_argument("--policy", type=Path, default=Path("configs/repository_admission_policy.json"))
    a = ap.parse_args()
    b = json.loads(a.branch.read_text(encoding="utf-8"))
    rules = json.loads(a.rulesets.read_text(encoding="utf-8"))
    policy = json.loads(a.policy.read_text(encoding="utf-8"))
    if not isinstance(rules, list):
        raise SystemExit("H08_READBACK_EXPECTS_EXPANDED_RULESETS_ARRAY")
    result = assess(b, rules, policy)
    print(json.dumps(result, sort_keys=True))
    if result["defects"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
