#!/usr/bin/env python3
"""Regression tests for the P0-B admission-control contract."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_admission_control import (  # noqa: E402
    AdmissionControlError,
    evaluate_live,
    validate_policy,
)


def _policy() -> dict:
    return json.loads(
        (ROOT / "control" / "P0B_ADMISSION_POLICY.json").read_text(encoding="utf-8")
    )


def _live_payloads(policy: dict) -> tuple[dict, list[dict], dict[int, dict]]:
    ruleset_id = 4242
    contexts = [{"context": item["context"]} for item in policy["required_checks"]]
    branch = {
        "name": "main",
        "protected": True,
        "protection": {
            "enabled": True,
            "required_status_checks": {
                "enforcement_level": "non_admins",
                "contexts": [item["context"] for item in contexts],
                "checks": contexts,
            },
        },
    }
    summaries = [
        {
            "id": ruleset_id,
            "name": policy["ruleset_contract"]["ruleset_name"],
            "target": "branch",
            "enforcement": "active",
        }
    ]
    details = {
        ruleset_id: {
            "id": ruleset_id,
            "name": policy["ruleset_contract"]["ruleset_name"],
            "target": "branch",
            "enforcement": "active",
            "bypass_actors": [],
            "conditions": {
                "ref_name": {
                    "include": ["~DEFAULT_BRANCH"],
                    "exclude": [],
                }
            },
            "rules": [
                {"type": "deletion"},
                {"type": "non_fast_forward"},
                {
                    "type": "pull_request",
                    "parameters": {
                        "required_approving_review_count": 1,
                        "dismiss_stale_reviews_on_push": True,
                        "required_review_thread_resolution": True,
                        "require_last_push_approval": True,
                    },
                },
                {
                    "type": "required_status_checks",
                    "parameters": {
                        "strict_required_status_checks_policy": True,
                        "required_status_checks": contexts,
                    },
                },
            ],
        }
    }
    return branch, summaries, details


class AdmissionControlTests(unittest.TestCase):
    def test_policy_schema_is_coherent(self) -> None:
        validate_policy(_policy())

    def test_expected_ruleset_passes(self) -> None:
        policy = _policy()
        evaluate_live(policy, *_live_payloads(policy))

    def test_unprotected_main_fails_closed(self) -> None:
        policy = _policy()
        branch, summaries, details = _live_payloads(policy)
        branch["protected"] = False
        with self.assertRaises(AdmissionControlError):
            evaluate_live(policy, branch, summaries, details)

    def test_missing_required_check_fails_closed(self) -> None:
        policy = _policy()
        branch, summaries, details = _live_payloads(policy)
        ruleset_id = summaries[0]["id"]
        status_rule = next(
            item
            for item in details[ruleset_id]["rules"]
            if item["type"] == "required_status_checks"
        )
        status_rule["parameters"]["required_status_checks"] = status_rule["parameters"][
            "required_status_checks"
        ][:-1]
        with self.assertRaises(AdmissionControlError):
            evaluate_live(policy, branch, summaries, details)

    def test_bypass_actor_fails_closed(self) -> None:
        policy = _policy()
        branch, summaries, details = _live_payloads(policy)
        ruleset_id = summaries[0]["id"]
        details[ruleset_id]["bypass_actors"] = [
            {"actor_id": 1, "actor_type": "RepositoryRole", "bypass_mode": "always"}
        ]
        with self.assertRaises(AdmissionControlError):
            evaluate_live(policy, branch, summaries, details)


if __name__ == "__main__":
    unittest.main(verbosity=2)
