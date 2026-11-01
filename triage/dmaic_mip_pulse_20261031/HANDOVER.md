# PR HANDOVER: DMAIC/MIP snap pulse, federation pandoc/bridge/workflow census (2026-10-31)

Branch: `claude/dmaic-mip-pulse-20261031` (base: `main` @ `7c1da80`; measured on `49e17c6`)
Scope: DOCX_RTM_Automation only. Other repos were measured read-only. Their
hardening was simulated on scratch copies and NOT committed.
Authority: derived evidence only. `authority_transfer:false`. No ACCEPT claim.

## 1. What this PR changes (in this repo)

| Path | Change | Risk |
|---|---|---|
| `tests/test_lua_filters_executed.py` | First executed tests for all 5 Lua filters (real pandoc, temp cwd). 4 pass; `config/filters/rtm_filter.lua` is strict-xfail: pandoc fails with "attempt to index a function value". | None (skips without pandoc) |
| `.github/workflows/*.yml` (27) | Additive only: `timeout-minutes: 60` on 25 jobs; PR-scoped `concurrency` (cancels superseded PR runs only, never main) on 26 workflows. `workflow_call` workflows and reusable-call jobs skipped. Verified: parsed(after) minus added keys == parsed(before). | 60 min may be short for `data-rich-document-consumer.yml` (LibreOffice + PNG). No run history was reachable for this repo, so confirm against a real duration before merge. |
| `triage/dmaic_mip_pulse_20261031/tools/` | `wf_analyze.py` (census and hygiene), `wf_harden.py` (additive hardening plus equivalence check), `red_classify.py` (MIP red taxonomy over Actions API, parallel), `ci_stats.py`, `pandoc_scale.py` (PoC plus USL scaling fit) | Read-only tools, stdlib + PyYAML |
| `triage/dmaic_mip_pulse_20261031/results/` | Census I0/I2/I3, CI baseline, red classes, MIP self-index summaries (4 repos), hygiene series, pandoc scaling | Data |

Note: `pytest` needs `-o addopts=""` locally, because `pyproject.toml` addopts require pytest-cov.

## 2. Snap DMAIC

- **Define.** Stabilize the method (measure, then classify, then change additively, then re-measure) before scaling it across the federation. CTQs are true red rate, runaway-runner exposure, pandoc asset proof, and MIP lane maturity.
- **Measure (I0).**
  - 754 workflows / 1,030 jobs over 6 repos. Hygiene index HI is 35.6 (concurrency 21.6%, timeout 34.2%, SHA pin 50.9%).
  - cryoplant raw red rate is 60.2%. PAH red rate is 14.1%.
  - 0/5 Lua filters were executed by any test.
  - The only pandoc pin is ABACUS `pandoc/*:3.1`.
- **Analyze.**
  - cryoplant reds are 98.6% EXTERNAL. "The job was not started because recent account payments have failed or your spending limit needs to be increased" has applied since about 2026-10-27 08:00Z, and its true code red rate is 2.0%.
  - PAH reds are real. 71% are still UNKNOWN, dominated by "First-Pass Closure Gate" (46/61 runs red).
  - 678 jobs inherit the 360-minute default timeout. That is up to about 4,068 runaway job-hours, which is now a billing-relevant exposure.
- **Improve.** Iterations I1 to I3 below.
- **Control.** Commit `wf_analyze.py` and `red_classify.py` as the measurement instrument. Proposed gate: HI ≥ 80 and `jobs_without_timeout` ≤ 20 federation-wide, re-measured per pulse.

## 3. MIP (Modernize, Innovate, Perpetuate) baseline

Self-index ran on exact local HEADs: CODEX `b09b1e2`, ABACUS `b92e228`, cryoplant `3be78bf`, DOCX_RTM `49e17c6`.

| Lane | CODEX | ABACUS | cryoplant | DOCX_RTM |
|---|---|---|---|---|
| debug_ldab | green (exec) | green (exec) | green (exec) | green (signals only) |
| runners_mcp | "green" (signals only) | "green" (signals only) | "green" (signals only) | "green" (signals only) |
| codz_health_selfheal | green (exec) | green (exec) | amber | amber |
| produce | green | green | green | amber |

