# Patch Package: Federated Artifact Ownership Refactor

> **Output contract:** This file is a single, fully self-contained Markdown patch
> package. It is simultaneously a patch description, an architecture decision
> note, a migration manifest, a handover document, and a packaging recipe. It is
> the canonical source of truth; every supporting file in this repository
> (`manifest/`, `handover/`, `scripts/package_patch.sh`, Makefile targets) is
> derivable from the data embedded here.

## Metadata
- Repository: GBOGEB/anthropic
- Repository ID: 1255640890
- Patch Version: v0.1.0
- Patch Date: 2026-06-01
- Patch Type: architecture / artifact-governance / handover
- Baseline Ref: <branch-or-commit>
- Output Mode: single-file self-contained patch manifest
- Custodian Repository (this clone): GBOGEB/DOCX_RTM_Automation
- Naming Convention: `YYYY-MM-DD_topic_vX.Y.patch.md`

## Summary
This patch establishes the **output contract** for federated artifact ownership
refactors. The deliverable is one self-contained `*.patch.md` file that captures
intent, repository context, the architectural concern, an artifact
classification taxonomy, governance move rules, a planned patch set, diff-like
file operations, integration / validation / rollback steps, packaging recipes,
and an embedded machine-readable manifest.

The refactor it describes is intentionally **governance-first**: it routes and
classifies artifacts and records ownership, rather than rewriting runtime logic.

## Architectural Position
`anthropic` is positioned as a **governance / custodian layer**, not a runtime or
primitive-library repository. Accordingly this patch emphasises:

- policy and ownership classification
- artifact-routing and move policies
- interoperability and federation principles
- review checkpoints and constraints on movement

It deliberately avoids implementation-heavy runtime code. The custodian role
means decisions recorded here are normative for downstream federated repos but
are applied to *artifacts*, never silently to *concepts*.

## Problem Statement
- **Architectural concern:** Artifacts (schemas, parsers, policies, taxonomies,
  federation contracts) accumulate at inconsistent depths and without explicit
  ownership, creating ambiguity about who governs a given artifact and where it
  belongs in the tree.
- **Current ambiguity:** Without a recorded ownership map, automated tooling
  cannot distinguish a depth-only reorganisation (safe) from a semantic
  reassignment (requires human review).
- **Ownership assumptions:** Each artifact has exactly one owning concern.
  Repo-level history files (`README`, `ADR`, `CHANGELOG`) are owned by the repo
  itself and are frozen against automated movement.

## Refactor Constraints
- **Allowed**
  - move artifacts deeper in the tree (depth movement)
  - add manifests
  - add setup / make packaging
- **Not allowed**
  - automatic semantic cross-repo moves
  - conceptual reassignment without review
  - splicing repo-level history files
- **Principle:** *move artifacts, not concepts*. The only automatic refactor is
  depth movement; everything else is a reviewed, recorded decision.
- **Frozen:** repo-level `README`, `ADR`, `CHANGELOG`.

## Artifact Classification Taxonomy
Every moved or created artifact is tagged with **exactly one** type from this
controlled vocabulary:

| Type                  | Meaning                                                      |
|-----------------------|-------------------------------------------------------------|
| `schema`              | Data shape / structure definitions                          |
| `parser`              | Code that reads/transforms an input format                  |
| `runtime`             | Executable runtime behaviour                                |
| `policy`              | Governance rules and constraints                            |
| `taxonomy`            | Classification vocabularies and ontologies                  |
| `federation-contract` | Cross-repo interoperability agreements                      |
| `governance`          | Custodianship, ownership, and review artifacts              |

## Artifact Ownership Rules
- Exactly one **Owning Concern** per artifact.
- A move that changes Owning Concern is a **semantic move** and requires human
  review; it is never automatic.
- A move that preserves Owning Concern and only increases tree depth is a
  **depth move** and may be automated.
- Repo-level history files are owned by `repo-governance` and are frozen.

## Patch Plan
> Each block is a single artifact move. Replace placeholders with concrete paths
> when this contract is instantiated against a real baseline.

### Move 001
- From: `schemas/artifact.schema.json`
- To: `governance/schema/artifact.schema.json`
- Move Type: depth
- Reason: Co-locate schema under the governance custodian tree without changing
  ownership.
