#!/usr/bin/env python3
"""Classify CI reds with the MIP taxonomy, evidence-first.

EXTERNAL            job never started; annotation names billing/spending limit/runner (evidence: annotation text)
PRE_EXISTING_CAND   same workflow also red on the default branch inside the window (base-side evidence)
BRANCH_CAUSED_CAND  red on a PR branch, same workflow green on default branch inside the window
UNKNOWN             evidence insufficient (MIP rule: do not guess)

Usage: red_classify.py REPO [--workers 8]
Reads runs/REPO.jsonl, writes runs/REPO.classified.json
"""
import argparse, collections, concurrent.futures as cf, json, re, subprocess, time

EXT = re.compile(r"spending limit|payments have failed|billing|no runner|runner .*offline|quota", re.I)


def gh(path):
    p = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=60)
    if p.returncode != 0:
        return None
    return json.loads(p.stdout)


def probe(run, repo):
    jobs = gh(f"repos/GBOGEB/{repo}/actions/runs/{run['id']}/jobs?per_page=20") or {}
    jl = jobs.get("jobs", [])
    steps = sum(len(j.get("steps") or []) for j in jl)
    msg = ""
    if jl and steps == 0:
        ann = gh(f"repos/GBOGEB/{repo}/check-runs/{jl[0]['id']}/annotations") or []
        msg = " | ".join(a.get("message", "") for a in ann)[:400]
    return {"id": run["id"], "name": run["name"], "branch": run["head_branch"], "created": run["created_at"],
            "jobs": len(jl), "steps": steps, "annotation": msg}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("repo"); ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--default-branch", default="main")
    a = ap.parse_args()
    runs = [json.loads(l) for l in open(f"runs/{a.repo}.jsonl") if l.strip()]
    reds = [r for r in runs if r["conclusion"] == "failure"]
    t0 = time.perf_counter()
    with cf.ThreadPoolExecutor(max_workers=a.workers) as ex:
        probes = list(ex.map(lambda r: probe(r, a.repo), reds))
    wall = time.perf_counter() - t0
    # base-side evidence per workflow (default branch, non-external outcomes)
    base = collections.defaultdict(collections.Counter)
    ext_ids = {p["id"] for p in probes if p["steps"] == 0 and EXT.search(p["annotation"] or "")}
    for r in runs:
        if r["head_branch"] == a.default_branch and r["conclusion"] in ("success", "failure") and r["id"] not in ext_ids:
            base[r["name"]][r["conclusion"]] += 1
    out = []
    for p in probes:
        if p["id"] in ext_ids:
            cls = "EXTERNAL"
        elif p["branch"] == a.default_branch:
            cls = "PRE_EXISTING_CAND" if base[p["name"]]["failure"] >= 2 else "UNKNOWN"
        elif base[p["name"]]["failure"] > 0:
            cls = "PRE_EXISTING_CAND"
        elif base[p["name"]]["success"] > 0:
            cls = "BRANCH_CAUSED_CAND"
        else:
            cls = "UNKNOWN"
        p["class"] = cls
        out.append(p)
    c = collections.Counter(p["class"] for p in out)
    nonext = [r for r in runs if r["conclusion"] in ("success", "failure") and r["id"] not in ext_ids]
    code_red = sum(1 for r in nonext if r["conclusion"] == "failure")
    summary = {"repo": a.repo, "reds": len(reds), "classes": dict(c),
               "classified_pct": round(100 * (len(reds) - c["UNKNOWN"]) / max(1, len(reds)), 1),
               "evidence_backed_pct": round(100 * c["EXTERNAL"] / max(1, len(reds)), 1),
               "raw_red_rate_pct": round(100 * len(reds) / max(1, sum(r["conclusion"] in ("success", "failure") for r in runs)), 1),
               "code_red_rate_pct": round(100 * code_red / max(1, len(nonext)), 1),
               "api_calls": len(reds) + sum(1 for p in probes if p["steps"] == 0), "workers": a.workers,
               "wall_s": round(wall, 1),
               "top_nonexternal": collections.Counter((p["name"], p["class"]) for p in out if p["class"] != "EXTERNAL").most_common(8),
               "external_samples": list({p["annotation"][:140] for p in out if p["class"] == "EXTERNAL"})[:3]}
    json.dump({"summary": summary, "runs": out}, open(f"runs/{a.repo}.classified.json", "w"), indent=1)
    print(json.dumps(summary, indent=1))
