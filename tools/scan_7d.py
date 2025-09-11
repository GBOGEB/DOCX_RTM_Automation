#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONF_REPOS = ROOT / "config" / "repositories.yaml"
CONF_PREFS = ROOT / "config" / "scan_prefs.yaml"
OUT_MD = ROOT / "docs" / "SCAN_7D.md"
OUT_JSON = ROOT / "docs" / "scan_7d.json"

GITHUB_API = "https://api.github.com"

def load_yaml(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text()) or default

def gh_get(url: str, params: Dict[str, Any]) -> Tuple[int, Any]:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.get(url, headers=headers, params=params, timeout=30)
    try:
        data = r.json()
    except Exception:
        data = r.text
    return r.status_code, data

def iso_now_minus_days(days: int) -> str:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=days)).isoformat(timespec="seconds").replace("+00:00", "Z")

def score_issue(issue: Dict[str, Any], prefs: Dict[str, Any]) -> float:
    labels = {l.get("name", "").lower() for l in issue.get("labels", [])}
    state = issue.get("state", "open")
    if state == "closed":
        return 1.0
    if labels & set(map(str.lower, prefs.get("labels_done", []))):
        return 1.0
    if labels & set(map(str.lower, prefs.get("labels_in_progress", []))):
        return 0.5
    if labels & set(map(str.lower, prefs.get("labels_todo", []))):
        return 0.2
    return 0.4 if state == "open" else 0.0

def score_pr(pr: Dict[str, Any]) -> float:
    if pr.get("merged_at"):
        return 1.0
    if pr.get("draft"):
        return 0.3
    if pr.get("state") == "open":
        return 0.6
    if pr.get("state") == "closed":
        return 0.8
    return 0.5

def activity_weight(commits_count: int) -> float:
    # Log-like scaling
    if commits_count <= 0:
        return 0.0
    if commits_count == 1:
        return 0.2
    if commits_count <= 3:
        return 0.4
    if commits_count <= 7:
        return 0.6
    if commits_count <= 15:
        return 0.8
    return 1.0

def detect_integration(reponame: str, issues: List[Dict[str, Any]], prs: List[Dict[str, Any]], prefs: Dict[str, Any]) -> Dict[str, Any]:
    merged_terms = set(map(str.lower, prefs.get("integration_hints", {}).get("keywords_merge", [])))
    separate_terms = set(map(str.lower, prefs.get("integration_hints", {}).get("keywords_separate", [])))
    shared_labels = set(map(str.lower, prefs.get("integration_hints", {}).get("shared_labels", [])))

    merge_hits = 0
    separate_hits = 0
    shared_label_hits = 0

    def hit(text: str, terms: set) -> int:
        t = text.lower()
        return sum(1 for k in terms if k in t)

    for it in issues:
        title = it.get("title", "")
        body = it.get("body", "") or ""
        labels = {l.get("name", "").lower() for l in it.get("labels", [])}
        merge_hits += hit(title + " " + body, merged_terms)
        separate_hits += hit(title + " " + body, separate_terms)
        shared_label_hits += len(labels & shared_labels)

    for pr in prs:
        title = pr.get("title", "")
        body = pr.get("body", "") or ""
        labels = {l.get("name", "").lower() for l in pr.get("labels", [])}
        merge_hits += hit(title + " " + body, merged_terms)
        separate_hits += hit(title + " " + body, separate_terms)
        shared_label_hits += len(labels & shared_labels)

    decision = "separate"
    rationale = "Low overlap"
    if merge_hits > separate_hits or shared_label_hits >= 2:
        decision = "merge"
        rationale = "Shared labels/terms suggest consolidation"
    if merge_hits == separate_hits and shared_label_hits == 0:
        decision = "separate"
        rationale = "No consolidation signals detected"

    return {"repo": reponame, "decision": decision, "rationale": rationale, "signals": {"merge_hits": merge_hits, "separate_hits": separate_hits, "shared_label_hits": shared_label_hits}}

def fetch_repo_data(owner: str, repo: str, since_iso: str, prefs: Dict[str, Any], max_items: int) -> Dict[str, Any]:
    repo_full = f"{owner}/{repo}"
    # Commits
    sc, commits = gh_get(f"{GITHUB_API}/repos/{owner}/{repo}/commits", {"since": since_iso, "per_page": 100})
    commits = commits if isinstance(commits, list) else []
    commits_slim = [
        {
            "sha": c.get("sha"),
            "date": ((c.get("commit") or {}).get("author") or {}).get("date"),
            "author": ((c.get("commit") or {}).get("author") or {}).get("name"),
            "message": ((c.get("commit") or {}).get("message") or "").splitlines()[0][:160],
            "html_url": c.get("html_url"),
        }
        for c in commits[:max_items]
    ]
    # Issues (includes PRs)
    sc, issues = gh_get(f"{GITHUB_API}/repos/{owner}/{repo}/issues", {"since": since_iso, "state": "all", "per_page": 100})
    issues = issues if isinstance(issues, list) else []
    issues_only = [i for i in issues if "pull_request" not in i]
    prs_stub = [i for i in issues if "pull_request" in i]

    # Resolve PRs for status
    resolved_prs: List[Dict[str, Any]] = []
    for i in prs_stub[:max_items]:
        num = i.get("number")
        sc, pr = gh_get(f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{num}", {})
        if isinstance(pr, dict):
            resolved_prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "state": pr.get("state"),
                "draft": pr.get("draft", False),
                "merged_at": pr.get("merged_at"),
                "updated_at": pr.get("updated_at"),
                "labels": pr.get("labels", []),
                "html_url": pr.get("html_url"),
            })

    # Scores
    issue_scores = [score_issue(i, prefs) for i in issues_only[:max_items]]
    pr_scores = [score_pr(p) for p in resolved_prs[:max_items]]
    act = activity_weight(len(commits))
    priority_boost = 0.15 if repo in (prefs.get("priority_projects") or []) else 0.0
    completion_score = round((sum(issue_scores + pr_scores) / max(1, len(issue_scores + pr_scores))) + act + priority_boost, 3)

    integration = detect_integration(repo, issues_only, resolved_prs, prefs)

    return {
        "repo": repo_full,
        "since": since_iso,
        "counts": {
            "commits": len(commits),
            "issues_all": len(issues),
            "issues_only": len(issues_only),
            "prs": len(resolved_prs),
        },
        "completion_score": completion_score,
        "activity_weight": act,
        "priority_boost": priority_boost,
        "top": {
            "commits": commits_slim,
            "issues": [
                {
                    "number": i.get("number"),
                    "title": i.get("title"),
                    "state": i.get("state"),
                    "labels": i.get("labels", []),
                    "updated_at": i.get("updated_at") or i.get("created_at"),
                    "html_url": i.get("html_url"),
                }
                for i in issues_only[:max_items]
            ],
            "prs": resolved_prs[:max_items],
        },
        "integration": integration,
    }

