# QPLANT-AI-AUTO execution guide

## Purpose

This is the executable bridge for the original QPLANT document-automation intent:
one versioned structured state for **RFO, ADR and OCD**, with requirements and
cross-document relationships stored as machine-readable data and regenerated on
every iteration.

The code lives in `src/qplant_auto/engine.py`.

## Governance model

The baseline is the last approved `Project_Data.json`. Every new input is an
**event**, not a replacement for history. Each event has an explicit intent:

- `NEW` — add source material and reconcile it.
- `UPDATE` — modify existing governed content.
- `REFINE` — improve or complete draft content without changing authority.
- `VERBATIM` — incorporate user-owned text without rewriting it.
- `OVERRIDE` — user/model-owner change that supersedes non-immutable prior text.
- `BRANCH` — independent candidate development; use `--branch-name`.
- `MASTER` — declare an exhaustive new master input, but still preserve lineage.

A new requirement may contain only a title. The model may draft missing fields
only from supplied context or closely related baseline material. Drafted fields
must be marked `INFERRED` in `field_provenance` and `needs_review=true`.
Unknown engineering facts, standards and numerical limits stay empty.

## Complete iteration output

Each run writes a new timestamped directory under
`output/qplant_ai_auto/<iteration-id>/` and refreshes
`output/qplant_ai_auto/LATEST/`.

Outputs:

- `Project_Data.json` — complete RFO/ADR/OCD + RTM + relationships + questions.
- `RTM.json` — requirement rows.
- `RTM.csv` and `RTM.xlsx` — tabular review surfaces.
- `Change_Log.json` — complete iteration history plus local diff receipt.
- `Input_Receipt.json` — exact source SHA-256 and declared intent.
- `Consolidated_Project_Document.md`
- `Consolidated_Project_Document.docx`

The input ledger is append-only at `state/qplant_input_ledger.jsonl`.

## First-time setup on Windows / Visual Studio

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m src.qplant_auto.engine --check
```

The preferred API-key method is an environment variable, not a committed file:

```powershell
$env:OPENAI_API_KEY="sk-..."
$env:OPENAI_MODEL="gpt-5.6"
python -m src.qplant_auto.engine --probe-api
```

If local policy requires a file, keep it **outside the repository** and pass
`--api-key-file C:\Users\gbonthuy\OneDrive\GPT_automation\Secrets\openai_key.txt`.

## Baseline intake

For the first governed run, a single user-refined master DOCX may be used:

```powershell
python -m src.qplant_auto.engine ^
  --input "C:\Users\gbonthuy\OneDrive\GPT_automation\Inputs\QPLANT_MASTER_CONTENT_v1.0_2025-03-17.docx" ^
  --intent MASTER ^
  --source "user-refined master" ^
  --target-pillars RFO,ADR,OCD ^
  --instructions "Establish the first complete structured baseline. Preserve user detail; refine sic/raw prose without making unsupported engineering claims."
```

The resulting `LATEST\Project_Data.json` becomes the next baseline.

## Normal update

```powershell
python -m src.qplant_auto.engine ^
  --baseline "output\qplant_ai_auto\LATEST\Project_Data.json" ^
  --input "C:\Users\gbonthuy\OneDrive\GPT_automation\Inputs\New_Content_v1.1_2025-03-18.docx" ^
  --intent NEW ^
  --source "stakeholder requirement update" ^
  --target-pillars RFO,ADR,OCD ^
  --dependencies "SR,REQ,OCD_USE_CASE" ^
  --instructions "Integrate the new evidence, propagate required cross-pillar impacts, and leave unsupported fields empty."
```

## Verbatim user change

```powershell
python -m src.qplant_auto.engine ^
  --baseline "output\qplant_ai_auto\LATEST\Project_Data.json" ^
  --input "Inputs\Mandated_Clause.txt" ^
  --intent VERBATIM ^
  --target-pillars RFO ^
  --instructions "Insert this model-owner text verbatim in the most appropriate RFO location and update traceability only."
```

## Branch candidate

```powershell
python -m src.qplant_auto.engine ^
  --baseline "output\qplant_ai_auto\LATEST\Project_Data.json" ^
  --input "Inputs\Alternative_Method_A.md" ^
  --intent BRANCH ^
  --branch-name "method-A" ^
  --instructions "Develop this as an independent candidate. Do not silently supersede baseline decisions."
```

A branch candidate is still a full structured project state. Git branches remain
the authoritative development isolation mechanism; `branch_name` is recorded
in the input receipt and prompt context.

## RFO / ADR / OCD propagation rule

Every iteration is reconciled against the **entire** structured baseline. The
model must evaluate whether one pillar forces changes in another. Examples:

- new `SR.#` in ADR -> evaluate new/changed RFO `REQ.#` and OCD use cases;
- changed RFO requirement -> evaluate ADR decision/constraint and OCD operating
  modes, interlocks, abnormal states and validation;
- changed OCD behavior -> evaluate whether RFO acceptance criteria or ADR
  architecture must change.

No relationship is silently invented. Inferred relationships carry
`source_state=INFERRED` and may be surfaced in `unresolved_questions`.

## Requirement row schema

Every requirement always contains all fields, even when empty:

`id, title, requirement, measurability, reference_standards, verification,
validation, rationale, topic_epic, related_requirements,
parent_stakeholder_ids, requirement_type, requirement_category, source_refs,
status, confidence, notes, field_provenance, immutable, needs_review`.

Stable IDs are preferred. Do not renumber all existing requirements because a
new row is inserted.

## Review / approval loop

1. Run iteration.
2. Review DOCX/MD and RTM XLSX/CSV.
3. Correct either the structured JSON or a human-facing output.
4. Reintroduce the approved correction as `UPDATE`, `VERBATIM` or `OVERRIDE`.
5. Re-run using the last approved `Project_Data.json` as baseline.
6. Commit code/configuration only; generated outputs remain local evidence unless
   explicitly promoted through repository governance.

## 3P* + MIP execution mapping

This implementation follows the repository's established selector:

1. **3PR / refresh-diagnose-re-entry** — inspect existing parser, OpenAI helper,
   session replay, requirements and current GitHub authority surfaces.
2. **MIP-M / Modernize** — add a current Responses API + Structured Outputs
   engine while keeping secrets outside the repository.
3. **3PC / prepare-prove-commit** — add deterministic schema, diff and immutable
   guard tests; create a PR for exact reviewable changes.
4. **MIP-I / Innovate** — add explicit input intents, complete-state
   reconciliation, missing-field provenance and multi-format intake.
5. **3P3 / one bounded propagation** — publish the integration contract through
   the existing DOCX/RTM repository only; no QPS engineering authority transfer.
6. **MIP-P / Perpetuate** — retain tests, execution guide, ledger, hashes and
   repeatable versioned outputs for subsequent iterations.

## Safety / authority boundaries

- The API key must never be committed.
- Tool-generated drafting is not engineering acceptance.
- Empty fields are valid and preferable to fabricated evidence.
- Immutable/user-verbatim content is protected.
- The QPS engineering authority boundary in the existing federation remains
  unchanged.
