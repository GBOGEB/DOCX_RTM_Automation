# CI / Test Census — 2026-10-02

Baseline: `main@33e02e26aa99b1c21dbf3bcf5c947800075e0d68`

This census is an evidence snapshot, not a production-readiness claim.

## Executive result

- Repository tree: **932** tracked blob files.
- GitHub Actions: **20** workflow files on the baseline.
- Trigger coverage: **18** pull-request workflows, **8** push workflows, **17** manual-dispatch workflows, **0** scheduled workflows.
- Every workflow has at least one executable `run` or `uses` step. The W111 bridge uses four unnamed executable steps; it is not a zero-step workflow.
- Tests tree: **43** Python files; GitHub code search finds **33** files under `tests/` containing `def test_`.
- Primary `python-ci.yml` selects six test files by path/direct directory expansion and enforces 80% coverage only on three core modules.
- Specialized proof workflows provide additional targeted pytest execution, often with `-o addopts=''`; these are targeted proofs and do not convert the 80% threshold into a repository-wide metric.
- The TypeScript orchestration package exposes `build`, `test`, `lint`, and `typecheck`, but current workflow search finds **no** `orchestration_ts`, `npm test`, or `npm run build` GitHub Actions admission lane.
- Main is **not protected** and there are **zero repository rulesets** at the baseline.
- The only workflow match for `|| true` is `.github/workflows/render_canonical.yml`; this branch removes that suppression and requires both expected render outputs before staging.

## Exact-head / merged-main proof status

PR #83 head was `cc3fbdc968479070ffe2d4dcf3142f661631a0a3` and was merged at 2026-10-02T10:05:50Z as `33e02e26aa99b1c21dbf3bcf5c947800075e0d68`.

At census time, the merged-main runs below were still queued without an executed step:

| Workflow | Run | State |
| --- | ---: | --- |
| Release identity guard | 36993566867 | queued / zero executed steps observed |
| Python CI | 36993566908 | queued / zero executed steps observed |
| Repository integrity | 36993566934 | queued / zero executed steps observed |
| Pages build and deployment | 36993566563 | queued / zero executed steps observed |

A runner queue is neither PASS nor an engineering red.

## Primary Python coverage boundary

The configured pytest addopts enforce `--cov-fail-under=80` for:

1. `src.core.idempotency_contract`
2. `src.core.lineage_metadata`
3. `src.core.artifact_alignment`

The repository snapshot contains **109** Python implementation files under the measured `parser/`, `pipeline/`, `src/`, and `visualization/` roots. Therefore the configured 80% value shall continue to be described as a **focused module gate**, not global repository coverage.

The primary Python CI command selects:

- `tests/test_basic.py`
- `tests/test_all.py`
- `tests/core/` (two test files)
- `tests/test_source_extractor.py`
- `tests/test_qplant_auto_engine.py`

## Specialized pytest lanes

Explicit pytest execution is present in:

- `python-ci.yml`
- `rtm-reconciliation-contract.yml`
- `w275-gmi-document-core-reentry.yml`
- `adr_ocd_bridge_validation.yml`
- `w276-gmi-requirement-local-validation.yml`

`qps_reliability_phase7_4.yml` installs pytest but exercises its governed runtime chain through scripts rather than invoking pytest.

## False-green census

Search across `.github/workflows/` found:

- `continue-on-error: true`: **0**
- `set +e`: **0**
- explicit `exit 0`: **0**
- `|| true`: **1**, in `render_canonical.yml`

The render workflow previously allowed `git add canonical/REPORT.md docs/CANONICAL_SSOT.md || true`, which could hide a missing generated output if the render command exited successfully without producing both files. This branch repairs that by checking both files and staging them without suppression.

The dependency-install fallback in the same workflow remains separately visible and is not classified here as the same false-green defect; it should be audited when dependency/runtime closure is addressed.

## P0-B admission policy

Repository-side required-check candidates are:

- `release-identity`
- `test-coverage-lineage`
- `gitlink-integrity`
- `admission-policy`

The governed desired policy also requires pull requests, two approving reviews, stale-review dismissal, last-push approval, conversation resolution, admin enforcement, strict up-to-date checks, no force pushes, and no branch deletion.

The connected GitHub integration does not expose the administration write needed to turn protection/rulesets on. Consequently `configs/repository_admission_policy.json` records an explicit **OPEN_CONNECTOR_ADMIN_SCOPE** owner gate. P0-B does not close until live branch metadata reports `main.protected=true` with the required controls configured.

## Ranked residual

1. **P0 / INFRA_ADMISSION — owner gate:** enable actual main protection/ruleset and bind the four required checks plus review/non-bypass rules.
2. **P0 / TEST_ADMISSION:** add TypeScript orchestration exact-head build/test/lint/typecheck CI.
3. **P1 / COVERAGE_SCOPE:** measure repository-wide Python test collection/coverage separately from the three-module 80% gate.
4. **P1 / DOC_TRUTH:** continue the non-root stale readiness/certification claim audit.

`authority_transfer=false`  
`formal_credit_delta=0`  
`engineering_credit_delta=0`
