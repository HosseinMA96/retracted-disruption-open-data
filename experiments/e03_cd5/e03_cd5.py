"""E3: compute and FREEZE CD5 (SPEC.md §5) for the focal iids of an E2 run. Reads the label-free focal list only.
Output (VM only): E_DATA/e03/RUN_ID/scores.parquet; its SHA-256 goes into run.json (frozen before E4 joins labels).
usage: python e03_cd5.py RUN_ID E2_RUN_ID [N_BATCHES] [WINDOW]   window default 5 (SPEC v1)
"""
import sys, duckdb, pandas as pd
from common import Run, C_WORK, E_DATA, E_ROOT, sha256
import cd_lib

E2, NB = sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 16
cd_lib.HI = int(sys.argv[4]) if len(sys.argv) > 4 else 5   # read by cd_lib at call time
focal_file = E_DATA / "e02" / E2 / "focal_iids.parquet"
run = Run(sys.argv[1], __file__, {"e2_run": E2, "n_batches": NB, "focal_sha256": sha256(focal_file),
                                   "cd_lib_sha256": sha256(cd_lib.__file__), "spec_sha256": sha256(E_ROOT / "SPEC.md"),
                                   "windows": {"w0": [0, cd_lib.HI], "w1": [1, cd_lib.HI]}})
out = E_DATA / "e03" / sys.argv[1]; out.mkdir(parents=True, exist_ok=False)
con = duckdb.connect(str(out / "work.duckdb"))
con.execute(f"SET threads=8; SET memory_limit='48GB'; SET temp_directory='{E_DATA / 'tmp'}'; SET preserve_insertion_order=false")
q = lambda s: con.execute(s).fetchall()[0][0]

con.execute(f"CREATE TABLE focal AS SELECT iid, pub_year FROM read_parquet('{focal_file}')")
run.log("focal", q("SELECT count(*) FROM focal"))
cd_lib.build_inputs(con, "focal", f"read_parquet('{C_WORK / 'edges.parquet'}')", f"read_parquet('{C_WORK / 'pubs_slim.parquet'}')")
run.log("focal_reference_pairs", q("SELECT count(*) FROM fr"))
run.log("target_nodes", q("SELECT count(*) FROM tgt"))
run.log("incoming_citations_kept", q("SELECT count(*) FROM inc"))

parts = []
for b in range(NB):
    con.execute(f"CREATE OR REPLACE TABLE fb AS SELECT * FROM focal WHERE iid % {NB} = {b}")
    parts.append(cd_lib.score_batch(con, "fb"))
    print(f"batch {b + 1}/{NB}: {len(parts[-1])} papers", flush=True)
df = pd.concat(parts).sort_values("iid").reset_index(drop=True)
assert len(df) == run.info["results"]["focal"] and df.iid.is_unique
df.to_parquet(out / "scores.parquet", index=False)
con.close(); (out / "work.duckdb").unlink()

# aggregate, label-free summaries only
run.log("cd_w0_defined", int(df.cd_w0.notna().sum()))
run.log("cd_w1_defined", int(df.cd_w1.notna().sum()))
run.log("cd1_w0_share_of_defined", round(float(df.cd1_w0.sum() / df.cd_w0.notna().sum()), 6))
run.log("cd_w0_quantiles", [round(float(x), 6) for x in df.cd_w0.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])])
run.log("frozen", {"scores.parquet": {"sha256": sha256(out / "scores.parquet"), "rows": len(df)}})
run.finish()
