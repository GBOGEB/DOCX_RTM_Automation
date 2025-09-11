# Agent Integration README

This directory contains files for deep agent integration and handover.

## Quick Start for Agents

1. **Initialize Environment**:
   ```bash
   make init
   ```

2. **Run 7-Day Scan**:
   ```bash
   make scan-7d
   ```

3. **Generate Package**:
   ```bash
   make package
   ```

## Agent Manifest

See `agent/agent_manifest.yaml` for capability definitions and command mappings.

## Session Tracking

Agents should update `docs/SESSIONS.md` with session timestamps and titles for traceability.

## Output Artifacts

- `docs/SCAN_7D.md` - Human-readable scan report
- `docs/scan_7d.json` - Machine-readable scan data
- `dist/orchestration_bundle.zip` - Complete bundle for handover