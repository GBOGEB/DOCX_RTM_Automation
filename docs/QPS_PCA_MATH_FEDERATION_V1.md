# QPS PCA Math Federation v1

Status: integration reference  
QPS consumer authority: `GBOGEB/DOCX_RTM_Automation`  
Generic math provider: `GBOGEB/gg_MATH` PR #5  
Governed visual PCA authority: `GBOGEB/cryoplant-project` PR #1115

## Scout entry map

Start here according to the question being asked:

- **Source/evidence reliability triage:** `docs/QPS_RELIABILITY_BRIDGE_V1.md` in this repo.
- **Visual PCA retention / checkpoint semantics:** `GBOGEB/cryoplant-project` PR #1115 and `controls/QPS_MISSION_WAVE_PCA_COMPANION_CURRENT_v1.yaml`.
- **Generic PCA/covariance/state-space math:** `GBOGEB/gg_MATH` PR #5, `mission/QPS/QPS_TRIAGE_PCA_MATH_APPLICATION.md`.
- **Engineering truth, compliance, negotiation, acceptance, release:** upstream QPS/cryoplant controlled evidence only.

## Mission status

### Reliability lane

PR #54 is merged. The narrow five-atom reliability bridge is established and keeps source-bound activation fail-closed. The first ALAT HP-compressor atom remains `SCENARIO_ONLY` / `component_only`; no system reliability promotion is implied.

### Visual PCA lane

The governed visual companion currently keeps N100 as the frozen PCA reference and N156 as collection staging. N200 PCA/PA95 remains blocked until exactly 50 artifacts per format pass provenance and dedupe. PC1 is retained stable CONTROL, PC2 retained with provisional semantic calibration, and PC3 remains monitor-only at N100.

### Math-provider lane

`gg_MATH` PR #5 provides reusable equations and presentation guidance only. It does not transfer authority.

## Usable math for QPS triage

The following are approved as generic diagnostics when their inputs are governed and explicit:

1. feature standardization;
2. covariance/correlation matrices to expose redundancy and reduce double counting;
3. PCA scores/loadings/eigenvalues with the consumer's governed retention rule;
4. Mahalanobis distance for multivariate anomaly scouting;
5. normalized distance to a governed threshold/reference;
6. contraction ratio across repeated waves/checkpoints;
7. quadratic residual penalties where sign cancellation is undesirable.

## Convergence diagnostic

For normalized state vector `s_t` and frozen governed reference `s_*`:

```math
d_t = ||s_t-s_*||_2
```

```math
rho_t = d_{t+1}/d_t
```

Interpretation:

- `rho_t < 1`: convergence toward the reference;
- `rho_t ~= 1`: stable/no material contraction;
- `rho_t > 1`: divergence.

This can sit beside PCA loading congruence as a wave-stability diagnostic. It is not an acceptance score.

## Multivariate anomaly diagnostic

```math
d_M^2=(x-mu)^T Sigma^{-1}(x-mu)
```

Use to prioritize scout review of rows that are unusual across several measured dimensions at once. Use a pseudoinverse or regularized inverse if covariance is ill-conditioned.

## Presentation contract

A QPS scout-facing panel should prefer this compact order:

```text
STATE        governed current state
FIRST-RED    blocking gate
PC STATUS    retained / monitor-only
TOP LOADINGS positive and negative poles
DISTANCE     normalized distance or contraction vs frozen reference
ANOMALY      optional Mahalanobis diagnostic
AUTHORITY    source repo + exact SHA/checkpoint
NEXT         one executable action
```

## Hard guardrails

- PCA output does not promote ACCEPT/DEFER.
- PCA is not Bradley-Terry.
- Reverse-pressure scalar is not Bradley-Terry unless pairwise outcomes are explicitly fitted.
- Math-provider results do not establish engineering truth or compliance.
- Cross-repo federation must preserve exact source/checkpoint identity.

## Next implementation pulse

Add a small, source-bound QPS state receipt containing:

- feature schema/version;
- reference checkpoint;
- retained/monitor PC states;
- top loadings;
- optional contraction metric;
- optional Mahalanobis anomaly metric;
- exact authority pointers.

Do not add a new dashboard ranking before measured runtime evidence exists.
