"""Synthetic positive and mutation-negative cases for H08 readback evaluator."""
import importlib.util
import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "h08", ROOT / "scripts/jade_h08_effective.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
POLICY = json.loads(
    (ROOT / "configs/repository_admission_policy.json").read_text(encoding="utf-8")
)


def good():
    checks = [
        {"context": x["job"], "integration_id": 15368}
        for x in POLICY["desired_enforcement"]["required_checks"]
    ]
    ruleset = {
        "name": "H08 owner main",
        "enforcement": "active",
        "target": "branch",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "bypass_actors": [],
        "rules": [
            {"type": "deletion"},
            {"type": "non_fast_forward"},
            {
                "type": "pull_request",
                "parameters": {
                    "required_approving_review_count": 2,
                    "dismiss_stale_reviews_on_push": True,
                    "require_last_push_approval": True,
                    "required_review_thread_resolution": True,
                },
            },
            {
                "type": "required_status_checks",
                "parameters": {
                    "strict_required_status_checks_policy": True,
                    "required_status_checks": checks,
                },
            },
        ],
    }
    return {"name": "main", "protected": True, "commit": {"sha": "a" * 40}}, [ruleset]


class H08EvidenceTests(unittest.TestCase):
    def test_config_matched_cannot_grant_release_or_canary_credit(self):
        b, r = good()
        v = m.assess(b, r, POLICY)
        self.assertEqual(v["status"], "CONFIG_MATCHED_PENDING_CANARY")
        self.assertEqual(v["h08_release_credit"], 0)
        self.assertFalse(v["red_canary_verified"])
        self.assertEqual(v["merge_admission"], "HOLD")

    def test_unprotected_default_fails(self):
        b, r = good()
        b["protected"] = False
        self.assertIn("unprotected_main", m.assess(b, r, POLICY)["defects"])

    def test_absent_ruleset_fails(self):
        b, _ = good()
        self.assertIn(
            "no_active_applicable_ruleset", m.assess(b, [], POLICY)["defects"]
        )

    def test_unmatched_branch_target_fails(self):
        b, r = good()
        r[0]["conditions"]["ref_name"]["include"] = ["refs/heads/dev"]
        self.assertIn("no_active_applicable_ruleset", m.assess(b, r, POLICY)["defects"])

    def test_bypass_actor_fails(self):
        b, r = good()
        r[0]["bypass_actors"] = [{"actor_id": 1, "actor_type": "Integration"}]
        self.assertIn("ruleset_bypass_present", m.assess(b, r, POLICY)["defects"])

    def test_missing_required_context_fails(self):
        b, r = good()
        r[0]["rules"][3]["parameters"]["required_status_checks"].pop()
        self.assertIn(
            "required_status_contexts_missing", m.assess(b, r, POLICY)["defects"]
        )

    def test_disabled_stale_last_push_and_review_threads_fail(self):
        for key in (
            "dismiss_stale_reviews_on_push",
            "require_last_push_approval",
            "required_review_thread_resolution",
        ):
            with self.subTest(key=key):
                b, r = good()
                r[0]["rules"][2]["parameters"][key] = False
                self.assertIn(
                    "review_policy_not_enforced", m.assess(b, r, POLICY)["defects"]
                )

    def test_approval_count_is_not_waived(self):
        b, r = good()
        r[0]["rules"][2]["parameters"]["required_approving_review_count"] = 0
        self.assertIn("review_policy_not_enforced", m.assess(b, r, POLICY)["defects"])

    def test_non_strict_checks_fail(self):
        b, r = good()
        r[0]["rules"][3]["parameters"]["strict_required_status_checks_policy"] = False
        self.assertIn(
            "required_status_contexts_missing", m.assess(b, r, POLICY)["defects"]
        )

    def test_deletion_only_protection_does_not_pass(self):
        b, r = good()
        r[0]["rules"] = r[0]["rules"][:2]
        v = m.assess(b, r, POLICY)
        self.assertEqual(v["status"], "BLOCKED")
        self.assertIn("review_policy_not_enforced", v["defects"])
        self.assertIn("required_status_contexts_missing", v["defects"])

    def test_hidden_bypass_list_is_unknown_not_empty(self):
        for hidden in (None, "omitted"):
            with self.subTest(hidden=hidden):
                b, r = good()
                if hidden == "omitted":
                    del r[0]["bypass_actors"]
                else:
                    r[0]["bypass_actors"] = hidden
                v = m.assess(b, r, POLICY)
                self.assertFalse(v["config_match"])
                self.assertEqual(v["status"], "UNKNOWN")
                self.assertIn(
                    "ruleset_bypass_visibility_unavailable", v["unknown_evidence"]
                )

    def test_one_approval_does_not_meet_two_review_policy(self):
        b, r = good()
        r[0]["rules"][2]["parameters"]["required_approving_review_count"] = 1
        self.assertFalse(m.assess(b, r, POLICY)["config_match"])

    def test_each_branch_mutation_protection_is_required(self):
        for kind in ("deletion", "non_fast_forward"):
            with self.subTest(kind=kind):
                b, r = good()
                r[0]["rules"] = [rule for rule in r[0]["rules"] if rule["type"] != kind]
                self.assertFalse(m.assess(b, r, POLICY)["config_match"])

    def test_offline_glob_exclusion_cannot_be_ignored(self):
        b, r = good()
        r[0]["conditions"]["ref_name"]["exclude"] = ["refs/heads/m*"]
        self.assertEqual(m.assess(b, r, POLICY)["status"], "UNKNOWN")

    def test_malformed_or_absent_branch_sha_cannot_match(self):
        for sha in (None, "", "bad", "a" * 39, "a" * 41, "z" * 40):
            with self.subTest(sha=sha):
                b, r = good()
                b["commit"]["sha"] = sha
                v = m.assess(b, r, POLICY)
                self.assertEqual(v["status"], "UNKNOWN")
                self.assertIn("branch_identity_unavailable", v["unknown_evidence"])


