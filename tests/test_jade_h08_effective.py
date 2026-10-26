"""Synthetic positive and mutation-negative cases for H08 readback evaluator."""
import importlib.util
import json
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("h08", ROOT / "scripts/jade_h08_effective.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
POLICY = json.loads((ROOT / "configs/repository_admission_policy.json").read_text(encoding="utf-8"))


def good():
    checks = [{"context": x["job"], "integration_id": 15368}
              for x in POLICY["desired_enforcement"]["required_checks"]]
    ruleset = {
        "name": "H08 owner main", "enforcement": "active", "target": "branch",
        "conditions": {"ref_name": {"include": ["~DEFAULT_BRANCH"], "exclude": []}},
        "bypass_actors": [],
        "rules": [
            {"type": "deletion"}, {"type": "non_fast_forward"},
            {"type": "pull_request", "parameters": {
                "required_approving_review_count": 2,
                "dismiss_stale_reviews_on_push": True,
                "require_last_push_approval": True,
                "required_review_thread_resolution": True}},
            {"type": "required_status_checks", "parameters": {
                "strict_required_status_checks_policy": True,
                "required_status_checks": checks}},
        ],
    }
    return {"name": "main", "protected": True,
            "commit": {"sha": "a" * 40}}, [ruleset]


class H08EvidenceTests(unittest.TestCase):
    def test_config_matched_cannot_grant_release_or_canary_credit(self):
        b, r = good()
        v = m.assess(b, r, POLICY)
        self.assertEqual(v["status"], "CONFIG_MATCHED_PENDING_CANARY")
        self.assertEqual(v["h08_release_credit"], 0)
        self.assertFalse(v["red_canary_verified"])
        self.assertEqual(v["merge_admission"], "HOLD")

    def test_unprotected_default_fails(self):
        b, r = good(); b["protected"] = False
        self.assertIn("unprotected_main", m.assess(b, r, POLICY)["defects"])

    def test_absent_ruleset_fails(self):
        b, _ = good()
        self.assertIn("no_active_applicable_ruleset", m.assess(b, [], POLICY)["defects"])

    def test_unmatched_branch_target_fails(self):
        b, r = good(); r[0]["conditions"]["ref_name"]["include"] = ["refs/heads/dev"]
        self.assertIn("no_active_applicable_ruleset", m.assess(b, r, POLICY)["defects"])

    def test_bypass_actor_fails(self):
        b, r = good(); r[0]["bypass_actors"] = [{"actor_id": 1, "actor_type": "Integration"}]
        self.assertIn("ruleset_bypass_present", m.assess(b, r, POLICY)["defects"])

    def test_missing_required_context_fails(self):
        b, r = good()
        r[0]["rules"][3]["parameters"]["required_status_checks"].pop()
        self.assertIn("required_status_contexts_missing", m.assess(b, r, POLICY)["defects"])

    def test_disabled_stale_last_push_and_review_threads_fail(self):
        for key in ("dismiss_stale_reviews_on_push", "require_last_push_approval",
                    "required_review_thread_resolution"):
            with self.subTest(key=key):
                b, r = good()
                r[0]["rules"][2]["parameters"][key] = False
                self.assertIn("review_policy_not_enforced", m.assess(b, r, POLICY)["defects"])

    def test_approval_count_is_not_waived(self):
        b, r = good()
        r[0]["rules"][2]["parameters"]["required_approving_review_count"] = 0
        self.assertIn("review_policy_not_enforced", m.assess(b, r, POLICY)["defects"])

    def test_non_strict_checks_fail(self):
        b, r = good()
        r[0]["rules"][3]["parameters"]["strict_required_status_checks_policy"] = False
        self.assertIn("required_status_contexts_missing", m.assess(b, r, POLICY)["defects"])


if __name__ == "__main__":
    unittest.main()
