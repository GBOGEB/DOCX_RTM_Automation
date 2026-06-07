# AGENT ENTRYPOINT — DOCX_RTM_Automation

## Federation identity

| Property | Value |
| --- | --- |
| Repo | GBOGEB/DOCX_RTM_Automation |
| Role | OUTPUT |
| Layer | rendering |
| Mini-federation | RTM_Documents |
| Big-Brother | Codex + Abacus + Style |
| SSOT source | GBOGEB/GEMINI |

## Reading order

1. AGENT_ENTRYPOINT.md
2. federation.yaml
3. handover/CURRENT.json
4. configs/workflow_config.yaml
5. orchestration_ts/src/index.ts

## Canonical folder map

| Folder | Role | SSOT? | Gitignored? |
| --- | --- | --- | --- |
| src/ | Source code | YES | NO |
| configs/ | Runtime config | YES | NO |
| manifest/ | File registry | YES | NO |
| tests/ | Tests | YES | NO |
| docs/ | Documentation | YES | NO |
| tools/ | Dev utilities | NO | NO |
| outputs/ | Generated render artifacts | NO | YES |
| archive/ | Historical reference | NO | NO |
| scratch/ | Throwaway workspace | NO | YES |

## Agent rules

- All manifest paths must be repo-root-relative.
- Never commit generated outputs, logs, scratch, or temporary files.
- Commit format: `type(scope): description [Wave-N/PR-NN]`.
- Refresh handover/CURRENT.json before ending a session.
- Report validation failures to the orchestration server.
