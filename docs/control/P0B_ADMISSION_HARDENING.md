# P0-B Admission Hardening

## Bound state

- repository: `GBOGEB/DOCX_RTM_Automation`
- P0-A merged main: `33e02e26aa99b1c21dbf3bcf5c947800075e0d68`
- predecessor PR: #83
- predecessor exact head: `cc3fbdc968479070ffe2d4dcf3142f661631a0a3`
- authority_transfer: `false`
- formal_credit_delta: `0`
- engineering_credit_delta: `0`

## Why P0-B is material

PR #83 was merged while its intended admission checks were still queued. The post-merge repository readback reported:

- `main.protected = false`
- required status checks: none
- repository rulesets: none

That is direct evidence that CI existence does not currently prevent an unadmitted merge.

## Required ruleset

Create one repository ruleset named exactly:

`P0-B main admission`

Target the default branch / `main`, set enforcement to **Active**, and configure:

- Require a pull request before merging.
- Require at least **1** approving review.
- Dismiss stale approvals when new commits are pushed.
- Require resolution of review conversations before merge.
- Require approval of the most recent reviewable push.
- Require branches to be up to date before merging / strict status checks.
- Block force pushes.
- Block branch deletion.
- Configure **no bypass actors**.

Required status-check contexts are the exact observed GitHub check-run names:

1. `release-identity`
2. `gitlink-integrity`
3. `test-coverage-lineage`
4. `admission-policy`

The first three names were read from the exact PR #83 head check runs. The fourth is created by this P0-B change.

## Proof workflow

`.github/workflows/admission-control.yml` runs three gates:

1. validates the machine-readable policy;
2. runs fail-closed regression tests;
3. reads the live GitHub branch/ruleset API and verifies the configured ruleset.

The live step is expected to fail while the repository remains unprotected. That failure is the gate, not an implementation defect.

## Closure predicate

P0-B is closed only when all of the following hold on the same current repository state:

- `main.protected == true`;
- the active ruleset `P0-B main admission` targets the default/main branch;
- no bypass actors are configured;
- pull-request review rules meet or exceed the policy;
- all four exact required status-check contexts are present;
- strict status checks are enabled;
- force pushes and deletions are blocked;
- the `admission-policy` job executes >0 steps and returns PASS.

Do not claim P0-B complete merely because this repository-side policy exists.
