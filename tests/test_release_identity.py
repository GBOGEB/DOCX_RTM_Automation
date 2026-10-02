#!/usr/bin/env python3
"""Regression tests for the repository release-identity control."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.validate_release_identity import ValidationError, validate  # noqa: E402


class ReleaseIdentityTests(unittest.TestCase):
    def test_current_repository_identity_is_coherent(self) -> None:
        validate(ROOT)

    def test_component_versions_are_explicitly_mapped(self) -> None:
        identity = json.loads(
            (ROOT / "release" / "RELEASE_IDENTITY.json").read_text(encoding="utf-8")
        )
        components = identity["component_versions"]
        self.assertTrue(components["python_package"]["release_coupled"])
        self.assertFalse(components["workflow_contract"]["release_coupled"])
        self.assertFalse(components["typescript_orchestration"]["release_coupled"])

    def test_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "release").mkdir()
            (root / "configs").mkdir()
            (root / "orchestration_ts").mkdir()
            (root / "handover").mkdir()

            identity = json.loads(
                (ROOT / "release" / "RELEASE_IDENTITY.json").read_text(encoding="utf-8")
            )
            identity["component_versions"]["python_package"]["version"] = "9.9.9"
            (root / "release" / "RELEASE_IDENTITY.json").write_text(
                json.dumps(identity), encoding="utf-8"
            )

            for relative in (
                "pyproject.toml",
                "configs/workflow_config.yaml",
                "orchestration_ts/package.json",
                "CHANGELOG.md",
                "handover/CURRENT.json",
            ):
                source = ROOT / relative
                target = root / relative
                target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

            with self.assertRaises(ValidationError):
                validate(root)


if __name__ == "__main__":
    unittest.main(verbosity=2)
