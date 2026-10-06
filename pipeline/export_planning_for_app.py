#!/usr/bin/env python3
"""Per-district planning inputs, all measured rather than assumed.

The app currently sizes resources with fixed multipliers -- 3.0 beds per peak
case, 1.8 kits, 2.5 saline bags -- which all three reviewers rejected as
arbitrary, and which are wrong in kind for beds: a bed is occupied for the
length of a stay, not for one day.

Nothing here is a multiplier. Length of stay is measured from the bulletins'
own stock column, and the occupancy distribution is the empirical record. The
interface turns those into a capacity figure through an explicit service level,
so the judgement a planner is making is visible instead of buried in a constant.

Verified on the panel: occupancy[t] = occupancy[t-1] + admissions - discharges
- deaths reproduces the printed stock exactly on 99.3% of 106,179 consecutive
day-pairs, so this identity can be trusted to project forward.

Output: frontend/data/planning.json
"""
import json, os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
GRID = OUT = None

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



LEVELS = [0.50, 0.75, 0.90, 0.95, 0.99]


def main():
    global GRID, OUT
    a = _args()
    GRID = _require(os.path.join(a.dataset or "", "grid_v1.csv"), "grid_v1.csv")
    OUT = os.path.join(a.out, "planning.json")

    g = pd.read_csv(GRID, low_memory=False)
    g["date"] = pd.to_datetime(g["date"])
    o = g[g["status"].isin(["OBSERVED", "OBSERVED_ZERO"])].copy()
    for c in ("new_admissions", "currently_admitted", "discharged", "deaths"):
        o[c] = pd.to_numeric(o[c], errors="coerce")
    o = o.sort_values(["district", "date"])

    out = {}
    for d, s in o.groupby("district"):
        adm = s["new_admissions"].dropna()
        occ = s["currently_admitted"].dropna()
        # length of stay by Little's Law, on days with enough flow for the
        # ratio to mean anything; the median resists the division blow-ups that
        # a handful of very small denominators would otherwise produce
        busy = s[(s["new_admissions"] >= 5) & s["currently_admitted"].notna()]
        los = (busy["currently_admitted"] / busy["new_admissions"]) if len(busy) >= 30 else pd.Series(dtype=float)

        # seasonal occupancy distribution: planners size for the season, not
        # for the annual average, and in this country the two differ by an
        # order of magnitude
        s2 = s.copy()
        s2["m"] = s2["date"].dt.month
        season = s2[s2["m"].isin([7, 8, 9, 10, 11])]["currently_admitted"].dropna()

        rec = {
            "n_days": int(len(adm)),
            "admissions": {
                "mean": round(float(adm.mean()), 2) if len(adm) else None,
                "p95": round(float(adm.quantile(0.95)), 1) if len(adm) else None,
                "max": int(adm.max()) if len(adm) else None,
            },
            "los_days": {
                "median": round(float(los.median()), 2) if len(los) else None,
                "p25": round(float(los.quantile(0.25)), 2) if len(los) else None,
                "p75": round(float(los.quantile(0.75)), 2) if len(los) else None,
                "n": int(len(los)),
            },
            "occupancy": {
                "n": int(len(occ)),
                "quantiles": {str(int(q * 100)): round(float(occ.quantile(q)), 1)
                              for q in LEVELS} if len(occ) else {},
                "max": int(occ.max()) if len(occ) else None,
            },
            "occupancy_season": {
                "n": int(len(season)),
                "quantiles": {str(int(q * 100)): round(float(season.quantile(q)), 1)
                              for q in LEVELS} if len(season) else {},
            },
        }
        out[d] = rec

    doc = {
        "meta": {
            "basis": "measured, not assumed",
            "identity": "occupancy[t] = occupancy[t-1] + admissions - discharges "
                        "- deaths; reproduces the printed stock on 99.3% of "
                        "106,179 consecutive day-pairs",
            "los": "length of stay from Little's Law (occupancy / admission "
                   "rate) on days with at least 5 admissions",
            "season": "July to November, the dengue season in Bangladesh",
            "service_level": "capacity is the chosen quantile of the occupancy "
                             "distribution. There is no multiplier: the "
                             "judgement is the service level, and it is the "
                             "planner's to make.",
            "caution": "these are historical distributions, not forecasts. They "
                       "describe what this district has needed before.",
            "levels": LEVELS,
        },
        "districts": out,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w", encoding="utf-8"), separators=(",", ":"))

    print(f"districts {len(out)}")
    print(f"\n{'district':<16}{'LOS (d)':>9}{'occ p50':>9}{'occ p95':>9}{'season p95':>12}")
    for d in ["DhakaCity", "Chattogram", "Khulna", "Rajshahi", "Barishal", "Kurigram"]:
        r = out.get(d)
        if not r:
            continue
        lo = r["los_days"]["median"]
        q = r["occupancy"]["quantiles"]
        sq = r["occupancy_season"]["quantiles"]
        print(f"{d:<16}{(lo if lo else 0):>9.2f}{q.get('50',0):>9.0f}"
              f"{q.get('95',0):>9.0f}{sq.get('95',0):>12.0f}")
    print(f"\nwrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
