#!/usr/bin/env python3
"""Validate the P0-B repository admission policy and live GitHub enforcement."""

from __future__ import annotations

import argparse
import json
import os
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "control" / "P0B_ADMISSION_POLICY.json"


class AdmissionControlError(RuntimeError):
    """Raised when the admission-control contract is incomplete or not enforced."""


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise AdmissionControlError(f"missing required file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AdmissionControlError(f"invalid JSON: {path}: {exc}") from exc


def validate_policy(policy: dict[str, Any]) -> None:
    if policy.get("repository") != "GBOGEB/DOCX_RTM_Automation":
        raise AdmissionControlError("repository identity mismatch")
    if policy.get("target_branch") != "main":
        raise AdmissionControlError("target branch must be main")
    if policy.get("control_id") != "P0-B_ADMISSION_HARDENING":
        raise AdmissionControlError("unexpected control id")

    checks = policy.get("required_checks")
    if not isinstance(checks, list) or not checks:
        raise AdmissionControlError("required_checks must be a non-empty list")
    contexts = [item.get("context") for item in checks if isinstance(item, dict)]
    if any(not isinstance(item, str) or not item for item in contexts):
        raise AdmissionControlError("every required check needs a non-empty context")
    if len(contexts) != len(set(contexts)):
        raise AdmissionControlError("required check contexts must be unique")

    contract = policy.get("ruleset_contract")
    if not isinstance(contract, dict):
        raise AdmissionControlError("ruleset_contract missing")
    if contract.get("enforcement") != "active":
        raise AdmissionControlError("ruleset contract must require active enforcement")
    if contract.get("bypass_actors") != []:
        raise AdmissionControlError("policy must not admit bypass actors")
    if contract.get("require_pull_request") is not True:
        raise AdmissionControlError("pull requests must be required")
    if int(contract.get("minimum_approving_reviews", 0)) < 1:
        raise AdmissionControlError("at least one approving review is required")
    if contract.get("strict_required_status_checks") is not True:
        raise AdmissionControlError("strict required status checks must be enabled")
    if contract.get("block_force_pushes") is not True:
        raise AdmissionControlError("force pushes must be blocked")
    if contract.get("block_deletions") is not True:
        raise AdmissionControlError("branch deletion must be blocked")

    for key in ("authority_transfer",):
        if policy.get(key) is not False:
            raise AdmissionControlError(f"{key} must remain false")
    for key in ("formal_credit_delta", "engineering_credit_delta"):
        if policy.get(key) != 0:
            raise AdmissionControlError(f"{key} must remain zero")


def _request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "docx-rtm-admission-control",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as exc:  # noqa: BLE001 - convert transport/auth failures to control failure
        raise AdmissionControlError(f"GitHub API request failed for {url}: {exc}") from exc


def _rule_map(ruleset: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rules = ruleset.get("rules", [])
    if not isinstance(rules, list):
        raise AdmissionControlError("ruleset rules payload is not a list")
    result: dict[str, dict[str, Any]] = {}
    for rule in rules:
        if isinstance(rule, dict) and isinstance(rule.get("type"), str):
            result[rule["type"]] = rule
    return result


def evaluate_live(
    policy: dict[str, Any],
    branch_payload: dict[str, Any],
    ruleset_summaries: list[dict[str, Any]],
    ruleset_details: dict[int, dict[str, Any]],
) -> None:
    validate_policy(policy)

    if branch_payload.get("name") != policy["target_branch"]:
        raise AdmissionControlError("live branch payload does not describe main")
    if branch_payload.get("protected") is not True:
        raise AdmissionControlError("main is not protected")

    contract = policy["ruleset_contract"]
    expected_name = contract["ruleset_name"]
    summary = next(
        (
            item
            for item in ruleset_summaries
            if isinstance(item, dict)
            and item.get("name") == expected_name
            and item.get("enforcement") == "active"
        ),
        None,
    )
    if summary is None:
        raise AdmissionControlError(f"active ruleset not found: {expected_name}")

    ruleset_id = summary.get("id")
    if not isinstance(ruleset_id, int) or ruleset_id not in ruleset_details:
        raise AdmissionControlError("ruleset detail payload missing")
    details = ruleset_details[ruleset_id]

    if details.get("enforcement") != "active":
        raise AdmissionControlError("ruleset is not active")
    bypass = details.get("bypass_actors", [])
    if bypass != []:
        raise AdmissionControlError(f"ruleset admits bypass actors: {bypass}")

    conditions = details.get("conditions", {})
    ref_names = conditions.get("ref_name", {}) if isinstance(conditions, dict) else {}
    includes = ref_names.get("include", []) if isinstance(ref_names, dict) else []
    if not isinstance(includes, list) or not any(
        ref in includes for ref in ("~DEFAULT_BRANCH", "refs/heads/main")
    ):
        raise AdmissionControlError("ruleset does not target the default/main branch")

    rules = _rule_map(details)
    for required_type in ("pull_request", "required_status_checks", "non_fast_forward", "deletion"):
        if required_type not in rules:
            raise AdmissionControlError(f"missing ruleset rule: {required_type}")

    pr_params = rules["pull_request"].get("parameters", {})
    if int(pr_params.get("required_approving_review_count", 0)) < int(
        contract["minimum_approving_reviews"]
    ):
        raise AdmissionControlError("approving review count is below policy")
    if contract["dismiss_stale_reviews_on_push"] and not pr_params.get(
        "dismiss_stale_reviews_on_push", False
    ):
        raise AdmissionControlError("stale approvals are not dismissed on push")
    if contract["require_review_thread_resolution"] and not pr_params.get(
        "required_review_thread_resolution", False
    ):
        raise AdmissionControlError("review thread resolution is not required")
    if contract["require_last_push_approval"] and not pr_params.get(
        "require_last_push_approval", False
    ):
        raise AdmissionControlError("last-push approval is not required")

    status_params = rules["required_status_checks"].get("parameters", {})
    if contract["strict_required_status_checks"] and not status_params.get(
        "strict_required_status_checks_policy", False
    ):
        raise AdmissionControlError("strict required status check policy is disabled")

    live_checks = status_params.get("required_status_checks", [])
    live_contexts = {
        item.get("context")
        for item in live_checks
        if isinstance(item, dict) and isinstance(item.get("context"), str)
    }
    expected_contexts = {item["context"] for item in policy["required_checks"]}
    missing = sorted(expected_contexts - live_contexts)
    if missing:
        raise AdmissionControlError(f"required status checks missing from ruleset: {missing}")


def validate_live(policy: dict[str, Any]) -> None:
    repository = policy["repository"]
    branch = policy["target_branch"]
    api = f"https://api.github.com/repos/{repository}"
    token = os.getenv("GITHUB_TOKEN")

    branch_payload = _request_json(f"{api}/branches/{branch}", token)
    summaries = _request_json(f"{api}/rulesets", token)
    if not isinstance(branch_payload, dict):
        raise AdmissionControlError("branch API response is not an object")
    if not isinstance(summaries, list):
        raise AdmissionControlError("rulesets API response is not a list")

    details: dict[int, dict[str, Any]] = {}
    for item in summaries:
        if not isinstance(item, dict):
            continue
        ruleset_id = item.get("id")
        if isinstance(ruleset_id, int):
            payload = _request_json(f"{api}/rulesets/{ruleset_id}", token)
            if isinstance(payload, dict):
                details[ruleset_id] = payload

    evaluate_live(policy, branch_payload, summaries, details)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="also require live GitHub ruleset/branch enforcement",
    )
    args = parser.parse_args()

    policy = _load_json(POLICY_PATH)
    if not isinstance(policy, dict):
        raise AdmissionControlError("policy root must be an object")
    validate_policy(policy)
    print("P0-B admission policy schema: PASS")

    if args.live:
        validate_live(policy)
        print("P0-B live admission enforcement: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
