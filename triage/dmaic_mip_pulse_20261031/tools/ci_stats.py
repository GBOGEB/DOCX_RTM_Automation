import json, sys, collections, datetime as dt, statistics as st
def load(p): return [json.loads(l) for l in open(p) if l.strip()]
def t(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))
res={}
for repo in sys.argv[1:]:
    R=load(f'runs/{repo}.jsonl')
    done=[r for r in R if r['status']=='completed']
    c=collections.Counter(r['conclusion'] for r in done)
    span=(t(R[0]['created_at'])-t(R[-1]['created_at'])).total_seconds()/3600
    dur=[(t(r['updated_at'])-t(r['run_started_at'])).total_seconds() for r in done if r.get('run_started_at')]
    # meaningful = success|failure only
    sf=c['success']+c['failure']
    byday=collections.defaultdict(lambda: collections.Counter())
    for r in done: byday[r['created_at'][:10]][r['conclusion']]+=1
    wf=collections.defaultdict(collections.Counter)
    for r in done: wf[r['name']][r['conclusion']]+=1
    worst=sorted(((v['failure'], k, sum(v.values())) for k,v in wf.items()), reverse=True)[:6]
    ev=collections.Counter(r['event'] for r in R)
    main_fail=sum(1 for r in done if r['head_branch'] in ('main','master') and r['conclusion']=='failure')
    main_all=sum(1 for r in done if r['head_branch'] in ('main','master') and r['conclusion'] in ('success','failure'))
    res[repo]=dict(n=len(R), window_h=round(span,1), runs_per_h=round(len(R)/span,1), conclusions=dict(c),
        red_rate_pct=round(100*c['failure']/sf,1) if sf else None,
        skip_cancel_pct=round(100*(c['skipped']+c['cancelled']+c['action_required'])/len(done),1),
        main_red_pct=round(100*main_fail/main_all,1) if main_all else None, main_n=main_all,
        dur_p50_s=round(st.median(dur)), dur_p90_s=round(sorted(dur)[int(.9*len(dur))]),
        runner_hours=round(sum(dur)/3600,1), events=dict(ev.most_common(5)),
        distinct_workflows=len(wf), worst=worst,
        byday={d:dict(v) for d,v in sorted(byday.items())})
json.dump(res, open('ci_baseline.json','w'), indent=1)
for k,v in res.items():
    print('==',k); [print(f'  {a}: {b}') for a,b in v.items() if a!='byday']
    for d,v2 in v['byday'].items(): 
        s=v2.get('success',0); f=v2.get('failure',0); print(f'   {d} n={sum(v2.values())} red={round(100*f/(s+f),1) if s+f else "-"}%')
