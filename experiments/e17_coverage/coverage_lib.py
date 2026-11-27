"""P17 citer reference coverage, coverage-restricted counts and whole-journal Mantel--Haenszel intervals."""
import numpy as np
import pandas as pd

ST = ["journal_id", "pub_year"]
CUTOFFS = (10, 25)


def coverage_events(con, edges, cutoffs=CUTOFFS):
    """Per-focal counts from P15's fr/citing tables; R(c) is the citer's out-degree without self-loops."""
    con.execute(f"""CREATE TABLE citer_refs AS SELECT DISTINCT e.citing_iid AS c, e.cited_iid AS r
        FROM {edges} e SEMI JOIN (SELECT DISTINCT c FROM citing) a ON e.citing_iid=a.c
        WHERE e.citing_iid<>e.cited_iid""")
    con.execute("CREATE TABLE citer_degree AS SELECT c, count(*) AS refs FROM citer_refs GROUP BY c")
    # Materialize pair-reference rows first so both focal and reference keys are joined together.
    con.execute("""CREATE TABLE pair_refs AS SELECT a.f, a.c, e.r
        FROM (SELECT DISTINCT f, c FROM citing) a JOIN citer_refs e ON a.c=e.c""")
    con.execute("""CREATE TABLE co_citing AS SELECT DISTINCT p.f, p.c
        FROM pair_refs p SEMI JOIN fr ON fr.f=p.f AND fr.r=p.r""")
    con.execute("""CREATE TABLE events AS SELECT a.f, a.c, a.y, g.refs, b.c IS NOT NULL AS also_ref
        FROM citing a JOIN citer_degree g ON a.c=g.c LEFT JOIN co_citing b ON a.f=b.f AND a.c=b.c""")
    citing, events, low = con.execute("""SELECT (SELECT count(*) FROM citing), (SELECT count(*) FROM events),
        (SELECT min(refs) FROM events)""").fetchone()
    if citing != events or (events and low < 1):
        raise ValueError("Every citing event needs a citer out-degree of at least one")
    columns = ["count(*) AS events", "count(*) FILTER (NOT also_ref) AS ni_all",
               "count(*) FILTER (also_ref) AS nj_all", "sum(ln(1 + refs)) AS sum_log_refs"]
    for k in cutoffs:
        columns += [f"count(*) FILTER (NOT also_ref AND refs >= {k}) AS ni_{k}",
                    f"count(*) FILTER (also_ref AND refs >= {k}) AS nj_{k}",
                    f"count(*) FILTER (refs < {k}) AS below_{k}"]
    return con.execute(f"SELECT f AS iid, {', '.join(columns)} FROM events GROUP BY f ORDER BY f").df()


def attach(frame, counts, cutoffs=CUTOFFS):
    d = frame.merge(counts, on="iid", how="left", validate="one_to_one")
    columns = [c for c in counts.columns if c != "iid"]
    d[columns] = d[columns].fillna(0)
    integer = [c for c in columns if c != "sum_log_refs"]
    d[integer] = d[integer].astype("int64")
    cited = d.events > 0
    d["mean_log_refs"] = (d.sum_log_refs / d.events.where(cited)).where(cited)
    for k in cutoffs:
        d[f"share_below_{k}"] = (d[f"below_{k}"] / d.events.where(cited)).where(cited)
    return d


def restricted_dinok(frame, k):
    total = frame[f"ni_{k}"] + frame[f"nj_{k}"]
    return ((frame[f"ni_{k}"] - frame[f"nj_{k}"]) / total.where(total > 0)).where(total > 0)


def pooled_coverage(con, groups, cutoffs=CUTOFFS):
    """Descriptive citing-event quartiles of R by group; groups holds compared iid and grp."""
    con.register("compared_groups", groups)
    shares = ", ".join(f"avg(CASE WHEN e.refs < {k} THEN 1.0 ELSE 0.0 END) AS below_{k}" for k in cutoffs)
    rows = con.execute(f"""SELECT g.grp, count(*) AS events, quantile_cont(e.refs, 0.25) AS q1,
        quantile_cont(e.refs, 0.5) AS median, quantile_cont(e.refs, 0.75) AS q3, {shares}
        FROM events e JOIN compared_groups g ON e.f=g.iid GROUP BY g.grp ORDER BY g.grp""").df()
    con.unregister("compared_groups")
    return {r.pop("grp"): {k: int(v) if k == "events" else float(v) for k, v in r.items()}
            for r in rows.to_dict("records")}


def stratum_tables(frame, outcome):
    g = pd.DataFrame({"journal_id": frame.journal_id.to_numpy(), "pub_year": frame.pub_year.to_numpy(),
                      "e": frame.grp.eq("retracted").astype(int).to_numpy(),
                      "y": frame[outcome].astype(bool).astype(int).to_numpy()})
    g["a"], g["b"] = g.e * g.y, g.e * (1 - g.y)
    g["c"], g["d"] = (1 - g.e) * g.y, (1 - g.e) * (1 - g.y)
    t = g.groupby(ST)[["a", "b", "c", "d"]].sum()
    return t[(t.a + t.b > 0) & (t.c + t.d > 0)]


def journal_mh(frame, outcome, rng, nboot=2000):
    """Mantel--Haenszel odds ratio with a percentile interval from resampling whole journals."""
    t = stratum_tables(frame, outcome)
    if t.empty:
        raise ValueError("No compared strata")
    n = t[["a", "b", "c", "d"]].sum(axis=1)
    parts = pd.DataFrame({"r": t.a * t.d / n, "s": t.b * t.c / n})
    journals = parts.groupby(level="journal_id").sum().sort_index()
    r, s = journals.r.to_numpy(), journals.s.to_numpy()
    if s.sum() == 0:
        raise ValueError("Odds ratio not estimable: no denominator events")
    draws = rng.integers(0, len(journals), size=(nboot, len(journals)))
    denominator = s[draws].sum(1)
    if (denominator == 0).any():
        raise ValueError("A journal bootstrap draw has no denominator events")
    boot = r[draws].sum(1) / denominator
    return {"or": float(r.sum() / s.sum()), "ci": np.quantile(boot, [0.025, 0.975]).tolist(),
            "retracted": int((t.a + t.b).sum()), "controls": int((t.c + t.d).sum()),
            "retracted_events": int(t.a.sum()), "control_events": int(t.c.sum()),
            "strata": len(t), "journals": len(journals), "bootstrap_unit": "journal"}
