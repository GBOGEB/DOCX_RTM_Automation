'use strict';
const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {execFileSync}=require('node:child_process');
const probe=require('./n32_owner_probe.cjs');
const ROOT=path.resolve(__dirname,'../../');
const HEAD=execFileSync('git',['-C',ROOT,'rev-parse','HEAD'],{encoding:'utf8'}).trim();
const {JobQueue}=require(path.join(ROOT,probe.COMPILED));

test('actual compiled TypeScript FIFO behavior across 32 real queue operations',()=>{
  const r=probe.exercise(JobQueue,32);
  assert.equal(r.completed,32);
  assert.equal(r.accepted_order[0],'Q001');
  assert.equal(r.accepted_order[31],'Q032');
  assert.equal(r.checks.positive_fifo,true);
  assert.equal(r.checks.empty_dequeue_guard,true);
});

test('owner adapter duplicate and counterfactual wrong-order fail closed',()=>{
  const q=new JobQueue(),known=new Set();
  probe.boundedEnqueue(q,{id:'A',type:'read-only',payload:null},known);
  assert.throws(()=>probe.boundedEnqueue(q,{id:'A',type:'read-only',payload:null},known),
                /DUPLICATE_ID_ADAPTER_REJECTED/);
  assert.throws(()=>probe.verifySequence(['B','A'],['A','B']),
                /ORDER_OR_POPULATION_MISMATCH/);
  // Native JobQueue itself does not reject duplicate IDs: no false native guard credit.
  q.enqueue({id:'A',type:'read-only',payload:null});
  assert.equal(q.size(),2);
});

test('out-of-scope task counts are never silently accepted',()=>{
  for(const n of [0,1,33,64,-1,1.2]) {
    assert.throws(()=>probe.exercise(JobQueue,n),/OUT_OF_BOUNDS/);
  }
});

test('exact-head check cannot be bypassed by a fabricated or stale SHA',()=>{
  assert.throws(()=>probe.requireSource(ROOT,'notsha'),/SOURCE_HEAD_INVALID/);
  assert.throws(()=>probe.requireSource(ROOT,'a'.repeat(40)),/SOURCE_HEAD_MISMATCH/);
  assert.equal(probe.requireSource(ROOT,HEAD),HEAD);
});

test('actual native component output and manifest hash are reproducible',()=>{
  const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'n32-docx-probe-'));
  try {
    const out=path.join(tmp,'out');
    const receipt=probe.run(ROOT,HEAD,out);
    assert.equal(receipt.observed.completed,32);
    assert.equal(receipt.caveats.native_job_authenticated,false);
    assert.equal(receipt.caveats.cross_repository_owner_approved,false);
    assert.equal(receipt.caveats.full_federation_process_covered,false);
    const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json'),'utf8'));
    assert.equal(manifest.files_sha256['owner_receipt.json'],
                 probe.digest(fs.readFileSync(path.join(out,'owner_receipt.json'))));
    assert.throws(()=>probe.run(ROOT,HEAD,out),/OUTPUT_NOT_EMPTY/);
    const out2=path.join(tmp,'out2');
    probe.run(ROOT,HEAD,out2);
    assert.equal(probe.digest(fs.readFileSync(path.join(out,'owner_receipt.json'))),
                 probe.digest(fs.readFileSync(path.join(out2,'owner_receipt.json'))));
  } finally {fs.rmSync(tmp,{recursive:true,force:true});}
});

test('candidate cannot overwrite source checkout or claim TS branch coverage',()=>{
  assert.throws(()=>probe.run(ROOT,HEAD,path.join(ROOT,'bad-output')),
                /OUTPUT_OVERLAPS_SOURCE/);
  const r=probe.exercise(JobQueue);
  assert.equal(r.checks.adapter_duplicate_id_rejected,true);
  assert.equal(r.checks.deliberate_bad_order_rejected,true);
});
