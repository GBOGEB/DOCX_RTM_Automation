# ADR_OCD QPS Procurement Bridge

Status: draft federation bridge
Branch: feature/ADR_OCD-qps-procurement-bridge

## Purpose

This bridge keeps ADR and OCD implementation inside `DOCX_RTM_Automation` while allowing procurement-facing language to remain aligned with the outward tender package.

The historical internal shorthand `RFO` may still be used as an alias in code or migration notes, but the outward-facing procurement content shall prefer:

- QPS Requirements
- Invitation to Tender (ITT), where appropriate
- Tender Specifications, where appropriate
- Fixed Price Offer
- Negotiation Stage
- Corrigendum
- Applicant
- Tenderer / Bidder, when the procurement context requires it

## Scope

This branch introduces a prune-friendly federation layer only. It does not replace the existing parser, RTM, OTC, DEL, DMAIC, visualization, or orchestration architecture described in the root README.

## Intended integration points

| Area | Existing system role | ADR_OCD bridge role |
|---|---|---|
| Parser | Extract RTM, OTC, DEL elements | Extend extraction taxonomy for ADR/OCD/QPS content types |
| RTM | Requirements traceability | Link QPS requirements to ADR design decisions and OCD scenarios |
| DEL | Deliverable tracking | Link QPS deliverables to ADR/OCD evidence obligations |
| DMAIC | Lifecycle control | Use QPS -> ADR -> OCD as Define/Measure/Analyze/Improve/Control chain |
| GitHub | Branch and PR workflow | Keep ADR_OCD changes reviewable and prunable |

## Document roles

### QPS Requirements

The QPS Requirements are the main procurement-facing technical requirements used by Applicants to prepare a Fixed Price Offer.

### ADR

The Architecture Design Report records the system, subsystem, interface, control, data, cybersecurity, RAMI, material, simulation, and lifecycle design rationale supporting the QPS Requirements.

### OCD

The Operational Concept Document records operational modes, scenarios, roles, workflows, degraded modes, maintenance concepts, training, diagnostics, and evidence paths.

## Rule

Do not duplicate master content across QPS, ADR, and OCD. Reuse glossary terms and structured content references wherever possible.
