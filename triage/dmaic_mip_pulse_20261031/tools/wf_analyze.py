#!/usr/bin/env python3
"""Workflow census + hygiene metrics across GBOGEB federation clones.

Usage: wf_analyze.py OUT.json REPO_PATH [REPO_PATH ...]
Read-only. Standard library + PyYAML.
"""
import hashlib, json, os, re, sys, collections
import yaml

# PyYAML parses bare `on:` as boolean True; keep it a string.
class Loader(yaml.SafeLoader):
    pass
for ch in list(Loader.yaml_implicit_resolvers):
    Loader.yaml_implicit_resolvers[ch] = [
        (tag, rx) for tag, rx in Loader.yaml_implicit_resolvers[ch] if tag != "tag:yaml.org,2002:bool"
    ]

SHA_PIN = re.compile(r"@[0-9a-f]{40}$")
USES = re.compile(r"^\s*-?\s*uses:\s*['\"]?([^'\"\s#]+)", re.M)
PANDOC = re.compile(r"pandoc", re.I)


def norm_text(t: str) -> str:
    t = re.sub(r"#.*", "", t)
    t = re.sub(r"^\s*name:.*$", "", t, flags=re.M)
    return re.sub(r"\s+", " ", t).strip()


def triggers(on):
    if on is None:
        return []
    if isinstance(on, str):
        return [on]
    if isinstance(on, list):
        return [str(x) for x in on]
    if isinstance(on, dict):
        return [str(k) for k in on.keys()]
    return ["?"]


def has_path_filter(on):
    if not isinstance(on, dict):
        return False
    for ev in ("push", "pull_request", "pull_request_target"):
        cfg = on.get(ev)
        if isinstance(cfg, dict) and any(k in cfg for k in ("paths", "paths-ignore")):
            return True
    return False


