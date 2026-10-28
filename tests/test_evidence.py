import math

import numpy as np
import pandas as pd
import pytest

from ai_gov.evidence import (
    data_documentation_completeness,
    demographic_parity_difference,
    equal_opportunity_difference,
    explainability_coverage,
    fairness_report,
    intersectional_report,
    population_stability_index,
)
from ai_gov.evidence.checks import (
    auc_interval,
    bootstrap_gaps,
    disparate_impact_ratio,
    drift_check,
    wilson_interval,
)

Y_TRUE = [1, 1, 1, 0, 1, 1, 0, 0]
Y_PRED = [1, 1, 0, 0, 1, 0, 0, 0]
GROUP = ["a"] * 4 + ["b"] * 4


def test_demographic_parity_hand_computed():
    # selection rate a = 2/4, b = 1/4
    assert demographic_parity_difference(Y_PRED, GROUP) == pytest.approx(0.25)


def test_equal_opportunity_hand_computed():
    # TPR a = 2/3, b = 1/2
    assert equal_opportunity_difference(Y_TRUE, Y_PRED, GROUP) == pytest.approx(1 / 6)


def test_disparate_impact_hand_computed():
    assert disparate_impact_ratio(Y_PRED, GROUP) == pytest.approx(0.5)


def test_perfect_parity_is_zero():
    p = [1, 0, 1, 0]
    assert demographic_parity_difference(p, ["a", "a", "b", "b"]) == 0
    assert equal_opportunity_difference([1, 0, 1, 0], p, ["a", "a", "b", "b"]) == 0


def test_eod_needs_positives_in_two_groups():
    with pytest.raises(ValueError):
        equal_opportunity_difference([1, 1, 0, 0], [1, 1, 0, 0], ["a", "a", "b", "b"])


def test_matches_fairlearn():
    fl = pytest.importorskip("fairlearn.metrics")
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 500)
    p = rng.integers(0, 2, 500)
    g = rng.choice(["x", "y"], 500)
    assert demographic_parity_difference(p, g) == pytest.approx(
        fl.demographic_parity_difference(y, p, sensitive_features=g)
    )
    mf = fl.MetricFrame(metrics=fl.true_positive_rate, y_true=y, y_pred=p, sensitive_features=g)
    assert equal_opportunity_difference(y, p, g) == pytest.approx(mf.difference())


def test_fairness_report_status():
    r = fairness_report(Y_TRUE, Y_PRED, GROUP, "g", tolerance=0.10, n_boot=0)
    assert r.status == "fail"  # 0.25 > 2 x tolerance
    assert fairness_report(Y_TRUE, Y_PRED, GROUP, "g", tolerance=0.20, n_boot=0).status == "warn"
    assert fairness_report(Y_TRUE, Y_PRED, GROUP, "g", tolerance=0.30, n_boot=0).status == "pass"
    assert r.metrics["demographic_parity_difference"] == 0.25


def test_psi_identical_is_zero():
    x = np.random.default_rng(0).normal(size=2000)
    assert population_stability_index(x, x) == pytest.approx(0, abs=1e-9)


def test_psi_hand_computed_two_bins():
    expected = [1] * 50 + [2] * 50
    actual = [1] * 80 + [2] * 20
    # pe = (.5,.5), pa = (.8,.2): .3*ln(.8/.5) + (-.3)*ln(.2/.5) = .3*ln 4
    assert population_stability_index(expected, actual, bins=2) == pytest.approx(0.3 * math.log(4))


def test_psi_grows_with_shift_and_flags():
    rng = np.random.default_rng(0)
    base = rng.normal(size=5000)
    small = population_stability_index(base, rng.normal(0.05, 1, 5000))
    big = population_stability_index(base, rng.normal(1.0, 1, 5000))
    assert small < 0.10 < 0.25 < big
    assert drift_check(base, rng.normal(1.0, 1, 5000)).status == "fail"


def test_psi_handles_empty_bins_and_constant_reference():
    assert math.isfinite(population_stability_index(np.arange(100), np.full(100, 500.0)))
    assert population_stability_index(np.ones(50), np.arange(50)) == 0.0


def test_explainability_coverage():
    imp = pd.Series({"a": 0.5, "b": 0.3, "c": 0.15, "d": 0.05, "e": -0.01})
    r = explainability_coverage(imp, {"a", "b", "c"}, reason_code_share=0.9)
    assert r.metrics["features_for_80pct_importance"] == 2
    assert r.metrics["documented_importance_share"] == pytest.approx(0.95)
    assert r.status == "pass"
    low = explainability_coverage(imp, {"d"})
    assert low.status == "warn"


