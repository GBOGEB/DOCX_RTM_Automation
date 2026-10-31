#!/usr/bin/env python3
"""Additive workflow hardening (text insertion, comments preserved).

1. Jobs with `runs-on` and no `timeout-minutes` get `timeout-minutes: N`
   (jobs that call reusable workflows via `uses:` are skipped: key not allowed).
2. Workflows triggered by push/pull_request, without workflow_call and without
   any concurrency, get a PR-scoped group that cancels only superseded PR runs.
Verification: parsed(after) minus the added keys == parsed(before).

Usage: wf_harden.py WORKFLOW_DIR [--timeout 30]
"""
import argparse, copy, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import yaml
from wf_analyze import Loader

CONC = ("concurrency:\n"
        "  group: ${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}\n"
        "  cancel-in-progress: ${{ github.event_name == 'pull_request' }}\n\n")


def harden(text, timeout):
    doc = yaml.load(text, Loader=Loader)
    if not isinstance(doc, dict) or not isinstance(doc.get("jobs"), dict):
        return text, 0, False
    lines = text.splitlines(keepends=True)
    jobs = doc["jobs"]
    need = {k for k, j in jobs.items() if isinstance(j, dict) and "runs-on" in j and "timeout-minutes" not in j and "uses" not in j}
    out, added_t, in_jobs, cur, job_indent = [], 0, False, None, None
    for ln in lines:
        out.append(ln)
        if re.match(r"^jobs:\s*(#.*)?$", ln):
            in_jobs = True; continue
        if in_jobs and re.match(r"^\S", ln):
            in_jobs = False
        if not in_jobs:
            continue
        m = re.match(r"^(\s+)([A-Za-z0-9_\-]+):\s*(#.*)?$", ln)
        if m and (job_indent is None or len(m.group(1)) == job_indent):
            if job_indent is None:
                job_indent = len(m.group(1))
            cur = m.group(2); continue
        m = re.match(r"^(\s+)runs-on:", ln)
        if m and cur in need and len(m.group(1)) > (job_indent or 0):
            # insert after runs-on (and its continuation lines, if a block value follows we still insert at same indent)
            out.append(f"{m.group(1)}timeout-minutes: {timeout}\n"); added_t += 1; need.discard(cur)
    text2 = "".join(out)
    on = doc.get("on")
    trig = set(on.keys()) if isinstance(on, dict) else set(on if isinstance(on, list) else [on])
    has_conc = "concurrency" in doc or any(isinstance(j, dict) and "concurrency" in j for j in jobs.values())
    added_c = False
    if {"push", "pull_request"} & trig and "workflow_call" not in trig and not has_conc:
        text2 = re.sub(r"^jobs:", CONC + "jobs:", text2, count=1, flags=re.M); added_c = True
    # verify additive-only
    after = yaml.load(text2, Loader=Loader)
    strip = copy.deepcopy(after)
    if added_c:
        strip.pop("concurrency", None)
    for k, j in strip["jobs"].items():
        if isinstance(j, dict) and isinstance(doc["jobs"].get(k), dict) and "timeout-minutes" not in doc["jobs"][k]:
            j.pop("timeout-minutes", None)
    if json.dumps(strip, sort_keys=True, default=str) != json.dumps(doc, sort_keys=True, default=str):
        raise ValueError("non-additive change")
    return text2, added_t, added_c


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--timeout", type=int, default=30)
    a = ap.parse_args()
    T = C = F = E = 0
    for fn in sorted(os.listdir(a.dir)):
        if not fn.endswith((".yml", ".yaml")):
            continue
        p = os.path.join(a.dir, fn); t = open(p, encoding="utf-8").read()
        try:
            t2, at, ac = harden(t, a.timeout)
        except Exception as e:  # noqa: BLE001
            E += 1; print("SKIP", fn, e, file=sys.stderr); continue
        if t2 != t:
            open(p, "w", encoding="utf-8").write(t2); F += 1; T += at; C += ac
    print(json.dumps({"dir": a.dir, "files_changed": F, "timeouts_added": T, "concurrency_added": C, "skipped_errors": E}))
