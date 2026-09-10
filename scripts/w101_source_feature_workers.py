#!/usr/bin/env python3
import argparse, hashlib, json, re, os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
TOKEN=re.compile(r"[a-z0-9]+")
CLAUSE=re.compile(r"^(\d+(?:\.\d+)*)")
SOURCE_DOC="addenda/Addendum_II_Cryoplant_Technical_Requirements.docx"
SEMANTIC_AS_OF="2026-09-10T00:00:00Z"
PARENT_HEAD="7aec5919ec5dcd693fb7c653ae467f47c302319a"

def sha_bytes(b): return hashlib.sha256(b).hexdigest()
def sha_file(p): return sha_bytes(Path(p).read_bytes())
def norm(s): return " ".join(TOKEN.findall(str(s or "").lower()))
def clause(s):
    m=CLAUSE.match(str(s or "").strip()); return m.group(1) if m else ""
def family(c): return c.split('.')[0] if c else "UNALLOCATED"
def stable_digest(obj):
    return sha_bytes(json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode())

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--extraction',required=True); ap.add_argument('--lane',choices=['clause','text','family'],required=True); ap.add_argument('--output',required=True)
    a=ap.parse_args(); d=json.loads(Path(a.extraction).read_text()); rows=list(d.get('rtm_requirements',[])); assert len(rows)==757, len(rows)
    feats=[]
    for r in rows:
        c=str(r.get('source_clause') or r.get('section') or '')
        base={'source_atom_id':r.get('id'),'source_index':r.get('source_index'),'source_kind':r.get('source_kind')}
        if a.lane=='clause': base.update({'source_clause':c,'clause':clause(c),'parent_chain':['.'.join(clause(c).split('.')[:i]) for i in range(len(clause(c).split('.')),0,-1)] if clause(c) else []})
        elif a.lane=='text': base.update({'normalized_text':norm(r.get('description')),'token_count':len(norm(r.get('description')).split())})
        else: base.update({'source_clause':c,'family':family(clause(c))})
        feats.append(base)
    semantic={'lane':a.lane,'source_atoms':757,'source_extraction_sha256':sha_file(a.extraction),'source_document_path':SOURCE_DOC,'features':feats,'parent_failed_head':PARENT_HEAD,'semantic_as_of':SEMANTIC_AS_OF}
    receipt={'schema':'w101-source-feature-receipt/v1','classification':'SOURCE_ONLY_MEASUREMENT','producer_commit_sha':os.environ.get('GITHUB_SHA','LOCAL'),'observed_at':datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),'semantic':semantic,'semantic_digest':stable_digest(semantic),'authority_effect':'NONE','compliance_credit':False,'release_credit':False}
    Path(a.output).parent.mkdir(parents=True,exist_ok=True); Path(a.output).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'lane':a.lane,'source_atoms':757,'semantic_digest':receipt['semantic_digest']},sort_keys=True))
if __name__=='__main__': main()
