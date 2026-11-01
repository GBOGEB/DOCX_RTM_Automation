import json, sys, collections, datetime as dt, statistics as st
def load(p): return [json.loads(l) for l in open(p) if l.strip()]
def t(s): return dt.datetime.fromisoformat(s.replace('Z','+00:00'))

def summarize(R):
    done=[r for r in R if r['status']=='completed']
    c=collections.Counter(r['conclusion'] for r in done)
    dates=[t(r['created_at']) for r in R if r.get('created_at')]
    span=(max(dates)-min(dates)).total_seconds()/3600 if dates else None
    dur=[(t(r['updated_at'])-t(r['run_started_at'])).total_seconds()
         for r in done if r.get('run_started_at') and r.get('updated_at')]
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
    return dict(n=len(R), window_h=round(span,1) if span is not None else None,
        runs_per_h=round(len(R)/span,1) if span and span > 0 else None, conclusions=dict(c),
        red_rate_pct=round(100*c['failure']/sf,1) if sf else None,
        skip_cancel_pct=round(100*(c['skipped']+c['cancelled']+c['action_required'])/len(done),1) if done else None,
        main_red_pct=round(100*main_fail/main_all,1) if main_all else None, main_n=main_all,
        dur_p50_s=round(st.median(dur)) if dur else None,
        dur_p90_s=round(sorted(dur)[int(.9*len(dur))]) if dur else None,
        workflow_elapsed_hours=round(sum(dur)/3600,1) if dur else None,
        events=dict(ev.most_common(5)), distinct_workflows=len(wf), worst=worst,
        byday={d:dict(v) for d,v in sorted(byday.items())})

def main():
    res={}
    for repo in sys.argv[1:]:
        R=load(f'runs/{repo}.jsonl')
        res[repo]=summarize(R)
    json.dump(res, open('ci_baseline.json','w'), indent=1)
    for k,v in res.items():
        print('==',k); [print(f'  {a}: {b}') for a,b in v.items() if a!='byday']
        for d,v2 in v['byday'].items():
            s=v2.get('success',0); f=v2.get('failure',0); print(f'   {d} n={sum(v2.values())} red={round(100*f/(s+f),1) if s+f else "-"}%')


if __name__ == "__main__":
    main()