def generate_md(reports: List[Dict[str, Any]], since_iso: str) -> str:
    lines = []
    lines.append(f"# 7-Day Scan since {since_iso}")
    lines.append("")
    # Overview ranking
    ranked = sorted(reports, key=lambda r: r.get("completion_score", 0), reverse=True)
    lines.append("## Ranking (by completion score)")
    for idx, r in enumerate(ranked, 1):
        lines.append(f"{idx}. {r['repo']} — score={r['completion_score']} (commits={r['counts']['commits']}, issues={r['counts']['issues_only']}, PRs={r['counts']['prs']})")
    lines.append("")

    # Integration proposals
    lines.append("## Pipeline Grouping (merge vs separate)")
    for r in ranked:
        integ = r["integration"]
        lines.append(f"- {r['repo']}: {integ['decision']} — {integ['rationale']} (merge_hits={integ['signals']['merge_hits']}, separate_hits={integ['signals']['separate_hits']}, shared_labels={integ['signals']['shared_label_hits']})")
    lines.append("")

    # Per-repo details
    for r in ranked:
        lines.append(f"## {r['repo']}")
        lines.append(f"- Commits: {r['counts']['commits']}  Issues: {r['counts']['issues_only']}  PRs: {r['counts']['prs']}")
        lines.append(f"- Completion score: {r['completion_score']} (activity={r['activity_weight']}, priority_boost={r['priority_boost']})")
        lines.append("")
        if r["top"]["commits"]:
            lines.append("### Recent commits")
            for c in r["top"]["commits"]:
                lines.append(f"- {c['sha'][:7]} {c['date']} {c['author']}: {c['message']} ({c['html_url']})")
            lines.append("")
        if r["top"]["issues"]:
            lines.append("### Issues (last 7 days)")
            for i in r["top"]["issues"]:
                lab = [l.get('name') for l in i.get('labels', [])]
                lines.append(f"- #{i['number']} [{i['state']}] {i['title']} — labels={lab} — {i['updated_at']} ({i['html_url']})")
            lines.append("")
        if r["top"]["prs"]:
            lines.append("### Pull Requests (last 7 days)")
            for p in r["top"]["prs"]:
                lab = [l.get('name') for l in p.get('labels', [])]
                state = "merged" if p.get("merged_at") else p.get("state")
                lines.append(f"- #{p['number']} [{state}]{' [draft]' if p.get('draft') else ''} {p['title']} — labels={lab} — {p['updated_at']} ({p['html_url']})")
            lines.append("")
    return "\n".join(lines) + "\n"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="Override days window")
    ap.add_argument("--no-md", action="store_true", help="Do not write Markdown")
    ap.add_argument("--no-json", action="store_true", help="Do not write JSON")
    ap.add_argument("--skip-baseline-candidate", action="store_true", help="Do not record candidate_Baseline note")
    args = ap.parse_args()

    prefs = load_yaml(CONF_PREFS, {})
    days = args.days if args.days > 0 else int(prefs.get("scan_window_days", 7))
    since_iso = iso_now_minus_days(days)

    repos_cfg = load_yaml(CONF_REPOS, {})
    owner = repos_cfg.get("owner") or os.getenv("GH_OWNER") or ""
    repos = repos_cfg.get("repos") or []
    max_items = int(prefs.get("max_items_per_section", 12))

    reports = []
    for repo in repos:
        try:
            reports.append(fetch_repo_data(owner, repo, since_iso, prefs, max_items))
        except Exception as e:
            reports.append({"repo": f"{owner}/{repo}", "error": str(e)})

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    if not args.no_json:
        OUT_JSON.write_text(json.dumps({"since": since_iso, "reports": reports}, indent=2))

    if not args.no_md:
        OUT_MD.write_text(generate_md(reports, since_iso))

    if not args.skip_baseline_candidate:
        # Record a candidate baseline note (best-effort)
        try:
            os.system(f"python tools/baseline.py --candidate --note \"7-day scan since {since_iso}\" >/dev/null 2>&1 || true")
        except Exception:
            pass

    print(f"[scan] Wrote {OUT_MD if not args.no_md else '(md skipped)'} and {OUT_JSON if not args.no_json else '(json skipped)'}")

if __name__ == "__main__":
    main()