# DOCX N3.2 TypeScript component federation intake — owner-side candidate

This source-owned, read-only probe executes the **real compiled**
orchestration_ts/src/queue/JobQueue.ts and generates a content-hashed
candidate receipt. It is intentionally narrower than a full DOCX
document/agent process. The JobQueue is FIFO and does NOT natively
reject duplicate IDs; duplicate protection is in the separately declared
probe adapter and does not qualify as native queue coverage.

## DOD/DoV

- Same exact head, source TS bytes, compiled JS and package-lock SHA256.
- Native npm ci from lock, TypeScript build, then 6 negative/source tests.
- Actually enqueue/dequeue 32 jobs in FIFO, verify empty dequeue.
- Repeat identical input and verify identical output bytes and hashes.
- Detect deliberate reverse order and duplicate ID in the probe adapter.
- Export only ID/order and hashes; no private documents or user data.
- Publish owner_receipt.json and manifest.json from the DOCX CI job.
- Require independent DOCX reviewer approval and native run/job/step
  authentication before Hub can treat this as an accepted federation input.

## What remains UNKNOWN

JavaScript branch coverage of JobQueue is NULL, not 0; source-native
TypeScript conditional-branch instrumentation is separate future work.
Actual document RTM processing, agent orchestration and cross-repo
federation are not exercised by this component receipt. A green probe
is not full pipeline or mission outcome evidence.

## Governance

No GitHub remote dispatch, new watcher, persistent token, document mutation,
merge or engineering credit. PR remains draft until owner accepts. Hub
may validate the candidate schema but must not self-approve it.

Disposition: TS_QUEUE_COMPONENT_CANDIDATE / OWNER_REVIEW_PENDING /
NATIVE_FEDERATION_READBACK_PENDING / MERGE_ADMISSION_HOLD.
