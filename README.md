# DOCX RTM Automation

> Governed document/RTM extraction, traceability, federation and rendering tooling.
>
> Status refreshed: 2026-10-02. This README is the root status surface; historical achievement/certification documents are not release or enterprise-readiness evidence unless backed by current executable proof.

## 1. Purpose

`DOCX_RTM_Automation` provides repository-local tooling for DOCX/RTM processing, canonical source extraction, traceability, QPS/ADR/OCD federation projections, validation and outward document/rendering workflows.

The repository currently acts as an **OUTPUT/rendering** member of the `RTM_Documents` mini-federation. `federation.yaml` identifies `GBOGEB/GEMINI` as its SSOT source. Tooling in this repository may validate, transform, trace and render evidence; it shall not silently promote upstream engineering or procurement authority.

## 2. Current implemented surfaces

- Standard DOCX processing through `python main.py`.
- Canonical extraction through `python main.py --extract-canonical`, currently routing DOCX, RTM XLSX, OFFER XLSX and OFFER PDF-table source patterns to versioned canonical artefacts.
- SHA-256/manifest/cross-reference verification through `scripts/verify_canonical.py`.
- QPS triage / ADR-OCD federation contracts, validators, parser bridge and traceability export.
- Reliability-analysis consumer surfaces with fail-closed evidence/disposition boundaries.
- TypeScript orchestration package under `orchestration_ts/` with build, test, lint and type-check scripts.
- GitHub Actions lanes for Python CI, repository integrity, canonical rendering, ADR/OCD validation, RTM reconciliation, source-byte proof and focused QPS/runtime proofs.
- Repository-integrity controls added after the September 2026 Pages/gitlink repair.

## 3. Quick start

### Python

```bash
python -m pip install -r requirements/requirements.txt
python main.py
```

Canonical extraction and verification:

```bash
python main.py --extract-canonical
python scripts/verify_canonical.py
```

### TypeScript orchestration

```bash
cd orchestration_ts
npm install
npm run build
npm test
```

Release-identity control:

```bash
python scripts/validate_release_identity.py
python tests/test_release_identity.py
```

Do not infer production readiness from a successful local command alone. Current readiness is determined by exact-head CI, repository controls and source/provenance evidence.

## 4. Current status

| Area | Current evidence | Status |
| --- | --- | --- |
| Canonical extraction / provenance | Extraction manifest, versioned artefacts, SHA verification and cross-reference checks exist | ACTIVE / HARDENING |
| QPS / ADR-OCD federation | Applicability contract v0.3.1, validator, parser bridge and traceability export exist | ACTIVE / HARDENING |
| Repository integrity | Dedicated workflow plus repaired orphan-gitlink failure mode | CONTROL PRESENT |
| Python quality gate | Focused pytest/coverage configuration exists; the configured 80% threshold applies to selected modules, not the whole repository | PARTIAL |
| TypeScript orchestration | Express/WS orchestration package and test/lint/typecheck scripts exist | IMPLEMENTED, PROOF TO BE RE-CENSUSED |
| GitHub branch protection | `main@33e02e26...` is measured unprotected with zero rulesets; `configs/repository_admission_policy.json` defines the desired fail-closed policy and owner gate | OWNER GATE OPEN |
| Version identity | `release/RELEASE_IDENTITY.json` is the repository release SSOT (`1.0.4`) and maps the independently versioned workflow contract (`2.0.0`) and TypeScript package (`1.0.0`) | CONTROL PRESENT |
| Handover identity | `handover/CURRENT.json` is refreshed from the PR #82 / `f2527735...` baseline and points to P0-B admission hardening | CURRENT CONTROL POINTER |
| Security claims | JWT/RBAC/encryption are declared in configuration/docs, but current code search does not establish executable implementation/proof | DECLARED / UNPROVEN |
| Cloud/Kubernetes deployment | No root `k8s/` deployment surface is present; previous README commands were documentation-only | NOT CLAIMED |
| Performance/SLA | No current governed benchmark receipt supports the former fixed throughput/latency figures | NOT CLAIMED |

## 5. Enterprise-readiness values and missing edges

The word **enterprise** is treated here as a set of verifiable controls, not a marketing label.

| Enterprise value | Required evidence | Current edge |
| --- | --- | --- |
| Authority separation | Machine-readable ownership/SSOT boundaries and fail-closed promotion rules | Present in federation/QPS surfaces; keep enforced across new consumers |
| Provenance and reproducibility | Exact source identity, hashes, manifests, deterministic transforms and exact-head receipts | Strong partial implementation; expand to every outward release product |
| Change control | Protected default branch, required checks, review policy and non-bypassable merge gates | **TODO P0:** repository enforcement is missing |
| Version/release governance | One authoritative repository release plus explicit component-version map, changelog binding and later binary/source receipt | Release SSOT + drift guard present; binary/source release receipt remains P1 |
| Test assurance | Current workflow/test inventory, >0-step census, regression gates and explicit coverage scope | Census recorded in `triage/ci/CI_TEST_CENSUS_2026-10-02.*`; TypeScript CI admission remains P0 |
| Security | Implemented authN/authZ, secrets handling, dependency controls, audit evidence and security tests | **TODO P1:** configuration is not proof |
| Observability | Structured logs, health signals, failure classification and retained run evidence | Partial; define supported production signals and retention |
| Performance | Repeatable benchmark harness, datasets, limits and SLOs | **TODO P1:** no governed benchmark baseline |
| Deployment | Supported packaging/runtime target with reproducible deploy and rollback proof | **TODO P1:** do not advertise Docker/Kubernetes/cloud targets until artefacts exist |
| Supportability | Named support channel, ownership, severity model and response expectations | GitHub Issues only; no SLA/commercial support contract is declared |
| Documentation truth | Root docs generated or checked against executable/configured state | **TODO P0/P1:** stale certification/achievement material remains elsewhere in repo |

