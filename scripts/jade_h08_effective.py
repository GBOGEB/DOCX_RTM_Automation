"""Read-only JADE H08 evidence assessment; never activates GitHub policy.

Pass in GitHub REST branch JSON and *expanded* repository ruleset JSON objects.
Matching control configuration is NOT a blocked RED-canary proof, eligible
review, or owner admission. Optional live mode performs authenticated GETs only.

Live callers supply the branch-rules endpoint's active rules so applicability is
decided by GitHub, including inherited rulesets and ref patterns. Missing bypass
visibility is unknown evidence, never an empty bypass list.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

REPOSITORY = "GBOGEB/DOCX_RTM_Automation"
TARGET = "main"


def assess(
    branch: dict,
    rulesets: list[dict],
    policy: dict,
    *,
    active_rules: list[dict] | None = None,
    unknown_evidence: list[str] | None = None,
) -> dict:
    defects = []
    unknown = list(unknown_evidence or [])

    def require(condition: bool, reason: str):
        if not condition:
            defects.append(reason)

    expected = policy["desired_enforcement"]
    require(branch.get("name") == TARGET, "wrong_branch")
    require(branch.get("protected") is True, "unprotected_main")
    head = (branch.get("commit") or {}).get("sha")
    if not isinstance(head, str) or re.fullmatch(r"[0-9a-f]{40}", head) is None:
        unknown.append("branch_identity_unavailable")
    applicable = []
    active_ids = None
    if active_rules is not None:
        active_ids = {rule.get("ruleset_id") for rule in active_rules}
        if any(type(value) is not int for value in active_ids):
            unknown.append("active_ruleset_identity_unavailable")
    for ruleset in rulesets:
        if ruleset.get("enforcement") != "active" or ruleset.get("target") != "branch":
            continue
        if active_ids is not None:
            if ruleset.get("id") in active_ids:
                applicable.append(ruleset)
            continue
        ref = (ruleset.get("conditions") or {}).get("ref_name") or {}
        includes = ref.get("include") or []
        excludes = ref.get("exclude") or []
        # Offline legacy inputs support exact targets. Ask GitHub to resolve any
        # glob rather than guessing at its fnmatch semantics or ignoring excludes.
        if any(any(char in value for char in "*?[") for value in includes + excludes):
            unknown.append("ref_pattern_requires_active_branch_rules")
            continue
        if not any(
            v in includes for v in ("~DEFAULT_BRANCH", "~ALL", "refs/heads/main")
        ):
            continue
        if any(v in excludes for v in ("refs/heads/main", "~DEFAULT_BRANCH", "~ALL")):
            continue
        applicable.append(ruleset)
    if active_ids is not None and active_ids != {r.get("id") for r in applicable}:
        unknown.append("active_ruleset_details_incomplete")
    require(bool(applicable), "no_active_applicable_ruleset")

    # No compensating evidence: a missing individual requirement is a failure.
    for ruleset in applicable:
        if not isinstance(ruleset.get("bypass_actors"), list):
            unknown.append("ruleset_bypass_visibility_unavailable")
        elif ruleset["bypass_actors"]:
            defects.append("ruleset_bypass_present")
        if not isinstance(ruleset.get("rules"), list):
            unknown.append("ruleset_rules_unavailable")
        elif active_rules is not None:

            def normalized(rules):
                return {
                    json.dumps(
                        {
                            "type": rule.get("type"),
                            "parameters": rule.get("parameters") or {},
                        },
                        sort_keys=True,
                    )
                    for rule in rules
                }

            effective = [
                r for r in active_rules if r.get("ruleset_id") == ruleset.get("id")
            ]
            if normalized(effective) != normalized(ruleset["rules"]):
                unknown.append("ruleset_changed_during_readback")
    by_type = {}
    for rule in applicable:
        for item in rule.get("rules") or []:
            by_type.setdefault(item.get("type"), []).append(
                item.get("parameters") or {}
            )
    require("deletion" in by_type, "delete_not_blocked")
    require("non_fast_forward" in by_type, "force_push_not_blocked")
    approvals = by_type.get("pull_request", [])
    matching_review = any(
        p.get("required_approving_review_count", 0)
        >= expected["required_approving_reviews"]
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
    config_match = not defects and not unknown
    status = "CONFIG_MATCHED_PENDING_CANARY" if config_match else "BLOCKED"
    if unknown:
        status = "UNKNOWN"
    return {
        "schema": "jade.docx.h08.effective_readback.v1",
        "repository": REPOSITORY,
        "branch": TARGET,
        "branch_head": (branch.get("commit") or {}).get("sha"),
        "config_match": config_match,
        "status": status,
        "defects": sorted(set(defects)),
        "unknown_evidence": sorted(set(unknown)),
        "red_canary_verified": False,
        "independent_review_verified": False,
        "h08_release_credit": 0,
        "merge_admission": "HOLD",
    }


class ReadbackUnavailable(RuntimeError):
    """Evidence could not be obtained; never interpret it as an empty policy."""


def github_get(path: str):
    """Read a fixed GitHub API path without printing credentials or response bodies."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"https://api.github.com{path}", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        raise ReadbackUnavailable(f"github_http_{error.code}") from None
    except (OSError, ValueError):
        raise ReadbackUnavailable("github_response_unavailable") from None


