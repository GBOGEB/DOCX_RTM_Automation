#!/usr/bin/env python3
"""Fail-closed release identity validation for DOCX_RTM_Automation."""

from __future__ import annotations

import json
import re
from pathlib import Path


class ValidationError(RuntimeError):
    pass


def _read(path: Path) -> str:
    if not path.is_file():
        raise ValidationError(f"missing required file: {path}")
    return path.read_text(encoding="utf-8")


def _pyproject_version(text: str) -> str:
    match = re.search(
        r'(?ms)^\[project\]\s*$.*?^version\s*=\s*["\']([^"\']+)["\']',
        text,
    )
    if not match:
        raise ValidationError("could not resolve [project].version from pyproject.toml")
    return match.group(1)


def _workflow_version(text: str) -> str:
    match = re.search(
        r'(?ms)^workflow:\s*$.*?^\s{2}version:\s*["\']?([^"\'\s]+)',
        text,
    )
    if not match:
        raise ValidationError("could not resolve workflow.version from configs/workflow_config.yaml")
    return match.group(1)


def _package_version(text: str) -> str:
    data = json.loads(text)
    version = data.get("version")
    if not isinstance(version, str) or not version:
        raise ValidationError("orchestration_ts/package.json has no string version")
    return version


def validate(root: Path) -> None:
    identity = json.loads(_read(root / "release" / "RELEASE_IDENTITY.json"))

    if identity.get("repository") != "GBOGEB/DOCX_RTM_Automation":
        raise ValidationError("release identity repository mismatch")

    repo_release = identity.get("repository_release", {})
    release_version = repo_release.get("version")
    if not isinstance(release_version, str) or not release_version:
        raise ValidationError("repository release version is missing")

    components = identity.get("component_versions", {})
    required = {"python_package", "workflow_contract", "typescript_orchestration"}
    if set(components) != required:
        raise ValidationError(
            f"component version map mismatch: expected {sorted(required)}, got {sorted(components)}"
        )

    actual = {
        "python_package": _pyproject_version(_read(root / "pyproject.toml")),
        "workflow_contract": _workflow_version(_read(root / "configs" / "workflow_config.yaml")),
        "typescript_orchestration": _package_version(
            _read(root / "orchestration_ts" / "package.json")
        ),
    }

    for name, actual_version in actual.items():
        declared = components[name].get("version")
        if declared != actual_version:
            raise ValidationError(
                f"{name} version drift: identity={declared!r}, source={actual_version!r}"
            )

    if components["python_package"].get("release_coupled") is not True:
        raise ValidationError("python_package must be release_coupled")
    if actual["python_package"] != release_version:
        raise ValidationError(
            "repository release version must equal the release-coupled Python package version"
        )

    for name in ("workflow_contract", "typescript_orchestration"):
        if components[name].get("release_coupled") is not False:
            raise ValidationError(f"{name} must be explicitly release_coupled=false")

    changelog = _read(root / str(repo_release.get("changelog", "")))
    if f"## [{release_version}]" not in changelog:
        raise ValidationError(
            f"CHANGELOG.md does not contain repository release {release_version}"
        )

    current = json.loads(_read(root / "handover" / "CURRENT.json"))
    current_identity = current.get("release_identity", {})
    if current_identity.get("path") != "release/RELEASE_IDENTITY.json":
        raise ValidationError("handover does not point to release identity SSOT")
    if current_identity.get("repository_version") != release_version:
        raise ValidationError("handover repository version does not match release identity")

    basis = current.get("basis", {})
    sha = basis.get("last_completed_main_sha", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValidationError("handover last_completed_main_sha is not a full SHA")
    last_completed_pr = basis.get("last_completed_pr")
    if not isinstance(last_completed_pr, int) or last_completed_pr < 82:
        raise ValidationError(
            "handover last_completed_pr must retain or advance beyond the PR #82 root-truth baseline"
        )

    completed_edges = current.get("completed_control_edges", [])
    if "P0-A_RELEASE_IDENTITY_AND_HANDOVER" not in completed_edges:
        raise ValidationError("handover must retain completed P0-A release-identity control")

    next_edge = current.get("next_control_edge", "")
    if not isinstance(next_edge, str) or not next_edge.startswith("P0-B_"):
        raise ValidationError("handover next control edge must remain within P0-B until admission hardening closes")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    validate(root)
    print("release identity guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