class H08LiveReadbackTests(unittest.TestCase):
    def setUp(self):
        self.branch, self.rulesets = good()
        self.rulesets[0]["id"] = 42
        self.active = [
            dict(deepcopy(rule), ruleset_id=42, ruleset_source_type="Repository")
            for rule in self.rulesets[0]["rules"]
        ]
        self.paths = []

    def get_json(self, path):
        self.paths.append(path)
        if path.endswith("/branches/main"):
            return deepcopy(self.branch)
        if "/rules/branches/main?" in path:
            return deepcopy(self.active)
        if path.endswith("/rulesets/42?includes_parents=true"):
            return deepcopy(self.rulesets[0])
        self.fail(f"Unexpected API path: {path}")

    def test_complete_active_contract_matches_without_admission_credit(self):
        result = m.read_live(POLICY, self.get_json)
        self.assertEqual(result["status"], "CONFIG_MATCHED_PENDING_CANARY")
        self.assertEqual(result["ruleset_ids"], [42])
        self.assertEqual(result["merge_admission"], "HOLD")
        self.assertEqual(result["h08_release_credit"], 0)

    def test_api_denial_is_unknown_not_pass(self):
        for status in (401, 403, 404, 429, 500):
            with self.subTest(status=status):

                def denied(path):
                    raise m.ReadbackUnavailable(f"github_http_{status}")

                result = m.read_live(POLICY, denied)
                self.assertEqual(result["status"], "UNKNOWN")
                self.assertFalse(result["config_match"])
                self.assertIn(f"github_http_{status}", result["unknown_evidence"])

    def test_ruleset_details_denial_keeps_discovered_rules_unknown(self):
        def denied_details(path):
            if "/rulesets/42?" in path:
                raise m.ReadbackUnavailable("github_http_403")
            return self.get_json(path)

        result = m.read_live(POLICY, denied_details)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("active_ruleset_details_incomplete", result["unknown_evidence"])

    def test_hidden_bypass_list_remains_unknown_in_live_mode(self):
        del self.rulesets[0]["bypass_actors"]
        self.assertEqual(m.read_live(POLICY, self.get_json)["status"], "UNKNOWN")

    def test_paginated_active_rules_are_all_consumed(self):
        def paginated(path):
            if "/rules/branches/main?" in path:
                self.paths.append(path)
                if path.endswith("page=1"):
                    return [deepcopy(self.active[0]) for _ in range(100)]
                return deepcopy(self.active[1:])
            return self.get_json(path)

        self.assertTrue(m.read_live(POLICY, paginated)["config_match"])
        self.assertTrue(any(path.endswith("page=2") for path in self.paths))

    def test_github_resolved_applicability_supports_ref_patterns(self):
        self.rulesets[0]["conditions"]["ref_name"]["include"] = ["refs/heads/m*"]
        self.assertTrue(m.read_live(POLICY, self.get_json)["config_match"])

    def test_disabled_ruleset_details_cannot_contradict_active_snapshot(self):
        self.rulesets[0]["enforcement"] = "disabled"
        self.assertEqual(m.read_live(POLICY, self.get_json)["status"], "UNKNOWN")

    def test_rules_changed_during_collection_cannot_pass(self):
        self.rulesets[0]["rules"][2]["parameters"][
            "required_approving_review_count"
        ] = 3
        result = m.read_live(POLICY, self.get_json)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("ruleset_changed_during_readback", result["unknown_evidence"])

    def test_main_head_change_during_collection_cannot_pass(self):
        calls = 0

        def moved(path):
            nonlocal calls
            value = self.get_json(path)
            if path.endswith("/branches/main"):
                calls += 1
                if calls == 2:
                    value["commit"]["sha"] = "b" * 40
            return value

        result = m.read_live(POLICY, moved)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIn("branch_changed_during_readback", result["unknown_evidence"])

    def test_policy_identity_mismatch_makes_no_network_request(self):
        policy = deepcopy(POLICY)
        policy["repository"] = "other/repository"
        self.assertEqual(m.read_live(policy, self.get_json)["status"], "UNKNOWN")
        self.assertEqual(self.paths, [])

    def test_http_error_is_sanitized(self):
        error = m.urllib.error.HTTPError(
            "https://api.github.com/", 403, "secret", {}, None
        )
        with patch.object(m.urllib.request, "urlopen", side_effect=error):
            with self.assertRaisesRegex(m.ReadbackUnavailable, "^github_http_403$"):
                m.github_get("/repos/GBOGEB/DOCX_RTM_Automation/branches/main")


if __name__ == "__main__":
    unittest.main()
