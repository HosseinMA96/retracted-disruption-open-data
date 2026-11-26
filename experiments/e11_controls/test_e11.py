"""Test of e11_controls.py on synthetic data (seconds; laptop or VM; reads no project data).
Builds two toy populations with the schemas of e02 (labels) and e03 (frozen scores), runs the real e04_eval.py on each
in a temporary copy of the experiments tree, then e11_controls.py, and checks every P11 count and share against a
direct computation with plain Python loops. Then checks that e11 is deterministic and that it stops when a value it
replays is altered (an e04 estimate, an e04 threshold, an e02 count, the frozen-score hash).
usage: python test_e11.py
"""
import hashlib, io, json, os, shutil, subprocess, sys, tempfile
import numpy as np, pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent; EXP = HERE.parent; ROOT = EXP.parent
CLASSES = ["misconduct", "paper_mill", "honest_error", "other"]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def synth(seed, str_journals):
    rng = np.random.default_rng(seed); years = list(range(2000, 2008)); rows, iid = [], 10 * seed
    for s in range(96):
        j = f"J{1000 + s // 8}" if str_journals else 1000 + s // 8
        y = years[s % 8]; n_p, n_s = int(rng.integers(0, 4)), int(rng.integers(0, 3))
        if n_p + n_s == 0: n_s = 1
        for k in range(n_p + n_s):
            iid += 1; rows.append([iid, "retracted", j, y, k < n_p, CLASSES[int(rng.integers(0, 4))],
                                   pd.Timestamp(y + (6 if k < n_p else 2), 6, 1)])
        n_c = 0 if s % 23 == 0 else 5 * (n_p + n_s) - int(rng.integers(0, 3))    # some strata without or short of controls
        for _ in range(n_c):
            iid += 1; rows.append([iid, "control", j, y, None, None, None])
    for y in years:
        for k in range(300):
            iid += 1; rows.append([iid, "context", f"J{9000 + k % 11}" if str_journals else 9000 + k % 11, y, None, None, None])
    L = pd.DataFrame(rows, columns=["iid", "grp", "journal_id", "pub_year", "primary_set", "cls", "first_notice"])
    L["review"] = rng.random(len(L)) < 0.1
    n = len(L); S = pd.DataFrame({"iid": L.iid, "pub_year": L.pub_year, "n_refs": rng.integers(1, 80, n)})
    undefined = rng.random(n) < 0.03
    S["ni_w0"] = np.where(undefined, 0, rng.poisson(3, n)); S["nj_w0"] = np.where(undefined, 0, rng.poisson(6, n))
    S["nk_w0"] = np.where(undefined, 0, rng.integers(0, 400, n))
    S.loc[(~undefined) & (rng.random(n) < 0.03), ["nj_w0", "nk_w0"]] = 0            # a few CD = 1
    for c in ("ni", "nj", "nk"):
        S[f"{c}_w1"] = rng.binomial(S[f"{c}_w0"], 0.8)
    for w in ("w0", "w1"):                                                          # as cd_lib.py
        den = S[f"ni_{w}"] + S[f"nj_{w}"] + S[f"nk_{w}"]
        S[f"cd_{w}"] = ((S[f"ni_{w}"] - S[f"nj_{w}"]) / den).where(den > 0)
        S[f"cites_{w}"] = S[f"ni_{w}"] + S[f"nj_{w}"]
        S[f"cd1_{w}"] = (S[f"nj_{w}"] == 0) & (S[f"nk_{w}"] == 0) & (S[f"ni_{w}"] > 0)
    return L, S


