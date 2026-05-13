# Canonical Artefacts Report

> Auto-generated at 2026-05-13 09:49 UTC by `scripts/render_canonical_report.py`.

## Overview

| Field | Value |
|-------|-------|
| Lock tag | `not locked` |
| Locked at | — |
| Total extraction runs | 0 |

## Artefacts

| Artefact | Version | Records | Locked |
|----------|---------|---------|--------|

## Hierarchy

```
master_requirements  ← ROOT: all requirements (keyed by req_id)
       ↑
rtm_matrix           ← references req_ids + listnum hooks
       ↑
offer_items          ← 50 offer items, references req_ids
       ↑
offer_tables         ← PDF table rows, keyed by offer_id
```

## User Workflow

```bash
# 1. Drop binaries (gitignored)
cp /path/to/MASTER.docx canonical/inputs/

# 2. Extract (idempotent)
python main.py --extract-canonical

# 3. Verify
python scripts/verify_canonical.py

# 4. Lock + tag
python scripts/lock_canonical.py --tag

# 5. Delete binaries
rm canonical/inputs/*.docx canonical/inputs/*.xlsx canonical/inputs/*.pdf

# 6. Push
git push && git push --tags
```
