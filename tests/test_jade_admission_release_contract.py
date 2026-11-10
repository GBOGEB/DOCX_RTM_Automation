"""JADE fail-closed noncompensating H08/H12 repository-contract regressions."""
import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "h08", ROOT / "scripts/jade_h08_effective.py"
)
h08 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(h08)
POLICY_PATH = ROOT / "configs/repository_admission_policy.json"
POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))


class AdmissionReleaseContractTests(unittest.TestCase):
    def test_release_remains_unpublished(self):
        identity = json.loads(
            (ROOT / "release/RELEASE_IDENTITY.json").read_text(encoding="utf-8")
        )
        release = identity["repository_release"]
        self.assertIs(release["release_published"], False)
        self.assertIsNone(release["tag"])
        self.assertEqual(release["lifecycle"], "HARDENING")

    def test_admission_policy_runs_on_pr_and_main_push(self):
        content = (ROOT / ".github/workflows/admission-policy.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("pull_request:", content)
        self.assertIn("push:", content)
        self.assertIn("branches: [main]", content)
        self.assertIn("validate_repository_admission_policy.py", content)

    def test_unprotected_main_fails_postmerge(self):
        # The old workflow Boolean admitted deletion-only protection. Exercise
        # the actual CLI boundary and retained receipt, including unknown reads.
        branch = {"name": "main", "protected": True, "commit": {"sha": "a" * 40}}
        for event, expected_exit in (
            ("push", 1),
            ("workflow_dispatch", 1),
            ("pull_request", 0),
        ):
            for unavailable in ([], ["github_http_403"]):
                with self.subTest(event=event, unavailable=unavailable):
                    result = h08.assess(
                        branch, [], POLICY, unknown_evidence=unavailable
                    )
                    with tempfile.TemporaryDirectory() as directory:
                        output = Path(directory) / "readback.json"
                        with patch.object(
                            h08, "read_live", return_value=result
                        ), patch.dict(
                            os.environ,
                            {
                                "EVENT_NAME": event,
                                "GITHUB_REF_NAME": "main",
                                "GITHUB_SHA": "a" * 40,
                                "SOURCE_SHA": "c" * 40,
                            },
                        ), redirect_stdout(
                            io.StringIO()
                        ):
                            code = h08.main(
                                [
                                    "--live",
                                    "--policy",
                                    str(POLICY_PATH),
                                    "--output",
                                    str(output),
                                ]
                            )
                        receipt = json.loads(output.read_text(encoding="utf-8"))
                    self.assertEqual(code, expected_exit)
                    self.assertFalse(receipt["config_match"])
                    self.assertEqual(
                        receipt["status"], "UNKNOWN" if unavailable else "BLOCKED"
                    )
                    self.assertEqual(receipt["merge_admission"], "HOLD")
                    self.assertEqual(receipt["red_canary_verified"], False)
                    self.assertEqual(receipt["source_sha"], "c" * 40)
                    self.assertEqual(receipt["workflow_sha"], "a" * 40)

    def test_stale_main_push_does_not_inherit_current_head_configuration(self):
        result = {
            "branch_head": "b" * 40,
            "config_match": True,
            "status": "CONFIG_MATCHED_PENDING_CANARY",
            "unknown_evidence": [],
        }
        with patch.object(h08, "read_live", return_value=result), patch.dict(
            os.environ,
            {"EVENT_NAME": "push", "GITHUB_REF_NAME": "main", "GITHUB_SHA": "a" * 40},
        ), redirect_stdout(io.StringIO()):
            code = h08.main(["--live", "--policy", str(POLICY_PATH)])
        self.assertEqual(code, 1)
        self.assertIn("main_push_source_is_stale", result["unknown_evidence"])

    def test_release_identity_guard_remains_required(self):
        content = (ROOT / ".github/workflows/release-identity.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("validate_release_identity.py", content)
        self.assertIn("test_release_identity.py", content)


if __name__ == "__main__":
    unittest.main()
