# Handover

This directory is the operational entry point for the federated artifact
ownership patch package.

## Canonical artifact

The single source of truth is:

```
patches/2026-06-01_federated-artifact-ownership_v0.1.patch.md
```

That file is fully self-contained. It serves at once as the patch description,
architecture decision note, migration manifest, handover document, and packaging
recipe. Everything else in this repository's patch tooling is derived from it.

## Supporting (generated, secondary) files

| File                              | Role                                            |
|-----------------------------------|-------------------------------------------------|
| `manifest/artifact-topology.yaml` | Standalone ownership/topology map               |
| `handover/README.md`              | This operational entry point                    |
| `scripts/package_patch.sh`        | Assembles the handover bundle                    |

## Workflow

```bash
make validate        # check the canonical patch file and supporting artifacts
make patch-bundle    # stage the bundle under dist/handover_bundle/
make handover-zip    # produce dist/handover_bundle.zip
```

Under strict single-file primacy, the canonical `*.patch.md` remains the source
of truth and the supporting files may be regenerated from its embedded manifest.

## Repository snapshot pack (`scripts/handover_pack.py`)

A separate tool from the patch bundle above. It packs the whole repository at
one pinned commit, so the result can go to Google Drive or another machine and
be checked there byte for byte.

| Output | Contents |
|---|---|
| `<repo>_<sha7>_source.zip` | tracked files at the commit (`git archive`) |
| `<repo>_<sha7>_history.bundle` | full history, all refs (`git bundle`) |
| `worktree_manifest.json` | SHA-256 of both archives and of every file |

The build re-reads every file in the zip and compares its git blob id with the
commit tree, and runs `git bundle verify`. Untracked and ignored files
(`.venv`, caches, local outputs) and uncommitted edits are **not** included.
Nothing is uploaded; copy the output folder to Drive yourself.

Build (PowerShell; replace the output path with your own):

```powershell
Set-Location "C:\repos\DOCX_RTM_Automation"
git fetch origin
python "C:\repos\DOCX_RTM_Automation\scripts\handover_pack.py" build --repo "C:\repos\DOCX_RTM_Automation" --ref origin/main --out "$env:USERPROFILE\Downloads\handover_out"
```

Check on the receiving side, against the downloaded folder that holds
`worktree_manifest.json` (needs Python only, not git):

```powershell
python "C:\repos\DOCX_RTM_Automation\scripts\handover_pack.py" check "$env:USERPROFILE\Downloads\handover_out"
```

Restore with history: `git clone <repo>_<sha7>_history.bundle <folder>`.
