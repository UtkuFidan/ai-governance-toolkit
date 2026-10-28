"""Evidence run on the UCI "Default of Credit Card Clients" data (UCI 350, CC BY 4.0, Yeh 2009).

The data is downloaded on demand into data/raw/ (gitignored) and never committed.
"""

from __future__ import annotations

import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from .checks import (
    EvidenceResult,
    auc_interval,
    data_documentation_completeness,
    drift_check,
    explainability_coverage,
    fairness_report,
    intersectional_report,
    permutation_importance_scores,
)

URL = "https://archive.ics.uci.edu/static/public/350/default+of+credit+card+clients.zip"
XLS = "default of credit card clients.xls"
DICTIONARY = Path(__file__).parent.parent / "data" / "taiwan_credit_dictionary.yaml"
SEED = 42


def fetch(raw_dir: Path) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    xls = raw_dir / XLS
    if not xls.exists():
        zp = raw_dir / "taiwan_credit.zip"
        urllib.request.urlretrieve(URL, zp)  # noqa: S310 (fixed https URL)
        with zipfile.ZipFile(zp) as z:
            z.extract(XLS, raw_dir)
    return xls


def load(xls: Path) -> pd.DataFrame:
    df = pd.read_excel(xls, header=1, engine="xlrd")
    return df.rename(columns={"default payment next month": "DEFAULT"})


def reason_code_share(model, X_flagged: pd.DataFrame, baseline: pd.Series, top_n: int = 3) -> float:
    """Share of flagged cases where the top-n drivers (single-feature occlusion to baseline)
    account for at least half of the case's positive attribution."""
    p0 = model.predict_proba(X_flagged)[:, 1]
    deltas = np.zeros((len(X_flagged), X_flagged.shape[1]))
    for j, c in enumerate(X_flagged.columns):
        Xo = X_flagged.copy()
        Xo[c] = baseline[c]
        deltas[:, j] = p0 - model.predict_proba(Xo)[:, 1]
    pos = np.clip(deltas, 0, None)
    tot = pos.sum(axis=1)
    top = np.sort(pos, axis=1)[:, -top_n:].sum(axis=1)
    ok = tot > 0
    return float(np.mean(top[ok] >= 0.5 * tot[ok])) if ok.any() else 0.0


def run(raw_dir: Path) -> dict:
    df = load(fetch(raw_dir))
    dictionary = yaml.safe_load(DICTIONARY.read_text())
    features = [
        c for c in df.columns if c not in ("ID", "DEFAULT", "SEX")
    ]  # SEX held out of the model

    trn, tmp = train_test_split(df, test_size=0.4, stratify=df.DEFAULT, random_state=SEED)
    val, tst = train_test_split(tmp, test_size=0.5, stratify=tmp.DEFAULT, random_state=SEED)
    model = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, random_state=SEED)
    model.fit(trn[features], trn.DEFAULT)

    def score(d):
        return model.predict_proba(d[features])[:, 1]

    s_trn, s_val, s_tst = score(trn), score(val), score(tst)
    ts = np.linspace(0.1, 0.7, 61)
    thr = float(ts[int(np.argmax([f1_score(val.DEFAULT, s_val >= t) for t in ts]))])
    pred = (s_tst >= thr).astype(int)
    perf = {
        "rows": int(len(df)),
        "default_rate": round(float(df.DEFAULT.mean()), 4),
        "train_rows": len(trn),
        "validation_rows": len(val),
        "test_rows": len(tst),
        "test_auc": round(float(roc_auc_score(tst.DEFAULT, s_tst)), 4),
        "test_auc_ci95": [
            round(x, 4) for x in auc_interval(tst.DEFAULT.to_numpy(), s_tst, seed=SEED)
        ],
        "threshold_from_validation_f1": round(thr, 2),
        "flag_rate_test": round(float(pred.mean()), 4),
        "model": "HistGradientBoostingClassifier (scikit-learn), SEX excluded from features",
    }

    results: list[EvidenceResult] = []
    # Drift: baseline (random split, expected ~0) and a labelled stress test (older customers)
    results.append(
        drift_check(
            s_trn, s_tst, trn[features], tst[features], "test vs train (random split baseline)"
        )
    )
    older = tst[tst.AGE >= 40]
    results.append(
        drift_check(
            s_trn,
            score(older),
            trn[features],
            older[features],
            "simulated shift: customers aged 40+ vs train",
        )
    )
    # Fairness on SEX (held out) and on an age proxy
    results.append(
        fairness_report(
            tst.DEFAULT,
            pred,
            tst.SEX.map({1: "male", 2: "female"}),
            "SEX",
            positive_means="predicted default (adverse)",
            seed=SEED,
        )
    )
    age_grp = np.where(tst.AGE >= 40, "40+", "under 40")
    results.append(
        fairness_report(
            tst.DEFAULT,
            pred,
            age_grp,
            "AGE group (proxy)",
            positive_means="predicted default (adverse)",
            seed=SEED,
        )
    )
    # Intersectional view: sex x age band, cells below 100 people are listed but not compared
    band = pd.cut(tst.AGE, [0, 29, 39, 49, 120], labels=["<30", "30-39", "40-49", "50+"]).astype(
        str
    )
    results.append(
        intersectional_report(
            tst.DEFAULT.to_numpy(),
            pred,
            {"SEX": tst.SEX.map({1: "male", 2: "female"}).to_numpy(), "AGE": band.to_numpy()},
            seed=SEED,
        )
    )
    # Explainability
    sub = val.sample(min(4000, len(val)), random_state=SEED)
    imp = permutation_importance_scores(
        lambda X: model.predict_proba(X)[:, 1],
        sub[features],
        sub.DEFAULT,
        lambda y, p: roc_auc_score(y, p),
        repeats=3,
        seed=SEED,
    )
    flagged = tst[pred == 1][features].head(1000)
    rcs = reason_code_share(model, flagged, trn[features].median())
    documented = {c for c in features if c in dictionary and dictionary[c].get("description")}
    results.append(explainability_coverage(imp, documented, reason_code_share=rcs))
    # Data documentation
    results.append(data_documentation_completeness(df, dictionary, target="DEFAULT"))

    return {
        "dataset": "UCI Default of Credit Card Clients (UCI 350), CC BY 4.0, Yeh (2009), DOI 10.24432/C55S3H",
        "seed": SEED,
        "performance": perf,
        "checks": [r.to_dict() for r in results],
    }
