# MIP Bootstrap Receipt Publication Decision

Date: 2026-09-11
Repository: `GBOGEB/DOCX_RTM_Automation`
Decision: `WITHDRAW_FROM_PUBLIC_SOURCE`

## Reviewed item

`MIP/receipts/repo_self_index.bootstrap.json`

## Reason

The file was a remote bootstrap receipt. Its own boundary stated that it proved only MIP contract seeding through the GitHub contents API and was not a substitute for an executable `repo_self_index` receipt produced in a checked-out repository or CI runner.

Because MIP receipts can contain path census, working-tree state, commit evidence, and environment-specific diagnostics, generated receipts are private by default. Ignore rules do not untrack already-versioned files, so the tracked bootstrap receipt is explicitly removed from public source in this N+1 protection pulse.

## Effect on verification

Removing the bootstrap receipt does not count as a failed rollout. It means executable verification remains `DoV withheld` until a commit-bound local or controlled-CI run produces fresh evidence and a sanitized acceptance summary is reviewed for publication.

## Public replacement

This decision record is the public summary. Raw/generated receipt payloads remain outside tracked source unless separately reviewed and approved.