- Artifact Type: `schema`
- Owning Concern: artifact-governance

### Move 002
- From: `contracts/federation.yaml`
- To: `governance/federation/federation.yaml`
- Move Type: depth
- Reason: Group federation contracts under a single custodian namespace.
- Artifact Type: `federation-contract`
- Owning Concern: federation-custodian

### Move 003
- From: `taxonomy/artifact-types.yaml`
- To: `governance/taxonomy/artifact-types.yaml`
- Move Type: depth
- Reason: Centralise the classification vocabulary referenced by this contract.
- Artifact Type: `taxonomy`
- Owning Concern: artifact-governance

## Proposed File Operations
```diff
# Representative, patch-style entries (depth moves only — no semantic moves).
rename from schemas/artifact.schema.json
rename to   governance/schema/artifact.schema.json

rename from contracts/federation.yaml
rename to   governance/federation/federation.yaml

rename from taxonomy/artifact-types.yaml
rename to   governance/taxonomy/artifact-types.yaml

# New governance/manifest artifacts created by this patch:
+ manifest/artifact-topology.yaml
+ handover/README.md
```

## Files to Create
- `manifest/artifact-topology.yaml` — machine-readable topology / ownership map
- `handover/README.md` — operational handover entry point
- `scripts/package_patch.sh` — assembles the handover bundle from this file
- Makefile additions: `patch-bundle`, `handover-zip`, `validate`

## Build / Package
```bash
make patch-bundle    # assemble the handover bundle (markdown + supporting files)
make handover-zip    # produce dist/handover_bundle.zip
```

## Validation
```bash
make validate        # verify the canonical patch file and supporting artifacts exist
```

## Rollback
1. Revert the Git commit that introduced this patch package, or
2. Remove the generated artifacts:
   - `rm -rf dist/handover_bundle.zip`
   - `git checkout -- patches/ manifest/ handover/ scripts/package_patch.sh Makefile`
3. Depth moves are reversed by inverting each `rename from`/`rename to` pair in
   *Proposed File Operations*. No semantic moves are performed, so rollback never
   requires re-deciding ownership.

## Handover Notes
- **Risks:** Placeholder paths in *Patch Plan* must be replaced with real
  baseline paths before the depth moves are applied to `GBOGEB/anthropic`.
- **Open questions:** Confirm the `Baseline Ref` and whether `governance/` is the
  agreed custodian root in `anthropic`.
- **Required human review:** Any future move that changes an Owning Concern.
- **Note on custody:** This file was authored in `GBOGEB/DOCX_RTM_Automation` as
  the custodian working copy; it targets `GBOGEB/anthropic` as documented in the
  metadata. Cross-repo application is a reviewed, manual step.

## Embedded Manifest
```yaml
version: 1
repository: GBOGEB/anthropic
repository_id: 1255640890
patch_version: v0.1.0
patch_date: 2026-06-01
patch_type: architecture/artifact-governance/handover
output_mode: single-file-self-contained
baseline_ref: null
custodian_repository: GBOGEB/DOCX_RTM_Automation
taxonomy:
  - schema
  - parser
  - runtime
  - policy
  - taxonomy
  - federation-contract
  - governance
constraints:
  allowed:
    - depth-move
    - add-manifest
    - add-packaging
  not_allowed:
    - automatic-semantic-cross-repo-move
    - conceptual-reassignment-without-review
    - splice-repo-level-history
  frozen:
    - README
    - ADR
    - CHANGELOG
moves:
  - id: 001
    from: schemas/artifact.schema.json
    to: governance/schema/artifact.schema.json
    move_type: depth
    artifact_type: schema
    owning_concern: artifact-governance
  - id: 002
    from: contracts/federation.yaml
    to: governance/federation/federation.yaml
    move_type: depth
    artifact_type: federation-contract
    owning_concern: federation-custodian
  - id: 003
    from: taxonomy/artifact-types.yaml
    to: governance/taxonomy/artifact-types.yaml
    move_type: depth
    artifact_type: taxonomy
    owning_concern: artifact-governance
creates:
  - manifest/artifact-topology.yaml
  - handover/README.md
  - scripts/package_patch.sh
```
