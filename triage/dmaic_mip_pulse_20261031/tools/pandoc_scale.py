#!/usr/bin/env python3
"""Pandoc PoC + scaling study.

Phase A (PoC): small cluster, each conversion must succeed and be deterministic.
Phase B (scale): grow corpus size S and worker count N; measure throughput.
Fit Universal Scalability Law  X(N) = l*N / (1 + s(N-1) + k N(N-1)).

Usage: pandoc_scale.py CORPUS_DIR OUT.json [--formats docx,html] [--ref REFERENCE_DOCX]
"""
import argparse, concurrent.futures as cf, hashlib, json, os, statistics, subprocess, sys, tempfile, time


def convert(args):
    src, fmt, outdir, ref, lua = args
    base = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(outdir, f"{base}.{fmt}")
    cmd = ["pandoc", src, "-f", "gfm+yaml_metadata_block", "-o", out, "--quiet"]
    if fmt == "html":
        cmd += ["-s", "--metadata", f"title={base}"]
    if fmt == "docx" and ref:
        cmd += ["--reference-doc", ref]
    for f in lua or []:
        cmd += ["--lua-filter", f]
    t0 = time.perf_counter()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    dt = time.perf_counter() - t0
    ok = p.returncode == 0 and os.path.exists(out) and os.path.getsize(out) > 0
    return {"src": src, "fmt": fmt, "ok": ok, "s": dt, "err": p.stderr[-300:] if not ok else "",
            "bytes": os.path.getsize(out) if ok else 0}


def digest(path, fmt):
    """Content digest robust to docx zip timestamps: hash the document.xml part."""
    if fmt == "docx":
        import zipfile
        with zipfile.ZipFile(path) as z:
            return hashlib.sha256(z.read("word/document.xml")).hexdigest()[:16]
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def run_batch(files, fmt, workers, ref, lua):
    with tempfile.TemporaryDirectory() as td:
        jobs = [(f, fmt, td, ref, lua) for f in files]
        t0 = time.perf_counter()
        if workers == 1:
            res = [convert(j) for j in jobs]
        else:
            with cf.ThreadPoolExecutor(max_workers=workers) as ex:  # each job is its own pandoc process
                res = list(ex.map(convert, jobs))
        wall = time.perf_counter() - t0
        digests = {}
        for r in res:
            if r["ok"]:
                base = os.path.splitext(os.path.basename(r["src"]))[0]
                digests[base] = digest(os.path.join(td, f"{base}.{fmt}"), fmt)
    return wall, res, digests


def usl_fit(points):
    """Grid-search least squares for USL on (N, X). Returns l, s, k, R2, N*."""
    best = None
    l0 = points[0][1]
    for si in range(0, 101):
        s = si / 100
        for ki in range(0, 101):
            k = ki / 1000
            pred = [(n, l0 * n / (1 + s * (n - 1) + k * n * (n - 1))) for n, _ in points]
            err = sum((x - p) ** 2 for (_, x), (_, p) in zip(points, pred))
            if best is None or err < best[0]:
                best = (err, s, k)
    _, s, k = best
    xs = [x for _, x in points]
    mean = statistics.mean(xs)
    ss_tot = sum((x - mean) ** 2 for x in xs) or 1e-9
    r2 = 1 - best[0] / ss_tot
    nstar = ((1 - s) / k) ** 0.5 if k > 0 else None
    return {"lambda": round(l0, 3), "sigma": s, "kappa": k, "R2": round(r2, 3),
            "N_star": round(nstar, 2) if nstar is not None else None}


def poc_summary(small, r1, r2, d1, d2):
    pairs = list(zip(small, r1, r2))
    successful = [a["ok"] and b["ok"] for _, a, b in pairs]
    deterministic = [
        a["ok"] and b["ok"] and d1.get(os.path.splitext(os.path.basename(src))[0]) is not None
        and d1.get(os.path.splitext(os.path.basename(src))[0]) == d2.get(os.path.splitext(os.path.basename(src))[0])
        for src, a, b in pairs
    ]
    failures = [r for _, a, b in pairs for r in (a, b) if not r["ok"]]
    n = len(small)
    return {
        "n": n,
        "success_pct": round(100 * sum(successful) / n, 1) if n else None,
        "deterministic_pct": round(100 * sum(deterministic) / n, 1) if n else None,
        "failures": [(os.path.basename(f["src"]), f["err"][-160:]) for f in failures][:5],
    }


def successful_trial_wall(wall, results):
    return wall if all(result["ok"] for result in results) else None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("corpus"); ap.add_argument("out")
    ap.add_argument("--formats", default="docx,html")
    ap.add_argument("--ref", default=None)
    ap.add_argument("--lua", action="append", default=[])
    ap.add_argument("--sizes", default="8,32,128")
    ap.add_argument("--workers", default="1,2,3,4,6,8,12")
    ap.add_argument("--trials", type=int, default=3)
    a = ap.parse_args()
    files = sorted(os.path.join(a.corpus, f) for f in os.listdir(a.corpus) if f.endswith(".md"))
    report = {"pandoc": subprocess.run(["pandoc", "--version"], capture_output=True, text=True).stdout.splitlines()[0],
              "cpus": os.cpu_count(), "corpus_files": len(files), "poc": {}, "scale": {}}

    # Phase A: PoC on the smallest cluster, twice, check success + determinism
    small = files[: int(a.sizes.split(",")[0])]
    for fmt in a.formats.split(","):
        w1, r1, d1 = run_batch(small, fmt, 1, a.ref, a.lua)
        w2, r2, d2 = run_batch(small, fmt, 2, a.ref, a.lua)
        report["poc"][fmt] = poc_summary(small, r1, r2, d1, d2)
        print("PoC", fmt, report["poc"][fmt], flush=True)

    # Phase B: gradual scale
    for fmt in a.formats.split(","):
        report["scale"][fmt] = {}
        for S in [int(x) for x in a.sizes.split(",")]:
            batch = files[:S]
            pts = []
            prev = None
            for N in [int(x) for x in a.workers.split(",")]:
                walls = []
                for _ in range(a.trials):
                    w, res, _ = run_batch(batch, fmt, N, a.ref, a.lua)
                    successful_wall = successful_trial_wall(w, res)
                    if successful_wall is not None:
                        walls.append(successful_wall)
                if not walls:
                    continue
                wall = statistics.median(walls)
                X = round(len(batch) / wall, 2)
                gain = None if prev is None else round(100 * (X - prev) / prev, 1)
                pts.append((N, X))
                report["scale"][fmt].setdefault(str(S), []).append(
                    {"N": N, "wall_s": round(wall, 3), "docs_per_s": X, "marginal_gain_pct": gain,
                     "cv_pct": round(100 * statistics.pstdev(walls) / statistics.mean(walls), 1), "ok": len(batch)})
                print(f"{fmt} S={S} N={N} X={X} docs/s gain={gain}%", flush=True)
                prev = X
            if pts:
                report["scale"][fmt][f"{S}_usl"] = usl_fit(pts)
                print(" USL", fmt, S, report["scale"][fmt][f"{S}_usl"], flush=True)
    json.dump(report, open(a.out, "w"), indent=1)