def brute(L, S):
    """P11 numbers by plain loops (independent of the pandas code in e11)."""
    sc = {r.iid: r for r in S.itertuples()}; lab = list(L.itertuples())
    cd = lambda r: sc[r.iid].cd_w0
    defined = lambda r: not np.isnan(cd(r))
    th = {}
    for p, q in (("p95", 0.95), ("p99", 0.99)):
        for y in sorted(set(L.pub_year)):
            v = [cd(r) for r in lab if r.grp == "context" and r.pub_year == y and defined(r)]
            th[(p, y)] = float(np.quantile(v, q))
    prim = [r for r in lab if r.grp == "retracted" and bool(r.primary_set)]
    ctl = [r for r in lab if r.grp == "control"]
    st = lambda r: (r.journal_id, r.pub_year)
    used = {st(r) for r in prim if defined(r)} & {st(r) for r in ctl if defined(r)}
    out = {"strata_used": len(used), "papers_in_used_strata": sum(defined(r) and st(r) in used for r in prim),
           "controls_used": sum(st(r) in used for r in ctl), "controls_defined_used": sum(defined(r) and st(r) in used for r in ctl),
           "controls_other": sum(st(r) not in used for r in ctl), "controls_defined_other": sum(defined(r) and st(r) not in used for r in ctl)}
    und = {}
    for r in lab:
        if not defined(r):
            g = ("retracted_primary" if bool(r.primary_set) else "retracted_secondary") if r.grp == "retracted" else r.grp
            und[g] = und.get(g, 0) + 1
    out["undefined"] = und
    ys = {"pos": lambda r: cd(r) > 0, "p95": lambda r: cd(r) >= th[("p95", r.pub_year)], "p99": lambda r: cd(r) >= th[("p99", r.pub_year)]}
    for o, f in ys.items():
        ru = [r for r in prim if defined(r) and st(r) in used]; cu = [r for r in ctl if defined(r) and st(r) in used]
        num = den = 0.0
        for s in sorted(used):
            cs = [f(r) for r in cu if st(r) == s]; ws = sum(st(r) == s for r in ru)
            num += ws * sum(cs) / len(cs); den += ws
        out[o] = {"ret_k": sum(map(f, ru)), "ret_n": len(ru), "ctl_k": sum(map(f, cu)), "ctl_n": len(cu), "weighted": num / den,
                  "other_k": sum(f(r) for r in ctl if defined(r) and st(r) not in used)}
    return out


