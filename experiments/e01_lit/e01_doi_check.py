"""E1: resolve every candidate reference through Crossref (journals) or DataCite (arXiv).
Usage: python3 e01_doi_check.py RUN_DIR
Writes RUN_DIR/run.json, RUN_DIR/dois.json, RUN_DIR/queries.json. Network only; no large files."""
import json, sys, time, hashlib, platform, urllib.request, urllib.parse, datetime
UA = "research-lit-check/1.0 (python urllib)"
DOIS = [
 "10.1038/s41586-022-05543-x", "10.1287/mnsc.2015.2366", "10.1038/s41586-019-0941-9",
 "10.1038/s41586-026-10787-y", "10.1038/s41586-026-10788-x", "10.1038/s41586-023-06767-1",
 "10.1162/qss_a_00333", "10.1016/j.joi.2024.101605", "10.1162/qss_a_00328",
 "10.1007/s11192-023-04751-0", "10.1142/s0219525923500066", "10.1016/j.joi.2022.101294",
 "10.3138/jsp-2023-0056", "10.1177/01655515241263545", "10.1371/journal.pone.0294946",
 "10.1038/s43588-025-00808-7", "10.2139/ssrn.4923505",
 "10.48550/arXiv.2402.14583", "10.48550/arXiv.2503.00184", "10.48550/arXiv.2602.05140",
 "10.48550/arXiv.2406.18792", "10.48550/arXiv.2504.09589", "10.48550/arXiv.2504.04677",
 "10.48550/arXiv.2308.02383", "10.48550/arXiv.2504.07828", "10.48550/arXiv.2406.15311",
]
QUERIES = [
 "disruption index Web of Science Dimensions OpenCitations comparison Journal of Informetrics 2025",
 "What do we know about the disruption index in scientometrics? An overview of the literature",
 "The Disruption Index measures displacement between a paper and its most cited reference",
]
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)
def resolve(doi):
    if doi.lower().startswith("10.48550/"):
        d = get("https://api.datacite.org/dois/" + urllib.parse.quote(doi))["data"]["attributes"]
        return {"agency": "datacite", "title": d["titles"][0]["title"], "year": d.get("publicationYear"),
                "venue": d.get("publisher"), "first_author": (d.get("creators") or [{}])[0].get("name")}
    m = get("https://api.crossref.org/works/" + urllib.parse.quote(doi))["message"]
    a = (m.get("author") or [{}])[0]
    return {"agency": "crossref", "title": (m.get("title") or [""])[0], "venue": (m.get("container-title") or [""])[0],
            "year": (m.get("issued", {}).get("date-parts") or [[None]])[0][0], "type": m.get("type"),
            "first_author": f"{a.get('family','')}, {a.get('given','')}", "volume": m.get("volume"), "page": m.get("page")}
def main(run_dir):
    import os; os.makedirs(run_dir, exist_ok=False)  # never overwrite a run
    out = {}
    for d in DOIS:
        try: out[d] = {"ok": True, **resolve(d)}
        except Exception as e: out[d] = {"ok": False, "error": repr(e)}
        time.sleep(0.3)
    q = {}
    for s in QUERIES:
        try:
            items = get("https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(s))["message"]["items"]
            q[s] = [{"doi": i["DOI"], "title": (i.get("title") or [""])[0], "venue": (i.get("container-title") or [""])[0],
                     "year": (i.get("issued", {}).get("date-parts") or [[None]])[0][0]} for i in items]
        except Exception as e: q[s] = {"error": repr(e)}
    for name, obj in (("dois.json", out), ("queries.json", q)):
        open(f"{run_dir}/{name}", "w").write(json.dumps(obj, indent=1, ensure_ascii=False))
    run = {"run": os.path.basename(run_dir), "script": "e01_doi_check.py",
           "script_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
           "utc": datetime.datetime.utcnow().isoformat() + "Z", "python": platform.python_version(),
           "n_dois": len(DOIS), "n_ok": sum(v["ok"] for v in out.values()), "host": "laptop (network-only, <1 MB output)"}
    open(f"{run_dir}/run.json", "w").write(json.dumps(run, indent=1))
    print(json.dumps(run, indent=1))
if __name__ == "__main__": main(sys.argv[1])
