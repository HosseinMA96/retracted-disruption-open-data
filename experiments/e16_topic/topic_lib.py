"""Identifier-aware focal metadata and fixed major-MeSH topic matches."""
import hashlib
import numpy as np
import pandas as pd

EXCLUDED = {"D016454", "D000078182", "D017418", "D016421", "D016422", "D016420",
            "D016425", "D016440", "D000075742"}
NOTICE_TYPES = {"D016425", "D016440", "D000075742"}
NOTICE_LINKS = {"RetractionOf", "ErratumFor", "ExpressionOfConcernFor"}


def values(row, key):
    if row[key] is None:
        return []
    return row[key].tolist() if isinstance(row[key], np.ndarray) else list(row[key])


def notice(row):
    return bool(set(values(row, "pub_type_ui")) & NOTICE_TYPES
                or set(values(row, "cc_reftype")) & NOTICE_LINKS)


def article(types):
    return bool(types) and "D016428" in types and not (types & EXCLUDED)


def metadata(rows):
    pmids = {int(r["pmid"]) for r in rows if r["is_pmid"]}
    chosen = [r for r in rows if r["is_pmid"]] if pmids else [r for r in rows if not notice(r)]
    original = {t for r in rows for t in values(r, "pub_type_ui")}
    types = {t for r in chosen for t in values(r, "pub_type_ui")}
    major = set()
    for r in chosen:
        ui, flags = values(r, "mesh_ui"), values(r, "mesh_major")
        if len(ui) != len(flags):
            raise ValueError("MeSH UI/major-flag lengths differ")
        major.update(t for t, flag in zip(ui, flags) if flag and t is not None)
    foreign = [r for r in rows if not r["is_pmid"] and int(r["pmid"]) not in pmids and notice(r)]
    targeted = []
    for r in foreign:
        links, targets = values(r, "cc_reftype"), values(r, "cc_pmid")
        if len(links) != len(targets):
            raise ValueError("Correction-type/target lengths differ")
        targeted.extend(p for link, p in zip(links, targets) if link in NOTICE_LINKS and p in pmids)
    return {"legacy_article": article(original), "article": article(types),
            "known_types": bool(types), "major_mesh": tuple(sorted(major)),
            "pmid_source": bool(pmids), "foreign_notice": bool(foreign),
            "notice_targets_native_pmid": bool(targeted),
            "doi_only_excluded_type": any(set(values(r, "pub_type_ui")) & EXCLUDED
                                          for r in rows if not r["is_pmid"]
                                          and int(r["pmid"]) not in pmids)}


def select_controls(retracted_iid, mesh, controls, k=5):
    selected = []
    for row in controls:
        other = set(row["major_mesh"])
        shared = len(mesh & other)
        if not shared:
            continue
        similarity = shared / len(mesh | other)
        tie = hashlib.sha256(f"20261109|{int(retracted_iid)}|{int(row['iid'])}".encode("ascii")).hexdigest()
        selected.append((-similarity, tie, row))
    return [(-score, row) for score, _, row in sorted(selected, key=lambda x: x[:2])[:k]]


def topic_pairs(ret, ctl):
    r = ret[ret.dinok.notna() & ret.major_mesh.map(bool)]
    c = ctl[ctl.dinok.notna() & ctl.major_mesh.map(bool)]
    groups = {key: g.to_dict("records") for key, g in c.groupby(["journal_id", "pub_year"])}
    rows, selected_ids, similarities, counts = [], set(), [], []
    for row in r.to_dict("records"):
        candidates = groups.get((row["journal_id"], row["pub_year"]), [])
        matches = select_controls(row["iid"], set(row["major_mesh"]), candidates)
        if not matches:
            continue
        baseline = np.mean([x["dinok"] for x in candidates])
        matched = np.mean([x["dinok"] for _, x in matches])
        rows.append({"journal_id": row["journal_id"], "pub_year": row["pub_year"],
                     "baseline_gap": row["dinok"] - baseline, "topic_gap": row["dinok"] - matched})
        counts.append(len(matches))
        similarities.extend(s for s, _ in matches)
        selected_ids.update(int(x["iid"]) for _, x in matches)
    if not rows:
        raise ValueError("No major-MeSH topic matches")
    output = {"primary_total": len(ret), "primary_defined": int(ret.dinok.notna().sum()),
              "primary_defined_with_major_mesh": len(r), "controls_defined_with_major_mesh": len(c),
              "retracted_compared": len(rows), "unmatched_major_mesh_primary": len(r) - len(rows),
              "unique_matched_controls": len(selected_ids), "matched_control_uses": sum(counts),
              "controls_per_paper": {str(n): counts.count(n) for n in sorted(set(counts))},
              "similarity_quantiles": np.quantile(similarities, [0, .25, .5, .75, 1]).tolist()}
    return pd.DataFrame(rows), output


def paired_journal_mean(pairs, rng, nboot=2000):
    grouped = pairs.groupby("journal_id", sort=True).agg(
        baseline=("baseline_gap", "sum"), topic=("topic_gap", "sum"), n=("topic_gap", "size"))
    if len(grouped) < 2:
        raise ValueError("At least two journals are needed for bootstrap uncertainty")
    draws = rng.integers(0, len(grouped), size=(nboot, len(grouped)))
    weights = grouped.n.to_numpy()
    out = {"journals": len(grouped), "bootstrap_unit": "journal", "n_boot": nboot}
    for key in ("baseline", "topic"):
        totals = grouped[key].to_numpy()
        boot = totals[draws].sum(1) / weights[draws].sum(1)
        out[key] = {"diff": float(totals.sum() / weights.sum()),
                    "ci": np.quantile(boot, [0.025, .975]).tolist()}
    return out
