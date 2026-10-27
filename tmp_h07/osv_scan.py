"""Temporary H07 triage: query OSV for every exactly pinned dependency in the repo's manifests."""
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY_MANIFESTS = ["requirements/requirements.lock", "requirements/requirements.txt", "requirements.txt",
                "requirements-dev.txt", "config/requirements.txt", "config/requirements_minimal.txt"]
pkgs = {}  # (eco, name, version) -> set(manifests)
for m in PY_MANIFESTS:
    for raw in (ROOT / m).read_text(encoding="utf-8").splitlines():
        line = raw.split("#")[0].strip().rstrip("\\").strip()
        mm = re.match(r"^([A-Za-z0-9._-]+)(?:\[[^\]]*\])?==([^\s;]+)", line)
        if mm:
            pkgs.setdefault(("PyPI", mm.group(1).lower(), mm.group(2)), set()).add(m)
lock = json.loads((ROOT / "orchestration_ts/package-lock.json").read_text(encoding="utf-8"))
for path, meta in lock["packages"].items():
    if not path or "version" not in meta:
        continue
    name = path.split("node_modules/")[-1]
    pkgs.setdefault(("npm", name, meta["version"]), set()).add("orchestration_ts/package-lock.json")

def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

keys = sorted(pkgs)
hits = []
for i in range(0, len(keys), 500):
    chunk = keys[i:i + 500]
    res = post("https://api.osv.dev/v1/querybatch",
               {"queries": [{"package": {"ecosystem": e, "name": n}, "version": v} for e, n, v in chunk]})
    for k, r in zip(chunk, res["results"]):
        for v in r.get("vulns", []):
            hits.append((k, v["id"]))
details = {}
for _, vid in hits:
    if vid not in details:
        with urllib.request.urlopen(f"https://api.osv.dev/v1/vulns/{vid}", timeout=60) as r:
            details[vid] = json.load(r)
out = []
for (eco, name, ver), vid in hits:
    d = details[vid]
    ghsa = [a for a in [vid] + d.get("aliases", []) if a.startswith("GHSA-")]
    sev = (d.get("database_specific") or {}).get("severity")
    fixed = []
    for aff in d.get("affected", []):
        if aff.get("package", {}).get("name", "").lower() != name.lower():
            continue
        for rng in aff.get("ranges", []):
            for ev in rng.get("events", []):
                if "fixed" in ev:
                    fixed.append(ev["fixed"])
    out.append({"ecosystem": eco, "package": name, "version": ver, "id": vid, "ghsa": ghsa,
                "severity": sev, "fixed": sorted(set(fixed)), "summary": d.get("summary", ""),
                "manifests": sorted(pkgs[(eco, name, ver)])})
dest = ROOT / "tmp_h07/osv_results.json"
dest.write_text(json.dumps({"scanned": len(keys), "findings": out}, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"scanned {len(keys)} pinned packages, {len(out)} findings")
