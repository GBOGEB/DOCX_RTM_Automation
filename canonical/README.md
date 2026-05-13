# Canonical Artefacts — Single Source of Truth (SSOT)

This directory is the **immutable, hierarchical, content-addressed Single Source of Truth**
for all structured data extracted from source documents. It is the only place other tools,
repos, and dashboards should reference.

## Directory Layout

```
canonical/
├── README.md          ← this file (SSOT entry point)
├── POINTER.md         ← latest canonical release URL (auto-updated)
├── LOCK.json          ← locked artefact manifest (immutable once set)
├── inputs/            ← gitignored binary staging area (drop binaries here)
│   └── .gitkeep
├── artefacts/         ← committed, versioned, content-addressed JSON outputs
│   ├── extraction_manifest.json
│   ├── master_requirements_v1.json
│   ├── rtm_matrix_v1.json
│   ├── offer_items_v1.json
│   └── offer_tables_v1.json
└── schemas/           ← JSON Schema definitions for each artefact type
    ├── master_requirements.schema.json
    ├── rtm_matrix.schema.json
    ├── offer_items.schema.json
    └── offer_tables.schema.json
```

## Hierarchy and Reference Order

```
master_requirements_v*.json   ← ROOT: all requirements keyed by req_id
        ↑
rtm_matrix_v*.json            ← references req_ids + listnum hooks
        ↑
offer_items_v*.json           ← references req_ids for traceability
        ↑
offer_tables_v*.json          ← references offer_ids from offer_items
```

## Rules

1. **Artefacts are immutable once locked.** After `scripts/lock_canonical.py --tag` is run,
   `LOCK.json` records the locked versions. The extraction pipeline refuses to overwrite them.
2. **Binaries never enter git.** Place source files in `canonical/inputs/` (gitignored).
   Only structured JSON outputs are committed.
3. **Idempotency.** Re-running extraction on the same source file (same SHA-256) produces
   no new output — the pipeline detects the match and skips extraction.
4. **Versioning.** When source data changes, a new version (`_v2.json`, `_v3.json`, …) is
   created. Previous versions are retained for temporal traceability.
5. **SHA-256 integrity.** Every artefact carries a `_meta.sha256` field computed over its
   own content. Downstream tools verify integrity without needing the source binary.

## User Workflow

```bash
# 1. Drop binaries into gitignored staging area (once per source update)
cp /path/to/MASTER.docx canonical/inputs/

# 2. Run extraction (idempotent — safe to re-run)
python main.py --extract-canonical

# 3. Verify artefacts are valid and complete
python scripts/verify_canonical.py

# 4. Lock artefacts and create git tag
python scripts/lock_canonical.py --tag

# 5. Delete local binaries (no longer needed after extraction)
rm canonical/inputs/*.docx canonical/inputs/*.xlsx canonical/inputs/*.pdf

# 6. Push (only JSON artefacts and LOCK.json are committed)
git push && git push --tags
```

## Cross-Repo References

After `lock_canonical.py --tag`, a GitHub Release is created tagged `canonical/v{date}-{sha}`.
JSON artefacts are attached as release assets. Other repos should reference the **stable asset
URL** — never the binary source. See `canonical/POINTER.md` for the latest release URL.
