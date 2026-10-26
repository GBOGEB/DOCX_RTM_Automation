"""JADE fail-closed noncompensating H08/H12 repository-contract regressions."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AdmissionReleaseContractTests(unittest.TestCase):
    def test_release_remains_unpublished(self):
        identity = json.loads((ROOT / "release/RELEASE_IDENTITY.json").read_text(encoding="utf-8"))
        release = identity["repository_release"]
        self.assertIs(release["release_published"], False)
        self.assertIsNone(release["tag"])
        self.assertEqual(release["lifecycle"], "HARDENING")

    def test_admission_policy_runs_on_pr_and_main_push(self):
        content = (ROOT / ".github/workflows/admission-policy.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", content)
        self.assertIn("push:", content)
        self.assertIn("branches: [main]", content)
        self.assertIn("validate_repository_admission_policy.py", content)

    def test_unprotected_main_fails_postmerge(self):
        content = (ROOT / ".github/workflows/admission-policy.yml").read_text(encoding="utf-8")
        self.assertIn('and not protected', content)
        self.assertIn('sys.exit(1)', content)
        self.assertIn("main.protected=", content)

    def test_release_identity_guard_remains_required(self):
        content = (ROOT / ".github/workflows/release-identity.yml").read_text(encoding="utf-8")
        self.assertIn("validate_release_identity.py", content)
        self.assertIn("test_release_identity.py", content)

if __name__ == "__main__":
    unittest.main()
