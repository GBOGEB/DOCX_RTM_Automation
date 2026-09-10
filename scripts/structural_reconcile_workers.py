#!/usr/bin/env python3
import argparse, hashlib, json, re
from collections import Counter, defaultdict
from pathlib import Path

TOKEN=re.compile(r"[a-z0-9]+")
CLAUSE=re.compile(r"^(\d+(?:\.\d+)*)")

def norm(s): return " ".join(TOKEN.findall(str(s or "").lower()))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def clause_of(s):
    m=CLAUSE.match(str(s or "").strip())
    return m.group(1) if m else ""
def parent_chain(c):
    if not c: return []
    bits=c.split('.')
    return ['.'.join(bits[:i]) for i in range(len(bits),0,-1)]

def load(path): return json.loads(Path(path).read_text(encoding='utf-8'))

def canonical_rows(d):
    rows=d.get('records', d.get('rows', []))
    out=[]
    for r in rows:
        rid=str(r.get('controlled_id') or r.get('rtm_id') or r.get('id') or '')
        stmt=str(r.get('statement') or r.get('full_verbatim_requirement') or r.get('description') or '')
        loc=str(r.get('source_locator') or r.get('locator') or r.get('section') or r.get('payload',{}).get('section_number') or '')
        sec=str(r.get('section') or r.get('payload',{}).get('section_number') or clause_of(loc))
        out.append({'id':rid,'statement':stmt,'norm':norm(stmt),'section':sec,'locator':loc})
    return out

def source_rows(d):
    return list(d.get('rtm_requirements', []))

def exact_worker(src, can):
    by=defaultdict(list)
    for r in can: by[r['norm']].append(r['id'])
    res=[]
    for s in src:
        ids=by.get(norm(s.get('description')),[])
        state='EXACT_TEXT' if len(ids)==1 else ('AMBIGUOUS' if len(ids)>1 else 'UNMATCHED')
        res.append({'source_atom_id':s.get('id'),'state':state,'candidates':ids})
    return res

def section_worker(src, can):
    by=defaultdict(list)
    for r in can:
        if r['section']: by[r['section']].append(r['id'])
    res=[]
    for s in src:
        sec=str(s.get('source_clause') or s.get('section') or '')
        chosen=[]; matched_level=''
        for p in parent_chain(sec):
            if by.get(p):
                chosen=by[p]; matched_level=p; break
        state='STRUCTURAL_PARENT' if len(chosen)==1 else ('AMBIGUOUS' if len(chosen)>1 else 'UNMATCHED')
        res.append({'source_atom_id':s.get('id'),'source_clause':sec,'state':state,'matched_clause':matched_level,'candidates':chosen})
    return res

def containment_worker(src, can):
    res=[]
    for s in src:
        st=norm(s.get('description'))
        ids=[]
        if st:
            ids=[r['id'] for r in can if st in r['norm'] or r['norm'] in st]
        state='TEXT_CONTAINMENT' if len(ids)==1 else ('AMBIGUOUS' if len(ids)>1 else 'UNMATCHED')
        res.append({'source_atom_id':s.get('id'),'state':state,'candidates':ids})
    return res

def summarize(rows):
    c=Counter(r['state'] for r in rows)
    accepted={x for r in rows if r['state'] in {'EXACT_TEXT','STRUCTURAL_PARENT','TEXT_CONTAINMENT'} and len(r['candidates'])==1 for x in r['candidates']}
    return {'states':dict(sorted(c.items())),'unique_canonical_candidates':len(accepted)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--extraction',required=True); ap.add_argument('--canonical',required=True); ap.add_argument('--worker',choices=['exact','section','containment','all'],default='all'); ap.add_argument('--output',required=True)
    a=ap.parse_args(); ext=load(a.extraction); can_doc=load(a.canonical); src=source_rows(ext); can=canonical_rows(can_doc)
    assert len(src)==757, len(src); assert len(can)==722, len(can)
    workers={'exact':exact_worker,'section':section_worker,'containment':containment_worker}
    selected=workers if a.worker=='all' else {a.worker:workers[a.worker]}
    out={'schema':'docx-structural-reconciliation-workers/v1','classification':'MEASUREMENT_ONLY_NOT_COMPLIANCE','inputs':{'source_atoms':len(src),'canonical_atoms':len(can),'extraction_sha256':sha(a.extraction),'canonical_sha256':sha(a.canonical)},'workers':{},'authority_effect':'NONE','compliance_credit':False,'release_credit':False}
    for name,fn in selected.items():
        rows=fn(src,can); out['workers'][name]={'summary':summarize(rows),'rows':rows}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({k:v['summary'] for k,v in out['workers'].items()},sort_keys=True))
if __name__=='__main__': main()