def test_data_documentation_completeness():
    df = pd.DataFrame({"sex": [1, 2, 3, 1], "age": [20, 30, 200, 40], "y": [0, 1, 0, 1]})
    d = {
        "sex": {
            "description": "s",
            "type": "cat",
            "personal_data": True,
            "role": "f",
            "valid_values": [1, 2],
        },
        "age": {
            "description": "a",
            "type": "int",
            "personal_data": True,
            "role": "f",
            "valid_range": [0, 120],
        },
        "y": {"description": "t", "type": "bin", "personal_data": False, "role": "target"},
    }
    r = data_documentation_completeness(df, d, target="y")
    assert r.status == "warn"
    assert r.metrics["column_coverage"] == 1.0
    assert r.metrics["columns_with_values_outside_domain"] == 2
    del d["age"]
    assert data_documentation_completeness(df, d, target="y").status == "fail"


def _biased_sample(n=4000, seed=3):
    rng = np.random.default_rng(seed)
    g = rng.choice(["a", "b"], n)
    y = rng.binomial(1, 0.3, n)
    p = rng.binomial(1, np.where(g == "a", 0.30, 0.20))  # selection gap of 0.10 by construction
    return y, p, g


def test_wilson_interval_known_values():
    lo, hi = wilson_interval(50, 100)
    assert (lo, hi) == pytest.approx((0.4038, 0.5962), abs=1e-3)
    assert wilson_interval(0, 20)[0] == 0 or wilson_interval(0, 20)[0] == pytest.approx(
        0, abs=1e-12
    )
    assert math.isnan(wilson_interval(0, 0)[0])


def test_bootstrap_interval_covers_the_point_estimate_and_shrinks_with_n():
    y, p, g = _biased_sample()
    ci = bootstrap_gaps(y, p, g, n_boot=300, seed=1)
    point = demographic_parity_difference(p, g)
    assert ci["dpd"][0] < point < ci["dpd"][1]
    y2, p2, g2 = _biased_sample(n=400)
    small = bootstrap_gaps(y2, p2, g2, n_boot=300, seed=1)["dpd"]
    assert small[1] - small[0] > ci["dpd"][1] - ci["dpd"][0]


def test_fairness_warns_when_interval_crosses_tolerance():
    y, p, g = _biased_sample(n=600)
    point = max(demographic_parity_difference(p, g), equal_opportunity_difference(y, p, g))
    tol = point + 0.005
    r = fairness_report(y, p, g, "g", tolerance=tol, n_boot=300)
    assert r.metrics["ci95"]["demographic_parity_difference"][1] > tol
    assert r.status == "warn"
    assert fairness_report(y, p, g, "g", tolerance=tol, n_boot=0).status == "pass"


def test_auc_interval_brackets_the_auc():
    from sklearn.metrics import roc_auc_score

    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 1500)
    s = y * 0.8 + rng.normal(size=1500)
    lo, hi = auc_interval(y, s, n_boot=300)
    assert lo < roc_auc_score(y, s) < hi


def test_intersectional_leaves_out_small_cells():
    rng = np.random.default_rng(5)
    n = 3000
    sex = rng.choice(["m", "f"], n)
    age = rng.choice(["<30", "30+"], n, p=[0.4, 0.6]).astype(object)
    age[:30] = "rare"  # a cell far below the minimum size
    y = rng.binomial(1, 0.3, n)
    p = rng.binomial(1, 0.25, n)
    r = intersectional_report(y, p, {"SEX": sex, "AGE": age}, min_n=100, n_boot=100)
    assert r.metrics["cells_total"] == 6 and r.metrics["cells_included"] == 4
    included = {d["cell"]: d["included"] for d in r.details}
    assert not included["m|rare"] and not included["f|rare"] and included["m|<30"]
    assert sum(d["n"] for d in r.details) == n


def test_intersectional_gap_exceeds_single_attribute_gap_when_effects_combine():
    rng = np.random.default_rng(8)
    n = 20000
    sex = rng.choice(["m", "f"], n)
    age = rng.choice(["young", "old"], n)
    rate = np.where((sex == "f") & (age == "old"), 0.40, 0.20)
    p = rng.binomial(1, rate)
    y = rng.binomial(1, 0.3, n)
    single = demographic_parity_difference(p, sex)
    r = intersectional_report(y, p, {"SEX": sex, "AGE": age}, min_n=100, n_boot=100)
    assert r.metrics["demographic_parity_difference"] > 2 * single
    assert r.metrics["highest_selection_cell"] == "f|old"
    assert r.status in {"warn", "fail"}
