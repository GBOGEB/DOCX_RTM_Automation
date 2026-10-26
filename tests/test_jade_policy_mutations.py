"""P0-B admission contract mutation tests: policy text must fail closed, no H08 credit."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/validate_repository_admission_policy.py"
SPEC = importlib.util.spec_from_file_location("jade_admission_validator", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class AdmissionPolicyMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in [
            "configs/repository_admission_policy.json",
            "configs/workflow_config.yaml",
            *validator.REQUIRED,
        ]:
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, dest)
        self.policy_path = self.root / "configs/repository_admission_policy.json"

    def mutate(self, change):
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        change(policy)
        self.policy_path.write_text(json.dumps(policy), encoding="utf-8")

    def test_original_contract_is_valid_but_not_enforcement(self):
        validator.validate(self.root)
        policy = json.loads(self.policy_path.read_text(encoding="utf-8"))
        self.assertFalse(policy["baseline"]["protected"])
        self.assertEqual(policy["owner_gate"]["state"], "OPEN_CONNECTOR_ADMIN_SCOPE")

    def test_false_protected_flag_rejected(self):
        self.mutate(lambda p: p["desired_enforcement"].update(protected=False))
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "protected"):
            validator.validate(self.root)

    def test_zero_approvals_rejected(self):
        self.mutate(lambda p: p["desired_enforcement"].update(required_approving_reviews=0))
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "approving review"):
            validator.validate(self.root)

    def test_admin_bypass_rejected(self):
        self.mutate(lambda p: p["desired_enforcement"].update(enforce_admins=False))
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "enforce_admins"):
            validator.validate(self.root)

    def test_required_check_deletion_rejected(self):
        self.mutate(lambda p: p["desired_enforcement"]["required_checks"].pop())
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "required-check map"):
            validator.validate(self.root)

    def test_missing_required_workflow_rejected(self):
        (self.root / ".github/workflows/admission-policy.yml").unlink()
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "missing required file"):
            validator.validate(self.root)

    def test_missing_executable_step_rejected(self):
        path = self.root / ".github/workflows/admission-policy.yml"
        body = path.read_text(encoding="utf-8")
        path.write_text(body.replace("    steps:", "    omitted_steps:"), encoding="utf-8")
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "steps block"):
            validator.validate(self.root)

    def test_owner_gate_must_not_be_silently_closed(self):
        self.mutate(lambda p: p["owner_gate"].update(state="PASS"))
        with self.assertRaisesRegex(validator.AdmissionPolicyError, "owner-gate"):
            validator.validate(self.root)


if __name__ == "__main__":
    unittest.main()
