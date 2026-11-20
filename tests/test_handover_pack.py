"""Tests for scripts/handover_pack.py (build, then check, then tamper)."""
from __future__ import annotations

import importlib.util
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "handover_pack.py"
spec = importlib.util.spec_from_file_location("handover_pack", SCRIPT)
hp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hp)

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="git not on PATH")


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture(autouse=True)
def _trust_test_repos(monkeypatch: pytest.MonkeyPatch) -> None:
    # Temp folders on managed Windows hosts can be owned by another principal,
    # which trips git's "dubious ownership" check. Trust them for this test only
    # (command-line scope via env), so the script itself keeps git's default check.
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "safe.directory")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", "*")


@pytest.fixture()
def tmp_path(tmp_path: Path):  # noqa: F811 - deliberately overrides pytest's fixture
    # On Windows, Python >= 3.12.4 gives pytest's tmp_path an owner-only ACL that
    # git.exe can be refused ("cannot change to ...: Permission denied"). Use a
    # folder made with default permissions instead.
    base = Path(tempfile.gettempdir()) / f"handover_pack_test_{uuid.uuid4().hex[:12]}"
    base.mkdir()
    yield base
    shutil.rmtree(base, ignore_errors=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "demo_repo"
    r.mkdir()
    _git(r, "init", "-q", "-b", "main")
    _git(r, "config", "user.email", "test@example.invalid")
    _git(r, "config", "user.name", "test")
    (r / "a.txt").write_bytes(b"line one\r\nline two\n")  # CRLF must survive
    (r / "sub").mkdir()
    (r / "sub" / "b.bin").write_bytes(bytes(range(256)))
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "init")
    (r / "untracked.txt").write_text("not in the pack")
    return r


def test_build_verifies_and_check_passes(repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    m = hp.build(repo, "HEAD", out)
    ic = m["integrity_check"]
    assert ic["status"] == "verified"
    assert ic["files_in_commit"] == ic["files_in_zip"] == 2
    assert {f["path"] for f in m["files"]} == {"a.txt", "sub/b.bin"}
    assert "refs/heads/main" in m["refs_in_bundle"]
    assert hp.check(out) == []
    assert hp.main(["check", str(out)]) == 0


def test_check_detects_tampered_and_missing_archive(repo: Path, tmp_path: Path) -> None:
    out = tmp_path / "out"
    m = hp.build(repo, "HEAD", out)
    zip_name, bundle_name = sorted(m["archives"], key=lambda n: not n.endswith(".zip"))
    with (out / zip_name).open("ab") as fh:
        fh.write(b"x")
    (out / bundle_name).unlink()
    bad = hp.check(out)
    assert zip_name in bad
    assert f"{bundle_name} (missing)" in bad
    assert hp.main(["check", str(out)]) == 1


def test_check_without_manifest_returns_2(tmp_path: Path) -> None:
    assert hp.main(["check", str(tmp_path)]) == 2