def read_live(policy: dict, get_json=None) -> dict:
    """Collect paginated applicable active rules, expanded bypass data and stable SHA.

    The branch-rules API needs metadata read, while hidden bypass actors remain
    UNKNOWN. Do not add an administrative token to make this check turn green.
    Classic branch-protection alone is not assessed by this ruleset evidence
    owner; incomplete ruleset proof stays blocked pending separate owner proof.
    """
    get_json = get_json or github_get
    branch = {}
    rulesets = []
    active_rules = []
    unknown = []
    prefix = f"/repos/{REPOSITORY}"
    try:
        if (
            policy.get("repository") != REPOSITORY
            or policy.get("target_branch") != TARGET
        ):
            raise ReadbackUnavailable("policy_identity_mismatch")
        branch = get_json(f"{prefix}/branches/{TARGET}")
        if not isinstance(branch, dict):
            branch = {}
            raise ReadbackUnavailable("branch_response_invalid")
        for page in range(1, 101):
            rows = get_json(
                f"{prefix}/rules/branches/{TARGET}?per_page=100&page={page}"
            )
            if not isinstance(rows, list) or any(
                not isinstance(row, dict) for row in rows
            ):
                raise ReadbackUnavailable("active_rules_response_invalid")
            active_rules.extend(rows)
            if len(rows) < 100:
                break
        else:
            raise ReadbackUnavailable("active_rules_pagination_incomplete")
        ids = {rule.get("ruleset_id") for rule in active_rules}
        if any(type(value) is not int or value < 1 for value in ids):
            raise ReadbackUnavailable("active_ruleset_identity_unavailable")
        for ruleset_id in sorted(ids):
            ruleset = get_json(f"{prefix}/rulesets/{ruleset_id}?includes_parents=true")
            if not isinstance(ruleset, dict) or ruleset.get("id") != ruleset_id:
                raise ReadbackUnavailable("ruleset_response_invalid")
            rules = ruleset.get("rules")
            if not isinstance(rules, list) or any(
                not isinstance(rule, dict) for rule in rules
            ):
                raise ReadbackUnavailable("ruleset_rules_unavailable")
            rulesets.append(ruleset)
        after = get_json(f"{prefix}/branches/{TARGET}")
        if (
            not isinstance(after, dict)
            or any(after.get(key) != branch.get(key) for key in ("name", "protected"))
            or (after.get("commit") or {}).get("sha")
            != (branch.get("commit") or {}).get("sha")
        ):
            raise ReadbackUnavailable("branch_changed_during_readback")
    except ReadbackUnavailable as error:
        unknown.append(str(error))
    result = assess(
        branch, rulesets, policy, active_rules=active_rules, unknown_evidence=unknown
    )
    result["evidence_scope"] = "APPLICABLE_ACTIVE_RULESETS"
    result["ruleset_ids"] = sorted(
        r["id"] for r in rulesets if type(r.get("id")) is int
    )
    return result


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", type=Path)
    ap.add_argument("--rulesets", type=Path)
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--output", type=Path)
    ap.add_argument(
        "--policy", type=Path, default=Path("configs/repository_admission_policy.json")
    )
    a = ap.parse_args(argv)
    policy = json.loads(a.policy.read_text(encoding="utf-8"))
    if a.live:
        if a.branch or a.rulesets:
            ap.error("--live cannot be combined with offline snapshots")
        result = read_live(policy)
        if (
            os.environ.get("EVENT_NAME") == "push"
            and os.environ.get("GITHUB_REF_NAME") == TARGET
            and result["branch_head"] != os.environ.get("GITHUB_SHA")
        ):
            result["config_match"] = False
            result["status"] = "UNKNOWN"
            result["unknown_evidence"].append("main_push_source_is_stale")
    else:
        if not a.branch or not a.rulesets:
            ap.error("supply --live or both --branch and --rulesets")
        b = json.loads(a.branch.read_text(encoding="utf-8"))
        rules = json.loads(a.rulesets.read_text(encoding="utf-8"))
        if not isinstance(rules, list):
            raise SystemExit("H08_READBACK_EXPECTS_EXPANDED_RULESETS_ARRAY")
        result = assess(b, rules, policy)

    # Preserve the existing PR observation boundary. A successful PR observation
    # job is not a configuration PASS; the JSON keeps BLOCKED/UNKNOWN and HOLD.
    report_only = a.live and os.environ.get("EVENT_NAME") == "pull_request"
    result["observation_mode"] = "PR_REPORT_ONLY" if report_only else "ENFORCE"
    result["source_sha"] = os.environ.get("SOURCE_SHA")
    result["workflow_sha"] = os.environ.get("GITHUB_SHA")
    body = json.dumps(result, sort_keys=True)
    print(body)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(body + "\n", encoding="utf-8")
    if not result["config_match"]:
        kind = "warning" if report_only else "error"
        print(
            f"::{kind}::P0-B effective policy {result['status']}; owner gate remains open."
        )
        return 0 if report_only else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
