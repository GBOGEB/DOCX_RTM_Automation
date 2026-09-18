#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / ".mesh/W286_GLOOB_PANDOC_WORKER_HOLD_v0.1.json"
D = json.loads(P.read_text(encoding="utf-8"))
assert D["repo"] == "GBOGEB/DOCX_RTM_Automation"
assert D["authority_role"] == "SOURCE_EXTRACTION_RTM_WORKER"
assert D["producer"]["merge_sha"] == "3ce6078a12b2fd139f7a674db5d5cf99df6e90da"
assert D["producer"]["proof_head_sha"] == "446d1b4520fe991bd18482bcc21939a8c5538170"
assert D["producer"]["proof_run_id"] == 35372225076
assert D["producer"]["status"] == "PROVEN_MERGED"
assert D["authority_transfer"] is False
assert "replace_original_source_with_derived_extraction" in D["must_not"]
assert "claim_PDF_ingress_lossless" in D["must_not"]
assert D["formal_credit_delta"] == 0
print("PASS W286 DOCX RTM independent P1 parity")
