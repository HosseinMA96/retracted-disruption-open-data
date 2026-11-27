"""P19 article-sample flags and the P13 conditional-logit wrapper."""
import sys
from pathlib import Path

import pandas as pd

EXP = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXP / "e16_topic"))
sys.path.insert(0, str(EXP / "e13_article_types"))
from topic_lib import metadata  # noqa: E402
from sensitivity_lib import clogit  # noqa: E402


def article_flags(links, focal_iids):
    """Union-link (P13) and PMID-priority (P16) article flags; nodes without PubMed metadata are not articles."""
    rows = []
    for iid, part in links.groupby("iid", sort=False):
        meta = metadata(part.to_dict("records"))
        rows.append((int(iid), bool(meta["legacy_article"]), bool(meta["article"])))
    out = pd.DataFrame(rows, columns=["iid", "union_link", "pmid_priority"])
    missing = sorted(set(int(i) for i in focal_iids) - set(out.iid))
    if missing:
        out = pd.concat([out, pd.DataFrame({"iid": missing, "union_link": False, "pmid_priority": False})],
                        ignore_index=True)
    return out


def sample(frame, flag):
    selected = frame[frame[flag]]
    return (selected[selected.grp.eq("retracted") & selected.primary_set.eq(True)],
            selected[selected.grp.eq("control")])


def models(frame, flag, thresholds):
    ret, ctl = sample(frame, flag)
    return clogit(ret, ctl, thresholds)
