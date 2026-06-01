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