def main():
    tmp = Path(tempfile.mkdtemp(prefix="e11test_")); data = tmp / "data"; ex = tmp / "experiments"
    env = {**os.environ, "E_DATA": str(data)}
    try:
        for f in ("SPEC.md", "POSTHOC.md"): shutil.copy(ROOT / f, tmp / f)
        for d, files in (("e04_eval", ["e04_eval.py", "common.py"]), ("e11_controls", ["e11_controls.py", "common.py"])):
            (ex / d).mkdir(parents=True)
            for f in files: shutil.copy(EXP / d / f, ex / d / f)
        pops, args = {}, []
        for tag, seed, strj in (("a", 1, True), ("b", 2, False)):
            L, S = synth(seed, strj); E2, E3, E4 = f"e02_t{tag}", f"e03_t{tag}", f"e04_t{tag}"
            (data / "e02" / E2).mkdir(parents=True); (data / "e03" / E3).mkdir(parents=True)
            L.to_parquet(data / "e02" / E2 / "labels.parquet", index=False); S.to_parquet(data / "e03" / E3 / "scores.parquet", index=False)
            for d, rid, js in (("e02_population", E2, {"results": {"strata": int(L[L.grp == "retracted"][["journal_id", "pub_year"]].drop_duplicates().shape[0]),
                                                                    "controls": int((L.grp == "control").sum())}}),
                               ("e03_cd5", E3, {"config": {"e2_run": E2}, "results": {"frozen": {"scores.parquet": {"sha256": sha(data / "e03" / E3 / "scores.parquet")}}}})):
                (ex / d / "runs" / rid).mkdir(parents=True); (ex / d / "runs" / rid / "run.json").write_text(json.dumps(js))
            r = subprocess.run([sys.executable, "e04_eval.py", E4, E2, E3], cwd=ex / "e04_eval", env=env, capture_output=True, text=True)
            assert r.returncode == 0, r.stdout + r.stderr
            pops[tag] = (L, S); args += [E2, E3, E4]

        def e11(rid):
            return subprocess.run([sys.executable, "e11_controls.py", rid, *args], cwd=ex / "e11_controls", env=env, capture_output=True, text=True)
        r = e11("t01"); assert r.returncode == 0, r.stdout + r.stderr
        print("e11 stdout (synthetic):\n  " + "\n  ".join(r.stdout.strip().splitlines()))
        res = json.loads((ex / "e11_controls" / "runs" / "t01" / "controls.json").read_text())
        close = lambda a, b: abs(a - b) < 1e-12
        for tag, win in (("a", "cd5"), ("b", "cd3")):
            b, o = brute(*pops[tag]), res[win]
            assert o["primary"]["strata_used"] == b["strata_used"] and o["primary"]["papers_in_used_strata"] == b["papers_in_used_strata"]
            assert o["controls_used_strata"] == {"controls": b["controls_used"], "controls_defined": b["controls_defined_used"]}
            assert o["controls_other_strata"]["controls"] == b["controls_other"]
            assert o["controls_other_strata"]["controls_defined"] == b["controls_defined_other"]
            assert o["controls_used_strata"]["controls"] + o["controls_other_strata"]["controls"] == o["population"]["controls"]
            assert o["undefined"]["label_rows_by_group"] == b["undefined"], (o["undefined"], b["undefined"])
            for y in ("pos", "p95", "p99"):
                s, bb = o["shares"][y], b[y]
                assert (s["retracted_used_strata"]["k"], s["retracted_used_strata"]["n"]) == (bb["ret_k"], bb["ret_n"])
                assert (s["controls_pooled_used_strata"]["k"], s["controls_pooled_used_strata"]["n"]) == (bb["ctl_k"], bb["ctl_n"])
                assert s["controls_pooled_other_strata"]["k"] == bb["other_k"]
                est, lo, hi = s["controls_weighted"]
                assert close(est, bb["weighted"]) and lo <= est <= hi and lo < hi, (y, s["controls_weighted"], bb["weighted"])
            assert o["shares"]["v1_mh_control_counts_are_all_scored_controls"] is True
            print(f"population {tag} ({win}): {b['strata_used']} used strata, {b['controls_used']} controls in them, "
                  f"{o['controls_other_strata']['controls']} elsewhere; weighted top-5% share {b['p95']['weighted']:.4f}; checks OK")
        r = e11("t02"); assert r.returncode == 0, r.stdout + r.stderr
        assert (ex / "e11_controls/runs/t02/controls.json").read_bytes() == (ex / "e11_controls/runs/t01/controls.json").read_bytes()
        print("deterministic: two runs give byte-identical controls.json")

        def mutate(path, fn, expect, n):
            orig = path.read_bytes(); path.write_bytes(fn(orig))
            try:
                r = e11(f"m{n:02d}"); assert r.returncode != 0 and expect in (r.stdout + r.stderr), (expect, r.stdout[-500:], r.stderr[-800:])
            finally:
                path.write_bytes(orig)
            print(f"mutation {n}: stops ({expect})")
        e4 = ex / "e04_eval" / "runs" / "e04_ta"
        def bump(key, sub=None, dv=1):
            def f(b):
                j = json.loads(b); t = j["primary"] if sub is None else j["primary"][sub]
                t[key] = t[key] + dv if not isinstance(t[key], list) else [t[key][0] + dv] + t[key][1:]
                return json.dumps(j).encode()
            return f
        mutate(e4 / "results.json", bump("strata_used"), "not reproduced", 1)
        mutate(e4 / "results.json", bump("control_n", "mh_cd_pos"), "not reproduced", 2)
        mutate(e4 / "results.json", bump("share_top_p95_controls", dv=1e-9), "not reproduced", 3)
        mutate(e4 / "results.json", bump("mean_cd_controls_matched", dv=1e-9), "not reproduced", 4)
        def th(b):
            t = pd.read_csv(io.BytesIO(b), index_col="pub_year")
            t.iloc[0, 0] += 1e-9; return t.to_csv().encode()
        mutate(e4 / "thresholds.csv", th, "thresholds differ", 5)
        mutate(ex / "e02_population/runs/e02_ta/run.json",
               lambda b: json.dumps({"results": {**json.loads(b)["results"], "controls": json.loads(b)["results"]["controls"] + 1}}).encode(),
               "e02 controls", 6)
        mutate(ex / "e03_cd5/runs/e03_ta/run.json", lambda b: b.replace(b'"sha256": "', b'"sha256": "0'), "changed after freezing", 7)
        print("test_e11: all checks passed")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