- Kit drift: ABACUS PASS and cryoplant PASS. DOCX_RTM has a drifted self-index or verifier, has no manifest, and its 0/8 kit files match.
- Finding: the receipt self-declares `runners_mcp` green from file signals, but CODEX `MIP/mip_lanes.json` correctly holds it at maturity 1. Score lanes by evidence maturity, not by receipt colour.
- This PR adds the first executed runner-side evidence. `red_classify.py` produces run-level classification from the Actions API, which is a candidate for promoting `runners_mcp` to maturity 2.

## 4. Iterations (local, disjoint workers)

| Metric | I0 baseline | I1 PoC (2 workers) | I2 pilot ×3 repos (3 parallel workers) | I3 scale ×6 repos |
|---|---|---|---|---|
| Reds classified (cryo / PAH) | 0% / 0% | 99.7% / 28.7% | same | same |
| cryo red rate (raw → code) | 60.2% | 60.2% → **2.0%** | same | same |
| Lua filters executed by a test | 0/5 | **5/5** (4 pass, 1 confirmed defect) | 5/5 | 5/5 |
| Concurrency coverage | 21.6% | 21.6% | 72.6% | **93.1%** |
| Job timeout coverage | 34.2% | 34.2% | 82.1% | **98.3%** |
| Hygiene index HI | 35.6 | 35.6 | 68.5 (+32.9) | **80.8** (+12.3, plateau) |
| Jobs on 360-minute default | 678 | 678 | 184 | **17** |
| Runaway exposure (job-hours) | 4,068 | 4,068 | 1,104 | **102** |
| Non-additive edits detected | n/a | n/a | 0 | 0 |
| Wall time per iteration | n/a | 92 s (1,170 API calls, 8 workers) | 2.15 s | 1.39 s |

How to read the gains:
- Marginal HI gain went +32.9 → +12.3, so the curve is decelerating.
- The residual is SHA pinning at 50.9%, which this transform does not touch, plus intentionally skipped reusable and schedule-only workflows.
- The next lever is pinning, not more of the same transform.

## 5. Pandoc PoC and scaling (USL fit)

- Setup: pandoc 3.1.3, 2 vCPU, 158-document corpus from 4 repos.
- PoC: 8 documents, 100% success and 100% deterministic (`word/document.xml` digest) for both docx and html.
- Scaling: throughput peaks at N=3 workers (docx about 17 docs/s, html about 20 docs/s), then declines. The USL fit gives σ≈0–0.06 and κ≈0.04–0.06 (contention-bound), with N*≈4–5 (R² 0.87–0.96).
- On GitHub runners, the ceiling shifts to the matrix fan-out and the concurrent-job quota, and on private repos to billing.

## 6. Owner actions (cannot be done in-repo)

1. **Billing**: restore payment or raise the spending limit for private repos (cryoplant-project and others). This removes about 98% of current cryoplant reds.
2. Decide the timeout for `data-rich-document-consumer.yml` using a real run duration.
3. Fix or retire `config/filters/rtm_filter.lua` (return `{ {Header=track_sections}, {Para=identify_requirements} }`), then remove the xfail.
4. Pick one membership SSOT. Seven files disagree (see the federation map in the session notes).

## 7. Not done / limits

- No CI history for CODEX, ABACUS or DOCX_RTM: API attach was declined in this session.
- actionlint was not available, so workflows were validated by YAML parse plus structural checks only.
- Hardening for the other 5 repos is simulated. Port it with `wf_harden.py` in per-repo PRs, base-anchored.
- Local SHAs are not MIP DoV evidence. That still requires GitHub-bound exact-SHA receipts on 3 distinct SHAs.

## 8. Next pulse (P+1)

1. Run the PR-head CI. The xfail must stay xfail.
2. Port the hardening to PAH, then CODEX, then ABACUS, then cryoplant, one PR each, in parallel workers on disjoint repos.
3. Add a SHA-pin transform (the HI residual lever).
4. Classify the PAH UNKNOWN reds with base-SHA replay.
5. Build a pandoc asset registry (SSOT) for the 8 pipelines and pin the pandoc version.