def analyze_repo(path):
    wfdir = os.path.join(path, ".github", "workflows")
    out = {"repo": os.path.basename(path.rstrip("/")), "workflows": []}
    if not os.path.isdir(wfdir):
        return out
    for fn in sorted(os.listdir(wfdir)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        fp = os.path.join(wfdir, fn)
        raw = open(fp, encoding="utf-8", errors="replace").read()
        rec = {"file": fn, "bytes": len(raw), "hash": hashlib.sha256(norm_text(raw).encode()).hexdigest()[:16],
               "raw_sha": hashlib.sha256(raw.encode()).hexdigest()[:16]}
        try:
            doc = yaml.load(raw, Loader=Loader)
            rec["parse_ok"] = isinstance(doc, dict)
        except Exception as e:  # noqa: BLE001
            rec["parse_ok"] = False
            rec["parse_err"] = str(e).splitlines()[0][:160]
            doc = None
        uses = USES.findall(raw)
        rec["uses"] = uses
        rec["uses_sha_pinned"] = sum(1 for u in uses if SHA_PIN.search(u))
        rec["uses_local"] = sum(1 for u in uses if u.startswith("./"))
        rec["pandoc"] = bool(PANDOC.search(raw))
        if isinstance(doc, dict):
            on = doc.get("on")
            rec["triggers"] = triggers(on)
            rec["path_filter"] = has_path_filter(on)
            rec["concurrency"] = "concurrency" in doc
            rec["permissions_top"] = "permissions" in doc
            jobs = doc.get("jobs") or {}
            rec["jobs"] = len(jobs) if isinstance(jobs, dict) else 0
            jt = 0; jperm = 0; runs_on = []; matrix = 0
            if isinstance(jobs, dict):
                for j in jobs.values():
                    if not isinstance(j, dict):
                        continue
                    jt += 1 if "timeout-minutes" in j else 0
                    jperm += 1 if "permissions" in j else 0
                    if "concurrency" in j:
                        rec["concurrency"] = True
                    ro = j.get("runs-on")
                    runs_on.append(json.dumps(ro) if not isinstance(ro, str) else ro)
                    if isinstance(j.get("strategy"), dict) and "matrix" in j["strategy"]:
                        matrix += 1
            rec["jobs_with_timeout"] = jt
            rec["jobs_with_perm"] = jperm
            rec["runs_on"] = runs_on
            rec["matrix_jobs"] = matrix
            crons = []
            if isinstance(on, dict) and isinstance(on.get("schedule"), list):
                crons = [s.get("cron") for s in on["schedule"] if isinstance(s, dict)]
            rec["crons"] = crons
        out["workflows"].append(rec)
    return out


def cron_runs_per_day(expr):
    """Rough upper bound of runs/day for a 5-field cron."""
    try:
        m, h, dom, mon, dow = expr.split()
    except Exception:  # noqa: BLE001
        return 0

    def count(field, lo, hi):
        if field == "*":
            return hi - lo + 1
        n = 0
        for part in field.split(","):
            if part.startswith("*/"):
                n += len(range(lo, hi + 1, int(part[2:])))
            elif "/" in part:
                rng, step = part.split("/")
                a, b = (rng.split("-") + [hi])[:2] if "-" in rng else (rng, hi)
                n += len(range(int(a), int(b) + 1, int(step)))
            elif "-" in part:
                a, b = part.split("-"); n += int(b) - int(a) + 1
            else:
                n += 1
        return n

    per_day = count(m, 0, 59) * count(h, 0, 23)
    days = count(dow, 0, 6) if dow != "*" else 7
    return per_day * days / 7.0


def summarize(rep):
    wfs = rep["workflows"]
    ok = [w for w in wfs if w.get("parse_ok")]
    n = len(wfs) or 1
    jobs = sum(w.get("jobs", 0) for w in ok) or 1
    uses = sum(len(w["uses"]) for w in wfs)
    ext_uses = sum(len(w["uses"]) - w["uses_local"] for w in wfs) or 1
    trig = collections.Counter(t for w in ok for t in w.get("triggers", []))
    hashes = collections.Counter(w["hash"] for w in wfs)
    dup_files = sum(c for c in hashes.values() if c > 1)
    push_pr = [w for w in ok if {"push", "pull_request"} & set(w.get("triggers", []))]
    unfiltered = [w for w in push_pr if not w.get("path_filter")]
    cron_day = sum(cron_runs_per_day(c) for w in ok for c in w.get("crons", []) if c)
    checkout = collections.Counter(u.split("@")[1] for w in wfs for u in w["uses"] if u.startswith("actions/checkout@"))
    selfhosted = sum(1 for w in ok for r in w.get("runs_on", []) if "self-hosted" in r)
    return {
        "repo": rep["repo"],
        "workflows": len(wfs),
        "parse_fail": len(wfs) - len(ok),
        "jobs": jobs,
        "pct_concurrency": round(100 * sum(w.get("concurrency", False) for w in ok) / n, 1),
        "pct_jobs_timeout": round(100 * sum(w.get("jobs_with_timeout", 0) for w in ok) / jobs, 1),
        "pct_permissions": round(100 * sum(1 for w in ok if w.get("permissions_top") or w.get("jobs_with_perm")) / n, 1),
        "pct_ext_actions_sha_pinned": round(100 * sum(w["uses_sha_pinned"] for w in wfs) / ext_uses, 1),
        "uses_total": uses,
        "push_or_pr_workflows": len(push_pr),
        "push_or_pr_unfiltered": len(unfiltered),
        "schedule_workflows": trig.get("schedule", 0),
        "cron_runs_per_day": round(cron_day, 1),
        "workflow_dispatch": trig.get("workflow_dispatch", 0),
        "workflow_call": trig.get("workflow_call", 0),
        "workflow_run": trig.get("workflow_run", 0),
        "repository_dispatch": trig.get("repository_dispatch", 0),
        "dup_normalized_files": dup_files,
        "pandoc_workflows": sum(w["pandoc"] for w in wfs),
        "checkout_versions": dict(checkout),
        "self_hosted_jobs": selfhosted,
        "triggers": dict(trig.most_common()),
    }


if __name__ == "__main__":
    out_path, repos = sys.argv[1], sys.argv[2:]
    reps = [analyze_repo(p) for p in repos]
    # cross-repo duplicate clusters on normalized content
    owner = collections.defaultdict(set)
    for r in reps:
        for w in r["workflows"]:
            owner[w["hash"]].add(r["repo"])
    cross = {h: sorted(s) for h, s in owner.items() if len(s) > 1}
    summ = [summarize(r) for r in reps]
    for s, r in zip(summ, reps):
        s["cross_repo_shared_files"] = sum(1 for w in r["workflows"] if w["hash"] in cross)
    json.dump({"summary": summ, "cross_repo_clusters": len(cross), "detail": reps}, open(out_path, "w"), indent=1)
    cols = ["repo", "workflows", "parse_fail", "jobs", "pct_concurrency", "pct_jobs_timeout", "pct_permissions",
            "pct_ext_actions_sha_pinned", "push_or_pr_unfiltered", "schedule_workflows", "cron_runs_per_day",
            "dup_normalized_files", "cross_repo_shared_files", "pandoc_workflows", "workflow_call", "workflow_run"]
    print("\t".join(cols))
    for s in summ:
        print("\t".join(str(s[c]) for c in cols))
    print("cross-repo duplicate clusters:", len(cross))
