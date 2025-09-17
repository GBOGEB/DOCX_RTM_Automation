# Baseline Directory

This directory contains baseline seeds and candidate baseline notes for traceability.

## Usage

Baselines are managed through the `tools/baseline.py` tool:

```bash
# Initialize baseline seed
python tools/baseline.py --init

# Add candidate baseline note
python tools/baseline.py --candidate --note "7-day scan completed"
```

## Keywords

- `BASELINE()` - Marks established baselines
- `candidate_Baseline()` - Marks potential baselines for review