"""Lossless, verifiable handover pack of a git repository at one pinned commit.

Writes three files to the output folder:

  <name>_<sha7>_source.zip       tracked files at that commit (git archive)
  <name>_<sha7>_history.bundle   full history, all refs (git bundle)
  worktree_manifest.json         SHA-256 of both archives and of every file

Every file in the zip is re-read and its git blob id is compared with the
commit tree, so "verified" in the manifest means byte-identical to the commit.
The bundle is checked with ``git bundle verify``. Nothing is uploaded.

Untracked and git-ignored files (.venv, caches, local outputs) and uncommitted
edits are not included; the manifest says so.

Build (sender), from any folder:

  python "C:\\repos\\DOCX_RTM_Automation\\scripts\\handover_pack.py" build \\
      --repo "C:\\repos\\DOCX_RTM_Automation" --ref origin/main \\
      --out "C:\\Users\\<you>\\Downloads\\handover_out"

Check (receiver), against the folder that holds worktree_manifest.json:

  python "C:\\repos\\DOCX_RTM_Automation\\scripts\\handover_pack.py" check \\
      "C:\\Users\\<you>\\Downloads\\handover_out"

The check needs only Python; git is not required on the receiving side.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MANIFEST = "worktree_manifest.json"
# git archive must write blobs exactly as stored, whatever the local eol config.
NO_EOL = ["-c", "core.autocrlf=false", "-c", "core.eol=lf"]


def _git(repo: Path, *args: str, config: list[str] | None = None) -> str:
    cmd = ["git", "-C", str(repo), *(config or []), *args]
    return subprocess.run(
        cmd, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _tree_blobs(repo: Path, sha: str) -> dict[str, str]:
    blobs = {}
    for entry in _git(repo, "ls-tree", "-r", "-z", sha).split("\0"):
        if not entry:
            continue
        meta, path = entry.split("\t", 1)
        _mode, kind, oid = meta.split()
        if kind == "blob":
            blobs[path] = oid
    return blobs


def _project_name(repo: Path) -> str:
    try:
        url = _git(repo, "remote", "get-url", "origin").strip()
    except subprocess.CalledProcessError:
        return repo.resolve().name
    name = url.rstrip("/").rsplit("/", 1)[-1]
    return name[:-4] if name.endswith(".git") else name


def build(repo: Path, ref: str, out: Path) -> dict:
    """Build the pack and return the manifest. Raises if verification fails."""
    sha = _git(repo, "rev-parse", "--verify", ref + "^{commit}").strip()
    name = _project_name(repo)
    out = out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    zip_path = out / f"{name}_{sha[:7]}_source.zip"
    bundle_path = out / f"{name}_{sha[:7]}_history.bundle"

    _git(repo, "archive", "--format=zip", "-o", str(zip_path), sha, config=NO_EOL)
    _git(repo, "bundle", "create", str(bundle_path), "--all")
    _git(repo, "bundle", "verify", str(bundle_path))
    heads = _git(repo, "bundle", "list-heads", str(bundle_path)).splitlines()

    expected = _tree_blobs(repo, sha)
    files, mismatched = [], []
    with zipfile.ZipFile(zip_path) as zf:
        members = {i.filename: i for i in zf.infolist() if not i.is_dir()}
        for path in sorted(members):
            data = zf.read(members[path])
            oid = git_blob_id(data)
            if expected.get(path) != oid:
                mismatched.append(path)
            files.append(
                {
                    "path": path,
                    "bytes": len(data),
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "git_blob": oid,
                }
            )
    missing = sorted(set(expected) - set(members))
    extra = sorted(set(members) - set(expected))
    ok = not (mismatched or missing or extra)

    try:
        remote = _git(repo, "remote", "get-url", "origin").strip()
    except subprocess.CalledProcessError:
        remote = None
    manifest = {
        "project_name": name,
        "source_remote": remote,
        "ref": ref,
        "commit": sha,
        "commit_date": _git(repo, "show", "-s", "--format=%cI", sha).strip(),
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "refs_in_bundle": sorted(h.split(" ", 1)[1] for h in heads if " " in h),
        "archives": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha256_file(p)}
            for p in (zip_path, bundle_path)
        },
        "integrity_check": {
            "algorithm": "SHA-256 per file; git blob id compared with the commit tree",
            "status": "verified" if ok else "FAILED",
            "files_in_commit": len(expected),
            "files_in_zip": len(members),
            "mismatched": mismatched,
            "missing_from_zip": missing,
            "not_in_commit": extra,
            "bundle_verify": "ok",
        },
        "not_included": (
            "Untracked and git-ignored files (.venv, caches, local outputs) "
            "and uncommitted edits."
        ),
        "files": files,
    }
    (out / MANIFEST).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if not ok:
        raise RuntimeError(
            f"verification failed: mismatched={len(mismatched)} "
            f"missing={len(missing)} extra={len(extra)}"
        )
    return manifest


def check(folder: Path) -> list[str]:
    """Return the names of archives or files that do not match the manifest."""
    folder = folder.resolve()
    manifest_path = folder / MANIFEST
    if not manifest_path.is_file():
        raise FileNotFoundError(f"{MANIFEST} not found in {folder}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad = []
    for fname, meta in manifest["archives"].items():
        path = folder / fname
        if not path.is_file():
            bad.append(f"{fname} (missing)")
        elif sha256_file(path) != meta["sha256"]:
            bad.append(fname)
    zip_name = next(n for n in manifest["archives"] if n.endswith(".zip"))
    if (folder / zip_name).is_file():
        with zipfile.ZipFile(folder / zip_name) as zf:
            names = set(zf.namelist())
            for f in manifest["files"]:
                if f["path"] not in names:
                    bad.append(f"{f['path']} (missing from zip)")
                elif hashlib.sha256(zf.read(f["path"])).hexdigest() != f["sha256"]:
                    bad.append(f["path"])
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="build and verify a handover pack")
    b.add_argument("--repo", type=Path, required=True, help="path to the git repo")
    b.add_argument("--ref", default="origin/main", help="commit-ish to pin")
    b.add_argument("--out", type=Path, required=True, help="output folder")
    c = sub.add_parser("check", help="verify a downloaded pack against its manifest")
    c.add_argument("folder", type=Path, help="folder holding worktree_manifest.json")
    a = ap.parse_args(argv)

    if a.cmd == "build":
        m = build(a.repo, a.ref, a.out)
        ic = m["integrity_check"]
        print(f"commit  {m['commit']}")
        for n, meta in m["archives"].items():
            print(f"wrote   {a.out.resolve() / n}  {meta['bytes']:,} bytes")
        print(f"status  {ic['status']}  {ic['files_in_zip']} files, "
              f"{len(m['refs_in_bundle'])} refs")
        return 0

    try:
        bad = check(a.folder)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}")
        return 2
    if bad:
        print(f"MISMATCH in {len(bad)} item(s):")
        for item in bad[:50]:
            print(f"  {item}")
        return 1
    print(f"OK: all archives and files in {a.folder.resolve()} match the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
