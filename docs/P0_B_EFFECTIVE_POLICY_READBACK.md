# P0-B effective policy readback

Owner issue: [#86](https://github.com/GBOGEB/DOCX_RTM_Automation/issues/86). The
existing [repository admission policy](../configs/repository_admission_policy.json)
remains the settings contract. This repair changes verification, not settings,
permissions, the required review count, or issue-closure authority.

## Why the Boolean check was insufficient

On 10 November 2026, main at `7e47219a60ac3da7b3976db0a9ca98bee12b0032`
reported `protected=true`. Active `Main_Protect2` ruleset `26047741` contained
deletion, force-push and Copilot review rules, but no mandatory pull-request
review or required-status-check rules. The old admission job could therefore
pass while the issue's required two reviews and four check contexts were absent.
The 2 October unprotected baseline in the policy remains historical evidence.

## Existing owners and resulting behavior

`validate_repository_admission_policy.py` validates the repository-side contract.
`jade_h08_effective.py` remains the effective-ruleset evidence owner; the admission
workflow now calls its live mode instead of inspecting only `protected`.

The workflow checks out and verifies the exact PR candidate SHA, or the push SHA
on main, before running tests. The receipt distinguishes `source_sha` (verified
checkout), `workflow_sha` (event SHA, which can be a PR merge ref), and
`branch_head` (observed main). A stale main push cannot inherit newer-main proof.

Live mode uses only GitHub GET requests: branch metadata, all pages of active
branch rules, and expanded details for their ruleset IDs. GitHub resolves ref
patterns and inherited-rule applicability. The evaluator checks deletion and
force-push protection, two approvals, stale-review dismissal, last-push approval,
resolved review threads, strict checks and the exact required context names.
Expanded ruleset bypass lists must be visible and empty. Changed rule snapshots
or a changed main SHA during collection invalidate the observation.

| Receipt state | Meaning and gate behavior |
| --- | --- |
| `CONFIG_MATCHED_PENDING_CANARY` | The inspected configuration matches. It supplies no independent review, native canary, issue closure, merge admission or release credit. |
| `BLOCKED` | Read evidence lacks one or more required controls. Main push and manual enforcement exit nonzero. |
| `UNKNOWN` | Evidence is unavailable, incomplete, hidden, malformed or changed during readback. This never becomes a configuration match; enforcement exits nonzero. |
| `observation_mode=PR_REPORT_ONLY` | Preserves the original PR observation boundary. The job may finish successfully while the receipt remains `BLOCKED` or `UNKNOWN`; this is not configuration PASS or admission. |

The artifact `admission-policy-readback-<source SHA>-<attempt>` retains the JSON
receipt even when the live check fails. Existing `merge_admission=HOLD`, zero
release credit and unverified independent-review/canary fields remain unchanged.

## Read visibility and conservative scope

GitHub may omit `bypass_actors` when the caller cannot see that information.
Omission is `UNKNOWN`, not an empty bypass list. A denied API read also remains
`UNKNOWN`. This workflow introduces no administrative credential or permission
escalation. The owner must provide independently readable evidence through the
existing authorized process where native visibility is insufficient.

There are two distinct evidence routes:

- **Authorized owner readback:** expanded ruleset snapshots obtained through
  already-authorized owner access can be assessed with the existing offline
  `--branch` and `--rulesets` options and independently reviewed. This is manual
  external evidence; it is not a native workflow execution receipt.
- **Native workflow readback:** the existing `github.token` has `contents: read`.
  If GitHub withholds the bypass list, its receipt remains `UNKNOWN`, even after
  the settings themselves are repaired. Native PASS then requires an owner
  decision about an authorized full-visibility readback route and separate
  reviewed implementation of that route. No such route or additional credential
  is introduced here, and an uploaded unsigned snapshot cannot bypass this gate.

Consequently, settings changes alone cannot promise completion of #86's native
verification obligation. Keep this candidate in draft pending owner disposition
of both configuration and evidence visibility; connector readback must never be
relabeled as native proof.

This evidence owner assesses **applicable active rulesets**. It does not prove a
classic-branch-protection-only configuration. It also conservatively requires a
single matching review rule and a single matching status-check rule: equivalent
controls distributed across several rulesets can remain `BLOCKED`. A separate
reviewed extension is needed before accepting those configurations. Offline
snapshots support explicit ref targets; unresolved glob applicability stays
`UNKNOWN`. These limitations cannot grant false closure or weaken live policy.

API contract references:

- [Active rules for a branch](https://docs.github.com/en/rest/repos/rules#get-rules-for-a-branch)
- [Expanded rulesets and bypass visibility](https://docs.github.com/en/rest/repos/rules#get-a-repository-ruleset)

## Finite issue #86 closure predicate

Preserve the original six obligations, bound to the same current-main state:

1. Branch metadata reports `main.protected=true`.
2. Effective readback proves the policy's required review controls.
3. The four required contexts are bound: `release-identity`,
   `test-coverage-lineage`, `gitlink-integrity`, and `admission-policy`.
4. No bypass actors or administrator bypass path is configured.
5. Current-main checks execute more than zero steps.
6. `admission-policy` passes under the actual protected configuration.

Passing verifier unit tests or a PR report-only job does not complete these
obligations. Owner implementation and source-bound native readback remain the
next gate. Broader H08 release and canary obligations retain their own evidence;
this repair neither expands #86 into a perpetual umbrella nor closes it.

## Focused verification

```sh
python scripts/validate_repository_admission_policy.py
python tests/test_jade_h08_effective.py
python tests/test_jade_admission_release_contract.py
python tests/test_jade_policy_mutations.py
```

For the read-only live receipt, the existing workflow runs
`python scripts/jade_h08_effective.py --live --output <receipt.json>` with its
existing token context. Do not introduce a broader token to turn missing
visibility into a green result.