## 6. TODO

### P0 - restore repository truth and admission controls

- [x] Reconcile version identity with `release/RELEASE_IDENTITY.json`: repository release `1.0.4` is authoritative; workflow-contract `2.0.0` and TypeScript `1.0.0` remain explicitly independent component versions and are drift-checked.
- [x] Refresh `handover/CURRENT.json` from the PR #82 / `f2527735...` baseline and advance the next control edge to P0-B admission hardening.
- [ ] Enable/enforce `main` branch protection with required exact-head checks and review rules. Repository-side policy/validation is implemented; live GitHub enforcement remains an explicit owner gate because the connected integration lacks administration write scope.
- [x] Generate the current test/workflow census at `main@33e02e26...`, including triggers, >0-step execution structure, focused coverage scope, TypeScript TEST_ADMISSION debt and false-green search.
- [ ] Audit root/current docs for unsupported `PRODUCTION READY`, `ENTERPRISE EXCELLENCE`, fixed coverage, throughput, latency and deployment claims; archive or rewrite them as historical evidence.

### P1 - prove enterprise controls

- [ ] Convert security configuration into executable implementation and tests, or mark each control disabled/not implemented.
- [ ] Define release identity: source SHA, generated artefact hashes, provenance manifest, changelog/version binding and reproducible release receipt.
- [ ] Add governed performance benchmarks before publishing throughput, concurrency or API-latency numbers.
- [ ] Define supported deployment target(s) and add reproducible packaging/deploy/rollback evidence before advertising cloud/Kubernetes readiness.
- [ ] Bind logging/health/notification behaviour to tested runtime paths and document retention/operational ownership.
- [ ] Reconcile the TypeScript orchestration API surface with the actual server routes and current federation contract.

### P2 - product evolution

- [ ] Re-baseline traceability, visualization, document-format and collaboration backlog against what is already implemented today.
- [ ] Promote only roadmap items with an owner, acceptance criteria, test/evidence path and dependency chain.
- [ ] Keep AI/ML/predictive features as development candidates until datasets, evaluation criteria and failure controls are defined.

## 7. Next execution order

1. **Root truth cleanup - DONE** - PR #82 removed unsupported support/performance/cloud claims from the root surface.
2. **Version + handover reconciliation - DONE** - repository release SSOT, component-version map, handover refresh and drift guard are present.
3. **Admission hardening - OWNER GATE** - repository policy and admission check are defined; enable live GitHub protection/ruleset and bind the required checks/review rules.
4. **CI/test census - DONE ON CURRENT BASELINE** - census is recorded; the first false-green `render_canonical.yml` suppression is repaired on this branch. Next measured P0 residual is TypeScript TEST_ADMISSION.
5. **Security proof lane** - map each configured security control to code, tests and runtime evidence; disable or relabel configuration-only controls.
6. **Release/provenance lane** - produce a reproducible source-to-artefact manifest with SHA-256 receipts for outward products.
7. **Operational proof lane** - add benchmark, health, logging and supported deployment evidence.
8. **Roadmap recensus** - replace date-based legacy roadmap promises with measured, issue/PR-bound development edges.

## 8. Definition of done for an enterprise-ready claim

An `enterprise-ready` or `production-ready` statement shall not be restored until all of the following are evidenced on the same current release line:

- one authoritative version/release identity;
- protected default branch with required non-bypassable checks;
- exact-head CI with >0-step execution and explicit test/coverage scope;
- source/provenance hashes for governed inputs and generated release artefacts;
- executable security controls with tests and secrets/dependency handling;
- documented supported runtime/deployment target with rollback/recovery evidence;
- governed performance/SLO measurements rather than hard-coded marketing numbers;
- current operational ownership/support path;
- no known stale root status, handover or certification surface contradicting the release state.

## 9. Support

Use the repository's GitHub Issues for defects, feature requests and support discussions.

No separate commercial support address, Slack channel, external documentation domain, LinkedIn page, professional-services offer or SLA is currently asserted by this README. Those details shall only be published when an owner and valid service/contact information are explicitly maintained.

## 10. Roadmap policy

The former Q1/Q2/Q3 2024 v2.1-v3.0 roadmap has been retired from the root README because the dates and feature claims no longer describe the live repository.

Future roadmap entries should be evidence-driven and use:

`current main -> measured gap -> bounded work item -> exact-head proof -> merge/readback -> next measured residual`

Date/version targets may be added when they are tied to maintained issues/milestones and a release owner.

---

Repository: https://github.com/GBOGEB/DOCX_RTM_Automation
