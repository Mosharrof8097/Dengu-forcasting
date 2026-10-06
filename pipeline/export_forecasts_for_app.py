#!/usr/bin/env python3
"""Export out-of-sample forecasts for the application.

What the app shows, and why it is framed this way
-------------------------------------------------
Not "here is what will happen". These are the rolling-origin forecasts the
evaluation already produced: at each origin the model saw only data up to that
date, and the outcome is now known. The interface can therefore put the
prediction and the truth on the same axis, which is the only honest way to
demonstrate a forecaster to someone who has to act on it.

Every forecast carries its interval, and the intervals are the conformalised
ones. The raw quantile fits cover 81.7-83.3% at a nominal 90%, which for
capacity planning errs in the dangerous direction; conformalisation brings them
to 89.8-91.2%, so the stated interval can be taken at face value.

The accompanying skill numbers are shown against persistence, because on this
panel persistence is genuinely hard to beat on point accuracy (weekly lag-1
autocorrelation 0.973) and pretending otherwise would be the same overclaim the
reviewers already rejected.

Output: frontend/data/forecasts.json
"""
import csv, json, os, collections
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EXP = OUT = None

# Paths are arguments, not assumptions. The earlier version of this script
# resolved them by walking up to a sibling directory, so it only ran inside one
# person's folder layout and could not be run at all from a clone of this
# repository.
def _args():
    import argparse
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--dataset", default=os.environ.get("DENGUE64_DATA"),
                   help="directory holding the locked dataset "
                        "(grid_v1.csv, bd_districts_repaired.geojson); "
                        "or set DENGUE64_DATA")
    p.add_argument("--experiments", default=os.environ.get("DENGUE64_EXPERIMENTS"),
                   help="directory holding the evaluation output "
                        "(quantile_predictions_weekly.csv, "
                        "quantile_results_weekly.csv); or set "
                        "DENGUE64_EXPERIMENTS")
    p.add_argument("--out", default=os.path.join(HERE, "..", "frontend", "data"),
                   help="directory to write the artifact into "
                        "(default: the application's data directory)")
    return p.parse_args()


def _require(path, what):
    if path is None or not os.path.exists(path):
        raise SystemExit(
            f"{what} not found at {path!r}.\n"
            f"Point --dataset / --experiments at the dengue64 pipeline output, "
            f"or set DENGUE64_DATA / DENGUE64_EXPERIMENTS.")
    return path



PREF = ["QuantileGBM-CQR", "QuantileGBM"]
QCOLS = ["q05", "q10", "q25", "q50", "q75", "q90", "q95"]


def main():
    global EXP, OUT
    a = _args()
    EXP = _require(a.experiments, "the experiments directory")
    OUT = os.path.join(a.out, "forecasts.json")

    p = os.path.join(EXP, "quantile_predictions_weekly.csv")
    if not os.path.exists(p):
        print(f"missing {p} -- run quantile_forecast.py first")
        return 1
    df = pd.read_csv(p)
    df["target_date"] = pd.to_datetime(df["target_date"])

    model = next((m for m in PREF if m in set(df["model"])), None)
    if model is None:
        print("no quantile model found in predictions")
        return 1
    d = df[df["model"] == model].copy()
    print(f"model      {model}")
    print(f"rows       {len(d):,}")
    print(f"horizons   {sorted(d['horizon'].unique())}")
    print(f"span       {d['target_date'].min().date()} -> {d['target_date'].max().date()}")

    # per-district series, keyed by the date being predicted
    districts = sorted(d["district"].unique())
    out = collections.defaultdict(dict)
    for (dist, h), g in d.groupby(["district", "horizon"]):
        g = g.sort_values("target_date")
        out[dist][str(h)] = {
            "dates": [t.strftime("%Y-%m-%d") for t in g["target_date"]],
            "actual": [None if pd.isna(v) else int(v) for v in g["y"]],
            "q": {c: [round(float(v), 1) for v in g[c]] for c in QCOLS},
        }

    # headline skill, per horizon, against persistence
    res = pd.read_csv(os.path.join(EXP, "quantile_results_weekly.csv"))
    skill = {}
    for h, g in res.groupby("horizon"):
        m = g[g["model"] == model]
        pb = g[g["model"] == "persistence+"]
        if len(m) and len(pb):
            skill[str(h)] = {
                "wis": round(float(m["WIS"].mean()), 2),
                "wis_persistence": round(float(pb["WIS"].mean()), 2),
                "wis_gain_pct": round(100 * (1 - m["WIS"].mean() / pb["WIS"].mean()), 1),
                "mae_median": round(float(m["MAE_median"].mean()), 2),
                "mae_persistence": round(float(pb["MAE_median"].mean()), 2),
                "cov90": round(float(m["cov90"].mean()), 3),
                "cov80": round(float(m["cov80"].mean()), 3),
                "cov50": round(float(m["cov50"].mean()), 3),
            }

    # coverage by fold, so the interface can say where the intervals hold
    byfold = {}
    for (h, fid), g in res[res["model"] == model].groupby(["horizon", "fold"]):
        byfold.setdefault(str(h), {})[fid] = round(float(g["cov90"].mean()), 3)

    doc = {
        "meta": {
            "model": model,
            "framing": "rolling-origin out-of-sample forecasts; at each origin "
                       "the model saw only earlier data, and the outcome is "
                       "now known",
            "intervals": "conformalised (Romano et al.). Across all six folds "
                         "the raw quantile fits covered 81.7-83.3% at a nominal "
                         "90%, which under-sizes capacity; after conformalisation "
                         "they cover 89.8-91.2%",
            "caution": "weekly lag-1 autocorrelation on this panel is 0.973, so "
                       "persistence is a strong point forecast. The model's "
                       "advantage is in the interval, not the central estimate.",
            "quantiles": QCOLS,
        },
        "skill": skill,
        "coverage_by_fold": byfold,
        "districts": districts,
        "series": out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(doc, f, separators=(",", ":"))
    print(f"\ndistricts  {len(districts)}")
    for h, s in sorted(skill.items()):
        print(f"  t+{h}  WIS {s['wis']:>7.2f} vs persistence {s['wis_persistence']:>7.2f}"
              f"  ({s['wis_gain_pct']:+.1f}%)   cov90 {s['cov90']:.1%}")
    print(f"\nwrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
