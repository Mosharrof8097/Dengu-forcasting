#!/usr/bin/env python3
"""Export the verified panel for the web application.

The app currently ships invented defaults -- 1,850 cases, 62 a day, 185 beds --
and a client-side fallback that is a fixed Gaussian with a hard-coded per-district
baseline, using neither current cases nor weather. Reviewers called that out, and
they were right: none of it traces back to anything.

This replaces all of it with the real surveillance record, so every number the
interface shows can be followed to a specific DGHS bulletin on a specific date.
Unobserved cells stay null; they are never filled, and the interface is expected
to render them as "no bulletin" rather than as zero.

Output: frontend/data/surveillance.json
"""
import csv, json, os, collections, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "reference")
# the three small lookup tables travel with this repository; only the
# large dataset artifacts are supplied by argument
POP = os.path.join(REF, "districts_bd64.csv")
GRID = GEO = OUT = None

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



OBS = ("OBSERVED", "OBSERVED_ZERO")


def centroids():
    import json as J
    feats = J.load(open(GEO, encoding="utf-8"))["features"]
    acc = collections.defaultdict(lambda: [[], []])
    for f in feats:
        d = f["properties"].get("district_en")
        if not d:
            continue
        g = f["geometry"]
        depth = {"Polygon": 2, "MultiPolygon": 3}.get(g["type"], 2)

        def walk(c, k):
            if k == 0:
                acc[d][0].append(c[0]); acc[d][1].append(c[1])
            else:
                for x in c:
                    walk(x, k - 1)
        walk(g["coordinates"], depth)
    return {d: [round(st.mean(v[1]), 4), round(st.mean(v[0]), 4)]
            for d, v in acc.items()}


def main():
    global GRID, GEO, OUT
    a = _args()
    GRID = _require(os.path.join(a.dataset or "", "grid_v1.csv"), "grid_v1.csv")
    GEO = os.path.join(a.dataset or "", "bd_districts_repaired.geojson")
    OUT = os.path.join(a.out, "surveillance.json")

    rows = list(csv.DictReader(open(GRID, encoding="utf-8")))
    cen = centroids()
    div = {}
    for r in rows:
        div.setdefault(r["district"], r["division"])

    pop = {}
    for r in csv.DictReader(open(POP, encoding="utf-8")):
        pop[r["district_en"]] = None   # filled below if available
    rawpop = os.path.join(REF, "district_population.csv")
    namemap = {r["canonical"]: r["weather_csv"] for r in
               csv.DictReader(open(os.path.join(REF, "source_name_map.csv"),
                                   encoding="utf-8"))}
    if os.path.exists(rawpop):
        pr = {r["District"]: int(r["Population"])
              for r in csv.DictReader(open(rawpop, encoding="utf-8"))}
        for d in div:
            pop[d] = pr.get(namemap.get(d, d)) or pr.get(d)

    # DhakaCity has no polygon of its own -- DGHS reports ঢাকা মহানগর as a unit
    # but it is not an administrative district, so it carries no geometry and no
    # separate census figure. It is placed at the city centre for the map and
    # left without a population, so the interface cannot compute a per-100k rate
    # for it from a denominator that does not exist.
    cen["DhakaCity"] = [23.7806, 90.4074]
    pop["DhakaCity"] = None

    districts = sorted(div)
    di = {d: i for i, d in enumerate(districts)}
    dates = sorted({r["date"] for r in rows})
    ti = {t: i for i, t in enumerate(dates)}

    # cases[date][district], null where there is no observation
    cases = [[None] * len(districts) for _ in dates]
    occ = [[None] * len(districts) for _ in dates]
    status = [[0] * len(districts) for _ in dates]   # 0 none, 1 obs, 2 censored
    SC = {"OBSERVED": 1, "OBSERVED_ZERO": 1, "INTERVAL_CENSORED": 2}
    for r in rows:
        i, j = ti[r["date"]], di[r["district"]]
        status[i][j] = SC.get(r["status"], 0)
        if r["status"] in OBS and r["new_admissions"] not in ("", "None"):
            cases[i][j] = int(r["new_admissions"])
            if r["currently_admitted"] not in ("", "None"):
                occ[i][j] = int(r["currently_admitted"])

    national = [
        (sum(v for v in row if v is not None)
         if any(v is not None for v in row) else None) for row in cases]

    out = {
        "meta": {
            "source": "DGHS daily dengue bulletins, Bangladesh",
            "built_from": "1,674 bulletin PDFs; see dengue64 pipeline",
            # Only the complete years can be compared. 2019 and 2024 are
            # short because bulletins are missing from the source, and
            # claiming 1.00x for them -- as an earlier version of this file
            # did -- overstates what the record supports.
            "validated": "where the bulletin record is complete, national "
                         "annual totals reconstruct to the published DGHS "
                         "figures at 1.00x (2022: 62,084 vs 62,382; 2023: "
                         "321,146 vs 321,179). 2019 and 2024 fall short "
                         "because only 125 and 238 bulletin dates survive, "
                         "not because of extraction error",
            "date_min": dates[0], "date_max": dates[-1],
            "n_dates": len(dates), "n_units": len(districts),
            "note": "null means no bulletin for that district-day. It is not "
                    "zero and must not be drawn as zero.",
        },
        "districts": [
            {"name": d, "division": div[d],
             "latlon": cen.get(d), "population": pop.get(d),
             "is_metro": d == "DhakaCity"}
            for d in districts],
        "dates": dates,
        "cases": cases,
        "occupancy": occ,
        "status": status,
        "national": national,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))

    size = os.path.getsize(OUT) / 1024
    nobs = sum(1 for row in cases for v in row if v is not None)
    nocen = sum(1 for row in status for v in row if v == 2)
    missing_cen = [d for d in districts if cen.get(d) is None]
    print(f"units      {len(districts)}")
    print(f"dates      {len(dates):,}  ({dates[0]} -> {dates[-1]})")
    print(f"observed   {nobs:,} district-days")
    print(f"censored   {nocen:,} (total known, daily split unknown)")
    print(f"centroids  {len(districts)-len(missing_cen)}/{len(districts)}"
          + (f"  missing {missing_cen}" if missing_cen else ""))
    print(f"population {sum(1 for d in districts if pop.get(d))}/{len(districts)}"
          f"  (DhakaCity deliberately null: no separate census denominator)")
    print(f"\nwrote {OUT}  ({size:.0f} KB)")


if __name__ == "__main__":
    main()
