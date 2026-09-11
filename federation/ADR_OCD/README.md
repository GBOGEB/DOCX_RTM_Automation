# ADR_OCD QPS Procurement Bridge

Status: controlled projection candidate

## Authority

QPS engineering ADR/OCD authority is owned by `GBOGEB/cryoplant-project`.

Canonical authority registry:

`ocd-adr/20_canonical/control/QPS_GLOBAL_ADR_OCD_SSOT_v1.json`

Current canonical QPS products:

- OCD: `ocd-adr/20_canonical/ocd/QPS_OCD_v0.8_CONSOLIDATED.md`
- ADR register: `ocd-adr/20_canonical/adr/QPS_ADR_REGISTER_v0.3.md`

This repository is a tooling projection. It may parse, enrich, transform, render, validate and export QPS content, but it may not establish or promote QPS engineering truth, compliance, OCD content or ADR disposition.

## Purpose

This bridge keeps ADR and OCD transformation support inside `DOCX_RTM_Automation` while allowing procurement-facing language and traceability to remain aligned with the child-authoritative QPS model.

The historical internal shorthand `RFO` may still be used as an alias in code or migration notes, but the outward-facing procurement content shall prefer QPS Requirements and the applicable procurement terms.

## Scope

This layer does not replace the existing parser, RTM, OTC, DEL, DMAIC, visualization, or orchestration architecture described in the root README. It is a prune-friendly bridge whose QPS-bearing outputs remain projections.

## Intended integration points

| Area | Existing system role | ADR_OCD bridge role |
|---|---|---|
| Parser | Extract RTM, OTC, DEL elements | Extend extraction taxonomy for child-bound ADR/OCD/QPS content types |
| RTM | Requirements traceability | Link QPS requirements to ADR decisions and OCD scenarios |
| DEL | Deliverable tracking | Link QPS deliverables to ADR/OCD evidence obligations |
| DMAIC | Lifecycle control | Analyze QPS -> ADR -> OCD propagation without promoting child state |
| GitHub | Branch and PR workflow | Keep ADR_OCD changes reviewable, testable and prunable |

## Document roles

### QPS Requirements

The QPS Requirements are the main procurement-facing technical requirements used by Applicants to prepare a Fixed Price Offer.

### ADR — Architecture Decision Record

An ADR captures a controlled architecture decision, its evidence, rationale, alternatives, consequences, status and approval boundary. The current QPS ADR register and individual ADRs are owned by the child repository. `Architecture Design Report` is retained only as a legacy bridge alias.

### OCD — Operational Concept Description

The OCD captures operational modes, scenarios, roles, workflows, degraded modes, interfaces, maintenance concepts, training, diagnostics and evidence paths. `Operational Concept Document` is retained only as a compatibility alias.

## Rules

1. Do not duplicate master QPS content across QPS, ADR and OCD projections.
2. Reuse glossary terms and structured content references wherever possible.
3. Bind exchanged projections to source/payload digest.
4. Never interpret a tooling `ACCEPT` as child engineering acceptance.
5. Route proposed engineering changes back to the child for explicit re-entry/disposition.
