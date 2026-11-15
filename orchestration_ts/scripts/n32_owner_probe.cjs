#!/usr/bin/env node
'use strict';
/**
 * N3.2 owner-side typed FIFO execution receipt.
 * Uses actual compiled TypeScript JobQueue, not a Python approximation.
 * Component evidence, not full DOCX agent federation or owner approval.
 */
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { execFileSync } = require('node:child_process');
const SHA = /^[0-9a-f]{40}$/;
const SCHEMA = 'docx.n32.typecript-queue-candidate.v1';
const SOURCE = 'orchestration_ts/src/queue/JobQueue.ts';
const LOCK = 'orchestration_ts/package-lock.json';
const COMPILED = 'orchestration_ts/dist/queue/JobQueue.js';
function digest(buf) { return crypto.createHash('sha256').update(buf).digest('hex'); }
function requireSource(root, head) {
  if (!SHA.test(head)) throw new Error('SOURCE_HEAD_INVALID');
  const observed = execFileSync('git', ['-C', root, 'rev-parse', 'HEAD'],
                                 { encoding: 'utf8', timeout: 10000 }).trim();
  if (observed !== head) throw new Error('SOURCE_HEAD_MISMATCH');
  return head;
}
function ownerSources(root) {
  return Object.fromEntries([SOURCE, LOCK, COMPILED].map(name => {
    const p = path.join(root, name);
    if (!fs.statSync(p).isFile()) throw new Error('COMPONENT_SOURCE_MISSING');
    return [name, digest(fs.readFileSync(p))];
  }));
}
function verifySequence(actual, expected) {
  if (actual.length !== expected.length ||
      actual.some((x, i) => x !== expected[i])) {
    throw new Error('ORDER_OR_POPULATION_MISMATCH');
  }
}
function boundedEnqueue(queue, job, accepted) {
  if (accepted.has(job.id)) throw new Error('DUPLICATE_ID_ADAPTER_REJECTED');
  accepted.add(job.id);
  queue.enqueue(job);
}
function exercise(JobQueue, n = 32) {
  if (!Number.isInteger(n) || n < 2 || n > 32) throw new Error('OUT_OF_BOUNDS');
  const q = new JobQueue();
  const expected = Array.from({length:n},(_,i)=>'Q'+String(i+1).padStart(3,'0'));
  const known = new Set();
  for (const id of expected) boundedEnqueue(q, {id,type:'read-only',payload:null}, known);
  if (q.size() !== n) throw new Error('QUEUE_COUNT_MISMATCH');
  const observed = [];
  while(q.size()) {
    const job = q.dequeue();
    if (!job) throw new Error('DEQUEUE_MISSING');
    observed.push(job.id);
  }
  verifySequence(observed, expected);
  if (q.dequeue() !== undefined || q.size() !== 0) throw new Error('EMPTY_QUEUE_CONTRACT');
  const checks = {positive_fifo:true, empty_dequeue_guard:true};
  try {boundedEnqueue(q, {id:expected[0],type:'read-only',payload:null}, known);}
  catch(e){ if(e.message==='DUPLICATE_ID_ADAPTER_REJECTED') checks.adapter_duplicate_id_rejected=true;
            else throw e; }
  try { verifySequence([...observed].reverse(),expected); }
  catch(e){ if(e.message==='ORDER_OR_POPULATION_MISMATCH') checks.deliberate_bad_order_rejected=true;
            else throw e; }
  if (Object.keys(checks).length !== 4) throw new Error('NEGATIVE_ORACLE_NOT_EXECUTED');
  return {submitted:n,completed:n,accepted_order:observed,checks};
}
function run(root, head, out) {
  root=path.resolve(root);out=path.resolve(out);
  if (out===root || out.startsWith(root+path.sep)) throw new Error('OUTPUT_OVERLAPS_SOURCE');
  if (fs.existsSync(out) && fs.readdirSync(out).length) throw new Error('OUTPUT_NOT_EMPTY');
  requireSource(root,head);
  const identities=ownerSources(root);
  const { JobQueue }=require(path.join(root,COMPILED));
  const first=exercise(JobQueue), again=exercise(JobQueue);
  if (JSON.stringify(first)!==JSON.stringify(again)) throw new Error('QUEUE_NONIDEMPOTENT');
  requireSource(root,head);
  const receipt={schema:SCHEMA,repository:'GBOGEB/DOCX_RTM_Automation',
    source_head:head,source_sha256:identities,
    owner_component:SOURCE,execution_type:'COMPILED_TYPESCRIPT_QUEUE_ACTUAL',
    independent_replay_identical:true,observed:first,
    caveats:{duplicate_id_rejected_by:'OWNER_PROBE_ADAPTER_NOT_NATIVE_QUEUE',
      full_federation_process_covered:false,javascript_branch_coverage_pct:null,
      cross_repository_owner_approved:false,native_job_authenticated:false,
      outbound_private_data:false,remote_dispatch_authorized:false,
      merge_authorized:false,engineering_credit_delta:0}};
  const bytes=Buffer.from(JSON.stringify(receipt,null,2)+'\n');
  fs.mkdirSync(out,{recursive:true});
  fs.writeFileSync(path.join(out,'owner_receipt.json'),bytes);
  const manifest={schema:'docx.n32.owner-member-manifest.v1',source_head:head,
    files_sha256:{'owner_receipt.json':digest(bytes)},
    authorized_federation_admission:false};
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  console.log(JSON.stringify({status:'DOCX_TS_COMPONENT_OBSERVED',
    source_sha:head,verified_jobs:first.completed,negative_guards:3,
    owner_accepted:false,native_authenticated:false}));
  return receipt;
}
function main(argv=process.argv.slice(2)) {
  const arg=(key)=>{const pos=argv.indexOf(key);return pos>=0?argv[pos+1]:undefined;};
  if(!arg('--root')||!arg('--head')||!arg('--out'))throw new Error('ARGS_ROOT_HEAD_OUT_REQUIRED');
  run(arg('--root'),arg('--head'),arg('--out'));
}
if (require.main===module) {
  try {main();} catch(e) {console.error(e.message);process.exitCode=1;}
}
module.exports={SCHEMA,SOURCE,COMPILED,exercise,run,requireSource,verifySequence,
                boundedEnqueue,ownerSources,digest,main};
