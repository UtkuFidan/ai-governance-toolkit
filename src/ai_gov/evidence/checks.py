"""Runnable audit-evidence checks. Pure numpy/pandas; each returns an EvidenceResult.

Thresholds are conventional starting points, not standards. The model owner and the
independent validator must set and approve tolerances for their own context.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass, field

import numpy as np
import pandas as pd


@dataclass
class EvidenceResult:
    check: str
    status: str  # pass | warn | fail
    metrics: dict
    thresholds: dict
    note: str = ""
    details: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- drift (PSI)
def population_stability_index(expected, actual, bins: int = 10, eps: float = 1e-4) -> float:
    """PSI = sum((a_i - e_i) * ln(a_i / e_i)) over bins cut at quantiles of `expected`.

    Bins are fixed on the reference sample; empty bins are floored at `eps` to stay finite.
    """
    e = np.asarray(expected, dtype=float)
    a = np.asarray(actual, dtype=float)
    edges = np.unique(np.quantile(e, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:  # near-constant reference: nothing to compare
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    pe = np.histogram(e, edges)[0] / len(e)
    pa = np.histogram(a, edges)[0] / len(a)
    pe, pa = np.clip(pe, eps, None), np.clip(pa, eps, None)
    return float(np.sum((pa - pe) * np.log(pa / pe)))


def psi_status(v: float) -> str:
    return "pass" if v < 0.10 else "warn" if v < 0.25 else "fail"


def drift_check(
    reference_score,
    current_score,
    reference_features: pd.DataFrame | None = None,
    current_features: pd.DataFrame | None = None,
    label: str = "current vs reference",
) -> EvidenceResult:
    score_psi = population_stability_index(reference_score, current_score)
    status = psi_status(score_psi)
    metrics: dict = {"score_psi": round(score_psi, 4)}
    details = []
    if reference_features is not None and current_features is not None:
        per = {
            c: population_stability_index(reference_features[c], current_features[c])
            for c in reference_features.columns
            if pd.api.types.is_numeric_dtype(reference_features[c])
        }
        top = sorted(per.items(), key=lambda kv: -kv[1])[:5]
        details = [{"feature": k, "psi": round(v, 4)} for k, v in top]
        metrics["max_feature_psi"] = round(top[0][1], 4)
        metrics["features_over_0.10"] = sum(v >= 0.10 for v in per.values())
        metrics["features_over_0.25"] = sum(v >= 0.25 for v in per.values())
        if any(v >= 0.25 for v in per.values()) and status == "pass":
            status = "warn"
    return EvidenceResult(
        f"drift_psi: {label}",
        status,
        metrics,
        {"warn_at": 0.10, "fail_at": 0.25},
        "PSI < 0.10 stable, 0.10 to 0.25 moderate shift, >= 0.25 significant shift (common convention).",
        details,
    )


# ---------------------------------------------------------------- fairness
def _rates(y_pred, group) -> pd.Series:
    df = pd.DataFrame({"p": np.asarray(y_pred).astype(float), "g": np.asarray(group)})
    return df.groupby("g")["p"].mean()


def selection_rates(y_pred, group) -> dict:
    return {str(k): float(v) for k, v in _rates(y_pred, group).items()}


def demographic_parity_difference(y_pred, group) -> float:
    """max over groups of P(pred=1 | g) minus the min. 0 means equal selection rates."""
    r = _rates(y_pred, group)
    return float(r.max() - r.min())


def equal_opportunity_difference(y_true, y_pred, group) -> float:
    """max minus min of the true-positive rate P(pred=1 | y=1, g) across groups."""
    df = pd.DataFrame(
        {"y": np.asarray(y_true), "p": np.asarray(y_pred).astype(float), "g": np.asarray(group)}
    )
    tpr = df[df["y"] == 1].groupby("g")["p"].mean()
    if len(tpr) < 2:
        raise ValueError("need positives in at least two groups")
    return float(tpr.max() - tpr.min())


def disparate_impact_ratio(y_pred, group) -> float:
    """min over groups of selection rate divided by the max (four-fifths screen: < 0.8)."""
    r = _rates(y_pred, group)
    return float(r.min() / r.max()) if r.max() > 0 else 1.0


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion k/n (95% by default)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return (float(centre - half), float(centre + half))


def bootstrap_gaps(
    y_true, y_pred, group, n_boot: int = 1000, seed: int = 0, min_group: int = 1
) -> dict[str, tuple[float, float]]:
    """Percentile 95% bootstrap intervals for the three group gaps, resampling individuals.

    Resamples in which a group has too few members or no positives are skipped; if too many are
    skipped the interval is NaN rather than a number built on a handful of draws.
    """
    y, p, g = np.asarray(y_true), np.asarray(y_pred).astype(float), np.asarray(group)
    rng = np.random.default_rng(seed)
    draws: dict[str, list[float]] = {"dpd": [], "eod": [], "di": []}
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        try:
            gi = g[i]
            if pd.Series(gi).value_counts().min() < min_group:
                continue
            draws["dpd"].append(demographic_parity_difference(p[i], gi))
            draws["eod"].append(equal_opportunity_difference(y[i], p[i], gi))
            draws["di"].append(disparate_impact_ratio(p[i], gi))
        except ValueError:
            continue
    out = {}
    for k, v in draws.items():
        ok = len(v) >= 0.9 * n_boot > 0
        out[k] = tuple(float(x) for x in np.percentile(v, [2.5, 97.5])) if ok else (np.nan, np.nan)
    return out


def auc_interval(y_true, score, n_boot: int = 1000, seed: int = 0) -> tuple[float, float]:
    """Percentile 95% bootstrap interval for the AUC (rank formulation, resampling individuals)."""
    from scipy.stats import rankdata

    y, s = np.asarray(y_true).astype(int), np.asarray(score, dtype=float)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n_boot):
        i = rng.integers(0, len(y), len(y))
        yi = y[i]
        n1 = int(yi.sum())
        if n1 == 0 or n1 == len(yi):
            continue
        r = rankdata(s[i])
        out.append((r[yi == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * (len(yi) - n1)))
    lo, hi = np.percentile(out, [2.5, 97.5])
    return float(lo), float(hi)


def _fairness_status(dpd: float, eod: float, tolerance: float, hi: float | None) -> str:
    worst = max(abs(dpd), abs(eod))
    status = "pass" if worst <= tolerance else "warn" if worst <= 2 * tolerance else "fail"
    # A point estimate inside the tolerance is only a pass if the interval does not reach past it.
    if status == "pass" and hi is not None and hi > tolerance:
        status = "warn"
    return status


def fairness_report(
    y_true,
    y_pred,
    group,
    attribute: str,
    tolerance: float = 0.10,
    positive_means: str = "flagged",
    n_boot: int = 1000,
    seed: int = 0,
) -> EvidenceResult:
    dpd = demographic_parity_difference(y_pred, group)
    eod = equal_opportunity_difference(y_true, y_pred, group)
    di = disparate_impact_ratio(y_pred, group)
    ci = bootstrap_gaps(y_true, y_pred, group, n_boot, seed) if n_boot else {}
    hi = None
    if ci and not any(np.isnan(v[1]) for k, v in ci.items() if k != "di"):
        hi = max(ci["dpd"][1], ci["eod"][1])
    status = _fairness_status(dpd, eod, tolerance, hi)
    df = pd.DataFrame({"y": np.asarray(y_true), "p": np.asarray(y_pred), "g": np.asarray(group)})
    sizes = {str(k): int(v) for k, v in df.groupby("g").size().items()}
    tprs = {str(k): float(v) for k, v in df[df.y == 1].groupby("g")["p"].mean().items()}
    metrics = {
        "demographic_parity_difference": round(dpd, 4),
        "equal_opportunity_difference": round(eod, 4),
        "disparate_impact_ratio": round(di, 4),
        "selection_rate": {k: round(v, 4) for k, v in selection_rates(y_pred, group).items()},
        "true_positive_rate": {k: round(v, 4) for k, v in tprs.items()},
        "group_sizes": sizes,
    }
    if ci:
        metrics["ci95"] = {
            "demographic_parity_difference": [round(x, 4) for x in ci["dpd"]],
            "equal_opportunity_difference": [round(x, 4) for x in ci["eod"]],
            "disparate_impact_ratio": [round(x, 4) for x in ci["di"]],
            "bootstrap_resamples": n_boot,
        }
    return EvidenceResult(
        f"fairness: {attribute}",
        status,
        metrics,
        {"max_abs_difference": tolerance},
        f"'Positive' means {positive_means}. Differences are gaps in rates, not proof of "
        "discrimination; base rates differ between groups and the tolerance is illustrative. "
        "A point estimate inside the tolerance is reported as warn when its 95% bootstrap "
        "interval reaches beyond it.",
    )


def intersectional_report(
    y_true,
    y_pred,
    groups: Mapping[str, Sequence],
    tolerance: float = 0.10,
    min_n: int = 100,
    n_boot: int = 1000,
    seed: int = 0,
) -> EvidenceResult:
    """Fairness across the cells formed by two or more attributes (for example sex x age band).

    Cells with fewer than ``min_n`` people are listed but left out of the gaps, because a rate on
    a handful of people says nothing. Per-cell intervals are Wilson intervals; the gaps carry a
    bootstrap interval over individuals.
    """
    names = list(groups)
    cell = pd.Series(
        ["|".join(str(groups[n][i]) for n in names) for i in range(len(y_true))], dtype=object
    )
    df = pd.DataFrame({"y": np.asarray(y_true), "p": np.asarray(y_pred).astype(int), "cell": cell})
    size = df.groupby("cell").size()
    kept = size[size >= min_n].index
    rows = []
    for c, d in df.groupby("cell"):
        pos = d[d.y == 1]
        sel_lo, sel_hi = wilson_interval(int(d.p.sum()), len(d))
        tpr_lo, tpr_hi = wilson_interval(int(pos.p.sum()), len(pos))
        rows.append(
            {
                "cell": c,
                "n": int(len(d)),
                "positives": int(len(pos)),
                "selection_rate": round(float(d.p.mean()), 4),
                "selection_ci95": [round(sel_lo, 4), round(sel_hi, 4)],
                "true_positive_rate": round(float(pos.p.mean()), 4) if len(pos) else None,
                "tpr_ci95": [round(tpr_lo, 4), round(tpr_hi, 4)],
                "included": bool(c in kept),
            }
        )
    use = df[df.cell.isin(kept)]
    dpd = demographic_parity_difference(use.p, use.cell)
    eod = equal_opportunity_difference(use.y, use.p, use.cell)
    di = disparate_impact_ratio(use.p, use.cell)
    ci = (
        bootstrap_gaps(use.y, use.p, use.cell, n_boot, seed, min_group=min_n // 2) if n_boot else {}
    )
    hi = None
    if ci and not any(np.isnan(v[1]) for k, v in ci.items() if k != "di"):
        hi = max(ci["dpd"][1], ci["eod"][1])
    rates = _rates(use.p, use.cell)
    metrics = {
        "attributes": names,
        "cells_total": len(size),
        "cells_included": len(kept),
        "min_cell_size": min_n,
        "demographic_parity_difference": round(dpd, 4),
        "equal_opportunity_difference": round(eod, 4),
        "disparate_impact_ratio": round(di, 4),
        "highest_selection_cell": str(rates.idxmax()),
        "lowest_selection_cell": str(rates.idxmin()),
    }
    if ci:
        metrics["ci95"] = {
            "demographic_parity_difference": [round(x, 4) for x in ci["dpd"]],
            "equal_opportunity_difference": [round(x, 4) for x in ci["eod"]],
            "disparate_impact_ratio": [round(x, 4) for x in ci["di"]],
            "bootstrap_resamples": n_boot,
        }
    return EvidenceResult(
        "fairness: intersectional " + " x ".join(names),
        _fairness_status(dpd, eod, tolerance, hi),
        metrics,
        {"max_abs_difference": tolerance},
        "Gaps are the maximum difference between cells, so they exceed single-attribute gaps by "
        "construction and with more cells the maximum drifts upward through noise alone. Read them "
        "together with the interval and the cell sizes.",
        rows,
    )


# ---------------------------------------------------------------- explainability
def permutation_importance_scores(
    predict_fn: Callable[[pd.DataFrame], np.ndarray],
    X: pd.DataFrame,
    y,
    metric: Callable,
    repeats: int = 3,
    seed: int = 0,
) -> pd.Series:
    """Drop in `metric` when one column is shuffled. Hand-rolled so the check has no model-type dependency."""
    rng = np.random.default_rng(seed)
    base = metric(y, predict_fn(X))
    out = {}
    for c in X.columns:
        drops = []
        for _ in range(repeats):
            Xp = X.copy()
            Xp[c] = rng.permutation(Xp[c].to_numpy())
            drops.append(base - metric(y, predict_fn(Xp)))
        out[c] = float(np.mean(drops))
    return pd.Series(out)


def explainability_coverage(
    importance: pd.Series,
    documented_features: set[str],
    mass: float = 0.80,
    reason_code_share: float | None = None,
    min_documented: float = 0.90,
    min_reason_share: float = 0.80,
) -> EvidenceResult:
    """How concentrated and how documented are the model's drivers?

    - features_for_mass: smallest number of features covering `mass` of positive importance
    - documented_importance_share: share of importance carried by features with a business description
    - reason_code_share (optional, supplied by caller): share of flagged cases whose top-3
      local drivers explain at least half of the case's positive attribution
    """
    pos = importance.clip(lower=0).sort_values(ascending=False)
    total = float(pos.sum())
    if total <= 0:
        return EvidenceResult("explainability_coverage", "fail", {}, {}, "no positive importance")
    cum = pos.cumsum() / total
    k = int((cum < mass).sum() + 1)
    doc_share = float(pos[pos.index.isin(documented_features)].sum() / total)
    metrics = {
        "features_total": int(len(importance)),
        f"features_for_{int(mass * 100)}pct_importance": k,
        "documented_importance_share": round(doc_share, 4),
        "top_features": [
            {"feature": f, "share": round(float(v / total), 4)} for f, v in pos.head(5).items()
        ],
    }
    ok = doc_share >= min_documented
    if reason_code_share is not None:
        metrics["reason_code_share"] = round(reason_code_share, 4)
        ok = ok and reason_code_share >= min_reason_share
    status = "pass" if ok else "warn"
    return EvidenceResult(
        "explainability_coverage",
        status,
        metrics,
        {
            "min_documented_importance_share": min_documented,
            "min_reason_code_share": min_reason_share,
        },
        "Importance is permutation-based (drop in AUC). Reason-code share uses single-feature "
        "occlusion to the training median; both are approximations to be confirmed with the "
        "model's own explanation method.",
    )


# ---------------------------------------------------------------- data documentation
REQUIRED_FIELDS = ("description", "type", "personal_data", "role")


def data_documentation_completeness(
    df: pd.DataFrame,
    dictionary: Mapping[str, Mapping],
    target: str | None = None,
) -> EvidenceResult:
    """Compare a dataframe with its data dictionary.

    Metrics: column coverage (columns that have an entry), field completeness (required fields
    filled), value-domain conformity (share of rows inside the documented valid values or range),
    missing-value share, duplicate rows.
    """
    cols = [c for c in df.columns]
    documented = [c for c in cols if c in dictionary]
    undocumented = [c for c in cols if c not in dictionary]
    stale = [c for c in dictionary if c not in df.columns]
    filled = total = 0
    for c in documented:
        for f in REQUIRED_FIELDS:
            total += 1
            v = dictionary[c].get(f)
            filled += v is not None and v != ""
    domain = []
    for c in documented:
        spec = dictionary[c]
        s = df[c]
        if "valid_values" in spec:
            bad = int((~s.isin(spec["valid_values"])).sum())
            values = sorted(s[~s.isin(spec["valid_values"])].unique().tolist())
        elif "valid_range" in spec:
            lo, hi = spec["valid_range"]
            bad = int(((s < lo) | (s > hi)).sum())
            values = []
        else:
            continue
        if bad:
            domain.append(
                {
                    "column": c,
                    "rows_outside_domain": bad,
                    "share": round(bad / len(df), 4),
                    "undocumented_values": values[:10],
                }
            )
    checked = [
        c for c in documented if "valid_values" in dictionary[c] or "valid_range" in dictionary[c]
    ]
    conform = 1 - (sum(d["rows_outside_domain"] for d in domain) / (len(df) * max(len(checked), 1)))
    coverage = len(documented) / len(cols)
    completeness = filled / total if total else 0.0
    metrics = {
        "columns": len(cols),
        "column_coverage": round(coverage, 4),
        "field_completeness": round(completeness, 4),
        "columns_with_domain_check": len(checked),
        "columns_with_values_outside_domain": len(domain),
        "domain_conformity": round(conform, 4),
        "missing_value_share": round(float(df.isna().mean().mean()), 6),
        "duplicate_rows": int(df.duplicated().sum()),
        "undocumented_columns": undocumented,
        "dictionary_entries_without_column": stale,
        "target_documented": bool(target and target in dictionary),
    }
    status = "pass"
    if coverage < 1 or completeness < 0.90 or (target and target not in dictionary):
        status = "fail"
    elif domain:
        status = "warn"
    return EvidenceResult(
        "data_documentation_completeness",
        status,
        metrics,
        {
            "column_coverage": 1.0,
            "field_completeness": 0.90,
            "domain_conformity": "no rows outside documented values",
        },
        "Fails when columns lack a dictionary entry or required fields are blank; warns when data holds values the dictionary does not define.",
        domain,
    )
